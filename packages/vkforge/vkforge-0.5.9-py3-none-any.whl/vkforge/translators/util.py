from vkforge.context import VkForgeContext
from vkforge.mappings import *


def CreateDebugMsgCallback(ctx: VkForgeContext) -> str:
    content = """\
VKAPI_ATTR VkBool32 VKAPI_CALL VkForge_DebugMsgCallback
(
    VkDebugUtilsMessageSeverityFlagBitsEXT severity,
    VkDebugUtilsMessageTypeFlagsEXT type,
    const VkDebugUtilsMessengerCallbackDataEXT* callback,
    void* user
)
{{
    (void)user;

    const char* typeStr = "";
    if (type & VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT)
    {{
        typeStr = "[VALIDATION]";
    }} else if (type & VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT)
    {{
        typeStr = "[PERFORMANCE]";
    }} else if (type & VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT)
    {{
        typeStr = "[GENERAL]";
    }}

    if (severity & VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT)
    {{
        SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "%s %s", typeStr, callback->pMessage);
    }} else if (severity & VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT)
    {{
        SDL_LogWarn(SDL_LOG_CATEGORY_APPLICATION, "%s %s", typeStr, callback->pMessage);
    }} else if (severity & VK_DEBUG_UTILS_MESSAGE_SEVERITY_INFO_BIT_EXT ||
               severity & VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT)
    {{
        SDL_Log("%s %s", typeStr, callback->pMessage);
    }}

    return VK_FALSE;
}}
"""
    output = content.format()

    return output


def CreateDebugMsgInfo(ctx: VkForgeContext) -> str:
    if not ctx.forgeModel.DebugUtilsMessengerCreateInfoEXT.messageSeverity:
        messageSeverity = "0"
    else:
        messageSeverity = ""
        for ms in ctx.forgeModel.DebugUtilsMessengerCreateInfoEXT.messageSeverity:
            ms = map_value(MSG_SEVERITY_MAP, ms)
            if len(messageSeverity) > 0:
                messageSeverity += "|" + "\n\t\t" + ms
            else:
                messageSeverity += ms
    
    if not ctx.forgeModel.DebugUtilsMessengerCreateInfoEXT.messageType:
        messageType = "0"
    else:
        messageType = ""
        for mt in ctx.forgeModel.DebugUtilsMessengerCreateInfoEXT.messageType:
            mt = map_value(MSG_TYPE_MAP, mt)
            if len(messageType) > 0:
                messageType += " | " + "\n\t\t" + mt
            else:
                messageType += mt

    content = """\
VkDebugUtilsMessengerCreateInfoEXT VkForge_GetDebugUtilsMessengerCreateInfo()
{{
    VkDebugUtilsMessengerCreateInfoEXT createInfo = {{0}};
    createInfo.sType = VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT;
    createInfo.messageSeverity = 
        {messageSeverity};
    createInfo.messageType =
        {messageType};
    createInfo.pfnUserCallback = VkForge_DebugMsgCallback;
    return createInfo;
}}
"""
    output = content.format(
        messageSeverity=messageSeverity,
        messageType=messageType,
    )

    return output


def CreateScorePhysicalDevice(ctx: VkForgeContext) -> str:
    content = """\
uint32_t VkForge_ScorePhysicalDeviceLimits(VkPhysicalDeviceLimits limits)
{{
    uint32_t score = 0;
    score += limits.maxImageDimension1D;
    score += limits.maxImageDimension2D;
    score += limits.maxImageDimension3D;
    score += limits.maxImageDimensionCube;
    score += limits.maxImageArrayLayers;
    score += limits.maxTexelBufferElements;
    score += limits.maxUniformBufferRange;
    score += limits.maxStorageBufferRange;
    score += limits.maxPushConstantsSize;
    score += limits.maxMemoryAllocationCount;
    score += limits.maxSamplerAllocationCount;
    score += limits.maxBoundDescriptorSets;
    score += limits.maxPerStageDescriptorSamplers;
    score += limits.maxPerStageDescriptorUniformBuffers;
    score += limits.maxPerStageDescriptorStorageBuffers;
    score += limits.maxPerStageDescriptorSampledImages;
    score += limits.maxPerStageDescriptorStorageImages;
    score += limits.maxPerStageDescriptorInputAttachments;
    score += limits.maxPerStageResources;
    score += limits.maxDescriptorSetSamplers;
    score += limits.maxDescriptorSetUniformBuffers;
    score += limits.maxDescriptorSetUniformBuffersDynamic;
    score += limits.maxDescriptorSetStorageBuffers;
    score += limits.maxDescriptorSetStorageBuffersDynamic;
    score += limits.maxDescriptorSetSampledImages;
    score += limits.maxDescriptorSetStorageImages;
    score += limits.maxDescriptorSetInputAttachments;
    score += limits.maxVertexInputAttributes;
    score += limits.maxVertexInputBindings;
    score += limits.maxVertexInputAttributeOffset;
    score += limits.maxVertexInputBindingStride;
    score += limits.maxVertexOutputComponents;
    score += limits.maxTessellationGenerationLevel;
    score += limits.maxTessellationPatchSize;
    score += limits.maxTessellationControlPerVertexInputComponents;
    score += limits.maxTessellationControlPerVertexOutputComponents;
    score += limits.maxTessellationControlPerPatchOutputComponents;
    score += limits.maxTessellationControlTotalOutputComponents;
    score += limits.maxTessellationEvaluationInputComponents;
    score += limits.maxTessellationEvaluationOutputComponents;
    score += limits.maxGeometryShaderInvocations;
    score += limits.maxGeometryInputComponents;
    score += limits.maxGeometryOutputComponents;
    score += limits.maxGeometryOutputVertices;
    score += limits.maxGeometryTotalOutputComponents;
    score += limits.maxFragmentInputComponents;
    score += limits.maxFragmentOutputAttachments;
    score += limits.maxFragmentDualSrcAttachments;
    score += limits.maxFragmentCombinedOutputResources;
    score += limits.maxComputeSharedMemorySize;
    score += limits.maxComputeWorkGroupInvocations;
    score += limits.maxDrawIndexedIndexValue;
    score += limits.maxDrawIndirectCount;
    score += limits.maxSamplerLodBias;
    score += limits.maxSamplerAnisotropy;
    score += limits.maxViewports;
    score += limits.maxTexelOffset;
    score += limits.maxTexelGatherOffset;
    score += limits.maxInterpolationOffset;
    score += limits.maxFramebufferWidth;
    score += limits.maxFramebufferHeight;
    score += limits.maxFramebufferLayers;
    score += limits.framebufferColorSampleCounts;
    score += limits.framebufferDepthSampleCounts;
    score += limits.framebufferStencilSampleCounts;
    score += limits.framebufferNoAttachmentsSampleCounts;
    score += limits.maxColorAttachments;
    score += limits.sampledImageColorSampleCounts;
    score += limits.sampledImageIntegerSampleCounts;
    score += limits.sampledImageDepthSampleCounts;
    score += limits.sampledImageStencilSampleCounts;
    score += limits.storageImageSampleCounts;
    score += limits.maxSampleMaskWords;
    score += limits.maxClipDistances;
    score += limits.maxCullDistances;
    score += limits.maxCombinedClipAndCullDistances;

    return score;
}}
"""
    output = content.format()

    return output


def CreateFence(ctx: VkForgeContext) -> str:
    content = """\
VkFence VkForge_CreateFence(VkDevice device)
{{
    VkFenceCreateInfo createInfo = {{0}};
    createInfo.sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;

    VkFence fence = VK_NULL_HANDLE;
    VkResult result;

    result = vkCreateFence(device, &createInfo, 0, &fence);

    if( VK_SUCCESS != result )
    {{
        SDL_Log("Failed to create VkFence.");
        exit(1);
    }}

    return fence;
}}
"""
    output = content.format()

    return output


