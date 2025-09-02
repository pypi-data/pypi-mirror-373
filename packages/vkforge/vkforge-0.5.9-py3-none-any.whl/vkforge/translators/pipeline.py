from vkforge.context import VkForgeContext
from vkforge.mappings import *
from vkforge.schema import VkPipelineModel
from .func import extract_function_declarations

def BuildShaderStage(
        ctx: VkForgeContext, 
        pipelineModule:VkPipelineModel, 
        pipelineName:str, 
        shaderIds:list,
        indent = 1
) -> str:
    stageInfo = ""
    indent2 = indent + 1
    indent3 = indent2 + 1

    for shaderId in shaderIds:
        shader = ctx.shaderData[SHADER.LIST][shaderId]
        stageInfo += "\t" * indent + f"VkShaderModule shader_{shader[SHADER.MODE]} = "
        stageInfo += f"VkForge_CreateShaderModule(device, \"{shader[SHADER.BINPATH].as_posix()}\");\n"
        stageInfo += "\t" * indent + f"if( VK_NULL_HANDLE == shader_{shader[SHADER.MODE]} )\n"
        stageInfo += "\t" * indent + "{\n"
        stageInfo += "\t" * indent2 + f'SDL_LogError(0, "Failed to create {shader[SHADER.MODE]} shader for {pipelineName} pipeline\\n");\n'
        stageInfo += "\t" * indent2 + "exit(1);\n"
        stageInfo += "\t" * indent + "}\n\n"

    stageInfo += "\t" * indent + "VkPipelineShaderStageCreateInfo stageInfo[] =\n"
    stageInfo += "\t" * indent + "{\n"

    for shaderId in shaderIds:
        stageInfo += "\t" * indent2 + "{\n"

        shader = ctx.shaderData[SHADER.LIST][shaderId]

        stageInfo += "\t" * indent3 + ".sType  = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,\n"
        stageInfo += "\t" * indent3 + ".stage  = " + f"{map_value(SHADER_STAGE_MAP, shader[SHADER.MODE])},\n"
        stageInfo += "\t" * indent3 + ".module = " + f"shader_{shader[SHADER.MODE]},\n"
        stageInfo += "\t" * indent3 + ".pName  = " + f"\"{shader[SHADER.ENTRYNAME]}\",\n"

        stageInfo += "\t" * indent2 + "},\n"

    stageInfo += "\t" * indent + "};\n"
    stageInfo += "\t" * indent + f"uint32_t stageInfoCount = {len(shaderIds)};\n"
    return stageInfo

def BuildInputBinding(
        ctx: VkForgeContext, 
        pipelineModule:VkPipelineModel, 
        pipelineName:str, 
        shaderIds:list,
        indent = 1
) -> str:
    binding = "\n"
    indent2 = indent + 1
    indent3 = indent2 + 1

    binding += "\t" * indent + "VkVertexInputBindingDescription bindingDesc[] =\n"
    binding += "\t" * indent + "{\n"

    for i, inputBinding in enumerate(pipelineModule.VertexInputBindingDescription):
        rate = map_value(INPUT_RATE_MAP, inputBinding.input_rate)
        if inputBinding.stride_kind == 'TYPE':
            stride = f"sizeof({inputBinding.stride})"
        else:
            stride = inputBinding.stride
        
        binding += "\t" * indent2 + "{\n"

        binding += "\t" * indent3 + f".binding = {i},\n"
        binding += "\t" * indent3 + f".stride = {stride},\n"
        binding += "\t" * indent3 + f".inputRate = {rate},\n"

        binding += "\t" * indent2 + "},\n"
    
    binding += "\t" * indent + "};\n"
    binding += "\t" * indent + f"uint32_t bindingDescCount = {len(pipelineModule.VertexInputBindingDescription)};\n"

    return binding

