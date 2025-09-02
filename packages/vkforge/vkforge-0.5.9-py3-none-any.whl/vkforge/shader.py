from typing import List, Tuple, Dict
from pathlib import Path
import os
import subprocess
import json
import subprocess
from .schema import VkForgeModel
from .mappings import *
import shutil

def find_shader(roots: List[str], id: str) -> Path:
    file_path = Path(id)
    if os.path.exists(file_path):
        return file_path

    for root in roots:
        joined = os.path.join(root, id)
        file_path = Path(joined)
        if os.path.exists(file_path):
            return file_path
    raise FileNotFoundError(f"Unable to find {id} shader")


def shader_is_source(extension: str) -> bool:
    extension_list = [".glsl"]
    extension_list.extend(["." + mode for mode in SHADER_STAGE_MAP.keys()])
    return extension in extension_list

def shader_is_binary(extension: str) -> bool:
    return extension == None or extension in [".spv"]

def disassemble_shader(build_dir: str, shader_path: Path, mode: str) -> Path:
    output_path = (
        Path(build_dir) / f"{shader_path.stem}.disassembled.{mode}.glsl"
    )

    Path(build_dir).mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            ["spirv-cross", "-h"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "spirv-cross not found! Please ensure 'VulkanSDK\\[Version]\\Bin' is added to your system's PATH."
        )
    except subprocess.CalledProcessError:
        pass

    result = subprocess.run(
        [
            "spirv-cross",
            str(shader_path),
            "--version",
            "450",
            "--output",
            str(output_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"spirv-cross failed for {shader_path}:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    return output_path

def copy_shader(source_dir: str, copy_dir: str, shader_path: Path, fm: VkForgeModel):
    if copy_dir:
        source_dir = Path(source_dir)
        source_from: Path = source_dir / (shader_path.name + ".spv")

        copy_to = Path(copy_dir) / (shader_path.name + ".spv")
        if source_from != copy_to: # if not already building to the location then copy
            copy_to.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_from, copy_to)
            print(f"COPIED: -> {copy_to}")

def compile_shader(build_dir: str, copy_dir: str, shader_path: Path, fm: VkForgeModel) -> Path:
    try:
        subprocess.run(
            ["glslangValidator", "-h"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "glslangValidator not found! Please ensure 'VulkanSDK\\[Version]\\Bin' is added to your system's PATH."
        )
    except subprocess.CalledProcessError:
        pass

    build_dir = Path(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    # Compose output path
    output_file: Path = build_dir / (shader_path.name + ".spv")

    if fm.CompileOnce:
        if shader_path.name in fm.CompileOnce and output_file.exists():
            print(f"SKIPPED (CompileOnce): {shader_path.name}")
            return output_file

    # Compile GLSL to SPIR-V
    result = subprocess.run(
        ["glslangValidator", "-V", str(shader_path), "-o", str(output_file)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Shader compilation failed for {shader_path}:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    
    print(f"COMPILED: {shader_path.name} -> {str(output_file)}")

    return output_file


def reflect_shader(shader_path: Path) -> dict:
    try:
        subprocess.run(
            ["spirv-cross", "-h"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "spirv-cross not found! Please ensure 'VulkanSDK\\[Version]\\Bin' is added to your system's PATH."
        )
    except subprocess.CalledProcessError:
        pass

    # Run reflection
    result = subprocess.run(
        ["spirv-cross", str(shader_path), "--reflect"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"spirv-cross reflection failed for {shader_path}:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    try:
        reflection_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"spirv-cross did not produce valid JSON:\n" f"Output:\n{result.stdout}"
        )

    return reflection_data


def get_shader_entrypoint(id: str, r: dict) -> Tuple[str, str]:
    entrypoints = r.get("entryPoints")
    if entrypoints:
        first_entrypoint = entrypoints[0]
        if not first_entrypoint:
            raise ValueError(f"Could not get entrypoint for shader {id}")
        
        name = first_entrypoint.get("name")
        if not name:
            raise ValueError(
                f"Can not confirm entrypoint name for shader {id}"
            )
        mode = first_entrypoint.get("mode")
        if not mode:
            raise ValueError(
                f"Can not confirm mode for shader {id} at entrypoint {name}"
            )
    return (name, mode)


def validate_shader_combination(build_dir: str, shader_list: List[dict]):
    try:
        subprocess.run(
            ["glslangValidator", "-h"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "glslangValidator not found! Please ensure 'VulkanSDK\\[Version]\\Bin' is added to your system's PATH."
        )
    except subprocess.CalledProcessError:
        pass

    shader_sources = [shader[SHADER.SRCPATH] for shader in shader_list]
    build_dir = Path(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    output_file = build_dir / "validation" / ("shader_validation" + ".mod")  

    result = subprocess.run(
        ["glslangValidator", "-l"] + shader_sources + ["-V", "-o", output_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Shader validation failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def load_shader_data(
    roots: List[str], build_dir: str, copy_dir: str|None, overwrite_dir:str|None, fm: VkForgeModel
):
    shader_list: Dict[dict] = {}
    shader_combinations: Dict[str, List[list]] = {}
    shader_seen = set()

    for pipeline in fm.Pipeline:
        pipeline_shader_list = []
        pipline_shader_combinations = []

        for shader_module in pipeline.ShaderModule:
            id = shader_module.path
            pipline_shader_combinations.append(id)

            if not id in shader_seen:
                shader_seen.add(id)

                shader_path = find_shader(roots, id)
                shader_ext = shader_path.suffix

                if shader_is_source(shader_ext):
                    shader_source_path = shader_path
                    shader_binary_path = compile_shader(build_dir, copy_dir, shader_path, fm)
                    copy_shader(build_dir, copy_dir, shader_path, fm)
                    spirv_reflect = reflect_shader(shader_binary_path)
                    entrypoint = get_shader_entrypoint(
                        id, spirv_reflect
                    )
                    entryname, mode = entrypoint
                elif shader_is_binary(shader_ext):
                    shader_binary_path = shader_path
                    copy_shader(shader_binary_path.stem, copy_dir, shader_path, fm)
                    spirv_reflect = reflect_shader(shader_binary_path)
                    entrypoint = get_shader_entrypoint(
                        id, spirv_reflect
                    )
                    entryname, mode = entrypoint
                    shader_source_path = disassemble_shader(
                        build_dir, shader_binary_path, mode
                    )
                else:
                    raise ValueError(
                        f"Can not determine if shader is GLSL source or "
                        "SPIR-V binary from the extension: {shader_ext}"
                    )

                if overwrite_dir:
                    baked_dir = Path(overwrite_dir) / shader_binary_path.name
                    print(f"BAKED({pipeline.name}): {shader_binary_path} -> {baked_dir}")
                    shader_binary_path = baked_dir

                shader = {
                    SHADER.MODE: mode,
                    SHADER.ENTRYNAME: entryname,
                    SHADER.BINPATH: shader_binary_path,
                    SHADER.SRCPATH: shader_source_path,
                    SHADER.REFLECT: spirv_reflect
                }

                shader_list[id] = shader
            else:
                shader = shader_list.get(id)
                if not shader:
                    raise ValueError(f"Could not find shader details for {id}")
            pipeline_shader_list.append(shader)
        validate_shader_combination(build_dir, pipeline_shader_list)
        shader_combinations[pipeline.name] = pipline_shader_combinations
    return {
        SHADER.LIST: shader_list,
        SHADER.COMBO: shader_combinations
    }