def CreateSemaphore(ctx: VkForgeContext) -> str:
    content = """\
VkSemaphore VkForge_CreateSemaphore(VkDevice device)
{{
    VkSemaphoreCreateInfo createInfo = {{0}};
    createInfo.sType = VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO;

    VkSemaphore semaphore = VK_NULL_HANDLE;
    VkResult result;

    result = vkCreateSemaphore(device, &createInfo, 0, &semaphore);

    if( VK_SUCCESS != result )
    {{
        SDL_Log("Failed to create VkSemaphore.");
        exit(1);
    }}

    return semaphore;
}}
"""
    output = content.format()

    return output


def CreateCmdImageBarrier(ctx: VkForgeContext) -> str:
    content = """\
void VkForge_CmdImageBarrier
(
    VkCommandBuffer cmdbuf,

    VkImage image,
    VkImageLayout oldLayout,
    VkImageLayout newLayout,
    VkAccessFlags srcAccessMask,
    VkAccessFlags dstAccessMask,
    VkPipelineStageFlags srcStageFlags,
    VkPipelineStageFlags dstStageFlags
)
{{
    VkImageMemoryBarrier barrier = {{0}};
    barrier.sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
    barrier.oldLayout = oldLayout;
    barrier.newLayout = newLayout;
    barrier.image = image;
    barrier.srcAccessMask = srcAccessMask;
    barrier.dstAccessMask = dstAccessMask;
    barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    barrier.subresourceRange.levelCount = 1;
    barrier.subresourceRange.layerCount = 1;
    barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;

    vkCmdPipelineBarrier(
        cmdbuf,
        srcStageFlags,
        dstStageFlags,
        0,
        0,0,
        0,0,
        1, &barrier
    );
}}


"""
    output = content.format()

    return output


def CreateCmdBufferBarrier(ctx: VkForgeContext) -> str:
    content = """\
void VkForge_CmdBufferBarrier
(
    VkCommandBuffer cmdbuf,

    VkBuffer buffer,
    VkDeviceSize offset,
    VkDeviceSize size,
    VkAccessFlags srcAccessMask,
    VkAccessFlags dstAccessMask,
    VkPipelineStageFlags srcStageFlags,
    VkPipelineStageFlags dstStageFlags
)
{{
    VkBufferMemoryBarrier barrier = {{0}};
    barrier.sType = VK_STRUCTURE_TYPE_BUFFER_MEMORY_BARRIER;
    barrier.buffer = buffer;
    barrier.offset = offset;
    barrier.size = size;
    barrier.srcAccessMask = srcAccessMask;
    barrier.dstAccessMask = dstAccessMask;
    barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;

    vkCmdPipelineBarrier(
        cmdbuf,
        srcStageFlags,
        dstStageFlags,
        0,
        0,0,
        1, &barrier,
        0,0
    );
}}

"""
    output = content.format()

    return output


def CreateGetSurfaceFormat(ctx: VkForgeContext) -> str:
    content = """\
VkSurfaceFormatKHR VkForge_GetSurfaceFormat
(
    VkSurfaceKHR     surface,
    VkPhysicalDevice physical_device,
    VkFormat         req_format
)
{{
    VKFORGE_ENUM(
        formats,
        VkSurfaceFormatKHR,
        vkGetPhysicalDeviceSurfaceFormatsKHR,
        64,
        physical_device,
        surface
    );

    for (uint32_t i = 0; i < formats_count; i++)
    {{
        if (req_format == formats_buffer[i].format)
            return formats_buffer[i];
    }}

    return formats_buffer[0];
}}

"""
    output = content.format()

    return output


def CreateGetSurfaceCapabilities(ctx: VkForgeContext) -> str:
    content = """\
VkSurfaceCapabilitiesKHR VkForge_GetSurfaceCapabilities
(
    VkSurfaceKHR     surface,
    VkPhysicalDevice physical_device
)
{{
    VkSurfaceCapabilitiesKHR surface_cap = {{0}};
    VkResult result = vkGetPhysicalDeviceSurfaceCapabilitiesKHR(physical_device, surface, &surface_cap);

    if( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to get physical device surface capabilities");
        exit(1);
    }}

    return surface_cap;
}}

"""
    output = content.format()

    return output

def CreateGetSwapchainSize(ctx:VkForgeContext) -> str:
    content = """\
uint32_t VkForge_GetSwapchainSize
(
    VkSurfaceKHR     surface,
    VkPhysicalDevice physical_device,
    uint32_t         req_size
)
{{

    VkSurfaceCapabilitiesKHR surface_cap = VkForge_GetSurfaceCapabilities(surface, physical_device);

    if ( surface_cap.maxImageCount == 0 )
    {{
        return req_size;
    }}

    if (req_size <= surface_cap.maxImageCount)
    {{
        return req_size;
    }}

    return surface_cap.minImageCount;
}}

"""
    output = content.format()

    return output

def CreateGetPresentMode(ctx: VkForgeContext) -> str:
    content = """\
VkPresentModeKHR VkForge_GetPresentMode
(
    VkSurfaceKHR     surface,
    VkPhysicalDevice physical_device,
    VkPresentModeKHR req_mode
)
{{
    VKFORGE_ENUM(
        modes,
        VkPresentModeKHR,
        vkGetPhysicalDeviceSurfacePresentModesKHR,
        4,
        physical_device,
        surface
    );

    for (uint32_t i = 0; i < modes_count; i++)
    {{
        if (req_mode == modes_buffer[i]) return req_mode;
    }}

    return modes_buffer[0];
}}

"""
    output = content.format()

    return output


def CreateGetMemoryTypeIndex(ctx: VkForgeContext) -> str:
    content = """\
uint32_t VkForge_GetMemoryTypeIndex
(
    VkPhysicalDevice      physical_device,
    uint32_t              typeFilter,
    VkMemoryPropertyFlags properties
)
{{
    VkPhysicalDeviceMemoryProperties memProperties = {{0}};
    vkGetPhysicalDeviceMemoryProperties(physical_device, &memProperties);

    for (uint32_t i = 0; i < memProperties.memoryTypeCount; i++)
    {{
        if ((typeFilter & (1 << i)) &&
            (memProperties.memoryTypes[i].propertyFlags & properties) == properties)
        {{
            return i;
        }}
    }}

    SDL_LogError(0, "Failed to find suitable Vulkan memory type");
    exit(1);
    return 0;
}}

"""
    output = content.format()

    return output

def CreateCreateBufferAlloc(ctx: VkForgeContext) -> str:
    content = """\
VkForgeBufferAlloc VkForge_CreateBufferAlloc
(
    VkPhysicalDevice           physical_device,
    VkDevice                   device,
    VkDeviceSize               size,
    VkBufferUsageFlags         usage,
    VkMemoryPropertyFlags      properties
)
{{
    VkResult result;
    VkMemoryRequirements memRequirements;
    VkForgeBufferAlloc allocation = {{0}};

    allocation.buffer = VkForge_CreateBuffer(device, size, usage, &memRequirements);
    allocation.memory = VkForge_AllocDeviceMemory(physical_device, device, memRequirements, properties);
    allocation.size   = memRequirements.size;
    VkForge_BindBufferMemory(device, allocation.buffer, allocation.memory, 0);

    return allocation;
}}
"""
    return content.format()

