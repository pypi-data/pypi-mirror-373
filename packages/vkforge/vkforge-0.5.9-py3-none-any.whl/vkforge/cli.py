import yaml
import json
import argparse
import os
from pathlib import Path
from .schema import VkForgeModel
from .shader import load_shader_data
from typing import Any
from dataclasses import is_dataclass, fields
from pydantic import BaseModel
from pathlib import Path
from .context import VkForgeContext
from .layout import create_pipeline_layouts
from .writer import Generate


def deep_serialize(obj: Any) -> Any:
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            # Convert tuple keys to strings
            if isinstance(k, tuple):
                new_key = str(k)
            else:
                new_key = k
            new_dict[new_key] = deep_serialize(v)
        return new_dict

    elif isinstance(obj, list):
        return [deep_serialize(v) for v in obj]

    elif isinstance(obj, tuple):
        return [deep_serialize(v) for v in obj]  # Optionally keep as tuple

    elif isinstance(obj, set):
        return [deep_serialize(v) for v in obj]  # sets → list for JSON

    elif isinstance(obj, Path):
        return str(obj)

    elif isinstance(obj, BaseModel):
        values = {k: deep_serialize(v) for k, v in obj.model_dump().items()}
        return values

    elif is_dataclass(obj):
        data = {f.name: deep_serialize(getattr(obj, f.name)) for f in fields(obj)}
        return data

    else:
        return obj


def load_file(config_path: str) -> dict:
    config_path: Path = Path(config_path)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Can not find {config_path} file.")

    if config_path.suffix.lower() in {".yaml", ".yml"}:
        with open(config_path) as f:
            return yaml.safe_load(f)
    elif config_path.suffix.lower() == ".json":
        with open(config_path) as f:
            return json.load(f)
    else:
        raise ValueError(
            f"Can determine file type from extension: {config_path.suffix}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="VkForge - Vulkan API Implemention Generation for Renderer Development."
    )
    parser.add_argument(
        "config_path",
        help="Relative or Absolute Path to VkForge Implementation VkForgeConfig. It may be YAML or JSON file. File type is determined by its extension.",
    )
    
    parser.add_argument(
        "--config-roots",
        help="Directories from which all path references (for example, shader path) in the VkForge config are relative to. Each path in the config, it is first checked by itself then by each path in --config-roots in order.",
        nargs="*",  # Accept 0 or more paths
        default=[],  # Fallback if user omits it
    )
    parser.add_argument(
        "--source-dir",
        default="VkForgeSrc",
        help="Directory where VkForge Source Implementation is generated. It is created if it does not exist. If the directory is not an absolute path then the directory is considered relative to the current working directory of the running VkForge script.",
    )
    
    parser.add_argument(
        "--build-dir",
        default="build",
        help="The build directory of your project. VkForge can share your project's build directory or it can point to a unique build directory for VkForge. Think of CMake's build directory. This is a Generic Build Directory. You can specify a more specific build directory.",
    )

    parser.add_argument(
        "--copy-shader-dir",
        default=None,
        help="This directory is specific to Shaders that VkForge compiles. VkForge stores compile shaders in --build-dir. However, if you want to store copies in another location then use this.",
    )

    parser.add_argument(
        "--remove-validations",
        action="store_true",
        help="If set, disables Vulkan validation layers (useful for release builds)."
    )

    parser.add_argument(
        "--overwrite-shader-dir",
        default=None,
        help="By default Pipeline Shaders are embedded with --build-dir as root path. This overwrite the root path. However, any compiled shader is still saved at --build-dir.",
    )

    args = parser.parse_args()
    raw_data = load_file(args.config_path)

    forgeModel = VkForgeModel(**raw_data)
    shaderData = load_shader_data(
        args.config_roots, 
        args.build_dir, 
        args.copy_shader_dir, 
        args.overwrite_shader_dir,
        forgeModel
    )
    layout = create_pipeline_layouts(forgeModel, shaderData)

    context = VkForgeContext(
        args.remove_validations,
        args.source_dir, 
        args.build_dir, 
        forgeModel, 
        shaderData, 
        layout
    )

    genFile = ".VkForgeGeneration"
    filepath = Path(context.buildDir) / genFile
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w") as f:
        f.write(json.dumps(deep_serialize(context), indent=4))
        print(f"GENERATED: {filepath}")

    

    Generate(context)


if __name__ == "__main__":
    main()

# from importlib.resources import files
# template_path = files("vkforge.templates") / "template1.glsl"
# print(template_path.read_text())
