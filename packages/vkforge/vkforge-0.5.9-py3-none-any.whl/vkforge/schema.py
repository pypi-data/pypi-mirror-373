# VkForge Config Schema
# (c) Alrick Grandison, Algodal

# This schema defines the default configuration layout for a graphics renderer.
# While VkForge can support Compute GPU functionalities, its primary focus is
# graphics rendering.

# Note that VkForge does not allow customization of the following:
# - Command buffers and synchronization are managed internally by VkForge.
#   If you require full control over command buffer handling and rendering
#   synchronization, VkForge may not be the right tool for your needs.
#
#   VkForge allocates two command buffers: one for copying and one for drawing.
#   Both command buffers remain active for the entire lifetime of the application.
#
#   Rendering synchronization is handled using semaphores for command ordering,
#   fence status checks via VkGetFenceStatus, and a custom internal VkForge
#   state system. Together, these mechanisms ensure your renderer runs as fast
#   as possible without blocking.
#
#   Importantly, VkForge never calls any wait functions during rendering.
#   Wait functions are only called during application shutdown.
#
# - Only one queue is supported by VkForge even if the physical device can support
#   multiple queues. That queue must support both graphics and transfer operations.
#
# Contributions are welcomed from the community to make VkForge more versatile
# and support other types of implementation of Vulkan.

from pydantic import (
    BaseModel, Field, field_validator, model_validator, PrivateAttr
)
from typing import List, Optional, Literal, Union
import re
from .mappings import *

class UserDefinedModel(BaseModel):
    includes: Optional[List[str]] = Field(
        default=None,
        description="#include of User headers. List the header filenames. If it is a standard header "
        "wrap in angle brackets. Eg: - MyHeader - <MyStandardHeader>. It will be generated as #include fileName"
    )
    insertions: Optional[List[str]] = Field(
        default=None,
        description="Inserts user defined strings into the generated code. The code is expected to be "
        "declaration type code because it will be included in the generated headers."
        "There is no restriction on what it can be. You are responsible for it to compile. "
        "Eg: - struct MyStruct; - extern int MyVar;"
    )

class VkInstanceCreateInfoModel(BaseModel):
    
    useValidationFeatureEnableBestPracticesEXT: Optional[bool] = Field(
        default=False,
        description="Set to True to enable VK_VALIDATION_FEATURE_ENABLE_BEST_PRACTICES_EXT"
    )

class VkApplicationInfoModel(BaseModel):
    apiVersion: Optional[
        Literal[
            "VK_API_VERSION_1_3",
            "1.3",
        ]
    ] = Field(default="VK_API_VERSION_1_3", description="Vulkan API version to target.")
    pEngineName: Optional[str] = Field(
        default="VkForge", description="Name of the engine."
    )
    pApplicationName: Optional[str] = Field(
        default="VkForge Renderer", description="Name of the application."
    )
    applicationVersion: Optional[int] = 0
    engineVersion: Optional[int] = 0

class VkDebugUtilsMessengerCreateInfoEXTModel(BaseModel):
    messageSeverity: Optional[
        List[
            Literal[
                "VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT",
                "VK_DEBUG_UTILS_MESSAGE_SEVERITY_INFO_BIT_EXT",
                "VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT",
                "VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT",
                "warning",
                "info",
                "verbose",
                "error",
            ]
        ]
    ] = Field(
        default=[
            "VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT",
            "VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT",
        ],
        description="List of message severities to enable for debug messenger.",
    )
    messageType: Optional[
        List[
            Literal[
                "VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT",
                "VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT",
                "VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT",
                "general",
                "validation",
                "performance",
            ]
        ]
    ] = Field(
        default=[
            "VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT",
            "VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT",
            "VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT",
        ],
        description="List of message types to enable for debug messenger.",
    )

