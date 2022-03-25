from dataclasses import dataclass

from .return_codes import ReturnCodes


@dataclass
class CLIResponse:
    status: ReturnCodes
    output: str
    error: str