def CreateCreateImageAlloc(ctx: VkForgeContext) -> str:
    content = """\
VkForgeImageAlloc VkForge_CreateImageAlloc
(
    VkPhysicalDevice           physical_device,
    VkDevice                   device,
    uint32_t                   width,
    uint32_t                   height,
    VkFormat                   format,
    VkImageUsageFlags          usage,
    VkMemoryPropertyFlags      properties
)
{{
    VkResult result;
    VkMemoryRequirements memRequirements;
    VkForgeImageAlloc allocation = {{0}};

    allocation.image  = VkForge_CreateImage(device, width, height, format, usage, &memRequirements);
    allocation.memory = VkForge_AllocDeviceMemory(physical_device, device, memRequirements, properties);
    allocation.size   = memRequirements.size;
    VkForge_BindImageMemory(device, allocation.image, allocation.memory, 0);

    return allocation;
}}
"""
    return content.format()

def CreateCreateImageOffset(ctx: VkForgeContext) -> str:
    content = """\
VkImage VkForge_CreateOffsetImage
(
    VkDevice                   device,
    VkDeviceMemory             memory,
    VkDeviceSize               offset,
    uint32_t                   width,
    uint32_t                   height,
    VkFormat                   format,
    VkImageUsageFlags          usage
)
{{
    VkImageCreateInfo imageInfo = {{0}};
    imageInfo.sType         = VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO;
    imageInfo.imageType     = VK_IMAGE_TYPE_2D;
    imageInfo.extent.width  = width;
    imageInfo.extent.height = height;
    imageInfo.extent.depth  = 1;
    imageInfo.mipLevels     = 1;
    imageInfo.arrayLayers   = 1;
    imageInfo.format        = format;
    imageInfo.tiling        = VK_IMAGE_TILING_OPTIMAL;
    imageInfo.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    imageInfo.usage         = usage;
    imageInfo.samples       = VK_SAMPLE_COUNT_1_BIT;
    imageInfo.sharingMode   = VK_SHARING_MODE_EXCLUSIVE;

    VkImage image;
    VkResult result = vkCreateImage(device, &imageInfo, 0, &image);
    if (VK_SUCCESS != result) 
    {{
        SDL_LogError(0, "Failed to create offset image");
        exit(1);
    }}

    result = vkBindImageMemory(device, image, memory, offset);
    if (VK_SUCCESS != result) 
    {{
        SDL_LogError(0, "Failed to bind offset image memory");
        exit(1);
    }}

    return image;
}}
"""
    return content.format()

def CreateCreateBufferOffset(ctx: VkForgeContext) -> str:
    content = """\
VkBuffer VkForge_CreateOffsetBuffer
(
    VkDevice                   device,
    VkDeviceMemory             memory,
    VkDeviceSize               offset,
    VkDeviceSize               size,
    VkBufferUsageFlags         usage
)
{{
    VkBufferCreateInfo bufferInfo = {{0}};
    bufferInfo.sType       = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;
    bufferInfo.size        = size;
    bufferInfo.usage       = usage;
    bufferInfo.sharingMode = VK_SHARING_MODE_EXCLUSIVE;

    VkBuffer buffer;
    VkResult result = vkCreateBuffer(device, &bufferInfo, 0, &buffer);
    if (VK_SUCCESS != result) 
    {{
        SDL_LogError(0, "Failed to create offset buffer");
        exit(1);
    }}

    result = vkBindBufferMemory(device, buffer, memory, offset);
    if (VK_SUCCESS != result) 
    {{
        SDL_LogError(0, "Failed to bind offset buffer memory");
        exit(1);
    }}

    return buffer;
}}
"""
    return content.format()

def CreateStagingBuffer(ctx: VkForgeContext):
    content = """VkForgeBufferAlloc VkForge_CreateStagingBuffer
(
    VkPhysicalDevice physical_device,
    VkDevice device,
    VkDeviceSize size
)
{{
    return VkForge_CreateBufferAlloc
    (
        physical_device,
        device,
        size,
        VK_BUFFER_USAGE_TRANSFER_SRC_BIT,
        VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
    );
}}
"""
    return content.format()

def CreateCreateTexture(ctx: VkForgeContext):
    content = """\
VkForgeTexture* VkForge_CreateTexture
(
    VkPhysicalDevice physical_device,
    VkDevice device,
    VkQueue queue,
    VkCommandBuffer commandBuffer,
    const char* filename,
    const char* pixel_order
)
{{
    VkImageUsageFlags usage = VK_IMAGE_USAGE_TRANSFER_DST_BIT | VK_IMAGE_USAGE_SAMPLED_BIT;
    VkSamplerAddressMode addressMode = VK_SAMPLER_ADDRESS_MODE_REPEAT;
    VkFilter filter = VK_FILTER_LINEAR;

    VkForgeTexture* texture = SDL_malloc(sizeof(VkForgeTexture));
    SDL_memset(texture, 0, sizeof(VkForgeTexture));

    VkForgePixelFormatPair fmtPair = VkForge_GetPixelFormatFromString(pixel_order);
    
    SDL_Surface* surface = IMG_Load(filename);
    if (!surface) 
    {{
        SDL_LogError(0, "Failed to load texture image: %s", filename);
        exit(1);
    }}

    SDL_Surface* converted = SDL_ConvertSurface(surface, fmtPair.sdl_format);
    SDL_DestroySurface(surface);
    if (!converted) 
    {{
        SDL_LogError(0, "Failed to convert surface format: %s", filename);
        return texture;
    }}
    surface = converted;

    texture->width = surface->w;
    texture->height = surface->h;
    texture->format = fmtPair.vk_format;
    texture->samples = VK_SAMPLE_COUNT_1_BIT;

    VkDeviceSize imageSize = surface->pitch * surface->h;

    VkForgeBufferAlloc staging = VkForge_CreateStagingBuffer(physical_device, device, imageSize);

    void* data;
    vkMapMemory(device, staging.memory, 0, imageSize, 0, &data);
    SDL_memcpy(data, surface->pixels, imageSize);
    vkUnmapMemory(device, staging.memory);
    SDL_DestroySurface(surface);

    VkForgeImageAlloc imageAlloc = VkForge_CreateImageAlloc
    (
        physical_device,
        device,
        texture->width,
        texture->height,
        texture->format,
        usage,
        VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT
    );

    texture->image = imageAlloc.image;
    texture->memory = imageAlloc.memory;

    VkForge_BeginCommandBuffer(commandBuffer);

    VkForge_CmdImageBarrier
    (
        commandBuffer,
        texture->image,
        VK_IMAGE_LAYOUT_UNDEFINED,
        VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
        0,
        VK_ACCESS_TRANSFER_WRITE_BIT,
        VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,
        VK_PIPELINE_STAGE_TRANSFER_BIT
    );

    VkForge_CmdCopyBufferToImage
    (
        commandBuffer, 
        staging.buffer,
        texture->image,
        0, 0,
        texture->width, texture->height,
        VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL
    );

    VkForge_CmdImageBarrier
    (
        commandBuffer,
        texture->image,
        VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
        VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,
        VK_ACCESS_TRANSFER_WRITE_BIT,
        VK_ACCESS_SHADER_READ_BIT,
        VK_PIPELINE_STAGE_TRANSFER_BIT,
        VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT
    );

    VkForge_EndCommandBuffer(commandBuffer);

    VkFence fence = VkForge_CreateFence(device);
    VkForge_QueueSubmit(queue, commandBuffer, 0, 0, 0, fence);
    vkWaitForFences(device, 1, &fence, VK_TRUE, UINT64_MAX);

    vkDestroyFence(device, fence, 0);
    VkForge_DestroyBufferAlloc(device, staging);

    texture->imageView = VkForge_CreateImageView(device, texture->image, texture->format);
    texture->sampler = VkForge_CreateSampler(device, filter, addressMode);

    return texture;
}}
"""
    return content.format()

