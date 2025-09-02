import importlib.util
import json
import requests
import sys
import string
import secrets
import uuid

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from cyst.api.configuration import ConfigItem


@dataclass
class ScenarioVariant:
    """
    Represents one variant of a particular scenario.

    :param id: An identifier of a this variant.
    :param path: A path to the variant's configuration file.
    :param config: A list of configuration items parsed from configuration file.
    """
    id: int
    path: str
    config: List[ConfigItem]


@dataclass
class Scenario:
    """
    Represents a scenario.

    :param name: A given name of the scenario.
    :param short_path: A name of the scenario directory inside the `scenarios` directory of the challenge.
    :param path: A full path to the scenario.
    :param description: A description of the scenario.
    :param goal: A goal of the scenario.
    :param parameters: A set of parameters that is passed to agents on top of the run parameters.
    :param variants: A list of variants for the scenario.
    """
    name: str
    short_path: str
    path: str
    description: str
    goal: str
    parameters: Dict[str, str]
    variants: Dict[int, ScenarioVariant]


class ScenarioManager:
    """
    Scenario manager takes care of tracking and downloading scenarios.
    """
    def __init__(self, scenarios_path: str | Path = ""):
        self._remote_scenarios: Dict[str, Scenario] = {}
        self._local_scenarios: Dict[str, Scenario] = {}

        self._repository_url = "https://gitlab.ics.muni.cz/aica/scenarios_1/-/raw/master/"

        if not scenarios_path:
            self._scenarios_path: Path = Path(__file__).parent / "scenarios"
        elif isinstance(scenarios_path, str):
            self._scenarios_path: Path = Path(scenarios_path)
        else:
            self._scenarios_path = scenarios_path

        if not self._scenarios_path.exists():
            raise ValueError("Path to scenarios does not exist.")

        self._scan_local_scenarios()

    @staticmethod
    def _get_configuration_objects(path: Path) -> List[ConfigItem]:
        module_name = "configuration_variant_" + str(uuid.uuid4())
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        configuration_objects =  module.configuration
        if type(configuration_objects) == List:
            return configuration_objects
        else:
            return [configuration_objects]

    def _scan_variant(self, id: str, variants_path: Path) -> Optional[ScenarioVariant]:
        path = variants_path / id

        configuration_path = path / "configuration.py"

        if not configuration_path.exists():
            print(f"Configuration files for the variant '{id}' not found. Variant ignored.")
            return None

        try:
            configuration_objects = self._get_configuration_objects(configuration_path)
        except:
            print(f"Failed to read the configuration file for the variant '{id}'. Variant ignored.")
            return None

        return ScenarioVariant(int(id), str(configuration_path), configuration_objects)

    def _scan_scenario(self, name: str, scenarios_path: Path) -> Optional[Scenario]:
        path = scenarios_path / name

        name_path = path / "name.md"
        if name_path.exists():
            name_s = name_path.read_text()
        else:
            name_s = name

        description_path = path / "description.md"
        if description_path.exists():
            description = description_path.read_text()
        else:
            description = "No description provided"

        goal_path = path / "goal.md"
        if goal_path.exists():
            goal = goal_path.read_text()
        else:
            goal = "No goal provided"

        parameters_path = path / "parameters.json"
        if parameters_path.exists():
            parameters = json.loads(parameters_path.read_text())
        else:
            parameters = {}

        result = Scenario(name_s, name, str(path), description, goal, parameters, {})

        variants_path = path / "variants"
        variants_on_path = set([x.parts[-1] for x in variants_path.iterdir() if x.is_dir()])

        for variants_id in variants_on_path:
            variant = self._scan_variant(variants_id, variants_path)
            if variant:
                result.variants[int(variants_id)] = variant

        if not result.variants:
            print(f"Could not find any valid scenario variants. Scenario '{name}' not included.")
            return None
        else:
            return result

    def _scan_local_scenarios(self) -> None:
        scenarios_on_path = set([x.parts[-1] for x in self._scenarios_path.iterdir() if x.is_dir()])

        for scenario_name in scenarios_on_path:
            scenario = self._scan_scenario(scenario_name, self._scenarios_path)
            if scenario:
                self._local_scenarios[scenario_name] = scenario

    def _scan_remote_scenarios(self) -> None:
        r = requests.get(self._repository_url + "scenarios.json")
        scenarios_info = r.json()

        for scenario in scenarios_info:
            if "parameters" in scenario:
                parameters = scenario["parameters"]
            else:
                parameters = {}

            s = Scenario(scenario["name"], scenario["path"], scenario["path"], scenario["description"], scenario["goal"], parameters, {})
            for variant in scenario["variants"]:
                v = ScenarioVariant(variant, str(variant), [])
                s.variants[variant] = v
            self._remote_scenarios[s.name] = s

    def download_remote_scenarios(self, overwrite: bool = False) -> None:
        """
        Attempts to download all scenarios that are currently published.

        :param overwrite: If False, it will not attempt to overwrite local scenarios. This is mostly useful in
            situations when you made local modifications that you want to preserve.
        """
        self._scan_remote_scenarios()

        for scenario in self._remote_scenarios.values():
            scenario_path = self._scenarios_path / scenario.path
            if not scenario_path.exists():
                scenario_path.mkdir()

            (scenario_path / "name.md").write_text(scenario.name)
            (scenario_path / "description.md").write_text(scenario.description)
            (scenario_path / "goal.md").write_text(scenario.goal)
            (scenario_path / "parameters.json").write_text(json.dumps(scenario.parameters))

            for variant in scenario.variants.values():
                variant_path_remote = Path(scenario.path) / variant.path / "configuration.py"
                variant_path_local = self._scenarios_path / scenario.path / "variants" / variant.path / "configuration.py"
                variant_config = requests.get(self._repository_url + variant_path_remote.as_posix()).text
                if not variant_path_local.parent.exists():
                    variant_path_local.parent.mkdir(parents=True)
                    variant_path_local.write_text(variant_config)
                elif overwrite:
                    variant_path_local.write_text(variant_config)

    def get_scenario(self, name: str) -> Optional[Scenario]:
        """
        Retrieve a local scenario by name.

        :param name: A short name (i.e., the directory in `scenarios` directory) of the scenario.

        :return: A scenario description if there is a scenario of the given name, None otherwise.
        """
        if name not in self._local_scenarios:
            return None
        else:
            return self._local_scenarios[name]

    def get_scenarios(self, remote: bool = False) -> List[Scenario]:
        """
        Retrieves descriptions of either local or remote scenarios.

        :param remote: If set to True, checks for all available scenarios online. Otherwise look only inside the
            `scenarios` directory.

        :return: A list of scenario descriptions.
        """
        if remote:
            self._scan_remote_scenarios()
            return list(sorted(self._remote_scenarios.values(), key=lambda v: v.name))
        else:
            self._scan_local_scenarios()
            return list(sorted(self._local_scenarios.values(), key=lambda v: v.name))
