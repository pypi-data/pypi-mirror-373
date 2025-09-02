from vkforge.context import VkForgeContext
from vkforge.mappings import *
from .core import GetCoreStrings
from .util import GetUtilStrings
from .layout import GetLayoutStrings
import re

def CreateVoidEnum(ctx: VkForgeContext) -> str:
    content = """\
#define VKFORGE_VOID_ENUM(Var, Type, Func, Sizelimit, ...) \\
    Type Var##_buffer[Sizelimit] = {{0}}; uint32_t Var##_count = 0; do {{ \\
    Func(__VA_ARGS__, &Var##_count, 0); \\
    Var##_count = (Var##_count < Sizelimit) ? Var##_count : Sizelimit; \\
    Func(__VA_ARGS__, &Var##_count, Var##_buffer); \\
}} while(0)
"""
    output = content.format()

    return output

def CreateEnum(ctx: VkForgeContext) -> str:
    content = """\
#define VKFORGE_ENUM(Var, Type, Func, Sizelimit, ...) \\
    Type Var##_buffer[Sizelimit] = {{0}}; uint32_t Var##_count = 0; do {{ \\
    Func(__VA_ARGS__, &Var##_count, 0); \\
    Var##_count = (Var##_count < Sizelimit) ? Var##_count : Sizelimit; \\
    Func(__VA_ARGS__, &Var##_count, Var##_buffer); \\
}} while(0)
"""
    output = content.format()

    return output

def extract_function_declarations(content: str) -> list[str]:
    """Extract all function declarations using regex, including pointer return types."""
    # This pattern is stricter to avoid catastrophic backtracking.
    # - Return type: sequences of identifiers/keywords + optional pointer stars/qualifiers
    # - Stops before function name (group 2)
    pattern = r"""
        ^\s*
        (                               # Group 1: return type
            (?:[a-zA-Z_]\w*             # Identifier (type or qualifier)
                (?:\s+[a-zA-Z_]\w*)*    # More identifiers (e.g., 'unsigned long')
            )
            (?:\s*\*+\s*(?:const\s*)?)* # Optional pointer stars with optional const
        )
        \s+                             # Space between type and name
        ([a-zA-Z_]\w*)                  # Group 2: function name
        \s*
        \(                              # Opening parenthesis
        ([^)]*)                         # Group 3: parameters
        \)                              # Closing parenthesis
        \s*
        (?:__attribute__\s*\(\([^)]*\)\)\s*)? # Optional attributes
        (?={)                           # Lookahead for opening brace
    """

    functions = []
    for match in re.finditer(pattern, content, re.VERBOSE | re.MULTILINE):
        return_type = match.group(1).strip()
        name = match.group(2).strip()
        params = match.group(3).strip()

        if return_type.startswith("static "):
            continue

        decl = f"{return_type} {name}({params});"
        
        if decl.startswith("else "):
            continue

        functions.append(decl)

    return functions



def CreateDeclarations(ctx: VkForgeContext) -> str:
    """Generate ONLY function forward declarations using robust regex parsing."""
    declarations = "// Function Declarations\n\n"
    
    # Collect all content from all modules
    all_content = []
    all_content.extend(GetCoreStrings(ctx))
    all_content.extend(GetUtilStrings(ctx))
    all_content.extend(GetLayoutStrings(ctx))
    
    # Process each content block
    for content in all_content:
        for decl in extract_function_declarations(content):
            declarations += decl + "\n\n"
    
    return declarations

def GetFuncStrings(ctx: VkForgeContext):
    return [
        CreateEnum(ctx),
        CreateVoidEnum(ctx),
        CreateDeclarations(ctx)
    ]