from vkforge.context import VkForgeContext
from vkforge.mappings import *


def CreateInstance(ctx: VkForgeContext) -> str:
    define_validation_layers = "/** NO VALIDATIONS **/"
    define_debug_messenger = "/** NO DEBUG MESSENGER **/"
    define_best_practices = "/** NO BEST PRACTICES **/"
    layer_buffer = "0"
    layer_count = "0"
    next = "0"

    if not ctx.removeValidations:
        define_validation_layers = """\
const char* layers[] =
    {{
        "VK_LAYER_KHRONOS_validation"
    }};

    const uint32_t layers_count = sizeof(layers) / sizeof(layers[0]);\
""".format()
        layer_buffer = "layers"
        layer_count = "layers_count"

        define_debug_messenger = """\
VkDebugUtilsMessengerCreateInfoEXT msgCreateInfo = VkForge_GetDebugUtilsMessengerCreateInfo();\
""".format()
        
        next = "&msgCreateInfo;\n\tmsgCreateInfo.pNext=0"
    
    if not ctx.removeValidations and ctx.forgeModel.InstanceCreateInfo.useValidationFeatureEnableBestPracticesEXT:
        define_best_practices = """\
VkValidationFeatureEnableEXT enables[] =
    {{
        VK_VALIDATION_FEATURE_ENABLE_BEST_PRACTICES_EXT
    }};

    VkValidationFeaturesEXT validationFeatures       = {{0}};
    validationFeatures.sType                         = VK_STRUCTURE_TYPE_VALIDATION_FEATURES_EXT;
    validationFeatures.enabledValidationFeatureCount = 1;
    validationFeatures.pEnabledValidationFeatures    = enables;

    validationFeatures.pNext = &msgCreateInfo;\
""".format()
        
        next = "&validationFeatures;\n\tvalidationFeatures.pNext=0"
        
    content = """\
void VkForge_CreateInstance
(
    VkInstance*            retInstance
)
{{
    assert(retInstance);

    VkResult result;
    VkInstance instance = VK_NULL_HANDLE;

    uint32_t extensions_count = 0;
    const char *const * extensions = SDL_Vulkan_GetInstanceExtensions(&extensions_count);

    {define_validation_layers}

    {define_debug_messenger}

    {define_best_practices}

    VkApplicationInfo appInfo = {{0}};
    appInfo.sType             = VK_STRUCTURE_TYPE_APPLICATION_INFO;
    appInfo.apiVersion        = {version};
    appInfo.pEngineName       = "{engine}";
    appInfo.pApplicationName  = "{appName}";

    VkInstanceCreateInfo createInfo    = {{0}};
    createInfo.sType                   = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;
    createInfo.pApplicationInfo        = &appInfo;
    createInfo.enabledExtensionCount   = extensions_count;
    createInfo.ppEnabledExtensionNames = extensions;
    createInfo.enabledLayerCount       = {layer_count};
    createInfo.ppEnabledLayerNames     = {layer_buffer};
    createInfo.pNext                   = {next};

    result = vkCreateInstance(&createInfo, 0, &instance);

    if( VK_SUCCESS != result)
    {{
        SDL_LogError(0, "Failed to create Vulkan Instance.");
        exit(1);
    }}

    *retInstance = instance;
}}

"""
    output = content.format(
        define_validation_layers=define_validation_layers,
        define_best_practices=define_best_practices,
        define_debug_messenger=define_debug_messenger,
        version=map_value(API_VERSION_MAP, ctx.forgeModel.ApplicationInfo.apiVersion),
        engine=ctx.forgeModel.ApplicationInfo.pEngineName,
        appName=ctx.forgeModel.ApplicationInfo.pApplicationName,
        layer_count=layer_count,
        layer_buffer=layer_buffer,
        next=next
    )

    return output

