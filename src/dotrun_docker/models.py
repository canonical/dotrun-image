# Standard library
import json
import os
import shutil
import subprocess
import sys
import time
from glob import glob

# Packages
from dotenv import load_dotenv
from termcolor import cprint

# Local
from dotrun_docker.file_helpers import file_md5


class State:
    def __init__(self, filepath):
        """
        Manage a JSON object in a file,
        as you would a dictionary
        """

        self.filepath = filepath

    def __getitem__(self, key):
        if not os.path.isfile(self.filepath):
            return None

        with open(self.filepath) as state_file:
            return json.load(state_file).get(key)

    def __setitem__(self, key, value):
        if os.path.isfile(self.filepath):
            with open(self.filepath) as state_file:
                state = json.load(state_file)
        else:
            state = {}

        state[key] = value

        with open(self.filepath, "w") as state_file:
            return json.dump(state, state_file)

    def clean(self):
        with open(self.filepath, "r") as state_file:
            state = json.load(state_file)
        with open(self.filepath, "w") as state_file:
            # keep project version preferences
            state = {
                key: value
                for key, value in state.items()
                if key.endswith("_version")
            }
            json.dump(state, state_file)


class Logger:
    def note(self, note):
        cprint(f"- {note}", "magenta")

    def error(self, error):
        cprint(f"\n= {error} =\n", "red")

    def step(self, title, aside=None):
        if aside:
            cprint(f"\n[ {title} ]", "cyan", end="")
            cprint(f" ( {aside} )\n", "magenta", attrs=["dark"])
        else:
            cprint(f"\n[ {title} ]\n", "cyan")