def GetInputAttributeList(
        ctx: VkForgeContext, 
        pipelineModule:VkPipelineModel, 
        pipelineName:str, 
        shaderIds:list,
) -> list:
    attribute_list = []
    binding_list = []
    
    for i, inputBinding in enumerate(pipelineModule.VertexInputBindingDescription):
        binding_list.append((i, inputBinding.first_location, inputBinding.input_rate, inputBinding.stride_kind))
    
    # Handle case where first_location 0 is not in the list
    if not any(b[1] == 0 for b in binding_list):
        binding_list.append((len(binding_list), 0, 'VK_VERTEX_INPUT_RATE_VERTEX', 'INT'))
    
    # Sort binding_list by binding first, first_location second
    binding_list.sort(key=lambda x: (x[0], x[1]))

    for shaderId in shaderIds:
        shader = ctx.shaderData[SHADER.LIST][shaderId]
        
        # input binding / attribute applies to only vertex shaders
        mode = shader[SHADER.MODE]
        if not mode == "vert":
            continue
        
        reflect = shader[SHADER.REFLECT]
        input_list = reflect.get(REFLECT.INPUT, {})
        for input_item in input_list:
            location = input_item["location"]
            type1 = input_item["type"]
            attribute = {
                ATTR.LOCATION: location,
                ATTR.FORMAT: map_dict(GLSL_TYPE_MAP, type1, "format"),
                ATTR.SIZE: map_dict(GLSL_TYPE_MAP, type1, "size")
            }
            attribute_list.append(attribute)
    
    def GetBindingInfo(binding_list, attribute):
        location = attribute[ATTR.LOCATION]
        # Find the binding with the largest first_location <= location
        candidates = [b for b in binding_list if b[1] <= location]
        if not candidates:
            return binding_list[0]  # default to first binding
        # Return the binding with largest first_location <= location
        return max(candidates, key=lambda x: x[1])
    
    for i in range(len(attribute_list)):
        bindingInfo = GetBindingInfo(binding_list, attribute_list[i])
        binding, _, _, _ = bindingInfo
        attribute_list[i][ATTR.BINDING] = binding

    # Sort attribute list by binding first and location second
    attribute_list.sort(key=lambda x: (x[ATTR.BINDING], x[ATTR.LOCATION]))

    def GetAttributeIndexList(attribute_list, binding):
        return [i for i, attr in enumerate(attribute_list) if attr[ATTR.BINDING] == binding]
    
    for binding, _, _, kind in binding_list:
        attribute_index_list = GetAttributeIndexList(attribute_list, binding)
        if kind == 'TYPE' and pipelineModule.VertexInputBindingDescription[binding].stride_members:
            members = pipelineModule.VertexInputBindingDescription[binding].stride_members
            type1 = pipelineModule.VertexInputBindingDescription[binding].stride
            for i, index in enumerate(attribute_index_list):
                if i < len(members):
                    attribute_list[index][ATTR.OFFSET] = f"offsetof({type1}, {members[i]})"
        else:
            sizeoffset = "0"
            for index in attribute_index_list:
                attribute_list[index][ATTR.OFFSET] = sizeoffset
                sizeoffset += " + " + attribute_list[index][ATTR.SIZE]
    
    return attribute_list
                
def BuildInputAttribute(
        ctx: VkForgeContext, 
        pipelineModule:VkPipelineModel, 
        pipelineName:str, 
        shaderIds:list,
        indent = 1
) -> str:
    attribute = "\n"
    indent2 = indent + 1
    indent3 = indent2 + 1

    attribute += "\t" * indent + "VkVertexInputAttributeDescription attributeDesc[] =\n"
    attribute += "\t" * indent + "{\n"

    attribute_list = GetInputAttributeList(ctx, pipelineModule, pipelineName, shaderIds)

    if attribute_list:
        for attribute_item in attribute_list:
            attribute += "\t" * indent2 + "{\n"

            attribute += "\t" * indent3 + f".binding = {attribute_item[ATTR.BINDING]},\n"
            attribute += "\t" * indent3 + f".location = {attribute_item[ATTR.LOCATION]},\n"
            attribute += "\t" * indent3 + f".format = {attribute_item[ATTR.FORMAT]},\n"
            attribute += "\t" * indent3 + f".offset = {attribute_item[ATTR.OFFSET]},\n"

            attribute += "\t" * indent2 + "},\n"
    else:
        attribute += "\t" * indent2 + "0\n"

    attribute += "\t" * indent + "};\n"
    attribute += "\t" * indent + f"uint32_t attributeDescCount = {len(attribute_list)};\n"
    return attribute

