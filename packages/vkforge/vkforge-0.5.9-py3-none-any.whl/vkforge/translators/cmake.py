from vkforge.context import VkForgeContext
from vkforge.mappings import *

def CreateCMake(ctx: VkForgeContext):
    files = [
        FILE.CORE,
        FILE.FUNC,
        FILE.LAYOUT,
        FILE.PIPELINE_C,
        FILE.PIPELINE_H,
        FILE.TYPE,
        FILE.UTIL
    ]
    files = "\n\t".join(files)

    vkIdcontent = ctx.forgeModel.ID.split(" ")
    project = vkIdcontent[0].strip()
    version = vkIdcontent[1].strip()

    content = """\
cmake_minimum_required(VERSION 3.14)

project({project}
    VERSION {version}.0
    DESCRIPTION "Vulkan User-End API Implementation Generator"
    LANGUAGES C
)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED TRUE)

add_compile_definitions(
    $<$<CONFIG:Debug>:DEBUG=1>
    $<$<CONFIG:Release>:NDEBUG=1>
)

add_library(vkforge_deps INTERFACE)

# SDL3 Configuration
find_package(SDL3 REQUIRED)
target_link_libraries(vkforge_deps INTERFACE SDL3::SDL3)

# if SDL3_image CMAKE find doesn't work so you need to copy the libary into your app directory
find_package(SDL3_image REQUIRED)
target_link_libraries(vkforge_deps INTERFACE SDL3_image::SDL3_image)

# Vulkan Configuration
find_package(Vulkan 1.3 REQUIRED)
target_link_libraries(vkforge_deps INTERFACE Vulkan::Vulkan)

add_library(vkforge SHARED
    {files}
)

target_link_libraries(vkforge PUBLIC vkforge_deps)
"""
    return content.format(
        files=files,
        project=project.upper(),
        version=version
    )

def GetCMakeStrings(ctx: VkForgeContext):
    return [
        CreateCMake(ctx),
    ]