class VkPhysicalDeviceFeaturesModel(BaseModel):
    robustBufferAccess: Optional[bool] = False
    fullDrawIndexUint32: Optional[bool] = False
    imageCubeArray: Optional[bool] = False
    independentBlend: Optional[bool] = False
    geometryShader: Optional[bool] = False
    tessellationShader: Optional[bool] = False
    sampleRateShading: Optional[bool] = False
    dualSrcBlend: Optional[bool] = False
    logicOp: Optional[bool] = False
    multiDrawIndirect: Optional[bool] = False
    drawIndirectFirstInstance: Optional[bool] = False
    depthClamp: Optional[bool] = False
    depthBiasClamp: Optional[bool] = False
    fillModeNonSolid: Optional[bool] = False
    depthBounds: Optional[bool] = False
    wideLines: Optional[bool] = False
    largePoints: Optional[bool] = False
    alphaToOne: Optional[bool] = False
    multiViewport: Optional[bool] = False
    samplerAnisotropy: Optional[bool] = False
    textureCompressionETC2: Optional[bool] = False
    textureCompressionASTC_LDR: Optional[bool] = False
    textureCompressionBC: Optional[bool] = False
    occlusionQueryPrecise: Optional[bool] = False
    pipelineStatisticsQuery: Optional[bool] = False
    vertexPipelineStoresAndAtomics: Optional[bool] = False
    fragmentStoresAndAtomics: Optional[bool] = False
    shaderTessellationAndGeometryPointSize: Optional[bool] = False
    shaderImageGatherExtended: Optional[bool] = False
    shaderStorageImageExtendedFormats: Optional[bool] = False
    shaderStorageImageMultisample: Optional[bool] = False
    shaderStorageImageReadWithoutFormat: Optional[bool] = False
    shaderStorageImageWriteWithoutFormat: Optional[bool] = False
    shaderUniformBufferArrayDynamicIndexing: Optional[bool] = False
    shaderSampledImageArrayDynamicIndexing: Optional[bool] = False
    shaderStorageBufferArrayDynamicIndexing: Optional[bool] = False
    shaderStorageImageArrayDynamicIndexing: Optional[bool] = False
    shaderClipDistance: Optional[bool] = False
    shaderCullDistance: Optional[bool] = False
    shaderFloat64: Optional[bool] = False
    shaderInt64: Optional[bool] = False
    shaderInt16: Optional[bool] = False
    shaderResourceResidency: Optional[bool] = False
    shaderResourceMinLod: Optional[bool] = False
    sparseBinding: Optional[bool] = False
    sparseResidencyBuffer: Optional[bool] = False
    sparseResidencyImage2D: Optional[bool] = False
    sparseResidencyImage3D: Optional[bool] = False
    sparseResidency2Samples: Optional[bool] = False
    sparseResidency4Samples: Optional[bool] = False
    sparseResidency8Samples: Optional[bool] = False
    sparseResidency16Samples: Optional[bool] = False
    sparseResidencyAliased: Optional[bool] = False
    variableMultisampleRate: Optional[bool] = False
    inheritedQueries: Optional[bool] = False


class VkDeviceCreateInfoModel(BaseModel):
    ppEnabledExtensionNames: Optional[List[str]] = Field(
        default_factory=lambda: ["VK_KHR_swapchain"],
        description='List device entensions. "VK_KHR_swapchain" extension is always required.',
    )

    PhysicalDeviceFeatures: Optional[VkPhysicalDeviceFeaturesModel] = Field(
        default=None, description="Boolean indicators of all the features to be enabled"
    )

    @field_validator("ppEnabledExtensionNames")
    def ensure_swapchain_extension(cls, v):
        if v is None or len(v) == 0:
            raise ValueError("VK_KHR_swapchain is required in ppEnabledExtensionNames!")
        elif "VK_KHR_swapchain" not in v:
            raise ValueError("VK_KHR_swapchain is required in ppEnabledExtensionNames!")
        return v


class VkShaderModuleModel(BaseModel):
    path: str = Field(
        ...,
        description="Path to the shader binary or shader GLSL source. "
        "The file must have the .spv or glsl (.vert, .frag, .geom, etc) extensions. "
        "If the shader path provided is a source, then VkForge will utilize glslValidator "
        "to compile the shader. The mode and entrypoint is extracted from the "
        "compiled shader.",
    )

