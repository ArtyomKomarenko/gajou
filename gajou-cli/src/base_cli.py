import logging
import time
from subprocess import PIPE, Popen

from .cli_response import CLIResponse
from .return_codes import ReturnCodes


class BaseCLI:
    def __init__(self, name, custom_path, allure=None):
        self.name = name
        self.path = custom_path
        self.allure = allure
        self.logger = logging.getLogger(__name__)

    def _log_request(self, command, arguments):
        rq_msg = f'INPUT: {self.name} {command or ""}'
        if arguments:
            rq_msg += f' {" ".join(arguments)}'
        self.logger.info(rq_msg)
        if self.allure:
            self.allure.attach(rq_msg, 'INPUT', attachment_type=self.allure.attachment_type.TEXT)

    def _log_response(self, process, output, error, start_time, end_time):
        rs_msg = f'OUTPUT (code {process.returncode}, elapsed time {"{0:.2f}".format(end_time - start_time)}s):'
        rs_msg = f'{rs_msg}\n{output or error or "<EMPTY MESSAGE>"}'
        self.logger.info(rs_msg)
        if self.allure:
            self.allure.attach(rs_msg, 'OUTPUT', attachment_type=self.allure.attachment_type.TEXT)

    def do(self, command: str, *args) -> CLIResponse:
        _args = list(filter(None.__ne__, args)) if args and args != (None,) else []
        self._log_request(command, _args)
        start_time = time.time()

        _cmd = [f'{self.path}{self.name}',
                *command.split(' '),
                *[arg for arg_group in _args for arg in arg_group.split(' ')]]
        process = Popen(_cmd, stdout=PIPE, stderr=PIPE)
        output, error = (_bytes.decode().strip() for _bytes in process.communicate())

        end_time = time.time()
        self._log_response(process, output, error, start_time, end_time)

        return CLIResponse(status=ReturnCodes(process.returncode), output=output, error=error)
