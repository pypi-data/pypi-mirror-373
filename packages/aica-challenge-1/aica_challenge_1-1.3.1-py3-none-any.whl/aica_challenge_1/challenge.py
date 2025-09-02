import inspect

from pathlib import Path
from typing import List, Dict

from aica_challenge_1.package_manager import PackageManager
from aica_challenge_1.scenario_manager import ScenarioManager
from aica_challenge_1.execution_manager import ExecutionManager, RunSpecification

from cyst.api.environment.environment import Environment

class Challenge:
    """
    This is the main class for programmatic manipulation with the AICA challenge. It provides access to challenge
    management functionality and enables launching of training runs.

    In most of the cases it is better to use the TUI.

    Example:

        from aica_challenge_1.challenge import Challenge

        # It is better to hide everything behind this flag if you are to ever execute
        # runs. They are separate processes and they could cause some strange errors.
        if __name__ == "__main__"
            challenge = Challenge()
    """
    def __init__(self, challenge_dir: str = ""):
        caller_frame = inspect.currentframe().f_back
        if "__file__" in caller_frame.f_locals:
            caller_dir = Path(caller_frame.f_locals["__file__"]).parent
        else:
            caller_dir = Path.cwd()

        if challenge_dir:
            cd = Path(challenge_dir)
            if not cd.is_absolute():
                cd = caller_dir / cd
        else:
            cd = caller_dir

        if not self.check_init_state(cd):
            raise ValueError("Challenge environment not properly initiated", cd)

        self._package_manager = PackageManager(cd / "agents")
        self._scenario_manager = ScenarioManager(cd / "scenarios")
        self._execution_manager = ExecutionManager(self._package_manager, self._scenario_manager)

    @property
    def packages(self) -> PackageManager:
        """
        Provides access to package and agent management utilities.

        :returns: package manager
        """
        return self._package_manager

    @property
    def scenarios(self) -> ScenarioManager:
        """
        Provides access to scenario management utilities.

        :returns: scenario manager
        """
        return self._scenario_manager

    @property
    def execution(self) -> ExecutionManager:
        """
        Provides access to run preparation and execution.

        :returns: execution manager
        """
        return self._execution_manager

    # Convenience function
    def execute(self, run_specification: RunSpecification | str, single_process=False) -> None:
        """
        Executes a run. This function is just a proxy for the same function in execution manager.

        :param run_specification: Either a RunSpecification object or a name of a run specification that is stored in
            the database.
        :param single_process: If set to True, it will execute only one run at a time (regardless of the run
            specification) and it will display the stdout and stderr. If set to False, it will execute each run in a
            new process (even if the run specification says no parallel runs) and stdout and stderr are hidden and
            stored in the database.
        """
        self._execution_manager.execute(run_specification, single_process)

    @staticmethod
    def init_environment():
        """
        Initializes the AICA challenge environment in the current working directory. The initialization currently
        entails only creation of `agents` and `scenarios` directories.
        """
        caller_frame = inspect.currentframe().f_back
        if "__file__" in caller_frame.f_locals:
            caller_dir = Path(caller_frame.f_locals["__file__"]).parent
        else:
            caller_dir = Path.cwd()

        agents_path = caller_dir / "agents"
        scenarios_path = caller_dir / "scenarios"

        if not agents_path.exists():
            print(f"Creating new agents directory: {str(agents_path)}")
            agents_path.mkdir()

        if not scenarios_path.exists():
            print(f"Creating new scenarios directory: {str(scenarios_path)}")
            scenarios_path.mkdir()

    @staticmethod
    def check_init_state(challenge_dir: Path) -> bool:
        """
        Checks, whether an AICA challenge is initialized at the specified directory. The function looks for a presence
        of `agents` and `scenarios` directories.

        :param challenge_dir: A directory where to check for the challenge environment.

        :returns: True if the challenge is initialized at the specified path.
        """
        if not challenge_dir.exists():
            return False

        agents_path = challenge_dir / "agents"
        scenarios_path = challenge_dir / "scenarios"

        if not (agents_path.exists() and scenarios_path.exists()):
            return False

        return True

    @staticmethod
    def list_actions() -> List[Dict[str, str]]:
        result = []

        env = Environment.create()
        actions = env.resources.action_store.get_prefixed("ac1")

        for action in actions:
            result.append({
                "id": action.id,
                "description": action.description,
                "parameters": [x.name for x in action.parameters.values()]
            })

        return result
