from .schema import VkForgeModel
from .mappings import *
from typing import List, Tuple, Dict
import hashlib

def hash_tuple(t: tuple) -> str:
    b = repr(t).encode('utf-8')
    h = hashlib.md5(b).hexdigest() #FIXME: use longer code such as sha256
    return h

def print_unsupported_warning(id: str, reflect: dict):
    unsupported = [REFLECT.SUBPASS]
    for r in reflect.keys():
        if r in unsupported:
            print(f"WARNING: VkForge does not support {r} in shader {id}.")

def raise_unrecognized_error(id: str, reflect: dict):
    recognized = [
        REFLECT.IMAGE, 
        REFLECT.UBO, 
        REFLECT.SSBO, 
        REFLECT.TEXTURE, 
        REFLECT.SAMPLER_IMAGE, 
        REFLECT.SAMPLER,
        REFLECT.SUBPASS,
        REFLECT.ENTRYPOINT,
        REFLECT.INPUT,
        REFLECT.OUTPUT,
        REFLECT.TYPE,
    ]

    unrecognized = []
    for r in reflect.keys():
        if not r in recognized:
            unrecognized.append(r)
    if len(unrecognized) > 0:
        raise ValueError(
            f"ERROR: VkForge does not recognize the {unrecognized} in your shader {id}"
        )


def get_reflect_member_size(member: dict) -> int:
    if MEMBER.ARRAY_LITERAL in member and MEMBER.ARRAY in member:
        if member[MEMBER.ARRAY_LITERAL] == [True]:
            return sum(member[MEMBER.ARRAY])
    return 1


def create_descriptorsets(shader: dict):
    dset_types = [
        REFLECT.IMAGE, 
        REFLECT.UBO, 
        REFLECT.SSBO, 
        REFLECT.TEXTURE, 
        REFLECT.SAMPLER_IMAGE, 
        REFLECT.SAMPLER
    ]

    reflect = shader[SHADER.REFLECT]
    mode    = shader[SHADER.MODE]

    dsets = []

    for dset_type in dset_types:
        if dset_type in reflect.keys():
            members = reflect[dset_type]
            for member in members:
                type = member[MEMBER.TYPE]
                if REFLECT.TYPE in reflect and type in reflect[REFLECT.TYPE]:
                    type = dset_type
                set1 = member[MEMBER.SET]
                binding = member[MEMBER.BIND]
                count = get_reflect_member_size(member)
                dsets.append((mode, set1, binding, type, count))

    return dsets


def check_for_errors_single_descriptorsets(id: str, dsets: List[Tuple]):
    for i, dset1 in enumerate(dsets[:-1]):
        mode1, set1, binding1, type1, count1 = dset1
        for dset2 in dsets[i + 1:]:
            mode2, set2, binding2, type2, count2 = dset2
            if set1 == set2 and binding1 == binding2 and mode1 == mode2:
                raise ValueError(
                    f"set {set1}, binding {binding1}, mode {mode1} overlapped for shader {id}"
                )


def check_for_errors_group_descriptorsets(shader_groups: Dict, shader_dsets: Dict,):
    for pipeline_name, shader_ids in shader_groups.items():
        dsets = []
        dsets_shaderids = []
        for shader_id in shader_ids:
            if shader_id in shader_dsets:
                for shader_dset in shader_dsets[shader_id]:
                    dsets.append(shader_dset)
                    dsets_shaderids.append(shader_id)
    
    for i, dset1 in enumerate(dsets[:-1]):
        for j, dset2 in enumerate(dsets[i+1:], start=i+1):
            mode1, set1, binding1, type1, count1 = dset1
            mode2, set2, binding2, type2, count2 = dset2
            shader_names = ', '.join([dsets_shaderids[i], dsets_shaderids[j]])

            if set1 == set2 and binding1 == binding2 and mode1 == mode2:
                raise ValueError(
                    f"Shaders {shader_names} are grouped together in pipeline {pipeline_name} "
                    f"but the mode {mode1} is duplicated. There must be 1 unique mode per shader"
                )
            if set1 == set2 and binding1 == binding2 and type1 != type2:
                raise ValueError(
                    f"Shaders {shader_names} are grouped together in pipeline {pipeline_name} "
                    f"but set {set1} and binding {binding1} have different types "
                    f"{type1}, {type2} across the shaders. If shaders share the same "
                    f"set and binding then the type and count must match."
                )
            if set1 == set2 and binding1 == binding2 and count1 != count2:
                raise ValueError(
                    f"Shaders {shader_names} are grouped together in pipeline {pipeline_name} "
                    f"but set {set1} and binding {binding1} have different types "
                    f"{count1}, {count2} across the shaders. If shaders share the same "
                    f"set and binding then the type and count must match."
                )