class VkVertexInputBindingDescriptionModel(BaseModel):
    stride: Union[str, int] = Field(
        ...,
        description="User defined type name, `sizeof(...)` string, or literal integer stride size.",
    )
    _stride_kind: Optional[Literal["TYPE", "SIZEOF", "INT", "CALC"]] = PrivateAttr(default=None)

    stride_members: Optional[List[str]] = Field(
        default=None,
        description="List of all members of the type in declaration order. If you omit this, then VkForge will attempt to calculate the offset. Otherwise, VkForge will use the listed members and the type to get the offset. The name must match the type used in the stride",
    )
    input_rate: Optional[Literal[
        "VK_VERTEX_INPUT_RATE_VERTEX",
        "VK_VERTEX_INPUT_RATE_INSTANCE",
        "vertex", 
        "instance"
    ]] = Field(
        default="VK_VERTEX_INPUT_RATE_VERTEX", description="Input rate for the binding."
    )
    first_location: int = Field(
        ..., description="First location index in the shader input."
    )

    @property
    def stride_kind(self):
        return self._stride_kind

    @model_validator(mode="after")
    def validate_stride_kind(self):
        if isinstance(self.stride, int):
            self._stride_kind = "INT"

        elif isinstance(self.stride, str):
            s = self.stride.strip()

            # Match SIZEOF
            sizeof_pattern = r"sizeof\s*\(?\s*\w+\s*\)?"
            type_pattern = r"[A-Za-z][A-Za-z0-9_]*"
            int_pattern = r"\d+"

            # Check pure SIZEOF
            if re.fullmatch(sizeof_pattern, s):
                self._stride_kind = "SIZEOF"

            # Check pure TYPE
            elif re.fullmatch(type_pattern, s):
                self._stride_kind = "TYPE"

            # Check CALC:
            # starts with int or SIZEOF, followed by an operator (+ - * /), then rest
            elif re.fullmatch(
                rf"(?:{int_pattern}|{sizeof_pattern})\s*[\%\+\-\*/]\s*.+", s
            ):
                self._stride_kind = "CALC"

            else:
                raise ValueError(
                    f"Invalid stride string: '{self.stride}'. "
                    "Must be sizeof(Type), valid C type name, integer, "
                    "or calculation starting with integer/SIZEOF."
                )

        else:
            raise ValueError(f"Invalid stride type: {type(self.stride)}")

        return self


    @model_validator(mode="after")
    def validate_stride_members(self):
        if self.stride_members is not None and self._stride_kind != "TYPE":
            raise ValueError(
                "If stride_members is provided, stride must be a typenot a literal int or sizeof(...) or expression. It must be a Type!"
            )
        return self


class VkPipelineInputAssemblyStateCreateInfoModel(BaseModel):
    topology: Optional[
        Literal[
            "VK_PRIMITIVE_TOPOLOGY_POINT_LIST",
            "VK_PRIMITIVE_TOPOLOGY_LINE_LIST",
            "VK_PRIMITIVE_TOPOLOGY_LINE_STRIP",
            "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST",
            "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP",
            "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_FAN",
            "VK_PRIMITIVE_TOPOLOGY_LINE_LIST_WITH_ADJACENCY",
            "VK_PRIMITIVE_TOPOLOGY_LINE_STRIP_WITH_ADJACENCY",
            "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST_WITH_ADJACENCY",
            "VK_PRIMITIVE_TOPOLOGY_TRIANGLE_STRIP_WITH_ADJACENCY",
            "VK_PRIMITIVE_TOPOLOGY_PATCH_LIST",
            "point_list",
            "line_list",
            "line_strip",
            "triangle_list",
            "triangle_strip",
            "triangle_fan",
            "line_list_with_adjacency",
            "line_strip_with_adjacency",
            "triangle_list_with_adjacency",
            "triangle_strip_with_adjacency",
            "patch_list",
        ]
    ] = Field(
        default="VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST",
        description="Primitive topology for input assembly.",
    )