def CreateSurface(ctx: VkForgeContext) -> str:
    content = """\
void VkForge_CreateSurface
(
    VkInstance             instance,
    SDL_Window*            window,

    VkSurfaceKHR*          retSurface
)
{{
    assert(retSurface);

    VkSurfaceKHR surface = VK_NULL_HANDLE;

    if( !SDL_Vulkan_CreateSurface(window, instance, 0, &surface) )
    {{
        SDL_Log("Failed to Create Vulkan/SDL3 Surface: %s", SDL_GetError());
        exit(1);
    }}

    *retSurface = surface;
}}


"""
    output = content.format()

    return output

def CreateSelectPhysicalDevice(ctx: VkForgeContext) -> str:
    content = """\
void VkForge_SelectPhysicalDevice
(
    VkInstance instance, 
    VkSurfaceKHR surface, 
    VkPhysicalDevice* inPhysicalDevice, 
    uint32_t* inQueueFamilyIndex
)
{{
    assert(inPhysicalDevice);
    assert(inQueueFamilyIndex);

    VKFORGE_ENUM(physical_dev, VkPhysicalDevice, vkEnumeratePhysicalDevices, 32, instance);

    uint32_t best_score = 0;
    VkPhysicalDevice best_physical_dev = VK_NULL_HANDLE;
    uint32_t best_queue_fam_ind;

    for (uint32_t i = 0; i < physical_dev_count; i++)
    {{
        VkPhysicalDeviceProperties physical_dev_prop = {{0}};
        vkGetPhysicalDeviceProperties(physical_dev_buffer[i], &physical_dev_prop);
        VKFORGE_ENUM(queue_fam_prop, VkQueueFamilyProperties, vkGetPhysicalDeviceQueueFamilyProperties, 32, physical_dev_buffer[i]);
        uint32_t score = VkForge_ScorePhysicalDeviceLimits(physical_dev_prop.limits);

        for (uint32_t j = 0; j < queue_fam_prop_count; j++) 
        {{
            uint32_t requested_flags = VK_QUEUE_GRAPHICS_BIT;
            if (requested_flags == (queue_fam_prop_buffer[j].queueFlags & requested_flags))
            {{
                VkBool32 supported = VK_FALSE;
                vkGetPhysicalDeviceSurfaceSupportKHR(physical_dev_buffer[i], j, surface, &supported);

                if (supported && (score > best_score)) 
                {{
                    best_score = score;
                    best_physical_dev = physical_dev_buffer[i];
                    best_queue_fam_ind = j;
                }}
            }}
        }}
    }}

    if(best_physical_dev == VK_NULL_HANDLE )
    {{
        SDL_LogError(0, "No physical device found!");
        exit(1);
    }}

    *inPhysicalDevice   = best_physical_dev;
    *inQueueFamilyIndex = best_queue_fam_ind;
}}
"""
    output = content.format()

    return output


