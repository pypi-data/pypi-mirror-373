import configparser
import os
import inspect
from dataclasses import dataclass
from typing import List

@dataclass
class ConfigDTO:
    work_space: str
    threads: int
    project: str
    steps: list[str]
    skipsteps: list[str]
    runsteps: list[str]
    multisteps: list[str]



class ConfigReader:
    def __init__(self, filename = None):
        filepath = None
        if filename is None:
            filepath = self.find_config_path()

        if filename is not None:
            cwd = os.getcwd()
            filepath = os.path.join(cwd, 'config', filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Configuration file not found: {filepath}")

        self.config = configparser.ConfigParser()
        self.config.optionxform = str

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if not content.lstrip().startswith('['):
            content = '[DEFAULT]\n' + content
        self.config.read_string(content)

    @classmethod
    def find_config_path(cls):
        cwd = os.getcwd()
        candidate_path = os.path.join(cwd, 'config', 'control.properties')
        if os.path.exists(candidate_path):
            return candidate_path

        stack = inspect.stack()
        for frame in stack:
            caller_file = frame.filename
            caller_dir = os.path.dirname(os.path.abspath(caller_file))
            possible_path = os.path.abspath(os.path.join(caller_dir, '..', '..', 'config', 'control.properties'))
            if os.path.exists(possible_path):
                return possible_path

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        fallback_path = os.path.join(base_dir, 'config', 'control.properties')
        if os.path.exists(fallback_path):
            return fallback_path

        raise FileNotFoundError("control.properties not found in expected locations")

    def get(self, section, option, fallback=None, cast_type=str):
        try:
            if cast_type == bool:
                return self.config.getboolean(section, option)
            elif cast_type == int:
                return self.config.getint(section, option)
            elif cast_type == float:
                return self.config.getfloat(section, option)
            else:
                return self.config.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback

    def get_dto(self) -> ConfigDTO:
        input_path = self.get('DEFAULT', 'input_path', fallback='.')
        work_space = self.get('DEFAULT', 'work_space', fallback='.')
        threads = int(self.get('DEFAULT', 'threads', fallback=1))
        project = self.get('DEFAULT', 'project', fallback='')
        steps_str = self.get('DEFAULT', 'steps', fallback='')
        steps = [s.strip() for s in steps_str.split(',')] if steps_str else []
        skipsteps_str = self.get('DEFAULT', 'skipsteps', fallback='')
        skipsteps = [s.strip() for s in skipsteps_str.split(',')] if skipsteps_str else []
        runsteps_str = self.get('DEFAULT', 'runsteps', fallback='')
        runsteps = [s.strip() for s in runsteps_str.split(',')] if runsteps_str else []
        multisteps_str = self.get('DEFAULT', 'multisteps', fallback='')
        multisteps = [s.strip() for s in multisteps_str.split(',')] if multisteps_str else []

        return ConfigDTO(
            work_space=work_space,
            threads=threads,
            project=project,
            steps=steps,
            skipsteps=skipsteps,
            runsteps=runsteps,
            multisteps=multisteps
        )