def CreateDestroyTexture(ctx: VkForgeContext):
    content = """\
void VkForge_DestroyTexture(VkDevice device, VkForgeTexture* texture)
{{
    if (device == VK_NULL_HANDLE) {{
        SDL_LogError(0, "Invalid device handle when destroying texture");
        return;
    }}

    // Destroy sampler if it exists
    if (texture->sampler != VK_NULL_HANDLE) {{
        vkDestroySampler(device, texture->sampler, NULL);
        texture->sampler = VK_NULL_HANDLE;
    }}

    // Destroy image view if it exists
    if (texture->imageView != VK_NULL_HANDLE) {{
        vkDestroyImageView(device, texture->imageView, NULL);
        texture->imageView = VK_NULL_HANDLE;
    }}

    // Destroy image if it exists
    if (texture->image != VK_NULL_HANDLE) {{
        vkDestroyImage(device, texture->image, NULL);
        texture->image = VK_NULL_HANDLE;
    }}

    // Free memory if it exists
    if (texture->memory != VK_NULL_HANDLE) {{
        vkFreeMemory(device, texture->memory, NULL);
        texture->memory = VK_NULL_HANDLE;
    }}

    // Reset other fields
    texture->width = 0;
    texture->height = 0;
    texture->format = VK_FORMAT_UNDEFINED;
    texture->samples = VK_SAMPLE_COUNT_1_BIT;

    SDL_free(texture);
}}
"""
    return content.format()

def CreateBeginCommandBuffer(ctx: VkForgeContext):
    content = """\
void VkForge_BeginCommandBuffer(VkCommandBuffer cmdBuf)
{{
    VkCommandBufferBeginInfo beginInfo = {{0}};
    beginInfo.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
    beginInfo.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;

    VkResult result = vkBeginCommandBuffer(cmdBuf, &beginInfo);

    if( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to Begin command buffer");
        exit(1);
    }}
}}
"""
    return content.format()

def CreateEndCommandBuffer(ctx: VkForgeContext):
    content = """\
void VkForge_EndCommandBuffer(VkCommandBuffer cmdBuf)
{{
    VkResult result = vkEndCommandBuffer(cmdBuf);

    if( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to End command buffer");
        exit(1);
    }}
}}
"""
    return content.format()

def CreateCopyBufferToImage(ctx: VkForgeContext):
    content = """\
void VkForge_CmdCopyBufferToImage
(
    VkCommandBuffer cmdBuf,
    VkBuffer buffer,
    VkImage image,
    float x, float y,
    float w, float h,
    VkImageLayout layout
)
{{
    VkBufferImageCopy region = {{0}};
    region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.imageSubresource.mipLevel = 0;
    region.imageSubresource.baseArrayLayer = 0;
    region.imageSubresource.layerCount = 1;
    region.imageOffset = (VkOffset3D){{x, y, 0}};
    region.imageExtent = (VkExtent3D){{w, h, 1}};

    vkCmdCopyBufferToImage(
        cmdBuf,
        buffer,
        image,
        layout,
        1,
        &region
    );
}}
"""
    return content.format()

def CreateQueueSubmit(ctx: VkForgeContext):
    content = """\
void VkForge_QueueSubmit
(
    VkQueue queue,
    VkCommandBuffer cmdBuf,
    VkPipelineStageFlags waitStage,
    VkSemaphore waitSemaphore,
    VkSemaphore signalSemaphore,
    VkFence fence
)
{{
    VkSubmitInfo submitInfo = {{0}};
    submitInfo.sType = VK_STRUCTURE_TYPE_SUBMIT_INFO;
    submitInfo.commandBufferCount = 1;
    submitInfo.pCommandBuffers = &cmdBuf;
    submitInfo.pWaitDstStageMask = &waitStage;
    submitInfo.pWaitSemaphores = waitSemaphore ? &waitSemaphore : 0;
    submitInfo.pSignalSemaphores = signalSemaphore ? &signalSemaphore : 0;
    submitInfo.waitSemaphoreCount = waitSemaphore ? 1 : 0;
    submitInfo.signalSemaphoreCount = signalSemaphore ? 1 : 0;

    VkResult result = vkQueueSubmit(queue, 1, &submitInfo, fence);

    if( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to Queue Submit");
        exit(1);
    }}
}}
"""
    return content.format()

def CreateImageView(ctx: VkForgeContext):
    content = """\
VkImageView VkForge_CreateImageView
(
    VkDevice device,
    VkImage image,
    VkFormat format
)
{{
    VkImageViewCreateInfo viewInfo = {{0}};
    viewInfo.sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO;
    viewInfo.image = image;
    viewInfo.viewType = VK_IMAGE_VIEW_TYPE_2D;
    viewInfo.format = format;
    viewInfo.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    viewInfo.subresourceRange.baseMipLevel = 0;
    viewInfo.subresourceRange.levelCount = 1;
    viewInfo.subresourceRange.baseArrayLayer = 0;
    viewInfo.subresourceRange.layerCount = 1;

    VkResult result;
    VkImageView imageView = VK_NULL_HANDLE;

    result = vkCreateImageView(device, &viewInfo, 0, &imageView);

    if ( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to create ImageView");
        exit(1);
    }}

    return imageView;
}}
"""
    return content.format()

def CreateSampler(ctx: VkForgeContext):
    content = """\
VkSampler VkForge_CreateSampler
(
    VkDevice device,
    VkFilter filter,
    VkSamplerAddressMode addressMode
)
{{
    // Create sampler
    VkSamplerCreateInfo samplerInfo = {{0}};
    samplerInfo.sType = VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO;
    samplerInfo.magFilter = filter;
    samplerInfo.minFilter = filter;
    samplerInfo.addressModeU = addressMode;
    samplerInfo.addressModeV = addressMode;
    samplerInfo.addressModeW = addressMode;
    samplerInfo.anisotropyEnable = VK_FALSE;
    samplerInfo.maxAnisotropy = 16.0f;
    samplerInfo.borderColor = VK_BORDER_COLOR_INT_OPAQUE_BLACK;
    samplerInfo.unnormalizedCoordinates = VK_FALSE;
    samplerInfo.compareEnable = VK_FALSE;
    samplerInfo.compareOp = VK_COMPARE_OP_ALWAYS;
    samplerInfo.mipmapMode = VK_SAMPLER_MIPMAP_MODE_LINEAR;
    samplerInfo.mipLodBias = 0.0f;
    samplerInfo.minLod = 0.0f;
    samplerInfo.maxLod = 0.0f;

    VkResult result;
    VkSampler sampler = VK_NULL_HANDLE;

    result = vkCreateSampler(device, &samplerInfo, 0, &sampler);

    if ( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to create Sampler");
        exit(1);
    }}

    return sampler;
}}
"""
    return content.format()

def CreateCreateBuffer(ctx: VkForgeContext):
    content = """\
VkBuffer VkForge_CreateBuffer
(
    VkDevice                   device,
    VkDeviceSize               size,
    VkBufferUsageFlags         usage,

    VkMemoryRequirements      *inMemReqs
)
{{
    VkResult result;
    VkBuffer buffer = VK_NULL_HANDLE;

    VkBufferCreateInfo bufferInfo = {{0}};
    bufferInfo.sType       = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO;
    bufferInfo.size        = size;
    bufferInfo.usage       = usage;
    bufferInfo.sharingMode = VK_SHARING_MODE_EXCLUSIVE;

    result = vkCreateBuffer(device, &bufferInfo, 0, &buffer);
    if (VK_SUCCESS != result)
    {{
        SDL_LogError(0, "Failed to create buffer");
        exit(1);
    }}

    if( inMemReqs )
    {{
        VkMemoryRequirements memRequirements = {{0}};
        vkGetBufferMemoryRequirements(device, buffer, &memRequirements);
        *inMemReqs = memRequirements;
    }}

    return buffer;
}}
"""
    return content.format()