def BuildInputState(
        ctx: VkForgeContext, 
        pipelineModule:VkPipelineModel, 
        pipelineName:str, 
        shaderIds:list,
        indent = 1
) -> str:
    state = "\n"
    indent2 = indent + 1
    indent3 = indent2 + 1

    state += "\t" * indent + "VkPipelineVertexInputStateCreateInfo inputStateInfo = {0};\n"
    state += "\t" * indent + "inputStateInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO;\n"
    state += "\t" * indent + "inputStateInfo.vertexBindingDescriptionCount = bindingDescCount;\n"
    state += "\t" * indent + "inputStateInfo.pVertexBindingDescriptions = bindingDescCount ? bindingDesc : 0;\n"
    state += "\t" * indent + "inputStateInfo.vertexAttributeDescriptionCount = attributeDescCount;\n"
    state += "\t" * indent + "inputStateInfo.pVertexAttributeDescriptions = attributeDescCount ? attributeDesc : 0;\n"

    return state

def BuildInputAssembly(
        ctx: VkForgeContext, 
        pipelineModule:VkPipelineModel, 
        pipelineName:str, 
        shaderIds:list,
        indent = 1
) -> str:
    assembly = "\n"
    indent2 = indent + 1
    indent3 = indent2 + 1

    topology = pipelineModule.InputAssemblyStateCreateInfo.topology

    assembly += "\t" * indent + "VkPipelineInputAssemblyStateCreateInfo inputAssemblyInfo = {0};\n"
    assembly += "\t" * indent + "inputAssemblyInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO;\n"
    assembly += "\t" * indent + f"inputAssemblyInfo.topology = {topology};\n"

    return assembly

def BuildDynamicState(
        ctx: VkForgeContext, 
        pipelineModule:VkPipelineModel, 
        pipelineName:str, 
        shaderIds:list,
        indent = 1
) -> str:
    states = "\n"
    info = "\n"
    indent2 = indent + 1

    states += "\t" * indent + "VkDynamicState dynamicStates[] =\n"
    states += "\t" * indent + "{\n"
    for dynamicState in pipelineModule.DynamicState:
        states += "\t" * indent2 + f"{map_value(DYNAMIC_STATE_MAP, dynamicState)},\n"
    states += "\t" * indent + "};\n"

    info = states + info
    info += "\t" * indent + "VkPipelineDynamicStateCreateInfo dynamicInfo = {0};\n"
    info += "\t" * indent + "dynamicInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_DYNAMIC_STATE_CREATE_INFO;\n"
    info += "\t" * indent + "dynamicInfo.dynamicStateCount = sizeof(dynamicStates) / sizeof(VkDynamicState);\n"
    info += "\t" * indent + "dynamicInfo.pDynamicStates = dynamicStates;\n"

    return info

def BuildViewportState(
        ctx: VkForgeContext, 
        pipelineModule: VkPipelineModel, 
        pipelineName: str, 
        shaderIds: list,
        indent: int = 1
) -> str:
    state = "\n"
    indent2 = indent + 1
    
    state += "\t" * indent + "VkPipelineViewportStateCreateInfo viewportState = {0};\n"
    state += "\t" * indent + "viewportState.sType = VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO;\n"
    state += "\t" * indent + "viewportState.viewportCount = 1;\n"
    state += "\t" * indent + "viewportState.scissorCount = 1;\n"
    
    return state