def create_descriptorset_layouts(dsets_list: List[List[Tuple]]):
    dset_layout_dict = {}
    dset_layout_seen = set()

    for dset in dsets_list:
        mode1, set1, binding1, type1, count1 = dset
        key = (set1, binding1, type1, count1)
        if not key in dset_layout_seen:
            dset_layout_seen.add(key)
            dset_layout_dict[key] = {
                LAYOUT.SET: set1,
                LAYOUT.BIND: binding1,
                LAYOUT.TYPE: type1,
                LAYOUT.COUNT: count1,
                LAYOUT.STAGES: {mode1}
            }
        else:
            stages = dset_layout_dict[key][LAYOUT.STAGES]
            stages.add(mode1)
    return dset_layout_dict
    
def create_pipeline_descriptorset_layouts(shader_groups: Dict, shader_dsets: Dict,):
    pipelines_dset_layouts = {}
    for pipeline_name, shader_ids in shader_groups.items():
        dsets_list = []
        for shader_id in shader_ids:
            dsets_list.extend(shader_dsets[shader_id])
        dset_layouts = create_descriptorset_layouts(dsets_list)
        pipelines_dset_layouts[pipeline_name] = dset_layouts
    return pipelines_dset_layouts

def optimize_pipeline_layouts(fm: VkForgeModel, data: dict) -> dict:
    def fill_bind_slots(bind:int, type:str, count:int, stages:set, bind_slots:List[tuple]):
        if bind < len(bind_slots):
            if bind_slots[bind]:
                slot_type, slot_count, slot_stages = bind_slots[bind]
                if type == slot_type and count == slot_count:
                    if not stages in slot_stages:
                        stages.union(slot_stages)
                    bind_slots[bind] = (type, count, stages)
                    return True
                else:
                    return False
            else:
                bind_slots[bind] = (type, count, stages)
                return True
        else:
            bind_slots.extend([None] * (bind + 1))
            bind_slots[bind] = (type, count, stages)
            return True
    
    def fill_set_slots(set1: int, bind:int, type:str, count:int, stages:set, set_slots:List[list]):
        if set1 < len(set_slots):
            if not set_slots[set1]:
                set_slots[set1] = []
            return fill_bind_slots(bind, type, count, stages, set_slots[set1])
        else:
            set_slots.extend([None] * (set1 - len(set_slots) + 1))
            set_slots[set1] = []
            return fill_bind_slots(bind, type, count, stages, set_slots[set1])
        
    dset_dict = data[LAYOUT.DSET_LAYOUT]
    reference_dict = data[LAYOUT.DSET_REF]

    layouts = [] # Each item is a Pipeline Layout
    references = {} # Reference for the Optimized Layout

    current = [] # Current Pipeline Layout being build. Each Item is a DescriptorSet
    previous = []

    pipeline_index = 0
    pipeline_keys = reference_dict.keys()
    pipeline_names = list(pipeline_keys)

    while(pipeline_index < len(pipeline_keys)):
        pipeline_name = pipeline_names[pipeline_index]
        hash_list = reference_dict[pipeline_name]

        previous = current.copy()
        incompletePipeline = False

        for hash in hash_list:
            dset_data = dset_dict[hash]
            set1 = dset_data[LAYOUT.SET]
            bind = dset_data[LAYOUT.BIND]
            type = dset_data[LAYOUT.TYPE]
            count = dset_data[LAYOUT.COUNT]
            stages = dset_data[LAYOUT.STAGES]

            if fill_set_slots(set1, bind, type, count, stages, current):
                continue
            else:
                incompletePipeline = True
                break

        if incompletePipeline == True:
            if previous:
                layouts.append(previous)
                current = []
                continue
            else:
                break # now descriptor layout exists
        else:
            references[pipeline_name] = len(layouts)
        pipeline_index += 1
    
    if current:
        layouts.append(current)
    
    # This code does not generate empty pipeline layout
    # It must be manually added if needed

    # Scenario 1: All Pipelines require empty pipeline layout
    # no layout mean no shader had descriptorset
    # therefore create blank pipline layout and assign all pipeline to it
    if not layouts: 
        pipeline_layout = None # no list of descriptorset layouts
        layouts.append(pipeline_layout)
        for pipeline in fm.Pipeline:
            references[pipeline.name] = 0 # only one pipeline layout
    
    # Scenario 2: Some Pipelines require empty pipeline layout
    # Ensure all pipelines were assigned a layout
    not_assigned = []
    for pipeline in fm.Pipeline:
        if not pipeline.name in references:
            not_assigned.append(pipeline)
    if not_assigned:
        pipeline_layout = None # empty pipeline layout
        layouts.append(pipeline_layout)
        for pipeline in not_assigned:
            references[pipeline.name] = len(layouts) - 1 # last added pipeline layout

    return {
        LAYOUT.LAYOUTS:    layouts,
        LAYOUT.REFERENCES: references
    }


