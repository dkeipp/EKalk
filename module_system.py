from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import importlib
import json

@dataclass
class ParameterDefinition:
    datatype: str
    defaultValue: object | None = None
    hardLimits: dict | None = None
    softLimits: dict | None = None
    options: list | None = None
    source: list[str] = field(default_factory=list)
    editableInFrontend: bool = True
    reference: str | None = None

@dataclass
class ModuleDefinition:
    moduleName: str
    moduleId: str
    logic: str
    parameters: dict[str, ParameterDefinition]
    steps: list[str]

    @classmethod
    def from_json(cls, path: Path) -> "ModuleDefinition":
        data = json.loads(path.read_text())
        params = {
            name: ParameterDefinition(**cfg)
            for name, cfg in data.get("parameters", {}).items()
        }
        return cls(
            moduleName=data["moduleName"],
            moduleId=data["moduleId"],
            logic=data.get("logic", data["moduleId"].lower()),
            parameters=params,
            steps=data.get("steps", []),
        )

class ModuleRuntime:
    def __init__(self, definition: ModuleDefinition):
        self.definition = definition
        self.values = {name: p.defaultValue for name, p in definition.parameters.items()}

    def run(self) -> dict:
        logic = importlib.import_module(f"modules.{self.definition.logic}_logic")
        for step in self.definition.steps:
            func = getattr(logic, step)
            self.values = func(self.values)
        return self.values


class ProjectRuntime:
    """Simple container tying a global module with other modules."""

    def __init__(self, global_def: ModuleDefinition, module_defs: list[ModuleDefinition]):
        self.global_runtime = ModuleRuntime(global_def)
        self.modules = [ModuleRuntime(md) for md in module_defs]

    def _apply_globals(self, module: ModuleRuntime, global_values: dict):
        for name, param in module.definition.parameters.items():
            if "global" in param.source and param.reference:
                module.values[name] = global_values.get(param.reference)

    def run(self) -> dict:
        results = {"global": self.global_runtime.run(), "modules": []}
        for module in self.modules:
            self._apply_globals(module, results["global"])
            results["modules"].append(module.run())
        return results

if __name__ == "__main__":
    base = Path(__file__).parent / "modules"
    global_def = ModuleDefinition.from_json(base / "global_mod.json")
    fb_def = ModuleDefinition.from_json(base / "foerderband_mod.json")
    project = ProjectRuntime(global_def, [fb_def, fb_def])
    print(project.run())
