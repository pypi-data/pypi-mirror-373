from concurrent.futures import ThreadPoolExecutor


from pilot.control.control_interface import ControlInterface
from pilot.unit.impl.base_unit import BaseUnit
from pilot.config.config_reader import ConfigReader


class BaseController(ControlInterface):

    def __init__(self):
        pass

    def _init_unit(self):
        return BaseUnit()

    def run(self,configfile: str = None):
        import time
        config_dto = ConfigReader(configfile).get_dto()
        unit = self._init_unit()
        unit.config_dto = config_dto

        steps = config_dto.steps
        runsteps = config_dto.runsteps

        def run_step(index):
            if index >= len(steps):
                return
            step = steps[index]
            if step in config_dto.skipsteps:
                run_step(index + 1)
                return

            if len(runsteps) == 0:
                pass
            elif len(runsteps) != 0 and step not in runsteps:
                run_step(index + 1)
                return

            max_workers = 1
            if step in config_dto.multisteps:
                max_workers = config_dto.threads

            def step_worker():
                unit.run(index)

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for _ in range(max_workers):
                    futures.append(executor.submit(step_worker))
                    time.sleep(0.5)
                for future in futures:
                    future.result()
                run_step(index + 1)

        run_step(0)