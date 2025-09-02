import dataclasses
import os
import signal

import psutil

from aica_challenge_1 import Challenge, RunSpecification
from pathlib import Path
from pythonclimenu import menu
from typing import Dict, List, Callable, Any, Optional

from aica_challenge_1.execution_manager import RunStatus, Run

background_color = (100, 100, 100)

def wait_for_key():
    print("Press any key to continue...")
    input()

# Forward references, yay!
menus: Dict[str, Any] = {}

menu_top_level = {
    "back": None,
    "menu": [
        f"AICA Challenge 1",
        {
            "Packages/Agents": None,
            "Scenarios": None,
            "Execution": None,
            "Exit": None
        },
        background_color
    ]}

def list_installed_agents(challenge: Challenge):
    print("Installed agents:")
    for agent in challenge.packages.list_installed_agents().values():
        print(f"Agent: {agent.name}, Package: {agent.package}, Description: {agent.description}")
    print("")
    wait_for_key()

def list_available_packages(challenge: Challenge):
    print("Available packages:")
    for package in challenge.packages.list_available_packages():
        print(package)
    print("")
    wait_for_key()

def install_package(challenge: Challenge, package_name):
    print(f"Installing a package from the directory '{package_name}'...", end='', flush=True)
    success, out, err = challenge.packages.install_package(package_name)
    if success:
        print("[OK]")
    else:
        print("[ERROR]")
        print(out.replace("\\n", '\n').replace('\\t', '\t').replace('\\r', '\r'))
        print(err.replace("\\n", '\n').replace('\\t', '\t').replace('\\r', '\r'))

    print("")

def install_package_menu(challenge: Challenge):
    available_packages = challenge.packages.list_available_packages()
    if not available_packages:
        print("No packages available to install")
        wait_for_key()
        return

    available_packages.append("Cancel")
    choice = menu("Install package: ", available_packages, background_color)
    if choice != "Cancel":
        install_package(challenge, choice)
        list_installed_agents(challenge)

def install_all(challenge: Challenge):
    available_packages = challenge.packages.list_available_packages()
    if not available_packages:
        print("No packages available to install")
        wait_for_key()
    else:
        for package in available_packages:
            install_package(challenge, package)
        list_installed_agents(challenge)

def remove_package(challenge: Challenge, package_name: str):
    print(f"Removing the package '{package_name}'...", end='', flush=True)
    success, out, err = challenge.packages.remove_package(package_name)
    if success:
        print("[OK]")
    else:
        print("[ERROR]")
        print(out)
        print(err)

    print("")

def remove_package_menu(challenge: Challenge):
    installed_packages = [x.name for x in challenge.packages.list_installed_packages()]
    if not installed_packages:
        print("No packages available to remove")
        wait_for_key()
        return

    installed_packages.append("Cancel")
    choice = menu("Remove package: ", installed_packages, background_color)
    if choice != "Cancel":
        remove_package(challenge, choice)
        list_installed_agents(challenge)

def remove_all(challenge: Challenge):
    installed_packages = [x.name for x in challenge.packages.list_installed_packages()]
    if not installed_packages:
        print("No packages available to remove")
        wait_for_key()
    else:
        for package in installed_packages:
            remove_package(challenge, package)
        list_installed_agents(challenge)

def init_agent(challenge: Challenge):
    agent_name = input("Please provide a name for the new agent: ")
    result, normalized_name = challenge.packages.init_agent(agent_name)

    if not result:
        wait_for_key()
        return

    choice = menu((f"Agent '{normalized_name}' was successfully initialized. Would you like to install it right away?", "(You can do it later without any problem)"),
                  ["Yes", "No"],
                  background_color)

    if choice == "Yes":
        install_package(challenge, normalized_name)
        list_installed_agents(challenge)

menu_packages = {
    "back": menu_top_level,
    "menu": [
        "Package/Agent management",
        {
            "List installed agents": list_installed_agents,
            "List available packages": list_available_packages,
            "Install package": install_package_menu,
            "Install all": install_all,
            "Remove package": remove_package_menu,
            "Remove all": remove_all,
            "Init agent": init_agent,
            "Back": None
        },
        background_color
    ]}

def list_remote_scenarios(challenge: Challenge):
    print("Remotely available scenarios:")
    for scenario in challenge.scenarios.get_scenarios(remote=True):
        print(f"\nName: {scenario.name}\nDescription: {scenario.description}\nGoal: {scenario.goal}\nVariants: {[x.id for x in scenario.variants.values()]}")
    print("")
    wait_for_key()