class VkPipelineRasterizationStateCreateInfoModel(BaseModel):
    polygonMode: Optional[str] = Field(
        default="VK_POLYGON_MODE_FILL", description="Polygon mode for rasterization."
    )
    cullMode: Optional[str] = Field(
        default="VK_CULL_MODE_NONE", description="Face culling mode."
    )
    frontFace: Optional[str] = Field(
        default="VK_FRONT_FACE_COUNTER_CLOCKWISE",
        description="Front face winding order.",
    )
    lineWidth: Optional[float] = Field(
        default=1.0, description="Width of rasterized line."
    )
    depthClampEnable: Optional[bool] = Field(
        default=False, description="Enables depth clamping."
    )
    rasterizerDiscardEnable: Optional[bool] = Field(
        default=False, description="Discard primitives before rasterization."
    )
    depthBiasEnable: Optional[bool] = Field(
        default=False, description="Enable depth bias during rasterization."
    )
    depthBiasConstantFactor: Optional[float] = Field(
        default=0, description="Constant depth bias factor."
    )
    depthBiasClamp: Optional[float] = Field(
        default=0, description="Maximum depth bias of a fragment."
    )
    depthBiasSlopeFactor: Optional[float] = Field(
        default=0, description="Slope factor applied to depth bias."
    )

class VkPipelineMultisampleStateCreateInfoModel(BaseModel):
    rasterizationSamples: Optional[str] = Field(
        default="VK_SAMPLE_COUNT_1_BIT",
        description="Number of samples used for rasterization"
    )
    sampleShadingEnable: Optional[bool] = Field(
        default=False,
        description="Enable sample shading"
    )
    minSampleShading: Optional[float] = Field(
        default=0.0,
        description="Minimum fraction of sample shading"
    )
    pSampleMask: Optional[List[str]] = Field(
        default=None,
        description="Array of sample masks"
    )
    alphaToCoverageEnable: Optional[bool] = Field(
        default=False,
        description="Enable alpha to coverage"
    )
    alphaToOneEnable: Optional[bool] = Field(
        default=False,
        description="Enable alpha to one"
    )

class VkPipelineColorBlendAttachmentStateModel(BaseModel):
    blendEnable: Optional[bool] = Field(
        default=True,
        description="Enable blending"
    )
    srcColorBlendFactor: Optional[str] = Field(
        default="VK_BLEND_FACTOR_SRC_ALPHA",
        description="Source color blend factor"
    )
    dstColorBlendFactor: Optional[str] = Field(
        default="VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA",
        description="Destination color blend factor"
    )
    colorBlendOp: Optional[str] = Field(
        default="VK_BLEND_OP_ADD",
        description="Color blend operation"
    )
    srcAlphaBlendFactor: Optional[str] = Field(
        default="VK_BLEND_FACTOR_ONE",
        description="Source alpha blend factor"
    )
    dstAlphaBlendFactor: Optional[str] = Field(
        default="VK_BLEND_FACTOR_ZERO",
        description="Destination alpha blend factor"
    )
    alphaBlendOp: Optional[str] = Field(
        default="VK_BLEND_OP_ADD",
        description="Alpha blend operation"
    )
    colorWriteMask: Optional[str] = Field(
        default="VK_COLOR_COMPONENT_R_BIT | VK_COLOR_COMPONENT_G_BIT | VK_COLOR_COMPONENT_B_BIT | VK_COLOR_COMPONENT_A_BIT",
        description="Color write mask"
    )

class VkPipelineColorBlendStateCreateInfoModel(BaseModel):
    logicOpEnable: Optional[bool] = Field(
        default=False,
        description="Enable logical operation"
    )
    logicOp: Optional[str] = Field(
        default="VK_LOGIC_OP_COPY",
        description="Logical operation to apply"
    )
    attachments: Optional[List[VkPipelineColorBlendAttachmentStateModel]] = Field(
        default_factory=lambda: [VkPipelineColorBlendAttachmentStateModel()],
        description="Array of color blend attachment states"
    )
    blendConstants: Optional[List[float]] = Field(
        default=[0.0, 0.0, 0.0, 0.0],
        description="Blend constants for RGBA"
    )