def CreateCreateImage(ctx: VkForgeContext):
    content = """\
VkImage VkForge_CreateImage
(
    VkDevice               device,
    uint32_t               width,
    uint32_t               height,
    VkFormat               format,
    VkImageUsageFlags      usage,

    VkMemoryRequirements  *inMemReqs
)
{{
    VkImage image = VK_NULL_HANDLE;

    VkImageCreateInfo imageInfo = {{0}};
    imageInfo.sType         = VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO;
    imageInfo.imageType     = VK_IMAGE_TYPE_2D;
    imageInfo.extent.width  = width;
    imageInfo.extent.height = height;
    imageInfo.extent.depth  = 1;
    imageInfo.mipLevels     = 1;
    imageInfo.arrayLayers   = 1;
    imageInfo.format        = format;
    imageInfo.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    imageInfo.usage         = usage;
    imageInfo.sharingMode   = VK_SHARING_MODE_EXCLUSIVE;
    imageInfo.samples       = VK_SAMPLE_COUNT_1_BIT;
    imageInfo.flags         = 0;

    VkResult result = vkCreateImage(device, &imageInfo, NULL, &image);
    if (result != VK_SUCCESS)
    {{
        SDL_LogError(0, "Failed to create image");
        exit(1);
    }}

    if( inMemReqs )
    {{
        VkMemoryRequirements memRequirements = {{0}};
        vkGetImageMemoryRequirements(device, image, &memRequirements);
        *inMemReqs = memRequirements;
    }}

    return image;
}}
"""
    return content.format()

def CreateAllocDeviceMemory(ctx: VkForgeContext):
    content = """\
VkDeviceMemory VkForge_AllocDeviceMemory
(
    VkPhysicalDevice physical_device,
    VkDevice device,
    VkMemoryRequirements memRequirements,
    VkMemoryPropertyFlags properties
)
{{
    VkMemoryAllocateInfo allocInfo = {{0}};
    allocInfo.sType               = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO;
    allocInfo.allocationSize      = memRequirements.size;
    allocInfo.memoryTypeIndex     = VkForge_GetMemoryTypeIndex
    (
        physical_device,
        memRequirements.memoryTypeBits,
        properties
    );

    VkDeviceMemory memory = VK_NULL_HANDLE;

    VkResult result = vkAllocateMemory(device, &allocInfo, 0, &memory);
    if (VK_SUCCESS != result)
    {{
        SDL_LogError(0, "Failed to Allocate Device Memory: %s", VkForge_StringifyResult(result));
        exit(1);
    }}

    return memory;
}}
"""
    return content.format()

def CreateBindBufferMemory(ctx: VkForgeContext):
    content = """\
void VkForge_BindBufferMemory(VkDevice device, VkBuffer buffer, VkDeviceMemory memory, VkDeviceSize offset)
{{
    VkResult result = vkBindBufferMemory(device, buffer, memory, offset);

    if (VK_SUCCESS != result)
    {{
        SDL_LogError(0, "Failed to Bind Buffer to Memory: %s", VkForge_StringifyResult(result));
        exit(1);
    }}
}}
"""
    return content.format()

def CreateBindImageMemory(ctx: VkForgeContext):
    content = """\
void VkForge_BindImageMemory(VkDevice device, VkImage image, VkDeviceMemory memory, VkDeviceSize offset)
{{
    VkResult result = vkBindImageMemory(device, image, memory, offset);

    if (VK_SUCCESS != result)
    {{
        SDL_LogError(0, "Failed to Image to Memory: %s", VkForge_StringifyResult(result));
        exit(1);
    }}
}}
"""
    return content.format()

def CreateDestroyBufferAlloc(ctx: VkForgeContext):
    content = """\
void VkForge_DestroyBufferAlloc(VkDevice device, VkForgeBufferAlloc bufferAlloc)
{{
    vkDestroyBuffer(device, bufferAlloc.buffer, 0);
    vkFreeMemory(device, bufferAlloc.memory, 0);
}}
"""
    return content.format()

def CreateDestroyBufferAlloc(ctx: VkForgeContext):
    content = """\
void VkForge_DestroyBufferAlloc(VkDevice device, VkForgeBufferAlloc bufferAlloc)
{{
    vkDestroyBuffer(device, bufferAlloc.buffer, 0);
    vkFreeMemory(device, bufferAlloc.memory, 0);
}}
"""
    return content.format()

def CreateDestroyImageAlloc(ctx: VkForgeContext):
    content = """\
void VkForge_DestroyImageAlloc(VkDevice device, VkForgeImageAlloc imageAlloc)
{{
    vkDestroyImage(device, imageAlloc.image, 0);
    vkFreeMemory(device, imageAlloc.memory, 0);
}}
"""
    return content.format()

def CreateSetColor(ctx: VkForgeContext):
    content = """\
void VkForge_SetColor(const char* hex, float alpha, float color[4])
{{
    // Skip '#' if present
    if (hex[0] == '#') {{
        hex++;
    }}

    // Must be exactly 6 hex digits
    if (strlen(hex) != 6)
    {{
        SDL_LogError(0, "Invalid hex color: %s\\n", hex);
        exit(1);
    }}

    // Extract pairs
    char rs[3] = {{ hex[0], hex[1], '\\0' }};
    char gs[3] = {{ hex[2], hex[3], '\\0' }};
    char bs[3] = {{ hex[4], hex[5], '\\0' }};

    // Convert hex to int
    int r = (int)strtol(rs, NULL, 16);
    int g = (int)strtol(gs, NULL, 16);
    int b = (int)strtol(bs, NULL, 16);

    // Normalize to [0, 1]
    color[0] = r / 255.0f;
    color[1] = g / 255.0f;
    color[2] = b / 255.0f;
    color[3] = alpha > 1.0 ? 1 : alpha;
}}
"""
    return content.format()

def CreateBeginRendering(ctx: VkForgeContext):
    content = """\
void VkForge_CmdBeginRendering
(
    VkCommandBuffer  cmdbuf,
    VkForgeImagePair imgPair,
    const char*      clearColorHex,
    VkForgeQuad      quad
)
{{
    VkForge_CmdImageBarrier(
        cmdbuf,
        imgPair.image,
        VK_IMAGE_LAYOUT_UNDEFINED,
        VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
        0,
        VK_ACCESS_2_COLOR_ATTACHMENT_WRITE_BIT,
        VK_PIPELINE_STAGE_2_TOP_OF_PIPE_BIT,
        VK_PIPELINE_STAGE_2_COLOR_ATTACHMENT_OUTPUT_BIT
    );

    VkRenderingAttachmentInfo colorAttachment = {{0}};
    colorAttachment.sType                     = VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO;
    colorAttachment.imageView                 = imgPair.imgview;
    colorAttachment.imageLayout               = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;
    colorAttachment.loadOp                    = VK_ATTACHMENT_LOAD_OP_CLEAR;
    colorAttachment.storeOp                   = VK_ATTACHMENT_STORE_OP_STORE;

    VkClearValue clearVal       = {{0}};
    clearVal.depthStencil.depth = 1.0f;
    VkForge_SetColor(clearColorHex, 1.0f, clearVal.color.float32);
    colorAttachment.clearValue = clearVal;

    VkRenderingInfo renderingInfo          = {{0}};
    renderingInfo.sType                    = VK_STRUCTURE_TYPE_RENDERING_INFO;
    renderingInfo.renderArea.offset.x      = quad.x;
    renderingInfo.renderArea.offset.y      = quad.y;
    renderingInfo.renderArea.extent.width  = quad.w;
    renderingInfo.renderArea.extent.height = quad.h;
    renderingInfo.layerCount               = 1;
    renderingInfo.colorAttachmentCount     = 1;
    renderingInfo.pColorAttachments        = &colorAttachment;

    vkCmdBeginRendering(cmdbuf, &renderingInfo);
}}
"""
    return content.format()