def list_local_scenarios(challenge: Challenge):
    print("Locally available scenarios:")
    for scenario in challenge.scenarios.get_scenarios():
        print(f"\nName: {scenario.name}\nDescription: {scenario.description}\nGoal: {scenario.goal}\nVariants: {sorted([x.id for x in scenario.variants.values()])}")
    print("")
    wait_for_key()

def download_scenarios(challenge: Challenge) -> None:
    choice = menu("Do you want to overwrite local files with remote ones?",
                  ["Yes", "No", "Back"],
                  background_color)

    if choice == "Back":
        return

    challenge.scenarios.download_remote_scenarios(overwrite=(choice == "Yes"))
    print("Scenarios successfully downloaded")
    wait_for_key()

menu_scenarios = {
    "back": menu_top_level,
    "menu": [
        "Scenario management",
        {
            "List remote scenarios": list_remote_scenarios,
            "List local scenarios": list_local_scenarios,
            "Download scenarios": download_scenarios,
            "Back": None
        },
        background_color
]}

def choose_agent(challenge: Challenge) -> Optional[str]:
    options = list(challenge.packages.list_installed_agents().keys())
    options.append("Back")

    choice = menu("Select agent:",
                  options,
                  background_color)

    if choice == "Back":
        return None
    else:
        return choice

def choose_scenario(challenge: Challenge) -> Optional[str]:
    available_scenarios = {x.name: x for x in challenge.scenarios.get_scenarios()}
    options = [x.name for x in available_scenarios.values()]
    options.append("Random")
    options.append("Back")

    choice = menu("Choose, which scenario to use in runs:",
                  options,
                  background_color)

    if choice == "Back":
        return None
    elif choice == "Random":
        return "Random"
    else:
        return available_scenarios[choice].short_path

def choose_variant(challenge: Challenge, scenario: str) -> Optional[int]:
    if scenario == "Random":
        print("Random scenario supports only random variants.")
        wait_for_key()
        return -1

    available_variants = challenge.scenarios.get_scenario(scenario).variants

    error = ""
    while True:
        print(f"Variants available for scenario '{scenario}': {sorted(available_variants.keys())}")
        if error:
            print(error)

        v = input("Choose, which variants to use or type '-1' for random variant: ")
        try:
            v_int = int(v)
        except:
            error = "Please specify a number"
            continue

        if v_int != -1 and v_int not in available_variants:
            error = "Please select one of the variants"
        else:
            return v_int

def set_run_parameters(challenge: Challenge, template: RunSpecification) -> None:
    parameters = iter(["max_time", "max_actions", "max_episodes", "max_parallel"])

    next_parameter = next(parameters)
    while True:
        user_input = input(f"Enter new value for '{next_parameter}'. (Current value - {getattr(template, next_parameter)}): ")

        try:
            value = int(user_input)
        except ValueError:
            print("Please, enter a number")
            continue

        setattr(template, next_parameter, value)
        next_parameter = next(parameters, None)
        if not next_parameter:
            break

def set_custom_parameters(challenge: Challenge, template: RunSpecification) -> None:
    if template.parameters:
        to_remove = []
        print("Modifying already set parameters")
        for name, value in template.parameters.items():
            user_input = input(f"Enter new value for '{name}', or <Enter> to remove it. (Current value - '{value}'): ")
            if not user_input:
                to_remove.append(name)
                print(f"Removed custom parameter '{name}'.")
            else:
                template.parameters[name] = user_input
        for name in to_remove:
            del template.parameters[name]

    print("Adding new parameters (empty parameter name to end)")
    while True:
        name = input("Enter parameter name: ")
        if not name:
            break
        elif name in template.parameters:
            print(f"Parameter with the name '{name}' already exists. Ignoring...")
            continue
        else:
            value = input("Enter parameter value: ")
        template.parameters[name] = value

