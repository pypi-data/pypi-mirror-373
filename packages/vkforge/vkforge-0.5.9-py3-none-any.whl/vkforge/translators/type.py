from vkforge.context import VkForgeContext
from vkforge.mappings import *


def CreateCore(ctx: VkForgeContext) -> str:
    content = """\
typedef struct VkForgeCore VkForgeCore;

struct VkForgeCore
{{
    VkInstance       instance;
    VkSurfaceKHR     surface;
    VkPhysicalDevice physical_device;
    uint32_t         queue_family_index;
    VkDevice         device;
    VkQueue          queue;
    VkCommandPool    cmdpool;
}};
"""
    output = content.format()

    return output


def CreateBufferAllocType(ctx: VkForgeContext) -> str:
    content = """\
typedef struct VkForgeBufferAlloc VkForgeBufferAlloc;

struct VkForgeBufferAlloc
{{
    VkBuffer       buffer;
    VkDeviceSize   size;
    VkDeviceMemory memory;
}};
"""
    output = content.format()

    return output

def CreateImageAllocType(ctx: VkForgeContext) -> str:
    content = """\
typedef struct VkForgeImageAlloc VkForgeImageAlloc;

struct VkForgeImageAlloc
{{
    VkImage        image;
    VkDeviceSize   size;
    VkDeviceMemory memory;
}};
"""
    output = content.format()

    return output

def CreateLayout(ctx: VkForgeContext) -> str:
    content = """\
typedef struct VkForgeLayout VkForgeLayout;
"""
    output = content.format()

    return output

def GetMaxPipelines(ctx: VkForgeContext):
    references = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.REFERENCES]
    return max(len(references), 1)

def GetMaxPipelineLayouts(ctx: VkForgeContext):
    layouts = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.LAYOUTS]
    return max(len(layouts), 1)

def GetMaxDescriptorSetLayouts(ctx: VkForgeContext):
    layouts = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.LAYOUTS]
    max_descriptorset_layout = 0
    for layout in layouts:
        if layout:
            if len(layout) > max_descriptorset_layout:
                max_descriptorset_layout = len(layout)
    return max(max_descriptorset_layout, 1)

def GetMaxDescriptorBindings(ctx: VkForgeContext):
    layouts = ctx.layout[LAYOUT.PIPELINE_LAYOUT][LAYOUT.LAYOUTS]
    max_descriptor_binding = 0
    for layout in layouts:
        if layout:
            for set1 in layout:
                if set1:
                    if len(set1) > max_descriptor_binding:
                        max_descriptor_binding = len(set1)
    return max(max_descriptor_binding, 1)

def Create_Maxes(ctx: VkForgeContext) -> str:
    content = """\
#define VKFORGE_MAX_PIPELINES {max_pipelines_value}
#define VKFORGE_MAX_PIPELINE_LAYOUTS {max_pipeline_layouts_value}
#define VKFORGE_MAX_DESCRIPTORSET_LAYOUTS {max_descriptorset_layouts_value}
#define VKFORGE_MAX_DESCRIPTOR_BINDINGS {max_descriptor_bindings_value}
"""
    output = content.format(
        max_pipelines_value=GetMaxPipelines(ctx),
        max_pipeline_layouts_value=GetMaxPipelineLayouts(ctx),
        max_descriptorset_layouts_value=GetMaxDescriptorSetLayouts(ctx),
        max_descriptor_bindings_value=GetMaxDescriptorBindings(ctx)
    )

    return output

def Create_Defaults(ctx: VkForgeContext) -> str:
    content = """\
#define VKFORGE_DEFAULT_FORMAT {default_format}
"""
    output = content.format(
        default_format="VK_FORMAT_B8G8R8A8_UNORM"
    )

    return output

def CreateTexture(ctx: VkForgeContext):
    content = """\
typedef struct VkForgeTexture VkForgeTexture;

struct VkForgeTexture
{{
    VkImage image;                      // The actual GPU image
    VkDeviceMemory memory;              // Memory bound to the VkImage
    VkImageView imageView;              // Optional: for sampling/viewing the image
    VkSampler sampler;                  // Sampler used to read from the texture
    uint32_t width;                     // Texture width in pixels
    uint32_t height;                    // Texture height in pixels
    VkSampleCountFlagBits samples;      // Multisample count (e.g., VK_SAMPLE_COUNT_1_BIT)
    VkFormat format;                    // Image format (e.g., VK_FORMAT_R8G8B8A8_UNORM)
}};
"""
    return content.format()