class VkPipelineDepthStencilStateCreateInfoModel(BaseModel):
    depthTestEnable: Optional[bool] = Field(
        default=False,
        description="Enable depth testing"
    )
    depthWriteEnable: Optional[bool] = Field(
        default=False,
        description="Enable depth writes"
    )
    depthCompareOp: Optional[str] = Field(
        default="VK_COMPARE_OP_LESS",
        description="Depth comparison operator"
    )
    depthBoundsTestEnable: Optional[bool] = Field(
        default=False,
        description="Enable depth bounds test"
    )
    stencilTestEnable: Optional[bool] = Field(
        default=False,
        description="Enable stencil testing"
    )
    front: Optional[dict] = Field(
        default=None,
        description="Front stencil state"
    )
    back: Optional[dict] = Field(
        default=None,
        description="Back stencil state"
    )
    minDepthBounds: Optional[float] = Field(
        default=0.0,
        description="Minimum depth bounds"
    )
    maxDepthBounds: Optional[float] = Field(
        default=1.0,
        description="Maximum depth bounds"
    )

class VkPipelineModel(BaseModel):
    name: str = Field(..., description="User defined pipeline name.")
    ShaderModule: List[VkShaderModuleModel] = Field(
        ..., description="List of shader modules."
    )
    VertexInputBindingDescription: List[VkVertexInputBindingDescriptionModel] = Field(
        ..., description="List of vertex input binding descriptions."
    )
    InputAssemblyStateCreateInfo: Optional[
        VkPipelineInputAssemblyStateCreateInfoModel
    ] = Field(
        default_factory=VkPipelineInputAssemblyStateCreateInfoModel,
        description="Input assembly state description.",
    )
    DynamicState: Optional[
        List[
            Literal[
                "VK_DYNAMIC_STATE_VIEWPORT",
                "VK_DYNAMIC_STATE_SCISSOR",
                "VK_DYNAMIC_STATE_LINE_WIDTH",
                "VK_DYNAMIC_STATE_DEPTH_BIAS",
                "VK_DYNAMIC_STATE_BLEND_CONSTANTS",
                "VK_DYNAMIC_STATE_DEPTH_BOUNDS",
                "VK_DYNAMIC_STATE_STENCIL_COMPARE_MASK",
                "VK_DYNAMIC_STATE_STENCIL_WRITE_MASK",
                "VK_DYNAMIC_STATE_STENCIL_REFERENCE",
                "VK_DYNAMIC_STATE_CULL_MODE",
                "VK_DYNAMIC_STATE_FRONT_FACE",
                "VK_DYNAMIC_STATE_PRIMITIVE_TOPOLOGY",
                "VK_DYNAMIC_STATE_VIEWPORT_WITH_COUNT",
                "VK_DYNAMIC_STATE_SCISSOR_WITH_COUNT",
                "VK_DYNAMIC_STATE_VERTEX_INPUT_BINDING_STRIDE",
                "VK_DYNAMIC_STATE_DEPTH_TEST_ENABLE",
                "VK_DYNAMIC_STATE_DEPTH_WRITE_ENABLE",
                "VK_DYNAMIC_STATE_DEPTH_COMPARE_OP",
                "VK_DYNAMIC_STATE_DEPTH_BOUNDS_TEST_ENABLE",
                "VK_DYNAMIC_STATE_STENCIL_TEST_ENABLE",
                "VK_DYNAMIC_STATE_STENCIL_OP",
                "VK_DYNAMIC_STATE_RASTERIZER_DISCARD_ENABLE",
                "VK_DYNAMIC_STATE_DEPTH_BIAS_ENABLE",
                "VK_DYNAMIC_STATE_PRIMITIVE_RESTART_ENABLE",
                "viewport",
                "scissor",
                "line_width",
                "depth_bias",
                "blend_constants",
                "depth_bounds",
                "stencil_compare_mask",
                "stencil_write_mask",
                "stencil_reference",
                "cull_mode",
                "front_face",
                "primitive_topology",
                "viewport_with_count",
                "scissor_with_count",
                "vertex_input_binding_stride",
                "depth_test_enable",
                "depth_write_enable",
                "depth_compare_op",
                "depth_bounds_test_enable",
                "stencil_test_enable",
                "stencil_op",
                "rasterizer_discard_enable",
                "depth_bias_enable",
                "primitive_restart_enable",
            ]
        ]
    ] = Field(
        default_factory=lambda: [
            "VK_DYNAMIC_STATE_VIEWPORT",
            "VK_DYNAMIC_STATE_SCISSOR",
        ],
        description="List of dynamic state enables (viewport and scissor always required).",
    )
    RasterizationStateCreateInfo: Optional[
        VkPipelineRasterizationStateCreateInfoModel
    ] = Field(
        default_factory=VkPipelineRasterizationStateCreateInfoModel,
        description="Rasterization state description.",
    )

    MultisampleStateCreateInfo: Optional[
        VkPipelineMultisampleStateCreateInfoModel
    ] = Field(
        default_factory=VkPipelineMultisampleStateCreateInfoModel,
        description="Multisample state description."
    )
    
    ColorBlendAttachmentState: Optional[
        VkPipelineColorBlendAttachmentStateModel
    ] = Field(
        default_factory=VkPipelineColorBlendAttachmentStateModel,
        description="Color blend attachment state."
    )
    
    ColorBlendStateCreateInfo: Optional[
        VkPipelineColorBlendStateCreateInfoModel
    ] = Field(
        default_factory=VkPipelineColorBlendStateCreateInfoModel,
        description="Color blend state description."
    )
    
    DepthStencilStateCreateInfo: Optional[
        VkPipelineDepthStencilStateCreateInfoModel
    ] = Field(
        default_factory=VkPipelineDepthStencilStateCreateInfoModel,
        description="Depth stencil state description."
    )

    @field_validator("DynamicState")
    def must_include_viewport_and_scissor(cls, v):
        required = {"VK_DYNAMIC_STATE_VIEWPORT", "VK_DYNAMIC_STATE_SCISSOR"}
        if v is None:
            raise ValueError(f"DynamicState must include: {required}!")
        missing = required - set(v)
        if missing:
            raise ValueError(f"DynamicState must include: {required}!")
        return v
    
    @field_validator("name", mode="before")
    @classmethod
    def validate_name_starts_uppercase(cls, v):
        if v and not (v[0].isupper() and v[0].isalpha()):
            raise ValueError(f"Pipeline name must start with an uppercase alpha letter: '{v}'")
        return v