def CreateEndRendering(ctx: VkForgeContext):
    content = """\
void VkForge_CmdEndRendering(VkCommandBuffer cmdbuf, VkForgeImagePair imgPair)
{{
    vkCmdEndRendering(cmdbuf);

    VkForge_CmdImageBarrier
    (
        cmdbuf,
        imgPair.image,
        VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
        VK_IMAGE_LAYOUT_PRESENT_SRC_KHR,
        VK_ACCESS_2_COLOR_ATTACHMENT_WRITE_BIT,
        0,
        VK_PIPELINE_STAGE_2_COLOR_ATTACHMENT_OUTPUT_BIT,
        VK_PIPELINE_STAGE_2_BOTTOM_OF_PIPE_BIT
    );
}}
"""
    return content.format()

def CreateQueuePresent(ctx: VkForgeContext):
    content = """\
VkResult VkForge_QueuePresent
(
    VkQueue queue,
    VkSwapchainKHR swapchain,
    uint32_t index,
    VkSemaphore waitSemaphore
)
{{
    VkPresentInfoKHR presentInfo = {{0}};
    presentInfo.sType = VK_STRUCTURE_TYPE_PRESENT_INFO_KHR;
    presentInfo.swapchainCount = 1;
    presentInfo.pSwapchains = &swapchain;
    presentInfo.pImageIndices = &index;
    presentInfo.pWaitSemaphores = &waitSemaphore;
    presentInfo.waitSemaphoreCount = 1;

    return vkQueuePresentKHR(queue, &presentInfo);
}}
"""
    return content.format()

def CreateReadFile(ctx: VkForgeContext):
    content = """\
void* VkForge_ReadFile(const char* filePath, Sint64* inSize)
{{
    SDL_IOStream* io = SDL_IOFromFile(filePath, "rb");
    if(!io)
    {{
        SDL_LogError(0, "Failed to read %s: %s", filePath, SDL_GetError());
        exit(1);
    }}

    const Sint64 size = SDL_GetIOSize(io);
    if(size < 0)
    {{
        SDL_LogError(0, "Size of %s is %d", filePath, size);
        exit(1);
    }}

    size_t buffer_size = size ? ((size_t)size % 4 + (size_t)size) : 4;

    if (inSize) {{
        *inSize = (Sint64)buffer_size;
    }}

    void* buffer = SDL_malloc(buffer_size);
    SDL_memset(buffer, 0, buffer_size);
    assert(buffer);

    size_t read_size = SDL_ReadIO(io, buffer, size);

    if(read_size != size)
    {{
        SDL_LogWarn(0, "%s: requested %d, but read %d, returned: %d", filePath, size, read_size, buffer_size);
    }}

    SDL_CloseIO(io);

    return buffer;
}}
"""
    return content.format()

def CreateCreateShaderModule(ctx: VkForgeContext):
    content = """\
VkShaderModule VkForge_CreateShaderModule(VkDevice device, const char* filePath)
{{
    VkShaderModule shadermod = VK_NULL_HANDLE;

    Sint64 size = 0;
    const char* buffer = VkForge_ReadFile(filePath, &size);

    VkShaderModuleCreateInfo shadermod_create_info = {{0}};
    shadermod_create_info.sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO;
    shadermod_create_info.codeSize = size;
    shadermod_create_info.pCode = (uint32_t*)buffer;

    VkResult result = vkCreateShaderModule(device, &shadermod_create_info, 0, &shadermod);

    if ( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to Create Shader Module for %s", filePath);
        exit(1);
    }}

    return shadermod;
}}
"""
    return content.format()

def CreateStringifyResult(ctx: VkForgeContext):
    content = """\
const char* VkForge_StringifyResult(VkResult result)
{{
    switch (result)
    {{
        case VK_SUCCESS:
            return "VK_SUCCESS";
        case VK_NOT_READY:
            return "VK_NOT_READY";
        case VK_TIMEOUT:
            return "VK_TIMEOUT";
        case VK_EVENT_SET:
            return "VK_EVENT_SET";
        case VK_EVENT_RESET:
            return "VK_EVENT_RESET";
        case VK_INCOMPLETE:
            return "VK_INCOMPLETE";
        case VK_ERROR_OUT_OF_HOST_MEMORY:
            return "VK_ERROR_OUT_OF_HOST_MEMORY";
        case VK_ERROR_OUT_OF_DEVICE_MEMORY:
            return "VK_ERROR_OUT_OF_DEVICE_MEMORY";
        case VK_ERROR_INITIALIZATION_FAILED:
            return "VK_ERROR_INITIALIZATION_FAILED";
        case VK_ERROR_DEVICE_LOST:
            return "VK_ERROR_DEVICE_LOST";
        case VK_ERROR_MEMORY_MAP_FAILED:
            return "VK_ERROR_MEMORY_MAP_FAILED";
        case VK_ERROR_LAYER_NOT_PRESENT:
            return "VK_ERROR_LAYER_NOT_PRESENT";
        case VK_ERROR_EXTENSION_NOT_PRESENT:
            return "VK_ERROR_EXTENSION_NOT_PRESENT";
        case VK_ERROR_FEATURE_NOT_PRESENT:
            return "VK_ERROR_FEATURE_NOT_PRESENT";
        case VK_ERROR_INCOMPATIBLE_DRIVER:
            return "VK_ERROR_INCOMPATIBLE_DRIVER";
        case VK_ERROR_TOO_MANY_OBJECTS:
            return "VK_ERROR_TOO_MANY_OBJECTS";
        case VK_ERROR_FORMAT_NOT_SUPPORTED:
            return "VK_ERROR_FORMAT_NOT_SUPPORTED";
        case VK_ERROR_FRAGMENTED_POOL:
            return "VK_ERROR_FRAGMENTED_POOL";
        case VK_ERROR_UNKNOWN:
            return "VK_ERROR_UNKNOWN";
        case VK_ERROR_VALIDATION_FAILED_EXT:
            return "VK_ERROR_VALIDATION_FAILED_EXT";
        case VK_ERROR_OUT_OF_POOL_MEMORY_KHR:
            return "VK_ERROR_OUT_OF_POOL_MEMORY_KHR";
        case VK_ERROR_INVALID_EXTERNAL_HANDLE_KHR:
            return "VK_ERROR_INVALID_EXTERNAL_HANDLE_KHR";
        case VK_ERROR_FRAGMENTATION_EXT:
            return "VK_ERROR_FRAGMENTATION_EXT";
        case VK_ERROR_NOT_PERMITTED_EXT:
            return "VK_ERROR_NOT_PERMITTED_EXT";
        case VK_ERROR_INVALID_DEVICE_ADDRESS_EXT:
            return "VK_ERROR_INVALID_DEVICE_ADDRESS_EXT";
        case VK_PIPELINE_COMPILE_REQUIRED_EXT:
            return "VK_PIPELINE_COMPILE_REQUIRED_EXT";
        case VK_ERROR_SURFACE_LOST_KHR:
            return "VK_ERROR_SURFACE_LOST_KHR";
        case VK_ERROR_NATIVE_WINDOW_IN_USE_KHR:
            return "VK_ERROR_NATIVE_WINDOW_IN_USE_KHR";
        case VK_SUBOPTIMAL_KHR:
            return "VK_SUBOPTIMAL_KHR";
        case VK_ERROR_OUT_OF_DATE_KHR:
            return "VK_ERROR_OUT_OF_DATE_KHR";
        case VK_ERROR_INCOMPATIBLE_DISPLAY_KHR:
            return "VK_ERROR_INCOMPATIBLE_DISPLAY_KHR";
        case VK_ERROR_INVALID_SHADER_NV:
            return "VK_ERROR_INVALID_SHADER_NV";
        case VK_ERROR_INVALID_DRM_FORMAT_MODIFIER_PLANE_LAYOUT_EXT:
            return "VK_ERROR_INVALID_DRM_FORMAT_MODIFIER_PLANE_LAYOUT_EXT";
        case VK_ERROR_FULL_SCREEN_EXCLUSIVE_MODE_LOST_EXT:
            return "VK_ERROR_FULL_SCREEN_EXCLUSIVE_MODE_LOST_EXT";
        case VK_THREAD_IDLE_KHR:
            return "VK_THREAD_IDLE_KHR";
        case VK_THREAD_DONE_KHR:
            return "VK_THREAD_DONE_KHR";
        case VK_OPERATION_DEFERRED_KHR:
            return "VK_OPERATION_DEFERRED_KHR";
        case VK_OPERATION_NOT_DEFERRED_KHR:
            return "VK_OPERATION_NOT_DEFERRED_KHR";
        default:
            return "<Unknown VkResult>";
    }}
}}
"""
    return content.format()