def CreateRender(ctx: VkForgeContext):
    content = """\
#define VKFORGE_MAX_SWAPCHAIN_RECREATION 128

typedef enum VkForgeRenderStatus VkForgeRenderStatus;

enum VkForgeRenderStatus
{{
    VKFORGE_RENDER_READY,
    VKFORGE_RENDER_COPYING,
    VKFORGE_RENDER_ACQING_IMG,
    VKFORGE_RENDER_PENGING_ACQ_IMG,
    VKFORGE_RENDER_DRAWING,
    VKFORGE_RENDER_SUBMITTING,
    VKFORGE_RENDER_PENDING_SUBMIT,
    VKFORGE_RENDER_RECREATE
}};

typedef struct VkForgeRender VkForgeRender;
typedef void (*VkForgeRenderCallback)(VkForgeRender render);

struct VkForgeRender
{{
    SDL_Window*           window;
    VkPhysicalDevice      physical_device;
    VkSurfaceKHR          surface;
    VkDevice              device;
    VkQueue               queue;
    VkCommandPool         cmdPool;
    VkExtent2D            extent;
    VkCommandBuffer       cmdbuf_copy;
    VkCommandBuffer       cmdbuf_draw;
    VkForgeRenderCallback copyCallback;
    VkForgeRenderCallback drawCallback;
    VkFormat              req_format;
    uint32_t              req_swapchain_size;
    VkPresentModeKHR      req_present_mode;
    VkSwapchainKHR        swapchain;
    uint32_t              swapchain_size;
    VkImage*              swapchain_images;
    VkImageView*          swapchain_imgviews;
    uint32_t              index;
    VkFence               fence_acquire;
    VkFence               fence_submit;
    VkSemaphore           semaphore_copy;
    VkSemaphore           semaphore_draw;
    const char*           color;
    VkForgeRenderStatus   status;
    void*                 userData;
    bool                  success_acquire;
    bool                  success_present;
    uint16_t              swapchainRecreationCount; //prevents a loop of recreating the swapchain
}};
"""
    return content.format()

def CreateDestroyCallback(ctx: VkForgeContext):
    content = """\
typedef void (*VkForgeDestroyCallback)(void);
"""
    return content.format()

def CreateQuad(ctx: VkForgeContext):
    content = """\
typedef union VkForgeQuad VkForgeQuad;

union VkForgeQuad
{{
    struct {{float x, y, w, h;}};
    struct {{float s, t, u, v;}};
    float p[4];
}};
"""
    return content.format()

def CreateImagePair(ctx: VkForgeContext):
    content = """\
typedef struct VkForgeImagePair VkForgeImagePair;

struct VkForgeImagePair
{{
    VkImage     image;
    VkImageView imgview;
}};
"""
    return content.format()

def CreatePixelFormatPair(ctx: VkForgeContext):
    content = """\
typedef struct VkForgePixelFormatPair  VkForgePixelFormatPair;

struct VkForgePixelFormatPair
{{
    Uint32 sdl_format;
    VkFormat vk_format;
}};
"""
    return content.format()

def CreateDescriptorResource(ctx: VkForgeContext):
    content = """\
typedef union VkForgeDescriptorResource VkForgeDescriptorResource;

union VkForgeDescriptorResource
{{
    VkDescriptorImageInfo  image;
    VkDescriptorBufferInfo buffer;
}};
"""
    return content.format()

def GetTypeStrings(ctx: VkForgeContext):
    return [
        Create_Defaults(ctx),
        Create_Maxes(ctx),
        CreateCore(ctx),
        CreateBufferAllocType(ctx),
        CreateImageAllocType(ctx),
        CreateLayout(ctx),
        CreateTexture(ctx),
        CreateRender(ctx),
        CreateDestroyCallback(ctx),
        CreateQuad(ctx),
        CreateImagePair(ctx),
        CreatePixelFormatPair(ctx),
        CreateDescriptorResource(ctx),
        
        
    ]