def CreateDevice(ctx: VkForgeContext) -> str:
    enabledFeaturesDefinition = "/** NO ENABLED FEATURES **/"
    enabledFeatures = "0"

    features = ctx.forgeModel.DeviceCreateInfo.PhysicalDeviceFeatures

    if features:
        enabledFeaturesDefinition = "VkPhysicalDeviceFeatures enabledFeatures = {0};"
        lines = []
        for key, value in features:
            if value:
                enabledFeaturesDefinition += f"\n\tenabledFeatures.{key} = VK_TRUE;"
                enabledFeatures = "&enabledFeatures"

    content = """\
void VkForge_CreateDevice
(
    VkPhysicalDevice       physical_device,
    uint32_t               queue_family_index,
    const char**           requested_extensions_buffer,
    uint32_t               requested_extensions_count,

    VkDevice*              retDevice,
    VkQueue*               retQueue
)
{{
    assert(retDevice);
    assert(retQueue);

    #define unit_size sizeof(const char*)

    // Required extensions for the device: Requested by VkForge
    const char* intern_required_ext_buffer[] =
    {{
        "VK_KHR_swapchain"
    }};

    #define intern_required_ext_count (sizeof(intern_required_ext_buffer) / unit_size)
    bool intern_required_ext_set[intern_required_ext_count] = {{false}};

    // Maximum amount of extensions that will be sent to the driver
    #define ext_limit 512
    assert(ext_limit > 128); // need room of RenderDoc, etc
    assert((ext_limit - 128) > intern_required_ext_count);

    // The buffer and size that will be sent to the driver
    const char* req_ext_b[ext_limit] = {{0}};
    uint32_t    req_ext_c            = 0;

    // Copy user requested extensions if any
    if(requested_extensions_buffer && requested_extensions_count)
    {{
        uint32_t user_limit = ext_limit - 128 -  intern_required_ext_count;
        if( requested_extensions_count > user_limit)
        {{
            SDL_Log("VkForge does not support more than %d requested Device extensions.", user_limit);
            exit(1);
        }}

        memcpy(req_ext_b, requested_extensions_buffer, requested_extensions_count * unit_size);
        req_ext_c += requested_extensions_count;

        for(uint32_t i = 0; i < intern_required_ext_count; i++)
        {{
            for(uint32_t j = 0; j < requested_extensions_count; j++)
            {{
                if(strcmp(intern_required_ext_buffer[i], requested_extensions_buffer[j]) == 0)
                {{
                    intern_required_ext_set[i] = true;
                    break;
                }}
            }}
        }}
    }}

    // Copy over any required externsions that were not copied
    for(uint32_t i = 0; i < intern_required_ext_count; i++)
    {{
        if(false == intern_required_ext_set[i])
        {{
            req_ext_b[req_ext_c ++] = intern_required_ext_buffer[i];
            intern_required_ext_set[i] = true;
        }}
    }}

    VKFORGE_ENUM
    (
        ext_prop,
        VkExtensionProperties,
        vkEnumerateDeviceExtensionProperties,
        ext_limit,
        physical_device,
        NULL
    );

    uint32_t missing_count = 0;
    for(uint32_t i = 0; i < req_ext_c; i++)
    {{
        bool found = false;
        for(uint32_t j = 0; j < ext_prop_count; j++)
        {{
            if(strcmp(req_ext_b[i], ext_prop_buffer[j].extensionName) == 0)
            {{
                found = true;
                break;
            }}
        }}

        if(found == false)
        {{
            SDL_Log("Requested extension, %s, is missing!", req_ext_b[i]);
            missing_count ++;
        }}
    }}

    if( missing_count )
    {{
        exit(1);
    }}

    float priority = 1.0f;

    VkDeviceQueueCreateInfo queueCreateInfo = {{0}};
    queueCreateInfo.sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO;
    queueCreateInfo.queueCount = 1;
    queueCreateInfo.queueFamilyIndex = queue_family_index;
    queueCreateInfo.pQueuePriorities = &priority;

    VkPhysicalDeviceVulkan13Features vk13Features = {{0}};
    vk13Features.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES;
    vk13Features.dynamicRendering = VK_TRUE;
    vk13Features.synchronization2 = VK_TRUE;

    {enabledFeaturesDefinition}

    VkDeviceCreateInfo createInfo = {{0}};
    createInfo.sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO;
    createInfo.queueCreateInfoCount = 1;
    createInfo.pQueueCreateInfos = &queueCreateInfo;
    createInfo.enabledExtensionCount = req_ext_c;
    createInfo.ppEnabledExtensionNames = req_ext_b;
    createInfo.pEnabledFeatures = {enabledFeatures};
    createInfo.pNext = &vk13Features;

    VkDevice device = VK_NULL_HANDLE;
    VkResult result;

    result = vkCreateDevice(physical_device, &createInfo, 0, &device);

    if( result != VK_SUCCESS )
    {{
        SDL_Log( "Failed to create VkDevice");
        exit(1);
    }}

    VkQueue queue = VK_NULL_HANDLE;

    vkGetDeviceQueue(device, queue_family_index, 0, &queue);

    *retDevice = device;
    *retQueue = queue;
}}

"""
    output = content.format(
        enabledFeaturesDefinition=enabledFeaturesDefinition,
        enabledFeatures=enabledFeatures
    )

    return output


