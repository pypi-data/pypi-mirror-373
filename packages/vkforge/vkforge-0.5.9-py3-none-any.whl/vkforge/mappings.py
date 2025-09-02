from typing import Any

############################################
# Map Function
############################################


def map_value(mapping: dict, key: str) -> Any:
    if key in mapping:
        return mapping[key]
    return key

def map_dict(mapping: dict, key: str, subkey: str) -> Any:
    if key in mapping:
        dict_value = mapping[key]
        if subkey in dict_value:
            return dict_value[subkey]
    raise ValueError(f"No value found for {key}.{subkey} in map dict")

def map_bool(key:bool)->str:
    if key:
        return "VK_TRUE"
    return "VK_FALSE"


############################################
# Maps
############################################

API_VERSION_MAP = {
    "1.0": "VK_API_VERSION_1_0",
    "1.1": "VK_API_VERSION_1_1",
    "1.2": "VK_API_VERSION_1_2",
    "1.3": "VK_API_VERSION_1_3",
}

MSG_SEVERITY_MAP = {
    "warning": "VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT",
    "info": "VK_DEBUG_UTILS_MESSAGE_SEVERITY_INFO_BIT_EXT",
    "verbose": "VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT",
    "error": "VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT",
}

MSG_TYPE_MAP = {
    "general": "VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT",
    "validation": "VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT",
    "performance": "VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT",
}

SHADER_STAGE_MAP = {
    "vert": "VK_SHADER_STAGE_VERTEX_BIT",
    "frag": "VK_SHADER_STAGE_FRAGMENT_BIT",
    "comp": "VK_SHADER_STAGE_COMPUTE_BIT",
    "geom": "VK_SHADER_STAGE_GEOMETRY_BIT",
    "tesc": "VK_SHADER_STAGE_TESSELLATION_CONTROL_BIT",
    "tese": "VK_SHADER_STAGE_TESSELLATION_EVALUATION_BIT",
    "mesh": "VK_SHADER_STAGE_MESH_BIT_EXT",
    "task": "VK_SHADER_STAGE_TASK_BIT_EXT",
    "rgen": "VK_SHADER_STAGE_RAYGEN_BIT_KHR",
    "rint": "VK_SHADER_STAGE_INTERSECTION_BIT_KHR",
    "rahit": "VK_SHADER_STAGE_ANY_HIT_BIT_KHR",
    "rchit": "VK_SHADER_STAGE_CLOSEST_HIT_BIT_KHR",
    "rmiss": "VK_SHADER_STAGE_MISS_BIT_KHR",
    "rcall": "VK_SHADER_STAGE_CALLABLE_BIT_KHR",
    "mesh_nv": "VK_SHADER_STAGE_MESH_BIT_NV",
    "task_nv": "VK_SHADER_STAGE_TASK_BIT_NV",
}

INPUT_RATE_MAP = {
    "vertex": "VK_VERTEX_INPUT_RATE_VERTEX",
    "instance": "VK_VERTEX_INPUT_RATE_INSTANCE",
}

TOPOLOGY_MAP = {
    "point_list": "VK_PRIMITIVE_TOPOLOGY_POINT_LIST",
    "line_list": "VK_PRIMITIVE_TOPOLOGY_LINE_LIST",
    "line_strip": "VK_PRIMITIVE_TOPOLOGY_LINE_STRIP",
    "triangle_list": "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST",
    "triangle_strip": "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP",
    "triangle_fan": "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_FAN",
    "line_list_with_adjacency": "VK_PRIMITIVE_TOPOLOGY_LINE_LIST_WITH_ADJACENCY",
    "line_strip_with_adjacency": "VK_PRIMITIVE_TOPOLOGY_LINE_STRIP_WITH_ADJACENCY",
    "triangle_list_with_adjacency": "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST_WITH_ADJACENCY",
    "triangle_strip_with_adjacency": "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP_WITH_ADJACENCY",
    "patch_list": "VK_PRIMITIVE_TOPOLOGY_PATCH_LIST",
}

