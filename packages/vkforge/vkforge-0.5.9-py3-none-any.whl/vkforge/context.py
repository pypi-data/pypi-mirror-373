from dataclasses import dataclass
from .schema import VkForgeModel


@dataclass
class VkForgeContext:
    removeValidations: bool = False
    sourceDir: str = None
    buildDir: str = None
    forgeModel: VkForgeModel = None
    shaderData: dict = None
    layout: dict = None
