import logging
import os

from ec_tools_cli.common.utils.logger_utils import setup_logger
from ec_tools_cli.vault.encryption import Encryption
from ec_tools_cli.vault.parameter.args import get_args
from ec_tools_cli.vault.parameter.parameter import Method, Parameter
from ec_tools_cli.vault.parameter.process import ParameterProcessor


class Processor:
    _encryption: Encryption
    _parameter_processor: ParameterProcessor
    _log: logging.Logger

    def __init__(self, parameter: Parameter, log: logging.Logger):
        self._encryption = Encryption(db_path=parameter.db_path)
        self._log = log
        self._parameter_processor = ParameterProcessor(log)

    def __call__(self, parameter: Parameter):
        function_map = {
            Method.LIST: self.list,
            Method.INSERT: self.insert,
            Method.GET: self.get,
            Method.DELETE: self.delete,
        }
        if parameter.method in function_map:
            function_map[parameter.method](parameter)
            self._log.info("Done")
            self._log.info("-" * 32)
            self._log.info("")
            return
        self._log.error(f"Error: Unknown method {parameter.method}")
        exit(-1)

    def list(self, parameter: Parameter):
        items = self._encryption.list_keys()
        self._log.info(f"Stored items ({len(items)}):")
        for item in items:
            self._log.info(f"  * {item}")
        self._log.info(f'Use `vault-cli -db "{parameter.db_path}" get -k <key> -p <password>` to retrieve an item.')

    def insert(self, parameter: Parameter):
        password = self._parameter_processor.verify_password(parameter.password)
        key = self._parameter_processor.verify_key(parameter.key)
        value = self._parameter_processor.verify_value(self._parameter_processor.get_value(parameter).strip())
        self._log.info(f'Inserting "{key}"...')
        try:
            self._encryption.insert(password, key, value)
        except Exception as e:
            self._log.error(f"Insert failed with {e}")
            exit(-1)

    def get(self, parameter: Parameter):
        password = self._parameter_processor.verify_password(parameter.password)
        if parameter.key is None:
            self.list(parameter)
        input_key = self._parameter_processor.verify_key(parameter.key)
        keys = self._encryption.list_keys() if input_key == "__all__" else [input_key]
        for key in keys:
            self._log.info(f'Reading "{key}"...')
            try:
                value = self._encryption.get(password, key)
                if not value:
                    self._log.error(f"Value is not exist!")
                    exit(-1)
                if parameter.output:
                    with open(parameter.output, "wb") as wf:
                        wf.write(value)
                    self._log.info(f"Data is written to {parameter.output}")
                else:
                    try:
                        print(value.decode("utf-8"))
                    except:
                        print(value)
            except Exception as e:
                self._log.error(f"Read failed with {e}")
                exit(-1)

    def delete(self, parameter: Parameter):
        key = self._parameter_processor.verify_key(parameter.key)
        self._log.info(f'Deleting "{key}"...')
        try:
            self._encryption.delete(key)
        except Exception as e:
            self._log.error(f"Delete failed with {e}")
            exit(-1)


def main():
    args = get_args()
    logger = setup_logger("Vault", args.silent)
    dir_path = os.path.dirname(os.path.expanduser(args.db_path))
    if not os.path.exists(dir_path):
        logger.info("Creating directory: " + dir_path)
        os.makedirs(dir_path, exist_ok=True)
    processor = Processor(args, logger)
    processor(args)


if __name__ == "__main__":
    main()