def CreateSwapchain(ctx: VkForgeContext) -> str:
    content = """\
void VkForge_CreateSwapchain
(
    VkSurfaceKHR           surface,
    VkPhysicalDevice       physical_device,
    VkDevice               device,
    VkSwapchainKHR         old_swapchain,
    VkFormat               req_format,
    uint32_t               req_swapchain_size,
    VkPresentModeKHR       req_present_mode,

    VkSwapchainKHR*        retSwapchain,
    uint32_t*              retSwapchainSize,
    VkImage**              retSwapchainImages,
    VkImageView**          retSwapchainImageViews
)
{{
    assert(retSwapchain);
    assert(retSwapchainSize);       //Must contain the number of images for old swapchain if old_swapchain is not null
    assert(retSwapchainImages);     //Must contain images for old swapchain if old_swapchain is not null
    assert(retSwapchainImageViews); //Must contain views for old swapchain if old_swapchain is not null

    VkResult result;
    VkSwapchainKHR swapchain = VK_NULL_HANDLE;

    VkSurfaceFormatKHR surface_format = VkForge_GetSurfaceFormat(surface, physical_device, req_format);
    VkSurfaceCapabilitiesKHR surface_cap = VkForge_GetSurfaceCapabilities(surface, physical_device);

    VkSwapchainCreateInfoKHR createInfo = {{0}};
    createInfo.sType = VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR;
    createInfo.surface = surface;
    createInfo.imageSharingMode = VK_SHARING_MODE_EXCLUSIVE;
    createInfo.minImageCount = VkForge_GetSwapchainSize(surface, physical_device, req_swapchain_size);
    createInfo.imageFormat = surface_format.format;
    createInfo.imageExtent = surface_cap.currentExtent;
    createInfo.imageArrayLayers = 1;
    createInfo.imageUsage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT;
    createInfo.imageColorSpace = surface_format.colorSpace;
    createInfo.preTransform = surface_cap.currentTransform;
    createInfo.compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;
    createInfo.presentMode = VkForge_GetPresentMode(surface, physical_device, req_present_mode);
    createInfo.clipped = VK_TRUE;
    createInfo.oldSwapchain = old_swapchain;

    result = vkCreateSwapchainKHR(device, &createInfo, 0, &swapchain);

    if( VK_SUCCESS != result )
    {{
        SDL_Log("Failed to create Swapchain.");
        exit(1);
    }}

    VKFORGE_ENUM(
        images,
        VkImage,
        vkGetSwapchainImagesKHR,
        16,
        device,
        swapchain
    );

    VkImage* swapchain_images;
    VkImageView* swapchain_image_views;
    uint32_t swapchain_size;

    if( old_swapchain )
    {{
        swapchain_images      = *retSwapchainImages;     //re-use allocated vars, freed when old_swapchain is freed
        swapchain_image_views = *retSwapchainImageViews; //re-use allocated vars, need to free old resources
        swapchain_size        = *retSwapchainSize;       //old_swapchain size

        // Free Old Resources
        for( uint32_t i = 0; i < swapchain_size; i++ )
        {{
            vkDestroyImageView(device, swapchain_image_views[i], 0);
        }}

        vkDestroySwapchainKHR(device, old_swapchain, 0);

        // Set new swapchain size
        swapchain_size = images_count;
    }}
    else
    {{
        swapchain_images      = SDL_malloc(sizeof(VkImage) * images_count);
        swapchain_image_views = SDL_malloc(sizeof(VkImageView) * images_count);
        swapchain_size        = images_count;
    }}

    SDL_memcpy(swapchain_images, images_buffer, images_count * sizeof(VkImage));

    for(unsigned int i = 0; i < images_count; i++)
    {{
        VkImageSubresourceRange subres = {{0}};
        subres.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
        subres.levelCount = 1;
        subres.layerCount = 1;

        VkImageViewCreateInfo viewInfo = {{0}};
        viewInfo.sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO;
        viewInfo.image = images_buffer[i];
        viewInfo.viewType = VK_IMAGE_VIEW_TYPE_2D;
        viewInfo.format = surface_format.format;
        viewInfo.subresourceRange = subres;

        result = vkCreateImageView(device, &viewInfo, 0, &swapchain_image_views[i]);

        if(VK_SUCCESS != result)
        {{
            SDL_LogError(0, "Failed to create Swapchain %d image view", i);
            exit(1);
        }}
    }}

    *retSwapchain = swapchain;
    *retSwapchainImages = swapchain_images;
    *retSwapchainImageViews = swapchain_image_views;
    *retSwapchainSize = swapchain_size;
}}

"""
    output = content.format()

    return output