def CreateLoadBuffer(ctx: VkForgeContext):
    content = """\
void VkForge_LoadBuffer
(
    VkPhysicalDevice physical_device,
    VkDevice         device,
    VkQueue          queue,
    VkCommandBuffer  cmdBuffer,
    VkBuffer         dstBuffer,
    VkDeviceSize     dstOffset,
    VkDeviceSize     size,
    const void*      srcData
)
{{
    VkForgeBufferAlloc staging = VkForge_CreateStagingBuffer(physical_device, device, size);

    void* data;
    vkMapMemory(device, staging.memory, 0, size, 0, &data);
    SDL_memcpy(data, srcData, (size_t)size);
    vkUnmapMemory(device, staging.memory);

    VkForge_BeginCommandBuffer(cmdBuffer);

    VkForge_CmdCopyBuffer(cmdBuffer, staging.buffer, dstBuffer, 0, 0, size);

    VkForge_EndCommandBuffer(cmdBuffer);

    VkFence fence = VkForge_CreateFence(device);

    VkForge_QueueSubmit(queue, cmdBuffer, 0, 0, 0, fence);

    VkResult result = vkWaitForFences(device, 1, &fence, VK_TRUE, UINT64_MAX);

    if( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to wait for Fence: %s", VkForge_StringifyResult(result));
        exit(1);
    }}

    vkDestroyFence(device, fence, 0);
    VkForge_DestroyBufferAlloc(device, staging);
}}
"""
    return content.format()

def CreateCmdCopyBuffer(ctx: VkForgeContext):
    content = """\
void VkForge_CmdCopyBuffer
(
    VkCommandBuffer cmdBuf,
    VkBuffer        srcBuffer,
    VkBuffer        dstBuffer,
    VkDeviceSize    srcOffset,
    VkDeviceSize    dstOffset,
    VkDeviceSize    size
)
{{
    VkBufferCopy region = {{0}};
    region.srcOffset = srcOffset;
    region.dstOffset = dstOffset;
    region.size = size;

    vkCmdCopyBuffer(
        cmdBuf,
        srcBuffer,
        dstBuffer,
        1,
        &region
    );
}}
"""
    return content.format()

def CreateAllocateCommandBuffer(ctx: VkForgeContext):
    content = """\
VkCommandBuffer VkForge_AllocateCommandBuffer
(
    VkDevice      device,
    VkCommandPool pool
)
{{
    VkCommandBufferAllocateInfo allocInfo = {{0}};
    allocInfo.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;
    allocInfo.commandPool = pool;
    allocInfo.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
    allocInfo.commandBufferCount = 1;

    VkCommandBuffer cmdBuffer = VK_NULL_HANDLE;
    VkResult result = vkAllocateCommandBuffers(device, &allocInfo, &cmdBuffer);
    if ( VK_SUCCESS != result )
    {{
        SDL_LogError(0, "Failed to allocate command buffer: %s", VkForge_StringifyResult(result));
        exit(1);
    }}

    return cmdBuffer;
}}
"""
    return content.format()

def CreateCreateDescriptorPool(ctx: VkForgeContext):
    content = """\
VkDescriptorPool VkForge_CreateDescriptorPool(
    VkDevice device,
    uint32_t max_sets,
    uint32_t pool_sizes_count,
    VkDescriptorPoolSize* pool_sizes
)
{{
    VkDescriptorPoolCreateInfo poolInfo = {{0}};
    poolInfo.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO;
    poolInfo.maxSets = max_sets;
    poolInfo.poolSizeCount = pool_sizes_count;
    poolInfo.pPoolSizes = pool_sizes;

    VkDescriptorPool pool = VK_NULL_HANDLE;

    VkResult result = vkCreateDescriptorPool(device, &poolInfo, 0, &pool);

    if(VK_SUCCESS != result)
    {{
        SDL_LogError(0, "Failed to Create Descriptor Pool: %s", VkForge_StringifyResult(result));
        exit(1);
    }}

    return pool;
}}
"""
    return content.format()

def CreateAllocateDescriptorSet(ctx: VkForgeContext):
    content = """\
/// @brief
/// @param device
/// @param pool
/// @param descriptorset_count
/// @param descriptorset_layouts
/// @param outDescriptorSets must be large enough to accomodate atleast descriptorset_count
void VkForge_AllocateDescriptorSet(
    VkDevice device,
    VkDescriptorPool pool,
    uint32_t descriptorset_count,
    VkDescriptorSetLayout* descriptorset_layouts,
    VkDescriptorSet* outDescriptorSets
)
{{
    VkDescriptorSetAllocateInfo allocInfo = {{ 0 }};
    allocInfo.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO;
    allocInfo.descriptorPool = pool;
    allocInfo.descriptorSetCount = descriptorset_count;
    allocInfo.pSetLayouts = descriptorset_layouts;

    vkAllocateDescriptorSets(device, &allocInfo, outDescriptorSets);
}}
"""
    return content.format()

def CreateGetPixelFormatFromString(ctx: VkForgeContext):
    content = """\
VkForgePixelFormatPair VkForge_GetPixelFormatFromString(const char* order)
{{
    // Default: ABGR (matches VK_FORMAT_R8G8B8A8_UNORM)
    VkForgePixelFormatPair fmt = {{ SDL_PIXELFORMAT_ABGR8888, VK_FORMAT_R8G8B8A8_UNORM }};

    if (!order) return fmt;

    if      (SDL_strcasecmp(order, "RGBA") == 0) fmt = (VkForgePixelFormatPair){{ SDL_PIXELFORMAT_RGBA8888, VK_FORMAT_R8G8B8A8_UNORM }};
    else if (SDL_strcasecmp(order, "BGRA") == 0) fmt = (VkForgePixelFormatPair){{ SDL_PIXELFORMAT_BGRA8888, VK_FORMAT_B8G8R8A8_UNORM }};
    else if (SDL_strcasecmp(order, "ARGB") == 0) fmt = (VkForgePixelFormatPair){{ SDL_PIXELFORMAT_ARGB8888, VK_FORMAT_A8B8G8R8_UNORM_PACK32 }};
    else if (SDL_strcasecmp(order, "ABGR") == 0) fmt = (VkForgePixelFormatPair){{ SDL_PIXELFORMAT_ABGR8888, VK_FORMAT_A8B8G8R8_UNORM_PACK32 }};

    // You can add more uncommon formats if you ever support them
    // e.g., XRGB, XBGR, RGBX, BGRX (Vulkan also has VK_FORMAT_B8G8R8A8_UNORM for BGRA)

    return fmt;
}}
"""
    return content.format()