def view_template(challenge: Challenge, template: RunSpecification) -> None:
    print(f"{'Name: ':<37}{template.name}")
    print(f"{'Description: ':<37}{template.description}")
    print(f"{'Agent: ':<37}{template.agent_name}")
    scenario_str = "Random" if template.scenario == "Random" else challenge.scenarios.get_scenario(template.scenario).name
    print(f"{'Scenario: ':<37}{scenario_str}")
    variant_str = "Random" if template.variant == -1 else str(template.variant)
    print(f"{'Variant: ':<37}{variant_str}")
    print(f"{'Maximum number of episodes: ':<37}{template.max_episodes}")
    print(f"{'Maximum time per episode: ':<37}{template.max_time}")
    print(f"{'Maximum actions per episode: ':<37}{template.max_actions}")
    print(f"{'Maximum number of parallel episodes: ':<37}{template.max_parallel}")
    print(f"Custom parameters: ", end="")
    if not template.parameters:
        print("                  None")
    else:
        print("")
        for name, value in template.parameters.items():
            print(f"    {name}:{value}")

def modify_template(challenge: Challenge, template: RunSpecification) -> RunSpecification:
    old_template = RunSpecification.copy(template)
    old_template.name = template.name

    if template.name:
        menu_title = f"Modifying a run template '{template.name}'"
    else:
        menu_title = "Creating a new run template"

    while True:
        choice = menu(menu_title,
                      ["Set name", "Set description", "Set agent", "Set scenario(s)", "Set variant(s)",
                              "Set run parameters", "Set custom parameters", "View template", "Save", "Back"],
                      background_color)

        if choice == "Back":
            break

        elif choice == "Set name":
            if template.name:
                print(f"Current template name: {template.name}")
            name = input("Please enter new name (or just hit enter to keep it): ")
            if name:
                template.name = name
                menu_title = f"Modifying a run template '{template.name}'"

        elif choice == "Set description":
            if template.description:
                print(f"Current template description: {template.description}")
            description = input("Please enter new description (or just hit enter to keep it): ")
            if description:
                template.description = description

        elif choice == "Set agent":
            agent_name = choose_agent(challenge)
            if agent_name:
                template.agent_name = agent_name

        elif choice == "Set scenario(s)":
            scenario = choose_scenario(challenge)
            if scenario:
                template.scenario = scenario

        elif choice == "Set variant(s)":
            variant = choose_variant(challenge, str(template.scenario))
            if variant:
                template.variant = variant

        elif choice == "Set run parameters":
            set_run_parameters(challenge, template)
            view_template(challenge, template)
            wait_for_key()

        elif choice == "Set custom parameters":
            set_custom_parameters(challenge, template)
            view_template(challenge, template)
            wait_for_key()

        elif choice == "View template":
            view_template(challenge, template)
            wait_for_key()

        elif choice == "Save":
            if not template.name:
                print("Cannot save a template without a name")
                wait_for_key()
                continue

            tmp = challenge.execution.get_run_specification(template.name)
            save = True
            if tmp:
                yes_no = menu(f"Do you want to overwrite the template '{template.name}",
                              ["Yes", "No"],
                              background_color)
                if yes_no == "No":
                    save = False

            if save:
                challenge.execution.set_run_specification(template, old_template)
                print(f"Run specification '{template.name}' saved.")
                wait_for_key()

    return template

def get_run_template(challenge: Challenge) -> RunSpecification:
    available_templates = challenge.execution.list_run_specifications()

    if not available_templates:
        print("No templates are available.")
        wait_for_key()
        return RunSpecification()

    available_templates.append("None")

    choice = menu("Select a run specification to use as a template:",
                  available_templates,
                  background_color)

    if choice == "None":
        return RunSpecification()
    else:
        return challenge.execution.get_run_specification(choice)

def new_run_specification(challenge: Challenge) -> None:
    choice = menu("Do you want to modify a saved run template?",
                  ["Yes", "No", "Back"],
                  background_color)

    if choice == "Back":
        return
    elif choice == "Yes":
        run_template = get_run_template(challenge)
        if not run_template.name:
            template = RunSpecification()
        else:
            template = RunSpecification.copy(run_template)
    else:
        template = RunSpecification()

    modify_template(challenge, template)

def edit_run_specification(challenge: Challenge) -> None:
    spec = get_run_template(challenge)
    if not spec.name:
        return
    else:
        modify_template(challenge, spec)

def new_run(challenge: Challenge) -> None:
    available_runs = challenge.execution.list_run_specifications()
    available_runs.append("Back")
    while True:
        choice = menu("Which run would you like to start?",
                      available_runs,
                      background_color)

        if choice == "Back":
            return

        run_spec = challenge.execution.get_run_specification(choice)
        choice_2 = menu(f"You have selected run '{choice}' on scenario '{run_spec.scenario}' with agent '{run_spec.agent_name}. Is this correct?",
                        ["Yes", "No", "Back"],
                        background_color)

        if choice_2 == "Back":
            continue
        elif choice_2 == "No":
            break
        else:
            challenge.execution.execute(run_spec)
            break