DYNAMIC_STATE_MAP = {
    "viewport": "VK_DYNAMIC_STATE_VIEWPORT",
    "scissor": "VK_DYNAMIC_STATE_SCISSOR",
    "line_width": "VK_DYNAMIC_STATE_LINE_WIDTH",
    "depth_bias": "VK_DYNAMIC_STATE_DEPTH_BIAS",
    "blend_constants": "VK_DYNAMIC_STATE_BLEND_CONSTANTS",
    "depth_bounds": "VK_DYNAMIC_STATE_DEPTH_BOUNDS",
    "stencil_compare_mask": "VK_DYNAMIC_STATE_STENCIL_COMPARE_MASK",
    "stencil_write_mask": "VK_DYNAMIC_STATE_STENCIL_WRITE_MASK",
    "stencil_reference": "VK_DYNAMIC_STATE_STENCIL_REFERENCE",
    "cull_mode": "VK_DYNAMIC_STATE_CULL_MODE",
    "front_face": "VK_DYNAMIC_STATE_FRONT_FACE",
    "primitive_topology": "VK_DYNAMIC_STATE_PRIMITIVE_TOPOLOGY",
    "viewport_with_count": "VK_DYNAMIC_STATE_VIEWPORT_WITH_COUNT",
    "scissor_with_count": "VK_DYNAMIC_STATE_SCISSOR_WITH_COUNT",
    "vertex_input_binding_stride": "VK_DYNAMIC_STATE_VERTEX_INPUT_BINDING_STRIDE",
    "depth_test_enable": "VK_DYNAMIC_STATE_DEPTH_TEST_ENABLE",
    "depth_write_enable": "VK_DYNAMIC_STATE_DEPTH_WRITE_ENABLE",
    "depth_compare_op": "VK_DYNAMIC_STATE_DEPTH_COMPARE_OP",
    "depth_bounds_test_enable": "VK_DYNAMIC_STATE_DEPTH_BOUNDS_TEST_ENABLE",
    "stencil_test_enable": "VK_DYNAMIC_STATE_STENCIL_TEST_ENABLE",
    "stencil_op": "VK_DYNAMIC_STATE_STENCIL_OP",
    "rasterizer_discard_enable": "VK_DYNAMIC_STATE_RASTERIZER_DISCARD_ENABLE",
    "depth_bias_enable": "VK_DYNAMIC_STATE_DEPTH_BIAS_ENABLE",
    "primitive_restart_enable": "VK_DYNAMIC_STATE_PRIMITIVE_RESTART_ENABLE",
}

DESCRIPTOR_TYPE_MAP = {
    # VK abbriations
    "sampler": "VK_DESCRIPTOR_TYPE_SAMPLER",
    "combined_image_sampler": "VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER",
    "sampled_image": "VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE",
    "storage_image": "VK_DESCRIPTOR_TYPE_STORAGE_IMAGE",
    "uniform_texel_buffer": "VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER",
    "storage_texel_buffer": "VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER",
    "uniform_buffer": "VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER",
    "storage_buffer": "VK_DESCRIPTOR_TYPE_STORAGE_BUFFER",
    "uniform_buffer_dynamic": "VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC",
    "storage_buffer_dynamic": "VK_DESCRIPTOR_TYPE_STORAGE_BUFFER_DYNAMIC",
    "input_attachment": "VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT",
    "inline_uniform_block": "VK_DESCRIPTOR_TYPE_INLINE_UNIFORM_BLOCK",
    "acceleration_structure": "VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR",
    "acceleration_structure_nv": "VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_NV",
    "sample_weight_image": "VK_DESCRIPTOR_TYPE_SAMPLE_WEIGHT_IMAGE_QCOM",
    "block_match_image": "VK_DESCRIPTOR_TYPE_BLOCK_MATCH_IMAGE_QCOM",
    "tensor": "VK_DESCRIPTOR_TYPE_TENSOR_ARM",
    "mutable": "VK_DESCRIPTOR_TYPE_MUTABLE_EXT",
    "partitioned_acceleration_structure": "VK_DESCRIPTOR_TYPE_PARTITIONED_ACCELERATION_STRUCTURE_NV",
    
    # GLSL types
    "sampler2D": "VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER",
    "sampler1D": "VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER",
    "sampler3D": "VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER",
    "samplerCube": "VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER",
    "sampler2DArray": "VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER",
    "sampler2DShadow": "VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER",
    "samplerCubeShadow": "VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER",
    "sampler2DMS": "VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER",
    
    "texture2D": "VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE",
    "texture1D": "VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE",
    "texture3D": "VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE",
    "textureCube": "VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE",
    "texture2DArray": "VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE",
    
    "image2D": "VK_DESCRIPTOR_TYPE_STORAGE_IMAGE",
    "image1D": "VK_DESCRIPTOR_TYPE_STORAGE_IMAGE",
    "image3D": "VK_DESCRIPTOR_TYPE_STORAGE_IMAGE",
    "imageCube": "VK_DESCRIPTOR_TYPE_STORAGE_IMAGE",
    "image2DArray": "VK_DESCRIPTOR_TYPE_STORAGE_IMAGE",
    
    "subpassInput": "VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT",
    "subpassInputMS": "VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT",
    
    # Buffer types
    "ubo": "VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER",
    "uniform_buffer": "VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER",
    "ssbo": "VK_DESCRIPTOR_TYPE_STORAGE_BUFFER",
    "storage_buffer": "VK_DESCRIPTOR_TYPE_STORAGE_BUFFER",
    
    # Special types
    "atomic_uint": "VK_DESCRIPTOR_TYPE_STORAGE_BUFFER",
    "buffer": "VK_DESCRIPTOR_TYPE_STORAGE_BUFFER",
    
    # Shader storage types
    "accelerationStructure": "VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR",
    
    # GLSL legacy types
    "gl_PerVertex": "VK_DESCRIPTOR_TYPE_MAX_ENUM",  # Built-in, not a descriptor type

    # Reflection
    "ubos": "VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER",
    "ssbos": "VK_DESCRIPTOR_TYPE_STORAGE_BUFFER",
    "subpass_inputs": "VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT",
}