def combine_pipeline_descriptorset_layouts(fm: VkForgeModel, pipeline_dset_layouts_dict: Dict[str, List]):
    layouts = {}
    references = {}

    for pipeline_name, dset_layouts_dict in pipeline_dset_layouts_dict.items():
        for dset_key, dset_layout in dset_layouts_dict.items():
            key = hash_tuple(dset_key)
            if not key in layouts:
                layouts[key] = dset_layout
            else:
                layouts[key][LAYOUT.STAGES].union(dset_layout[LAYOUT.STAGES])
            if not pipeline_name in references:
                references[pipeline_name] = set()
            references[pipeline_name].add(key)
    for key in references: # optimizing logic depends on this being consitently ordered
        references[key] = sorted(list(references[key]))

    pipeline_descriptorset_layouts =  {
        LAYOUT.DSET_LAYOUT: layouts,
        LAYOUT.DSET_REF: references
    }
    pipeline_layouts = optimize_pipeline_layouts(fm, pipeline_descriptorset_layouts)

    return {
        LAYOUT.RAW_LAYOUT: pipeline_descriptorset_layouts,
        LAYOUT.PIPELINE_LAYOUT: pipeline_layouts
    }

def create_pipeline_layouts(fm: VkForgeModel, shaders: dict):
    shader_dsets = {}

    for shader_id, shader_data in shaders[SHADER.LIST].items():
        reflect = shader_data[SHADER.REFLECT]

        print_unsupported_warning(shader_id, reflect)
        raise_unrecognized_error(shader_id, reflect)

        dsets = create_descriptorsets(shader_data)
        check_for_errors_single_descriptorsets(shader_id, dsets)

        shader_dsets[shader_id] = dsets
    check_for_errors_group_descriptorsets(shaders[SHADER.COMBO], shader_dsets)

    pipeline_dset_layouts_dict = create_pipeline_descriptorset_layouts(shaders[SHADER.COMBO], shader_dsets)
    return combine_pipeline_descriptorset_layouts(fm, pipeline_dset_layouts_dict)
