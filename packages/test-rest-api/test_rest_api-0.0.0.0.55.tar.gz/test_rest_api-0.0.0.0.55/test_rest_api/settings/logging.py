from dataclasses import dataclass


@dataclass(frozen=True)
class Logging:
    sub_point: str = '✧'
    key_val_sep: str = '➜'
    console_report: str = f"{' ' * 29}{key_val_sep}"


logging = Logging()