def BuildMultisampleState(
        ctx: VkForgeContext, 
        pipelineModule: VkPipelineModel, 
        pipelineName: str, 
        shaderIds: list,
        indent: int = 1
) -> str:
    state = "\n"
    indent2 = indent + 1
    
    state += "\t" * indent + "VkPipelineMultisampleStateCreateInfo multisampleState = {0};\n"
    state += "\t" * indent + "multisampleState.sType = VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO;\n"
    state += "\t" * indent + "multisampleState.rasterizationSamples = VK_SAMPLE_COUNT_1_BIT;\n"
    
    return state

def BuildRasterizationState(
        ctx: VkForgeContext, 
        pipelineModule: VkPipelineModel, 
        pipelineName: str, 
        shaderIds: list,
        indent: int = 1
) -> str:
    state = "\n"
    indent2 = indent + 1
    
    raster = pipelineModule.RasterizationStateCreateInfo
    
    state += "\t" * indent + "VkPipelineRasterizationStateCreateInfo rasterizerInfo = {0};\n"
    state += "\t" * indent + "rasterizerInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO;\n"
    state += "\t" * indent + f"rasterizerInfo.depthClampEnable = {map_bool(raster.depthClampEnable)};\n"
    state += "\t" * indent + f"rasterizerInfo.rasterizerDiscardEnable = {map_bool(raster.rasterizerDiscardEnable)};\n"
    state += "\t" * indent + f"rasterizerInfo.polygonMode = {raster.polygonMode};\n"
    state += "\t" * indent + f"rasterizerInfo.cullMode = {raster.cullMode};\n"
    state += "\t" * indent + f"rasterizerInfo.frontFace = {raster.frontFace};\n"
    state += "\t" * indent + f"rasterizerInfo.depthBiasEnable = {map_bool(raster.depthBiasEnable)};\n"
    state += "\t" * indent + f"rasterizerInfo.depthBiasConstantFactor = {raster.depthBiasConstantFactor};\n"
    state += "\t" * indent + f"rasterizerInfo.depthBiasClamp = {raster.depthBiasClamp};\n"
    state += "\t" * indent + f"rasterizerInfo.depthBiasSlopeFactor = {raster.depthBiasSlopeFactor};\n"
    state += "\t" * indent + f"rasterizerInfo.lineWidth = {raster.lineWidth};\n"
    
    return state

def BuildColorBlendAttachment(
        ctx: VkForgeContext, 
        pipelineModule: VkPipelineModel, 
        pipelineName: str, 
        shaderIds: list,
        indent: int = 1
) -> str:
    state = "\n"
    indent2 = indent + 1
    
    blend = pipelineModule.ColorBlendAttachmentState
    
    state += "\t" * indent + "VkPipelineColorBlendAttachmentState colorBlendAttachment = {0};\n"
    state += "\t" * indent + f"colorBlendAttachment.blendEnable = {map_bool(blend.blendEnable)};\n"
    state += "\t" * indent + f"colorBlendAttachment.srcColorBlendFactor = {blend.srcColorBlendFactor};\n"
    state += "\t" * indent + f"colorBlendAttachment.dstColorBlendFactor = {blend.dstColorBlendFactor};\n"
    state += "\t" * indent + f"colorBlendAttachment.colorBlendOp = {blend.colorBlendOp};\n"
    state += "\t" * indent + f"colorBlendAttachment.colorWriteMask = {blend.colorWriteMask};\n"
    
    return state