class Project:
    """
    A class for performing operations on a project directory
    """

    def __init__(self, path, env_extra):
        self.path = path
        self.log = Logger()
        self.statefile_path = f"{self.path}/.dotrun.json"
        self.state = State(self.statefile_path)
        self.env_extra = {}
        self.pyenv_dir = ".venv"
        self.pyenv_path = f"{self.path}/{self.pyenv_dir}"
        self._background_processes = []

        # Load the env file if it exists
        load_dotenv(dotenv_path=f"{self.path}/.env")
        load_dotenv(dotenv_path=f"{self.path}/.env.local", override=True)
        self.env = os.environ

        # Check all env values are string format
        for key, value in env_extra.items():
            self.env[key] = str(value)

    def is_yarn(self):
        """
        Check if the project is set up for NPM or Yarn.
        """

        return os.path.isfile(os.path.join(f"{self.path}/yarn.lock"))

    def get_package_manager(self):
        """
        Get the package manager that is being used in this project.
        """

        return "yarn" if self.is_yarn() else "npm"
    
    def has_script(self, script_name):
        """
        Check if the project's package.json contains the named script
        """

        with open(f"{self.path}/package.json") as json_file:
            return script_name in json.load(json_file).get("scripts", {})

    def install(self, force=False):
        """
        Install dependencies from requirements.txt and package.json,
        if there have been any changes detected
        """

        self._install_yarn_dependencies(force=force)
        self._install_python_dependencies(force=force)

    def clean(self):
        """
        Clean all dotrun data from project
        """

        self.yarn_run("clean", exit_on_error=False)

        if os.path.isfile(self.statefile_path):
            self.log.step("Removing `.dotrun.json` state file")
            self.state.clean()

        if os.path.isdir("node_modules"):
            self.log.step("Removing `node_modules`")
            shutil.rmtree("node_modules")

        if os.path.isdir(self.pyenv_path):
            self._clean_python_env()

    def _clean_python_env(self):
        self.log.step("Removing `.venv` python environment")
        shutil.rmtree(self.pyenv_path)

    def yarn_run(self, script_name, arguments=[], exit_on_error=True):
        """
        Run `yarn run {script_name}`, but check if the script exists first
        """

        error = ""

        if not os.path.isfile(os.path.join(f"{self.path}/package.json")):
            error = f"package.json not found in {self.path}"
        else:
            with open(f"{self.path}/package.json") as json_file:
                if script_name not in json.load(json_file).get("scripts", {}):
                    error = f"'{script_name}' script not found in package.json"

        if error:
            if exit_on_error:
                self.log.error(error)
                sys.exit(1)
            else:
                self.log.note(error)
                return False

        self.exec(
            [self.get_package_manager(), "run", script_name] + arguments,
            exit_on_error=exit_on_error,
        )

    def exec(self, commands, exit_on_error=True, background=False):
        """
        Run commands in the environment
        """

        result = None

        if os.path.isfile(f"{self.pyenv_path}/bin/python3"):
            self.env["VIRTUAL_ENV"] = self.pyenv_path
            self.env["PATH"] = self.pyenv_path + "/bin:" + self.env["PATH"]
            self.env.pop("PYTHONHOME", None)
            self.log.step(
                f"$ {' '.join(commands)}",
                aside=f"virtualenv `{self.pyenv_dir}`",
            )
        else:
            self.log.step(f"$ {' '.join(commands)}")

        try:
            if background:
                # Any background process is attached to dotrun
                # they will be ended with SIGTERM when dotrun is finish
                process = subprocess.Popen(
                    commands, env=self.env, cwd=self.path
                )
                self._background_processes.append(process)
                return True

            result = subprocess.check_call(
                commands, env=self.env, cwd=self.path
            )
        except KeyboardInterrupt:
            self.log.step(f"`{' '.join(commands)}` cancelled - exiting")
            time.sleep(1)
        except subprocess.CalledProcessError as call_error:
            self.log.error(f"`{' '.join(commands)}` errored")

            if exit_on_error:
                sys.exit(call_error.returncode)

        print("")

        return result

    def terminate_background_processes(self):
        for process in self._background_processes:
            process.terminate()

    # Node dependencies

    def _get_yarn_state(self):
        """
        Save package.json, lockfile and installed dependencies state
        """

        # Get installed package versions
        with open(
            os.path.join(self.path, "package.json"), "rb"
        ) as package_json:
            package_settings = json.load(package_json)
            dependencies = package_settings.get("dependencies", {})
            dependencies.update(package_settings.get("devDependencies", {}))

        package_jsons = glob(f"{self.path}/node_modules/*/package.json")
        packages = {}

        # Read package.json dependencies
        for package_json in package_jsons:
            with open(package_json, "r") as package_contents:
                package = json.load(package_contents)
                packages[package["name"]] = package["version"]

        lock_hash = None
        if os.path.isfile(os.path.join(self.path, "yarn.lock")):
            lock_hash = file_md5(os.path.join(self.path, "yarn.lock"))
        elif os.path.isfile(os.path.join(self.path, "package-lock.json")):
            lock_hash = file_md5(os.path.join(self.path, "package-lock.json"))

        return {
            "dependencies": dependencies,
            "installed_packages": packages,
            "lockfile_hash": lock_hash,
        }

    def _install_yarn_dependencies(self, force=False):
        """
        Install yarn dependencies if anything has changed
        """

        if not os.path.isfile(os.path.join(f"{self.path}/package.json")):
            self.log.error(f"package.json not found in {self.path}")
            sys.exit(1)

        changes = False

        if not force:
            current_state = self._get_yarn_state()
            previous_state = self.state[self.get_package_manager()]
            changes = current_state != previous_state

        if changes or force:
            if changes:
                self.log.note("Yarn dependencies have changed, reinstalling")
            if force:
                self.log.note("Installing yarn dependencies (forced)")

            self.exec([self.get_package_manager(), "install"])
            self.state[self.get_package_manager()] = self._get_yarn_state()
        else:
            self.log.note("Yarn dependencies up to date")

    # Python dependencies

    def _get_python_state(self):
        """
        Save requirements.txt and installed dependencies state
        """

        package_dirs = glob(
            f"{self.pyenv_path}/lib/python*/site-packages/*.*-info"
        )
        packages = [os.path.basename(path) for path in package_dirs]

        with open(f"{self.path}/requirements.txt", "r") as requirements_file:
            requirements = requirements_file.read()

        return {"requirements": requirements, "installed_packages": packages}

    def _create_python_environment(self):
        """
        Create a Python environment using python3-venv
        """

        self.log.note(f"Creating python environment: {self.pyenv_dir}")
        custom_python_version = self.state["python_version"]
        if custom_python_version:
            # use mise en place python version
            self.exec(
                [
                    "mise",
                    "use",
                    "-g",
                    f"python@{custom_python_version}",
                ]
            )
        python_path = shutil.which("python3")
        self.exec(
            [
                python_path,
                "-m",
                "venv",
                self.pyenv_path,
            ]
        )
        self.exec(
            [
                f"{self.pyenv_path}/bin/python",
                "-m",
                "pip",
                "install",
                "--upgrade",
                "setuptools==69.5.1",
            ]
        )

    def _install_python_dependencies(self, force=False):
        """
        Install python dependencies if anything has changed
        """

        if not os.path.isfile(os.path.join(self.path, "requirements.txt")):
            self.log.note("No requirements.txt found")
            return False

        changes = False

        if not os.path.isdir(self.pyenv_path):
            self._create_python_environment()

        if not force:
            current_state = self._get_python_state()
            previous_state = self.state["python"]
            changes = current_state != previous_state

        if changes or force:
            if changes:
                self.log.note("Python dependenices have changed, reinstalling")
            if force:
                self.log.note("Installing python dependencies (forced)")

            self.exec(
                [
                    "pip3",
                    "install",
                    "--requirement",
                    "requirements.txt",
                ]
            )
            self.state["python"] = self._get_python_state()
        else:
            self.log.note("Python dependencies up to date")
