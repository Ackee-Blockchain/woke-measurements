import csv
import json
import subprocess
import toml
import pathlib

CONFIG_FILE = "test_tests_config.json"
TEST_RUNS = 10
RESULTS_FILE = "test_results.csv"
WOKE_TOML = "woke.toml"


def update_woke_toml(network, project_path):
    woke_toml_path = pathlib.Path(project_path).joinpath(WOKE_TOML)
    woke_data = toml.load(woke_toml_path)
    woke_data["testing"]["cmd"] = network
    with open(woke_toml_path, "w") as woke_file:
        toml.dump(woke_data, woke_file)


def update_hardhat_config(project_path, mode):
    config_path = pathlib.Path(project_path).joinpath("hardhat.config.ts")
    config = config_path.read_text()
    if mode == 'disable':
        config = config.replace('import "@foundry-rs/hardhat-anvil";', '//import "@foundry-rs/hardhat-anvil";')
        config = config.replace('import "@nomiclabs/hardhat-ganache";', '//import "@nomiclabs/hardhat-ganache";')
    if mode == 'enable':
        config = config.replace('//import "@foundry-rs/hardhat-anvil";', 'import "@foundry-rs/hardhat-anvil";')
        config = config.replace('//import "@nomiclabs/hardhat-ganache";', 'import "@nomiclabs/hardhat-ganache";')
    config_path.write_text(config)


def run_tests(python_venv_path, command, network, framework, project_path):
    print(f"Running {framework} {network} tests...")
    command_with_network = f"{command} {network}"
    if framework == "woke":
        update_woke_toml(network, project_path)
        command_with_network = f"{command}"
    if framework == "hardhat" and network in ["anvil", "ganache"]:
        update_hardhat_config(project_path, 'enable')

    if python_venv_path:
        source_command = f"source {python_venv_path}/bin/activate" if python_venv_path else ""
        full_command = f"cd {project_path} && {source_command} && time {command_with_network}"
    else:
        full_command = f"cd {project_path} && time {command_with_network}"

    # Execute the command and capture the output
    result = subprocess.run(full_command, shell=True, executable="/bin/bash", check=True, capture_output=True,
                            text=True)

    # Extract the elapsed time from the output
    stderr_res = result.stderr.splitlines()
    elapsed_time = None
    for line in stderr_res:
        if line.startswith("real"):
            time_parts = line.split()[1].split("m")
            elapsed_time = float(time_parts[0]) * 60 + float(time_parts[1][:-1])  # Convert time to seconds
            break

    if framework == "hardhat" and network in ["anvil", "ganache"]:
        update_hardhat_config(project_path, 'disable')

    return elapsed_time


def write_data(framework, network, time):
    with open(RESULTS_FILE, "a", newline="") as csvfile:
        result_writer = csv.writer(
            csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        result_writer.writerow([framework, network, time])


def test_configuration(configuration):
    # Run the one-time compile command
    compile_command = f"cd {configuration['project_path']} && {configuration['compile_command']}"
    if 'python_venv_path' in configuration:
        compile_command = f"cd {configuration['project_path']} && source {configuration['python_venv_path']}/bin/activate && {configuration['compile_command']}"

    subprocess.Popen(
        compile_command,
        shell=True,
        executable="/bin/bash",
    ).wait()

    for network in configuration["networks"]:
        sum_time = 0
        venv_path = None
        if "python_venv_path" in configuration:
            venv_path = configuration["python_venv_path"]

        run_tests(
            venv_path,
            configuration["command"],
            network,
            configuration["framework"],
            configuration["project_path"],
        )  # dry run
        for _ in range(TEST_RUNS):
            sum_time += run_tests(
                venv_path,
                configuration["command"],
                network,
                configuration["framework"],
                configuration["project_path"],
            )
        write_data(
            framework=configuration["framework"],
            network=network,
            time=sum_time / TEST_RUNS,
        )


def main():
    with open(CONFIG_FILE, "r") as config_file:
        configurations = json.load(config_file)
    for configuration in configurations:
        test_configuration(configuration)


if __name__ == "__main__":
    main()