def CreatesIsDescriptorTypeImage(ctx: VkForgeContext):
    content = """\
/**
 * @brief Checks if a descriptor type is for image resources
 * @param type The Vulkan descriptor type to check
 * @return True if the descriptor type is for images, false otherwise
 */
bool VkForge_IsDescriptorTypeImage(VkDescriptorType type)
{{
    return (type == VK_DESCRIPTOR_TYPE_SAMPLER ||
            type == VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER ||
            type == VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE ||
            type == VK_DESCRIPTOR_TYPE_STORAGE_IMAGE ||
            type == VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT);
}}
"""
    return content.format()

def CreatesIsDescriptorTypeBuffer(ctx: VkForgeContext):
    content = """\
/**
 * @brief Checks if a descriptor type is for buffer resources
 * @param type The Vulkan descriptor type to check
 * @return True if the descriptor type is for buffers, false otherwise
 */
bool VkForge_IsDescriptorTypeBuffer(VkDescriptorType type)
{{
    return (type == VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER ||
            type == VK_DESCRIPTOR_TYPE_STORAGE_BUFFER ||
            type == VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC ||
            type == VK_DESCRIPTOR_TYPE_STORAGE_BUFFER_DYNAMIC);
}}
"""
    return content.format()

def CreateStringifyDescriptorType(ctx: VkForgeContext):
    content = """\
const char* VkForge_StringifyDescriptorType(VkDescriptorType descriptortype)
{{
    switch (descriptortype)
    {{
        case VK_DESCRIPTOR_TYPE_SAMPLER:
            return "VK_DESCRIPTOR_TYPE_SAMPLER";
        case VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER:
            return "VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER";
        case VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE:
            return "VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE";
        case VK_DESCRIPTOR_TYPE_STORAGE_IMAGE:
            return "VK_DESCRIPTOR_TYPE_STORAGE_IMAGE";
        case VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER:
            return "VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER";
        case VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER:
            return "VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER";
        case VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER:
            return "VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER";
        case VK_DESCRIPTOR_TYPE_STORAGE_BUFFER:
            return "VK_DESCRIPTOR_TYPE_STORAGE_BUFFER";
        case VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC:
            return "VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC";
        case VK_DESCRIPTOR_TYPE_STORAGE_BUFFER_DYNAMIC:
            return "VK_DESCRIPTOR_TYPE_STORAGE_BUFFER_DYNAMIC";
        case VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT:
            return "VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT";
        case VK_DESCRIPTOR_TYPE_INLINE_UNIFORM_BLOCK:
            return "VK_DESCRIPTOR_TYPE_INLINE_UNIFORM_BLOCK";
        #ifdef VK_KHR_acceleration_structure
        case VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR:
            return "VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_KHR";
        #endif
        #ifdef VK_NV_ray_tracing
        case VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_NV:
            return "VK_DESCRIPTOR_TYPE_ACCELERATION_STRUCTURE_NV";
        #endif
        #ifdef VK_QCOM_image_processing
        case VK_DESCRIPTOR_TYPE_SAMPLE_WEIGHT_IMAGE_QCOM:
            return "VK_DESCRIPTOR_TYPE_SAMPLE_WEIGHT_IMAGE_QCOM";
        case VK_DESCRIPTOR_TYPE_BLOCK_MATCH_IMAGE_QCOM:
            return "VK_DESCRIPTOR_TYPE_BLOCK_MATCH_IMAGE_QCOM";
        #endif
        #ifdef VK_ARM_tensors
        case VK_DESCRIPTOR_TYPE_TENSOR_ARM:
            return "VK_DESCRIPTOR_TYPE_TENSOR_ARM";
        #endif
        #ifdef VK_EXT_mutable_descriptor_type
        case VK_DESCRIPTOR_TYPE_MUTABLE_EXT:
            return "VK_DESCRIPTOR_TYPE_MUTABLE_EXT";
        #endif
        #ifdef VK_NV_partitioned_acceleration_structure
        case VK_DESCRIPTOR_TYPE_PARTITIONED_ACCELERATION_STRUCTURE_NV:
            return "VK_DESCRIPTOR_TYPE_PARTITIONED_ACCELERATION_STRUCTURE_NV";
        #endif
        #ifdef VK_VALVE_mutable_descriptor_type
        case VK_DESCRIPTOR_TYPE_MUTABLE_VALVE:
            return "VK_DESCRIPTOR_TYPE_MUTABLE_VALVE";
        #endif
        default:
            return "VK_DESCRIPTOR_TYPE_UNKNOWN";
    }}
}}
"""
    return content.format()

def GetUtilStrings(ctx: VkForgeContext):
    return [
        CreateDebugMsgInfo(ctx),
        CreateDebugMsgCallback(ctx),
        CreateScorePhysicalDevice(ctx),
        CreateGetMemoryTypeIndex(ctx),
        CreateGetSwapchainSize(ctx),
        CreateGetSurfaceFormat(ctx),
        CreateGetSurfaceCapabilities(ctx),
        CreateGetPresentMode(ctx),        
        CreateCmdBufferBarrier(ctx),
        CreateCmdImageBarrier(ctx),        
        CreateFence(ctx),
        CreateSemaphore(ctx),       
        CreateBeginCommandBuffer(ctx),
        CreateEndCommandBuffer(ctx),
        CreateCopyBufferToImage(ctx),
        CreateQueueSubmit(ctx),
        CreateCreateBuffer(ctx),
        CreateCreateBufferAlloc(ctx),
        CreateCreateBufferOffset(ctx),
        CreateCreateImage(ctx),
        CreateCreateImageAlloc(ctx),
        CreateCreateImageOffset(ctx),
        CreateStagingBuffer(ctx),
        CreateImageView(ctx),
        CreateSampler(ctx),
        CreateCreateTexture(ctx),
        CreateDestroyTexture(ctx),
        CreateAllocDeviceMemory(ctx),
        CreateBindBufferMemory(ctx),
        CreateBindImageMemory(ctx),
        CreateDestroyBufferAlloc(ctx),
        CreateDestroyImageAlloc(ctx),
        CreateSetColor(ctx),
        CreateBeginRendering(ctx),
        CreateEndRendering(ctx),
        CreateQueuePresent(ctx),
        CreateReadFile(ctx),
        CreateCreateShaderModule(ctx),
        CreateStringifyResult(ctx),
        CreateLoadBuffer(ctx),
        CreateCmdCopyBuffer(ctx),
        CreateAllocateCommandBuffer(ctx),
        CreateCreateDescriptorPool(ctx),
        CreateAllocateDescriptorSet(ctx),
        CreateGetPixelFormatFromString(ctx),
        CreatesIsDescriptorTypeBuffer(ctx),
        CreatesIsDescriptorTypeImage(ctx),
        CreateStringifyDescriptorType(ctx)

    ]
