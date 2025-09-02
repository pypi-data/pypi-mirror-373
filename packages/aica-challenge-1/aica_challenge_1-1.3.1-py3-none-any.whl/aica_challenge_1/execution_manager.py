import base64
import functools
import io
import json
import os
import pprint
import random
import uuid
import zlib

from concurrent.futures import ProcessPoolExecutor, Future
from contextlib import redirect_stderr, redirect_stdout, nullcontext
from dataclasses import dataclass, field
from enum import Enum, auto
from random import choice
from threading import Event

import requests
import sqlalchemy
from sqlalchemy import create_engine, select, ForeignKey, delete, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedAsDataclass, Session, relationship
from typing import Dict, Any, Optional, List, Self, Set, Tuple

from cyst.api.environment.environment import Environment
from cyst.api.utils.counter import Counter

from aica_challenge_1.package_manager import PackageManager
from aica_challenge_1.scenario_manager import ScenarioManager, ScenarioVariant
from aica_challenge_1.launcher import launch_simulation
from aica_challenge_1.execution_structures import Episode, DBEpisode, DBRun, RunStatus, RunSpecification, Run, Base, \
    DBRunParameter, DBRunSpecification


class ExecutionManager:
    """
    The execution manager retrieves run specifications and takes care of run executions.
    """
    def __init__(self, package_manager: PackageManager, scenario_manager: ScenarioManager):
        self._package_manager = package_manager
        self._scenario_manager = scenario_manager
        self._run_specifications: Dict[str, RunSpecification] = {}
        self._run_specifications_by_id: Dict[id, RunSpecification] = {}

        self._db = create_engine("sqlite+pysqlite:///aica_challenge.db")
        Base.metadata.create_all(self._db)

        # --------------------------------------------------------------------------------------------------------------
        # Fixing of later changes to the database to maintain backwards compatibility
        md = sqlalchemy.MetaData()
        t = sqlalchemy.Table("challenge_episode_statistics", md, autoload_with=self._db)
        if not "episode_variant" in [col.name for col in t.c]:
            print("Need to alter the table")
            connection = self._db.connect()
            query = f"ALTER TABLE challenge_episode_statistics ADD episode_variant INT DEFAULT -1"
            connection.execute(text(query))
        # --------------------------------------------------------------------------------------------------------------

        with Session(self._db) as session:
            for obj in session.execute(select(DBRunSpecification)).scalars():
                spec = RunSpecification.from_db_spec(obj)
                self._run_specifications[obj.name] = spec
                self._run_specifications_by_id[obj.id] = spec

            parameters: Dict[int, List[DBRunParameter]] = {}
            for obj in session.execute(select(DBRunParameter)).scalars():
                if not obj.run_id in parameters:
                    parameters[obj.run_id] = []
                parameters[obj.run_id].append(obj)

            for spec in self._run_specifications.values():
                if spec.db_id in parameters:
                    for param in parameters[spec.db_id]:
                        spec.parameters[param.key] = param.value

        self._runs: Dict[int, Run] = {}

        self._evaluation_finished = Event()

    def list_run_specifications(self) -> List[str]:
        """
        Provides a list of run names that are available for execution.

        :return: A list of run names.
        """
        return sorted([x for x in self._run_specifications.keys() if not x.startswith("__evaluation")])

    def get_run_specification(self, name: str) -> Optional[RunSpecification]:
        """
        Attempts to retrieve a run specification by name.

        :param name: A name of the specification.

        :return: A run specification if it exists for a given name, or None otherwise.
        """
        return self._run_specifications.get(name, None)

    def set_run_specification(self, specification: RunSpecification, old_specification: Optional[RunSpecification] = None) -> None:
        """
        Saves a run specification to the database.

        :param specification: A specification that should be saved.
        :param old_specification: If provided, this specification will be overwritten by the other specification
        """
        if old_specification and old_specification.name and old_specification.name != specification.name:
            del self._run_specifications[str(old_specification.name)]

        self._run_specifications[specification.name] = specification

        with Session(self._db) as session:
            db_obj = None
            if specification.db_id != -1:
                db_obj = session.execute(select(DBRunSpecification).where(DBRunSpecification.id==specification.db_id)).scalar_one()
                db_obj.replace(specification)
            else:
                db_obj = DBRunSpecification.copy(specification)

            session.add(db_obj)
            session.flush()

            if specification.db_id == -1:
                specification.db_id = db_obj.id

            specification_keys = set(specification.parameters.keys())
            db_keys = set()

            for obj in session.execute(select(DBRunParameter).where(DBRunParameter.run_id==db_obj.id)).scalars():
                # Key was deleted
                if obj.key not in specification.parameters:
                    session.execute(delete(DBRunParameter).where(DBRunParameter.id == obj.id))
                else:
                    db_keys.add(obj.key)
                    obj.value = specification.parameters[obj.key]
                    session.add(obj)

            new_keys = specification_keys - db_keys
            for key in new_keys:
                session.add(DBRunParameter(run_id=db_obj.id, key=key, value=specification.parameters[key]))

            session.commit()

    def save_run_information(self, run: Run) -> None:
        with Session(self._db, expire_on_commit=False) as session:
            stmt = select(DBRun).where(DBRun.id == run.id)
            run_db: DBRun = session.scalars(stmt).one()

            details = f"Successfull episodes: {sorted(list(run.successful))}, failed episodes: {sorted(list(run.error))}"

            run.detail = details
            run_db.details = details

            # We set status to finished whenever there was at elast one successful episode
            status = RunStatus.FINISHED if run.successful else RunStatus.ERROR
            run.status = status
            run_db.status = str(status)

            session.commit()

    def get_run(self, run_id: int) -> Run:
        """
        Gets the information about a specific run.

        :param run_id: An ID of the run to get.

        :return: A run information.
        """
        return self._runs[run_id]

    def get_runs(self) -> List[Tuple[int, RunStatus]]:
        """
        Gets the IDs and statuses of all runs executed in the challenge instance.

        :return: Tuple containing the ID [0] and status [1] for each run.
        """
        result = []
        for k in sorted(self._runs.keys()):
            r = self._runs[k]
            result.append((k, self._runs[k].status))
        return result

    def execution_callback(self, episode_number: int, future: Future):
        if future.exception():
            print(f"The episode {episode_number} has been terminated.")
            return

        e: Episode = future.result()
        run = self._runs[e.run]
        run.episodes[episode_number] = e
        run.running.remove(episode_number)
        if e.status == RunStatus.FINISHED:
            run.successful.add(episode_number)
        else:
            run.error.add(episode_number)

        if run.specification.name.startswith("__evaluation"):
            progress = (len(run.episodes) / run.specification.max_episodes) * 100
            print(f"Progress: {progress:.1f} %")

        if not run.running:
            self.save_run_information(run)
            if run.specification.name.startswith("__evaluation"):
                print("Evaluation finished. Uploading results...")
                self._upload_evaluation_results(run)
                self._evaluation_finished.set()

    def _upload_evaluation_results(self, run: Run) -> None:
        # For the evaluation the following is exported
        # - run specification
        # - run status
        # - episodes status
        # - actions
        # - messages
        # - signals
        result_obj = None

        with Session(self._db) as session:
            run_db_id = run.id

            result = session.execute(select(DBRun).where(DBRun.id == run_db_id)).scalar_one()
            result_obj = {
                "status": result.status,
                "specification": {
                    "name": result.specification.name,
                    "agent": result.specification.agent_name,
                    "scenario": result.specification.scenario
                },
                "episodes": []
            }

            for episode in result.episodes:
                out = {
                    "number": episode.episode_number,
                    "variant": episode.episode_variant,
                    "status": episode.status,
                    "actions": [],
                    "messages": [],
                    "signals": []
                }

                actions = session.execute(text("select action.*, "
                                                 "max(case when action_parameter.name == 'net' then action_parameter.value END) as param_net, "
                                                 "max(case when action_parameter.name == 'path' then action_parameter.value END) as param_path "
                                               "from action "
                                               "left join action_parameter on action.id = action_parameter.action_id "
                                               "group by action.id "
                                              f"having action.run_id == '{episode.cyst_run_id}'")).all()

                for action in actions:
                    out["actions"].append(dict(action._mapping))

                messages = session.execute(text(f"select message.* from message where message.run_id == '{episode.cyst_run_id}'")).all()

                for message in messages:
                    out["messages"].append(dict(message._mapping))

                signals = session.execute(text(f"select signal.* from signal where signal.run_id == '{episode.cyst_run_id}'")).all()

                for signal in signals:
                    out["signals"].append(dict(signal._mapping))

                result_obj["episodes"].append(out)

        if result_obj:
            result_str = json.dumps(result_obj)
            compressed = zlib.compress(bytearray(result_str, "utf-8")).hex()
            params = {
                "api_key": "f5f13b7c-eaaa-4695-824e-53548f8ce576",
                "data": compressed
            }
            response = requests.post("http://127.0.0.1:8000/evaluation_submit/", json=params)
            if not response.ok:
                print(f"Failed to submit evaluation results. Reason: {response.text}")
            else:
                print(f"Evaluation successful. Resulting score: {response.json()["score"]}")

    def evaluate(self, scenario_name: str, agent_name: str, api_key: str) -> None:
        """
        Commences an evaluation. Beware that it will download and overwrite all local scenarios.

        :param scenario_name:
        :param api_key:
        :return:
        """

        # Download and overwrite scenarios
        self._scenario_manager.download_remote_scenarios(True)

        evaluation_url = "http://127.0.0.1:8000/"

        # Get template for the given scenario
        result = requests.get(evaluation_url + "evaluation_template/" + scenario_name)
        if not result.ok:
            raise ValueError(f"There was an error attempting to download evaluation template for scenario '{scenario_name}'. "
                             f"Error: {result.text}")

        template = json.loads(result.content)
        if not template["success"]:
            raise ValueError(f"There was an error attempting to download evaluation template for scenario '{scenario_name}'. "
                             f"Error: {template["content"]}")


        # Prepare a run specification
        specification = RunSpecification(
            name=f"__evaluation_" + str(uuid.uuid4()),
            description="Evaluation run specification",
            agent_name=agent_name,
            scenario=scenario_name,
            variant=-1,
            max_time=template["content"]["max_time"],
            max_actions=template["content"]["max_actions"],
            max_episodes=template["content"]["episodes"],
            max_parallel=1,
            parameters={
                "disable_platform_logging": 1
            }
        )

        self.set_run_specification(specification)

        print(f"Executing evaluation run, please don't turn off the challenge...")
        print(f"Scenario: {specification.scenario}\nAgent: {specification.agent_name}")
        print(f"Progress: 0.0 %")
        self._evaluation_finished.clear()
        self.execute(specification)
        self._evaluation_finished.wait()

    def execute(self, specification: RunSpecification | str, single_process=False) -> None:
        """
        Executes a run.

        :param specification: Either a RunSpecification object or a name of a run specification that is stored in
            the database.
        :param single_process: If set to True, it will execute only one run at a time (regardless of the run
            specification) and it will display the stdout and stderr. If set to False, it will execute each run in a
            new process (even if the run specification says no parallel runs) and stdout and stderr are hidden and
            stored in the database.
        """
        if isinstance(specification, str):
            spec_name = specification
            specification = self._run_specifications.get(specification, None)
            if not specification:
                raise ValueError(f"Run with the name '{spec_name}' not available in the system.")

        with Session(self._db) as session:
            """
            # Refresh run specification
            specification = session.get(DBRunSpecification, specification.db_id)

            if not specification:
               raise ValueError(f"There was an error extracting run specification from the database")

            parameters = []
            for obj in session.execute(select(DBRunParameter).where(DBRunParameter.run_id==specification.id)).scalars():
                parameters.append(obj)
            """

            run = Run(specification)

            db_specification = session.get(DBRunSpecification, specification.db_id)
            db_run = DBRun(
                status=str(RunStatus.INIT),
                details="",
                episodes=[],
                specification_id=specification.db_id,
                specification=db_specification
            )

            session.add(db_run)
            session.flush()

            if not specification.name:
                run.status = RunStatus.ERROR
                run.detail = "Run specification must have a name."
                db_run.status = str(RunStatus.ERROR)
                db_run.details = run.detail
                session.commit()
                return

            if specification.agent_name not in self._package_manager.list_installed_agents():
                run.status = RunStatus.ERROR
                run.detail = f"Chosen agent '{specification.agent_name}' not installed in the system."
                db_run.status = str(RunStatus.ERROR)
                db_run.details = run.detail
                session.commit()
                return

            scenario_name = specification.scenario
            scenario = self._scenario_manager.get_scenario(scenario_name)
            scenarios = self._scenario_manager.get_scenarios()

            if scenario_name == "Random":
                if not scenarios:
                    run.status = RunStatus.ERROR
                    run.detail = "No scenarios installed in the system. Cannot choose a random one."
                    db_run.status = str(RunStatus.ERROR)
                    db_run.details = run.detail
                    session.commit()
                    return
                # s = choice(scenarios)
                # scenario_name = s.short_path
                # scenario = s
            elif not scenario:
                run.status = RunStatus.ERROR
                run.detail = f"Chosen scenario '{specification.scenario}' not available."
                db_run.status = str(RunStatus.ERROR)
                db_run.details = run.detail
                session.commit()
                return

            variant_id = specification.variant

            # Only non-random scenarios can have non-random variants
            if variant_id != -1 and variant_id not in scenario.variants:
                run.status = RunStatus.ERROR
                run.detail = f"Variant '{variant_id}' of the scenario '{scenario_name}' is not available in the system."
                db_run.status = str(RunStatus.ERROR)
                db_run.details = run.detail
                session.commit()
                return

            run.id = db_run.id
            self._runs[run.id] = run

            run.status = RunStatus.RUNNING
            db_run.status = str(RunStatus.RUNNING)

            session.commit()

        if not single_process:
            run.executor = ProcessPoolExecutor(max_workers=specification.max_parallel)

        for e in range(specification.max_episodes):
            if scenario_name == "Random":
                s = choice(scenarios)
            else:
                s = scenario

            parameters = specification.parameters.copy()
            for key, value in s.parameters.items():
                if key not in parameters:
                    parameters[key] = value

            if variant_id == -1:
                scenario_variant = random.choice(list(s.variants.values()))
            else:
                scenario_variant = s.variants[variant_id]

            if not single_process:
                future: Future = run.executor.submit(launch_simulation, run.id, e, scenario_variant,
                                                     specification.agent_name, specification.max_time,
                                                     specification.max_actions, parameters)
                future.add_done_callback(functools.partial(self.execution_callback, e))
                run.running.add(e)
            else:
                ep = launch_simulation(run.id, e, scenario_variant, specification.agent_name, specification.max_time,
                                       specification.max_actions, parameters, supress_output=False)

                if ep.status == RunStatus.FINISHED:
                    run.successful.add(e)
                else:
                    run.error.add(e)

                self.save_run_information(run)
