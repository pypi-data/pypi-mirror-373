import io
import os

from contextlib import redirect_stderr, redirect_stdout, nullcontext
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from typing import Dict, Any

from aica_challenge_1.scenario_manager import ScenarioVariant
from cyst.api.environment.environment import Environment

from aica_challenge_1.execution_structures import Episode, DBEpisode, DBRun, RunStatus

def launch_simulation(run_id: int, episode_number: int, scenario: ScenarioVariant, agent: str, max_time: float,
                      max_actions: int, agent_configuration: Dict[str, str] | None = None, supress_output=True) -> Episode:
    # This is a bit of a hack, but we do it this way for backwards compatibility
    if "disable_platform_logging" in agent_configuration:
        os.environ["CYST_PLATFORM_DISABLE_MESSAGE_STORAGE"] = "1"
        del agent_configuration["disable_platform_logging"]

    if "data_batch_storage" in agent_configuration:
        os.environ["CYST_DATA_BATCH_STORAGE"] = "1"
        del agent_configuration["data_batch_storage"]

    parameters: Dict[str, Any] = { "agent-name": agent }
    if agent_configuration:
        parameters["agent-configuration"] = agent_configuration

    os.environ["CYST_MAX_RUNNING_TIME"] = str(max_time)
    os.environ["CYST_MAX_ACTION_COUNT"] = str(max_actions)
    os.environ["CYST_DATA_BACKEND"] = "sqlite"
    os.environ["CYST_DATA_BACKEND_PARAMS"] = "path,aica_challenge.db"
    os.environ["CYST_RUN_ID_LOG_SUFFIX"] = "1"

    db = create_engine("sqlite+pysqlite:///aica_challenge.db")

    with redirect_stdout(io.StringIO()) if supress_output else nullcontext() as stdout:
        with redirect_stderr(io.StringIO()) if supress_output else nullcontext() as stderr:

            env = Environment.create()
            try:
                env.configure(*scenario.config, parameters=parameters)
            except RuntimeError as e:
                print(f"Could not configure a simulation. Reason: {str(e)}")

            env.control.init()

            episode_id = -1

            with Session(db) as session:
                stmt = select(DBRun).where(DBRun.id == run_id)
                run: DBRun = session.scalars(stmt).one()

                db_episode = DBEpisode(
                        stdout="",
                        stderr="",
                        cyst_run_id=env.infrastructure.statistics.run_id,
                        status=str(RunStatus.RUNNING),
                        run_id=run_id,
                        run=run,
                        episode_number=episode_number,
                        episode_variant=scenario.id,
                    )

                session.add(db_episode)
                run.episodes.append(db_episode)

                session.add(run)
                session.flush()

                episode_id = db_episode.id

                session.commit()

            success, state = env.control.run()
            env.control.commit()

            episode = Episode(
                cyst_run_id=env.infrastructure.statistics.run_id,
                stdout=stdout.getvalue() if supress_output else "",
                stderr=stderr.getvalue() if supress_output else "",
                run=run_id,
                variant=scenario.id,
                number=episode_number,
                status=RunStatus.FINISHED if success else RunStatus.ERROR
            )

            with Session(db) as session:
                stmt = select(DBEpisode).where(DBEpisode.id == episode_id)
                db_episode: DBEpisode = session.scalars(stmt).one()

                db_episode.stdout = episode.stdout
                db_episode.stderr = episode.stderr
                db_episode.status = str(episode.status)

                session.commit()

    return episode