def CreateCommandBuffers(ctx: VkForgeContext) -> str:
    content = """\
void VkForge_CreateCommandPoolAndBuffers
(
    uint32_t               queue_family_index,
    VkDevice               device,
    uint32_t               bufferCount,

    VkCommandPool*         retCommandPool,
    VkCommandBuffer*       retCommandBuffers
)
{{
    assert(retCommandPool);

    VkResult result;
    VkCommandPool cmdpool      = VK_NULL_HANDLE;
    VkCommandBuffer cmdbuf_copy = VK_NULL_HANDLE;
    VkCommandBuffer cmdbuf_draw = VK_NULL_HANDLE;

    VkCommandPoolCreateInfo poolInfo = {{0}};
    poolInfo.sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO;
    poolInfo.flags = VK_COMMAND_POOL_CREATE_TRANSIENT_BIT | VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;
    poolInfo.queueFamilyIndex = queue_family_index;

    result = vkCreateCommandPool(device, &poolInfo, 0, &cmdpool);

    if( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to create Command Pool.");
        exit(1);
    }}

    if(bufferCount) 
    {{
        VkCommandBuffer cmdbufs[2] = {{VK_NULL_HANDLE}};

        VkCommandBufferAllocateInfo allocInfo = {{0}};
        allocInfo.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;
        allocInfo.commandPool = cmdpool;
        allocInfo.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
        allocInfo.commandBufferCount = bufferCount;

        result = vkAllocateCommandBuffers(device, &allocInfo, retCommandBuffers);

        if( VK_SUCCESS != result )
        {{
            SDL_LogError(0, "Failed to allocate Command Buffers.");
            exit(1);
        }}
    }}

    

    *retCommandPool = cmdpool;
}}

"""
    output = content.format()

    return output

from vkforge.context import VkForgeContext
from vkforge.mappings import *

def CreateCreateCore(ctx: VkForgeContext) -> str:
    content = """\
VkForgeCore* VkForge_CreateCore
(
    SDL_Window*            window,
    const char**           requested_device_extensions_buffer,
    uint32_t               requested_device_extensions_count
)
{{
    VkForgeCore* core = (VkForgeCore*)SDL_malloc(sizeof(VkForgeCore));
    if ( !core )
    {{
        SDL_LogError(0, "Failed to allocate memory for VkForgeCore");
        exit(1);
    }}

    SDL_memset(core, 0, sizeof(VkForgeCore));

    // Create Vulkan instance
    VkForge_CreateInstance(&core->instance);

    // Create surface
    VkForge_CreateSurface(core->instance, window, &core->surface);

    // Select physical device and queue family
    VkForge_SelectPhysicalDevice(core->instance, core->surface, &core->physical_device, &core->queue_family_index);

    // Create logical device
    VkForge_CreateDevice(
        core->physical_device,
        core->queue_family_index,
        requested_device_extensions_buffer,
        requested_device_extensions_count,
        &core->device,
        &core->queue
    );

    // Create command buffers
    VkForge_CreateCommandPoolAndBuffers(
        core->queue_family_index,
        core->device,
        0,
        &core->cmdpool,
        0
    );

    return core;
}}
"""
    return content.format()

def CreateDestroyCore(ctx: VkForgeContext) -> str:
    content = """\
void VkForge_DestroyCore(VkForgeCore* core)
{{
    if (!core) return;

    vkDeviceWaitIdle(core->device);

    // Destroy command pool (automatically frees command buffers)
    if (core->cmdpool)
    {{
        vkDestroyCommandPool(core->device, core->cmdpool, 0);
    }}

    // Destroy device
    if (core->device)
    {{
        vkDestroyDevice(core->device, 0);
    }}

    // Destroy surface
    if (core->surface)
    {{
        vkDestroySurfaceKHR(core->instance, core->surface, 0);
    }}

    // Destroy instance
    if (core->instance)
    {{
        vkDestroyInstance(core->instance, 0);
    }}

    SDL_free(core);
}}
"""
    return content.format()