class VkForgeModel(BaseModel):
    model_config = {
        "extra": "forbid",
    }

    ID: Literal[
        "VkForge 0.5"
    ] = Field(
        ...,
        description="VkForge Identifier"
    )

    UserDefined: Optional[UserDefinedModel] = Field(
        default_factory=UserDefinedModel, description="References to the User code external to the generated code"
    )

    GenerateOnce: Optional[List[Literal[
            FILE.CORE,
            FILE.CMAKE,
            FILE.FUNC,
            FILE.PIPELINE_C,
            FILE.PIPELINE_H,
            FILE.TYPE,
            FILE.UTIL,
            FILE.LAYOUT
        ]]
    ] = Field(
        default=None,
        description="VkForge generates a list of files. You can mark specific files to only generate once. "
        "Once VkForge sees that these files already exists, it will not overwrite them. "
        "This is useful if you only want to use VkForge as a starter and then manually update the code "
        "afterwards."
    )

    CompileOnce: Optional[List[str]] = Field(
        default=None,
        descriptions="List of shader source path you do not want to be re-compiled on each VkForge call. Path match path under Pipeline of config."
    )

    InstanceCreateInfo: Optional[VkInstanceCreateInfoModel] = Field(
        default_factory=VkInstanceCreateInfoModel, description="Instance creation info."
    )
    ApplicationInfo: Optional[VkApplicationInfoModel] = Field(
        default_factory=VkApplicationInfoModel, description="Application info."
    )
    DebugUtilsMessengerCreateInfoEXT: Optional[VkDebugUtilsMessengerCreateInfoEXTModel] = (
        Field(
            default_factory=VkDebugUtilsMessengerCreateInfoEXTModel,
            description="Debug messenger creation info.",
        )
    )
    
    DeviceCreateInfo: Optional[VkDeviceCreateInfoModel] = Field(
        default_factory=VkDeviceCreateInfoModel, description="Device creation info."
    )

    Pipeline: List[VkPipelineModel] = Field(..., description="List of graphics pipelines.")

    @model_validator(mode="before")
    @classmethod
    def check_id_present_and_valid(cls, data):
        if "ID" not in data:
            raise ValueError("ID:\nThe 'ID' field is required and must be oneof 'VkForge 0.5'")
        if data["ID"] != "VkForge 0.5":
            raise ValueError("Invalid VkForge Config")
        return data
