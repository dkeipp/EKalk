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
    def __init__(self, definition: ModuleDefinition, overrides: dict | None = None):
        self.definition = definition
        self.values = {name: p.defaultValue for name, p in definition.parameters.items()}
        if overrides:
            self.values.update(overrides)

    def run(self) -> dict:
        logic = importlib.import_module(f"modules.{self.definition.logic}_logic")
        for step in self.definition.steps:
            func = getattr(logic, step)
            self.values = func(self.values)
        return self.values


class ProjectRuntime:
    """Simple container tying a global module with other modules."""

    def __init__(self, global_def: ModuleDefinition, module_defs: list[tuple[ModuleDefinition, dict | None]]):
        self.global_runtime = ModuleRuntime(global_def)
        self.modules = [ModuleRuntime(md, overrides) for md, overrides in module_defs]

    def _apply_globals(self, module: ModuleRuntime, global_values: dict):
        for name, param in module.definition.parameters.items():
            if "global" in param.source and param.reference:
                if module.values.get(name) is None:
                    module.values[name] = global_values.get(param.reference)

    def run(self) -> dict:
        results = {"global": self.global_runtime.run(), "modules": []}
        cabinet_elements: dict[str, list] = {}
        motor_currents = []
        motor_rated_loads = []
        motor_operating_loads = []
        sc_module = None
        for module in self.modules:
            if module.definition.logic == "schaltschrank":
                sc_module = module
                continue
            self._apply_globals(module, results["global"])
            res = module.run()
            results["modules"].append(res)
            if "control_cabinet" in res:
                for elem in res["control_cabinet"]:
                    origin = elem.get("origin")
                    item = dict(elem)
                    item.pop("origin", None)
                    cabinet_elements.setdefault(origin, []).append(item)
            if "motor_rated_current" in res:
                motor_currents.append(res["motor_rated_current"])
            if "drives" in res:
                for drive in res["drives"]:
                    if "motor_rated_current" in drive:
                        motor_currents.append(drive["motor_rated_current"])
            if "motor_rated_load" in res:
                motor_rated_loads.append(res["motor_rated_load"])
            if "motor_operating_load" in res:
                motor_operating_loads.append(res["motor_operating_load"])
        if sc_module:
            sc_module.values["elements"] = cabinet_elements
            sc_module.values["motor_currents"] = motor_currents
            sc_module.values["motor_rated_loads"] = motor_rated_loads
            sc_module.values["motor_operating_loads"] = motor_operating_loads
            self._apply_globals(sc_module, results["global"])
            results["modules"].append(sc_module.run())
        return results

if __name__ == "__main__":
    base = Path(__file__).parent / "modules"
    global_def = ModuleDefinition.from_json(base / "global_mod.json")
    fb_def = ModuleDefinition.from_json(base / "foerderband_mod.json")
    sp_def = ModuleDefinition.from_json(base / "splitter_mod.json")
    sc_def = ModuleDefinition.from_json(base / "schaltschrank_mod.json")

    modules = [
        (fb_def, {
            "id": "H101",
            "label": "Zuführband",
            "length": 6,
            "motor_rated_power": 5.5,
            "start_type": "DOL",
            "repair_switch": "integriert",
            "pull_cord": "beidseitig",
        }),
        (sp_def, {
            "id": "F102",
            "label": "Splitter",
            "length": 5,
            "motor_rated_power": 5.5,
            "start_type": "FU",
            "frequency": 87,
            "repair_switch": "extern",
            "pull_cord": "links",
            "drive_count": 3,
            "cable_cross_section": 16,
        }),
        (fb_def, {
            "id": "H103",
            "label": "Überkorn",
            "length": 25,
            "motor_rated_power": 9.2,
            "start_type": "DOL",
            "repair_switch": "integriert",
            "pull_cord": "beidseitig",
            "avg_cable_length": 40,
        }),
        (fb_def, {
            "id": "H104",
            "label": "Unterkorn",
            "length": 10,
            "motor_rated_power": 4.0,
            "start_type": "DOL",
            "repair_switch": "integriert",
            "pull_cord": "einseitig",
        }),
        (
            sc_def,
            {
                "id": "SC1",
                "label": "Virtueller Schrank",
                "virtual_cabinet": True,
            },
        ),
    ]

    project = ProjectRuntime(global_def, modules)
    print(json.dumps(project.run(), indent=2, ensure_ascii=False))
