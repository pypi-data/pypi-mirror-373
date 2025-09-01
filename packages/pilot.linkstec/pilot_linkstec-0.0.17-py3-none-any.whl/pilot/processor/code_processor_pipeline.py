from typing import List

from pilot.processor.code_processor import CodeProcessor


class CodeProcessorPipeline:
    def __init__(self, processors: List[CodeProcessor]):
        self.processors = processors

    def run(self, lines: List[str]) -> List[str]:
        result = lines
        for processor in self.processors:
            result = processor.process(result)
        return result