def show_run_status(run: Run):
    print(f"Run id: {run.id}")
    print(f"Status: {run.status}")
    print(f"Episodes:")
    print(f"  - All     : {sorted(run.episodes.keys())}")
    print(f"  - Running : {sorted(run.running)}")
    print(f"  - Finished: {sorted(run.successful)}")
    print(f"  - Error   : {sorted(run.error)}")
    wait_for_key()


def status(challenge: Challenge):
    categorized_runs = {
        RunStatus.INIT: [],
        RunStatus.RUNNING: [],
        RunStatus.FINISHED: [],
        RunStatus.ERROR: []
    }

    all_runs = challenge.execution.get_runs()
    for run in all_runs:
        categorized_runs[run[1]].append(run[0])

    print("Status of runs (status: IDs)\n")
    print(f"{'Initialized: ':<14}{"None" if not categorized_runs[RunStatus.INIT] else categorized_runs[RunStatus.INIT]}")
    print(f"{'Running: ':<14}{"None" if not categorized_runs[RunStatus.RUNNING] else categorized_runs[RunStatus.RUNNING]}")
    print(f"{'Finished: ':<14}{"None" if not categorized_runs[RunStatus.FINISHED] else categorized_runs[RunStatus.FINISHED]}")
    print(f"{'Error: ':<14}{"None" if not categorized_runs[RunStatus.ERROR] else categorized_runs[RunStatus.ERROR]}")
    print("")

    while True:
        choice = input("Do you want to view a detailed status of any run (just press enter to return back)? ")
        if not choice:
            break

        try:
            run_id = int(choice)
        except:
            print(f"Selected value '{choice}' does not convert to integral run id. Please, try again.")
            continue

        if run_id not in [x[0] for x in all_runs]:
            print(f"Selected run id '{run_id}' not among the runs. Please, try again.")
            continue

        show_run_status(challenge.execution.get_run(run_id))
        break


def evaluation(challenge: Challenge):
    print("Evaluation is currently disabled")
    wait_for_key()

menu_execution = {
    "back": menu_top_level,
    "menu": [
        "Execution of training and evaluation runs",
        {
            "New run specification": new_run_specification,
            "Edit run specification": edit_run_specification,
            "New run": new_run,
            "Run status": status,
            "New evaluation": evaluation,
            "Back": None
        },
        background_color
]}

menus["Packages/Agents"] = menu_packages
menus["Scenarios"] = menu_scenarios
menus["Execution"] = menu_execution

def run():
    try:
        challenge = Challenge()
    except ValueError as e:
        path = e.args[1]
        choice = menu(("The challenge environment does not appear to be initiated in the current running directory.", str(path), "Would you like to..."),
                      ["Init the challenge environment here", "Set the path to the challenge environment", "Exit and run this from elsewhere"],
                      background_color)

        if choice.startswith("Init"):
            Challenge.init_environment()
            challenge = Challenge()
        elif choice.startswith("Exit"):
            return
        else:
            path_set_correctly = False
            while not path_set_correctly:
                path_str = input("Please, provide the path to the environment: ")
                path = Path(path_str)
                if not Challenge.check_init_state(path):
                    print("Provided directory is not a correct challenge environment.")
                else:
                    path_set_correctly = True
                    challenge = Challenge(str(path))

    next_menu = menu_top_level

    while True:
        menu_spec = next_menu["menu"]
        choice = menu(menu_spec[0], list(menu_spec[1].keys()), menu_spec[2])
        if choice == "Back":
            next_menu = next_menu["back"]
            continue
        elif choice == "Exit":
            all_runs = challenge.execution.get_runs()
            if RunStatus.RUNNING in [x[1] for x in all_runs]:
                choice = menu("Some runs have not finished. If you exit, it will terminate them. Do you really want to exit?",
                              ["Yes", "No"], background_color)
                if choice == "No":
                    continue
                else:
                    current_process = psutil.Process()
                    children_process = current_process.children(recursive=True)
                    for p in children_process:
                        try:
                            p.send_signal(signal.SIGTERM)
                        except psutil.NoSuchProcess:
                            pass
                    break
            break
        else:
            selected = menu_spec[1][choice]
            if not selected:
                next_menu = menus[choice]
            elif isinstance(selected, Callable):
                selected(challenge)


if __name__ == "__main__":
    run()