def BuildColorBlendState(
        ctx: VkForgeContext, 
        pipelineModule: VkPipelineModel, 
        pipelineName: str, 
        shaderIds: list,
        indent: int = 1
) -> str:
    state = "\n"
    indent2 = indent + 1
    
    blend = pipelineModule.ColorBlendStateCreateInfo
    
    state += "\t" * indent + "VkPipelineColorBlendStateCreateInfo colorBlending = {0};\n"
    state += "\t" * indent + "colorBlending.sType = VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO;\n"
    state += "\t" * indent + f"colorBlending.logicOpEnable = {map_bool(blend.logicOpEnable)};\n"
    state += "\t" * indent + "colorBlending.attachmentCount = 1;\n"
    state += "\t" * indent + "colorBlending.pAttachments = &colorBlendAttachment;\n"
    
    return state

def BuildDepthStencilState(
        ctx: VkForgeContext, 
        pipelineModule: VkPipelineModel, 
        pipelineName: str, 
        shaderIds: list,
        indent: int = 1
) -> str:
    state = "\n"
    indent2 = indent + 1
    
    depth = pipelineModule.DepthStencilStateCreateInfo
    
    state += "\t" * indent + "VkPipelineDepthStencilStateCreateInfo depthStencil = {0};\n"
    state += "\t" * indent + "depthStencil.sType = VK_STRUCTURE_TYPE_PIPELINE_DEPTH_STENCIL_STATE_CREATE_INFO;\n"
    state += "\t" * indent + f"depthStencil.depthTestEnable = {map_bool(depth.depthTestEnable)};\n"
    state += "\t" * indent + f"depthStencil.depthWriteEnable = {map_bool(depth.depthWriteEnable)};\n"
    state += "\t" * indent + f"depthStencil.depthCompareOp = {depth.depthCompareOp};\n"
    state += "\t" * indent + f"depthStencil.depthBoundsTestEnable = {map_bool(depth.depthBoundsTestEnable)};\n"
    state += "\t" * indent + f"depthStencil.stencilTestEnable = {map_bool(depth.stencilTestEnable)};\n"
    
    return state

def BuildPipelineInfo(
        ctx: VkForgeContext, 
        pipelineModule: VkPipelineModel, 
        pipelineName: str, 
        shaderIds: list,
        indent: int = 1
) -> str:
    info = "\n"
    indent2 = indent + 1
    
    info += "\t" * indent + "VkGraphicsPipelineCreateInfo pipelineInfo = {0};\n"
    info += "\t" * indent + "pipelineInfo.sType = VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO;\n"
    info += "\t" * indent + "pipelineInfo.stageCount = sizeof(stageInfo)/sizeof(VkPipelineShaderStageCreateInfo);\n"
    info += "\t" * indent + "pipelineInfo.pStages = stageInfo;\n"
    info += "\t" * indent + "pipelineInfo.pVertexInputState = &inputStateInfo;\n"
    info += "\t" * indent + "pipelineInfo.pInputAssemblyState = &inputAssemblyInfo;\n"
    info += "\t" * indent + "pipelineInfo.pRasterizationState = &rasterizerInfo;\n"
    info += "\t" * indent + "pipelineInfo.pColorBlendState = &colorBlending;\n"
    info += "\t" * indent + "pipelineInfo.pDepthStencilState = &depthStencil;\n"
    info += "\t" * indent + "pipelineInfo.pDynamicState = &dynamicInfo;\n"
    info += "\t" * indent + "pipelineInfo.pViewportState = &viewportState;\n"
    info += "\t" * indent + "pipelineInfo.pMultisampleState = &multisampleState;\n"
    info += "\t" * indent + "pipelineInfo.layout = pipeline_layout;\n"
    info += "\n"
    info += "\t" * indent + "/// Ensure VkRenderingInfo is passed to pNext for Successful Dynamic Rendering ///\n"
    info += "\t" * indent + "pipelineInfo.pNext = next;\n"
    info += "\t" * indent + "///********************///\n"
    
    return info

