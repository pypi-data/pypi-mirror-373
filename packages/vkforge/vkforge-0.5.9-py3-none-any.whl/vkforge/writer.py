import os
from pathlib import Path
from vkforge.context import VkForgeContext
from vkforge.translators import *
from vkforge.mappings import *

TYPE_INCLUDE = f'#include "{FILE.TYPE}"'
FUNC_INCLUDE = f'#include "{FILE.FUNC}"'

def IncludeStandardDefinitionHeaders():
    return """\
#include <assert.h>
#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>
#include <SDL3/SDL_vulkan.h>
"""

def IncludeStandardDeclarationHeaders():
    return """\
#include <vulkan/vulkan.h>
#include <SDL3/SDL.h>
"""

def Write_Plain_File(ctx: VkForgeContext, filename, stringFunc):
    output = "\n".join(stringFunc(ctx))

    filepath = Path(ctx.sourceDir) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if (
        ctx.forgeModel.GenerateOnce 
        and filename in ctx.forgeModel.GenerateOnce 
        and filepath.exists()
    ):
        print(f"SKIPPED (GenerateOnce): {filepath}")
    else:
        with open(filepath, "w") as f:
            f.write(output)
            print(f"GENERATED: {filepath}")


def Write_C_Definition_Module(ctx: VkForgeContext, filename, stringFunc, additionalIncludes = []):
    content = """\
{standard_includes}
{type_include}
{func_include}{additionalIncludes}

{user_defined_includes}
{user_defined_insertions}

{code}

"""
    if additionalIncludes:
        additionalIncludes = "\n" + "\n".join([GetInclude(x) for x in additionalIncludes])
    else:
        additionalIncludes = ""

    output = content.format(
        standard_includes=IncludeStandardDefinitionHeaders(),
        type_include=TYPE_INCLUDE,
        func_include=FUNC_INCLUDE,
        additionalIncludes=additionalIncludes,
        user_defined_includes=GetUserDefinedIncludes(ctx),
        user_defined_insertions=GetUserDefinedInsertions(ctx),
        code="\n".join(stringFunc(ctx)),
    )

    filepath = Path(ctx.sourceDir) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if (
        ctx.forgeModel.GenerateOnce 
        and filename in ctx.forgeModel.GenerateOnce 
        and filepath.exists()
    ):
        print(f"SKIPPED (GenerateOnce): {filepath}")
    else:
        with open(filepath, "w") as f:
            f.write(output)
            print(f"GENERATED: {filepath}")


def Write_C_Declaration_Module(ctx: VkForgeContext, filename, stringFunc):
    content = """\
#pragma once

{standard_includes}
{forge_includes}

#ifdef __cplusplus
extern "C" {{
#endif

{code}

#ifdef __cplusplus
}}
#endif
"""
    forge_includes = ""
    if filename != FILE.TYPE:
        forge_includes += f"#include \"{FILE.TYPE}\""
    
    output = content.format(
        standard_includes=IncludeStandardDeclarationHeaders(),
        forge_includes=forge_includes,
        code="\n".join(stringFunc(ctx)),
    )

    filepath = Path(ctx.sourceDir) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if (
        ctx.forgeModel.GenerateOnce 
        and filename in ctx.forgeModel.GenerateOnce 
        and filepath.exists()
    ):
        print(f"SKIPPED (GenerateOnce): {filepath}")
    else:
        with open(filepath, "w") as f:
            f.write(output)
            print(f"GENERATED: {filepath}")

def GetInclude(name:str)->str:
    if "#include" in name:
        return name
    else:
        if name.startswith('<') and name.endswith('>'):
            return f"#include {name}"
        else:
            return f'#include "{name}"'

def GetUserDefinedIncludes(ctx: VkForgeContext) -> str:
    if ctx.forgeModel.UserDefined:
        if ctx.forgeModel.UserDefined.includes:
            includes = []
            for header in ctx.forgeModel.UserDefined.includes:
                includes.append(GetInclude(header))
            
            return '\n'.join(includes) + '\n'
    return "/** NO USER INCLUDES **/"

def GetUserDefinedInsertions(ctx: VkForgeContext) -> str:
    if ctx.forgeModel.UserDefined:
        if ctx.forgeModel.UserDefined.insertions:
            insertions = ctx.forgeModel.UserDefined.insertions
            return '\n'.join(insertions) + '\n'
    return "/** NO USER DECLARATIONS **/"

def Generate(ctx: VkForgeContext):
    Write_C_Definition_Module(ctx, FILE.CORE, GetCoreStrings)
    Write_C_Definition_Module(ctx, FILE.UTIL, GetUtilStrings, additionalIncludes=["<stdlib.h>", "<SDL3_image/SDL_image.h>"])
    Write_C_Definition_Module(ctx, FILE.LAYOUT, GetLayoutStrings, additionalIncludes=[FILE.PIPELINE_H])
    Write_C_Definition_Module(ctx, FILE.PIPELINE_C, GetPipelineStrings)
    Write_C_Declaration_Module(ctx, FILE.TYPE, GetTypeStrings)
    Write_C_Declaration_Module(ctx, FILE.FUNC, GetFuncStrings)
    Write_C_Declaration_Module(ctx, FILE.PIPELINE_H, GetPipelineDeclarationStrings)
    Write_Plain_File(ctx, FILE.CMAKE, GetCMakeStrings)