def CreateDestroy(ctx: VkForgeContext):
    content = """\
void VkForge_Destroy(VkDevice device, uint32_t count, VkForgeDestroyCallback* destroyers)
{{
    vkDeviceWaitIdle(device);
    for (uint32_t i = 0; i < count; ++i) 
    {{
        destroyers[i]();
    }}
}}
"""
    return content.format()

def CreateCreateRender(ctx: VkForgeContext):
    content = """\
VkForgeRender* VkForge_CreateRender
(
    SDL_Window*           window,
    VkSurfaceKHR          surface,
    VkPhysicalDevice      physical_device,
    VkDevice              device,
    VkQueue               queue,
    VkCommandPool         cmdPool,
    VkFormat              req_format,
    uint32_t              req_swapchain_size,
    VkPresentModeKHR      req_present_mode,
    VkForgeRenderCallback copyCallback,
    VkForgeRenderCallback drawCallback,
    const char*           clearColorHex,
    void*                 userData
)
{{
    assert(physical_device);
    assert(surface);
    assert(device);
    assert(queue);
    assert(cmdPool);
    assert(req_swapchain_size);
    assert(copyCallback);
    assert(drawCallback);

    if( VK_FORMAT_UNDEFINED == req_format ) req_format = VK_FORMAT_B8G8R8A8_UNORM;

    VkForgeRender* render = SDL_malloc(sizeof(VkForgeRender));
    SDL_memset(render, 0, sizeof(VkForgeRender));

    render->window             = window;
    render->physical_device    = physical_device;
    render->surface            = surface;
    render->device             = device;
    render->queue              = queue;
    render->cmdPool            = cmdPool;
    render->req_format         = req_format;
    render->req_swapchain_size = req_swapchain_size;
    render->req_present_mode   = req_present_mode;
    render->copyCallback       = copyCallback;
    render->drawCallback       = drawCallback;
    render->color              = clearColorHex;
    render->userData           = userData;

    VkForge_CreateSwapchain(
        surface,
        physical_device,
        device,
        0,
        req_format,
        req_swapchain_size,
        req_present_mode,
        &render->swapchain,
        &render->swapchain_size,
        &render->swapchain_images,
        &render->swapchain_imgviews
    );

    render->fence_acquire  = VkForge_CreateFence(device);
    render->fence_submit   = VkForge_CreateFence(device);
    render->semaphore_copy = VkForge_CreateSemaphore(device);
    render->semaphore_draw = VkForge_CreateSemaphore(device);

    VkSurfaceCapabilitiesKHR surface_cap = VkForge_GetSurfaceCapabilities(surface, physical_device);
    render->extent                       = surface_cap.currentExtent;

    VkCommandBuffer cmdbufs[2] = {{VK_NULL_HANDLE}};

    VkCommandBufferAllocateInfo allocInfo = {{0}};
    allocInfo.sType                       = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;
    allocInfo.commandPool                 = cmdPool;
    allocInfo.level                       = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
    allocInfo.commandBufferCount          = sizeof(cmdbufs) / sizeof(VkCommandBuffer);

    VkResult result = vkAllocateCommandBuffers(device, &allocInfo, cmdbufs);

    if( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to allocate Command Buffers.");
        exit(1);
    }}

    render->cmdbuf_copy = cmdbufs[0];
    render->cmdbuf_draw = cmdbufs[1];

    render->status = VKFORGE_RENDER_READY;

    return render;
}}
"""
    return content.format()

def CreateRefreshRender(ctx: VkForgeContext):
    content = """\
void VkForge_RefreshRenderData(VkForgeRender* r)
{{
    VkSurfaceCapabilitiesKHR surface_cap = VkForge_GetSurfaceCapabilities(r->surface, r->physical_device);
    r->extent                            = surface_cap.currentExtent;
}}
"""
    return content.format()