def BuildPipeline(ctx: VkForgeContext, pipelineModule: VkPipelineModel) -> str:
    pipelineName = pipelineModule.name
    shaderIds = ctx.shaderData[SHADER.COMBO][pipelineName]

    indent = 1
    indent2 = indent + 1

    pipeline = "\n"
    pipeline += "\t" * indent + "VkResult result;\n"
    pipeline += "\t" * indent + "VkPipeline pipeline = VK_NULL_HANDLE;\n"
    pipeline += "\n"
    
    # Build all pipeline states
    pipeline += BuildShaderStage(ctx, pipelineModule, pipelineName, shaderIds)
    pipeline += BuildInputBinding(ctx, pipelineModule, pipelineName, shaderIds)
    pipeline += BuildInputAttribute(ctx, pipelineModule, pipelineName, shaderIds)
    pipeline += BuildInputState(ctx, pipelineModule, pipelineName, shaderIds)
    pipeline += BuildInputAssembly(ctx, pipelineModule, pipelineName, shaderIds)
    pipeline += BuildViewportState(ctx, pipelineModule, pipelineName, shaderIds)
    pipeline += BuildRasterizationState(ctx, pipelineModule, pipelineName, shaderIds)
    pipeline += BuildMultisampleState(ctx, pipelineModule, pipelineName, shaderIds)
    pipeline += BuildDepthStencilState(ctx, pipelineModule, pipelineName, shaderIds)
    pipeline += BuildColorBlendAttachment(ctx, pipelineModule, pipelineName, shaderIds)
    pipeline += BuildColorBlendState(ctx, pipelineModule, pipelineName, shaderIds)
    pipeline += BuildDynamicState(ctx, pipelineModule, pipelineName, shaderIds)
    pipeline += BuildPipelineInfo(ctx, pipelineModule, pipelineName, shaderIds)
    
    # Pipeline creation call
    pipeline += "\t" * indent + f"result = vkCreateGraphicsPipelines(device, VK_NULL_HANDLE, 1, &pipelineInfo, allocator, &pipeline);\n"
    pipeline += "\t" * indent + "if (result != VK_SUCCESS) {\n"
    pipeline += "\t" * indent2 + "SDL_LogError(0, \"Failed to create pipeline %s\");\n" % pipelineName
    pipeline += "\t" * indent2 + "return VK_NULL_HANDLE;\n"
    pipeline += "\t" * indent + "}\n\n"
    
    # Cleanup shader modules
    for shaderId in shaderIds:
        shader = ctx.shaderData[SHADER.LIST][shaderId]
        shader_mode = shader[SHADER.MODE]
        pipeline += "\t" * indent + f"vkDestroyShaderModule(device, shader_{shader_mode}, allocator);\n"
    pipeline += "\n"
    
    pipeline += "\t" * indent + "return pipeline;\n"
    
    # Wrap in function
    function_body = pipeline
    function_def = f"""\
VkPipeline VkForge_CreatePipelineFor{pipelineName}
(
    VkAllocationCallbacks* allocator,
    void* next,
    VkDevice device,
    VkPipelineLayout pipeline_layout
)\n{{\n{function_body}}}\n
"""
    
    return function_def

def CreatePipelines(ctx: VkForgeContext):
    pipelines = ""
    for pipelineModule in ctx.forgeModel.Pipeline:
        pipelines += BuildPipeline(ctx, pipelineModule)
    
    return pipelines

def CreatePipelineDeclarations(ctx: VkForgeContext) -> str:
    """Generate ONLY function forward declarations using robust regex parsing."""
    declarations = "// Function Declarations\n\n"
    
    # Collect all content from all modules
    all_content = []
    all_content.extend([CreatePipelines(ctx)])
    
    # Process each content block
    for content in all_content:
        for decl in extract_function_declarations(content):
            declarations += decl + "\n\n"
    
    return declarations

def GetPipelineStrings(ctx: VkForgeContext):
    return [
        CreatePipelines(ctx),
    ]

def GetPipelineDeclarationStrings(ctx: VkForgeContext):
    return [
        CreatePipelineDeclarations(ctx)
    ]