GLSL_TYPE_MAP = {
    # Float types
    "float": {"size": "sizeof(float) * 1", "format": "VK_FORMAT_R32_SFLOAT"},
    "vec2": {"size": "sizeof(float) * 2", "format": "VK_FORMAT_R32G32_SFLOAT"},
    "vec3": {"size": "sizeof(float) * 3", "format": "VK_FORMAT_R32G32B32_SFLOAT"},
    "vec4": {"size": "sizeof(float) * 4", "format": "VK_FORMAT_R32G32B32A32_SFLOAT"},
    
    # Double types
    "double": {"size": "sizeof(double) * 1", "format": "VK_FORMAT_R64_SFLOAT"},
    "dvec2": {"size": "sizeof(double) * 2", "format": "VK_FORMAT_R64G64_SFLOAT"},
    "dvec3": {"size": "sizeof(double) * 3", "format": "VK_FORMAT_R64G64B64_SFLOAT"},
    "dvec4": {"size": "sizeof(double) * 4", "format": "VK_FORMAT_R64G64B64A64_SFLOAT"},
    
    # Integer types
    "int": {"size": "sizeof(int32_t) * 1", "format": "VK_FORMAT_R32_SINT"},
    "ivec2": {"size": "sizeof(int32_t) * 2", "format": "VK_FORMAT_R32G32_SINT"},
    "ivec3": {"size": "sizeof(int32_t) * 3", "format": "VK_FORMAT_R32G32B32_SINT"},
    "ivec4": {"size": "sizeof(int32_t) * 4", "format": "VK_FORMAT_R32G32B32A32_SINT"},
    
    # Unsigned integer types
    "uint": {"size": "sizeof(uint32_t) * 1", "format": "VK_FORMAT_R32_UINT"},
    "uvec2": {"size": "sizeof(uint32_t) * 2", "format": "VK_FORMAT_R32G32_UINT"},
    "uvec3": {"size": "sizeof(uint32_t) * 3", "format": "VK_FORMAT_R32G32B32_UINT"},
    "uvec4": {"size": "sizeof(uint32_t) * 4", "format": "VK_FORMAT_R32G32B32A32_UINT"},
    
    # Matrix types (column-major, each column consumes a location)
    "mat2": {"size": "sizeof(float) * 4", "format": "VK_FORMAT_R32G32_SFLOAT", "columns": 2},
    "mat3": {"size": "sizeof(float) * 9", "format": "VK_FORMAT_R32G32B32_SFLOAT", "columns": 3},
    "mat4": {"size": "sizeof(float) * 16", "format": "VK_FORMAT_R32G32B32A32_SFLOAT", "columns": 4},
    "mat2x3": {"size": "sizeof(float) * 6", "format": "VK_FORMAT_R32G32B32_SFLOAT", "columns": 2},
    "mat2x4": {"size": "sizeof(float) * 8", "format": "VK_FORMAT_R32G32B32A32_SFLOAT", "columns": 2},
    "mat3x2": {"size": "sizeof(float) * 6", "format": "VK_FORMAT_R32G32_SFLOAT", "columns": 3},
    "mat3x4": {"size": "sizeof(float) * 12", "format": "VK_FORMAT_R32G32B32A32_SFLOAT", "columns": 3},
    "mat4x2": {"size": "sizeof(float) * 8", "format": "VK_FORMAT_R32G32_SFLOAT", "columns": 4},
    "mat4x3": {"size": "sizeof(float) * 12", "format": "VK_FORMAT_R32G32B32_SFLOAT", "columns": 4},
    
    # Double matrix types
    "dmat2": {"size": "sizeof(double) * 4", "format": "VK_FORMAT_R64G64_SFLOAT", "columns": 2},
    "dmat3": {"size": "sizeof(double) * 9", "format": "VK_FORMAT_R64G64B64_SFLOAT", "columns": 3},
    "dmat4": {"size": "sizeof(double) * 16", "format": "VK_FORMAT_R64G64B64A64_SFLOAT", "columns": 4},
    "dmat2x3": {"size": "sizeof(double) * 6", "format": "VK_FORMAT_R64G64B64_SFLOAT", "columns": 2},
    "dmat2x4": {"size": "sizeof(double) * 8", "format": "VK_FORMAT_R64G64B64A64_SFLOAT", "columns": 2},
    "dmat3x2": {"size": "sizeof(double) * 6", "format": "VK_FORMAT_R64G64_SFLOAT", "columns": 3},
    "dmat3x4": {"size": "sizeof(double) * 12", "format": "VK_FORMAT_R64G64B64A64_SFLOAT", "columns": 3},
    "dmat4x2": {"size": "sizeof(double) * 8", "format": "VK_FORMAT_R64G64_SFLOAT", "columns": 4},
    "dmat4x3": {"size": "sizeof(double) * 12", "format": "VK_FORMAT_R64G64B64_SFLOAT", "columns": 4},
}

