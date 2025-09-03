from dataclasses import dataclass


@dataclass(frozen=True)
class CommandLineExecution:
    test_suite_path: str = '-t'
    concurrency: str = '-c'
    test_result_path: str = '-r'
    test_tags: str = '-h'
    env_path: str = '-e'
    test_data_path: str = '-d'


command_line_execution = CommandLineExecution()