def CreateReCreateRenderSwapchain(ctx: VkForgeContext):
    content = """\
void VkForge_ReCreateRenderSwapchain(VkForgeRender* r)
{{
    VkForge_CreateSwapchain(
        r->surface,
        r->physical_device,
        r->device,
        r->swapchain,
        r->req_format,
        r->req_swapchain_size,
        r->req_present_mode,
        &r->swapchain,
        &r->swapchain_size,
        &r->swapchain_images,
        &r->swapchain_imgviews
    );
}}
"""
    return content.format()

def CreateDestroyRender(ctx: VkForgeContext):
    content = """\
void VkForge_DestroyRender(VkForgeRender* r)
{{
    // Destroy swapchain image views
    if (r->swapchain_imgviews)
    {{
        for (uint32_t i = 0; i < r->swapchain_size; i++)
        {{
            if (r->swapchain_imgviews[i])
            {{
                vkDestroyImageView(r->device, r->swapchain_imgviews[i], 0);
            }}
        }}
        SDL_free(r->swapchain_imgviews);
    }}

    // Free swapchain images array (images are owned by swapchain)
    if (r->swapchain_images)
    {{
        SDL_free(r->swapchain_images);
    }}

    // Destroy swapchain
    if (r->swapchain)
    {{
        vkDestroySwapchainKHR(r->device, r->swapchain, 0);
    }}

    VkCommandBuffer cmdbufs[2] = {{r->cmdbuf_copy, r->cmdbuf_draw}};
    vkFreeCommandBuffers(r->device, r->cmdPool, 2, cmdbufs);

    vkDestroyFence(r->device, r->fence_acquire, 0);
    vkDestroyFence(r->device, r->fence_submit, 0);
    vkDestroySemaphore(r->device, r->semaphore_copy, 0);
    vkDestroySemaphore(r->device, r->semaphore_draw, 0);

    SDL_free(r);
}}
"""
    return content.format()