############################################
# Keys
############################################

from enum import Enum

class StringEnum(str, Enum):
    def __format__(self, format_spec):
        return format(self.value, format_spec)

class SHADER(StringEnum):
    MODE      = "mode"
    ENTRYNAME = "entryname"
    BINPATH   = "binary_path"
    SRCPATH   = "source_path"
    REFLECT   = "reflect"
    LIST      = "shader_list"
    COMBO     = "shader_combinations"

class LAYOUT(StringEnum):
    STAGES          = "stages"
    SET             = "set"
    BIND            = "binding"
    TYPE            = "type"
    COUNT           = "count"
    DSET_LAYOUT     = "descriptorset_layouts"
    DSET_REF        = "descriptorset_layout_references"
    PIPELINE_LAYOUT = "pipeline_layouts"
    RAW_LAYOUT      = "raw_layouts"
    LAYOUTS         = "layouts"
    REFERENCES      = "references"

class REFLECT(StringEnum):
    TEXTURE       = "textures"
    SAMPLER_IMAGE = "separate_images"
    SAMPLER       = "separate_samplers"
    IMAGE         = "images"
    SSBO          = "ssbos"
    UBO           = "ubos"
    SUBPASS       = "subpass_inputs"
    INPUT         = "inputs"
    OUTPUT        = "outputs"
    ENTRYPOINT    = "entryPoints"
    TYPE          = "types"

class ATTR(StringEnum):
    LOCATION = "location"
    BINDING  = "binding"
    FORMAT   = "format"
    OFFSET   = "offset"
    SIZE     = "size"

class MEMBER(StringEnum):
    TYPE = "type"
    NAME = "name"
    ARRAY = "array"
    ARRAY_LITERAL = "array_size_is_literal"
    SET = "set"
    BIND = "binding"

class FILE(StringEnum):
    CORE       = "vkforge_core.c"
    UTIL       = "vkforge_utils.c"
    TYPE       = "vkforge_typedecls.h"
    FUNC       = "vkforge_funcdecls.h"
    PIPELINE_C = "vkforge_pipelines.c"
    PIPELINE_H = "vkforge_pipelines.h"
    LAYOUT     = "vkforge_layout.c"
    CMAKE      = "CMakeLists.txt"