def CreateUpdateRender(ctx: VkForgeContext):
    content = """\
int counter = 0;
void VkForge_UpdateRender(VkForgeRender* render)
{{
    if( VKFORGE_RENDER_READY == render->status )
    {{
        render->status = VKFORGE_RENDER_COPYING;
    }}

    if( VKFORGE_RENDER_COPYING == render->status )
    {{
        VkForge_BeginCommandBuffer(render->cmdbuf_copy);

        render->copyCallback(*render);

        VkForge_EndCommandBuffer(render->cmdbuf_copy);

        render->status = VKFORGE_RENDER_ACQING_IMG;
    }}

    if( VKFORGE_RENDER_ACQING_IMG == render->status )
    {{
        VkResult result = vkAcquireNextImageKHR
        (
            render->device,
            render->swapchain,
            1000000 / 60 / 16,
            VK_NULL_HANDLE,
            render->fence_acquire,
            &render->index
        );

        if( VK_SUCCESS == result )
        {{
            render->success_acquire = true;
        }}
        else if( VK_SUBOPTIMAL_KHR == result || VK_ERROR_OUT_OF_DATE_KHR == result )
        {{
            SDL_LogError(0, "Failed to Acquire Image due to %s. The swapchain will be re-created.", VkForge_StringifyResult(result));
            render->success_acquire = false;
        }}
        else
        {{
            SDL_LogError(0, "Failed to Acquire Image: %s", VkForge_StringifyResult(result));
            exit(1);
        }}

        render->status = VKFORGE_RENDER_PENGING_ACQ_IMG;
    }}

    if( VKFORGE_RENDER_PENGING_ACQ_IMG == render->status )
    {{
        if( VK_SUCCESS == vkGetFenceStatus(render->device, render->fence_acquire)  )
        {{
            vkResetFences(render->device, 1, &render->fence_acquire);
            if( render->success_acquire )
                render->status = VKFORGE_RENDER_DRAWING;
            else
                render->status = VKFORGE_RENDER_RECREATE;
        }}
    }}

    if( VKFORGE_RENDER_DRAWING == render->status )
    {{
        VkForgeImagePair imgPair = {{ render->swapchain_images[render->index], render->swapchain_imgviews[render->index] }};
        VkForgeQuad quad = {{ 0, 0, render->extent.width, render->extent.height }};

        VkForge_BeginCommandBuffer(render->cmdbuf_draw);

        VkForge_CmdBeginRendering(render->cmdbuf_draw, imgPair, render->color, quad);

        render->drawCallback(*render);

        VkForge_CmdEndRendering(render->cmdbuf_draw, imgPair);

        VkForge_EndCommandBuffer(render->cmdbuf_draw);

        render->status = VKFORGE_RENDER_SUBMITTING;
    }}

    if( VKFORGE_RENDER_SUBMITTING == render->status )
    {{
        VkForge_QueueSubmit(render->queue, render->cmdbuf_copy, 0, 0, render->semaphore_copy, 0);
        VkForge_QueueSubmit
        (
            render->queue,
            render->cmdbuf_draw,
            VK_PIPELINE_STAGE_TRANSFER_BIT,
            render->semaphore_copy,
            render->semaphore_draw,
            render->fence_submit
        );

        VkResult result = VkForge_QueuePresent
        (
            render->queue, 
            render->swapchain, 
            render->index, 
            render->semaphore_draw
        );

        if( VK_SUCCESS == result )
        {{
            render->success_present = true;
            render->swapchainRecreationCount = 0; // reset swapchain creation count once there is a successful present.
        }}
        else if( VK_SUBOPTIMAL_KHR == result || VK_ERROR_OUT_OF_DATE_KHR == result )
        {{
            render->success_present = false;
            SDL_LogError(0, "Failed to Present Queue due to %s. %d The swapchain will be re-created.", counter++, VkForge_StringifyResult(result));
        }}
        else
        {{
            SDL_LogError(0, "Failed to Present Queue: %s", VkForge_StringifyResult(result));
            exit(1);
        }}

        render->status = VKFORGE_RENDER_PENDING_SUBMIT;
    }}

    if( VKFORGE_RENDER_PENDING_SUBMIT == render->status )
    {{
        if( VK_SUCCESS == vkGetFenceStatus(render->device, render->fence_submit) )
        {{
            vkResetFences(render->device, 1, &render->fence_submit);

            if( render->success_present )
                render->status = VKFORGE_RENDER_READY;
            else
                render->status = VKFORGE_RENDER_RECREATE;
        }}
    }}

    if( VKFORGE_RENDER_RECREATE == render->status )
    {{
        // Ensure Window is no longer minimized
        int width, height;
        if( !SDL_GetWindowSizeInPixels(render->window, &width, &height) )
        {{
            SDL_LogError(0, "Can not acquire the Window Size");
            exit(1);
        }}

        VkSurfaceCapabilitiesKHR surface_cap = VkForge_GetSurfaceCapabilities(render->surface, render->physical_device);

        if( width && height && surface_cap.currentExtent.width && surface_cap.currentExtent.height )
        {{
            if( VKFORGE_MAX_SWAPCHAIN_RECREATION < render->swapchainRecreationCount )
            {{
                SDL_LogError(0, "Swapchain has been recreated too many times without resolution.");
                exit(1);
            }}

            SDL_LogInfo(0, "Recreating Swapchain for Window %dx%d", width, height);

            VkForge_ReCreateRenderSwapchain(render);
            VkForge_RefreshRenderData(render);
            render->swapchainRecreationCount ++;

            render->status = VKFORGE_RENDER_READY;
        }}
    }}
}}
"""
    return content.format()

def GetCoreStrings(ctx: VkForgeContext):
    return [
        CreateInstance(ctx),
        CreateSurface(ctx),
        CreateSelectPhysicalDevice(ctx),
        CreateDevice(ctx),
        CreateSwapchain(ctx),
        CreateCommandBuffers(ctx),
        CreateCreateCore(ctx),
        CreateDestroyCore(ctx),
        CreateDestroy(ctx),
        CreateCreateRender(ctx),
        CreateUpdateRender(ctx),
        CreateRefreshRender(ctx),
        CreateDestroyRender(ctx),
        CreateReCreateRenderSwapchain(ctx)
    ]
