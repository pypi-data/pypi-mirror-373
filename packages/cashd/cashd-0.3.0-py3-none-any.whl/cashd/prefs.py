from os import path, makedirs
from typing import Literal
import configparser
import logging


SCRIPT_PATH = path.split(path.realpath(__file__))[0]
CONFIG_PATH = path.join(SCRIPT_PATH, "configs")
LOG_PATH = path.join(SCRIPT_PATH, "logs")

PREFS_CONFIG_FILE = path.join(CONFIG_PATH, "prefs.ini")
BACKUP_CONFIG_FILE = path.join(CONFIG_PATH, "backup.ini")
LOG_FILE = path.join(LOG_PATH, "prefs.log")
DB_FILE = path.join(SCRIPT_PATH, "data", "database.db")

for dirpath in [LOG_PATH, CONFIG_PATH]:
    makedirs(dirpath, exist_ok=True)


class SettingsHandler:
    """
    Valores de configuração usados:

    ### prefs.ini

    `[default]`
    - last_transacs_limit: `int`
    - highest_balaces_limit: `int`
    - main_state: `str`
    - main_city: `str`

    ### backup.ini

    `[default]`
    - backup_on_exit: `bool`
    - backup_places: `list`

    `[data]`
    - dbsize: `int`
    """

    def __init__(self, configname):
        self.config_file = path.join(CONFIG_PATH, f"{configname}.ini")
        self.log_file = path.join(LOG_PATH, f"{configname}.log")

        # config parser
        self.conf = configparser.ConfigParser()
        self.conf.read(self.config_file, "iso 8859-1")
        try:
            self.conf.add_section("default")
        except configparser.DuplicateSectionError:
            pass

        # logger
        self.logger = logging.getLogger(f"cashd.{__name__}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        log_fmt = logging.Formatter("%(asctime)s :: %(levelname)s %(message)s")
        log_handler = logging.FileHandler(LOG_FILE)
        log_handler.setLevel(logging.DEBUG)
        log_handler.setFormatter(log_fmt)
        self.logger.addHandler(log_handler)

        # create files, if not exist
        for file in [self.config_file, self.log_file]:
            makedirs(path.split(file)[0], exist_ok=True)
            if not path.isfile(file):
                with open(file=file, mode="a"):
                    pass

    def parse_list_from_config(self, string: str) -> list[str]:
        """
        Transforma uma config com multiplos itens uma uma lista de strings
        do python.
        """
        string = string.replace("[", "").replace("]", "")
        list_of_items = string.split(",")
        return [i.strip() for i in list_of_items if i.strip() != ""]

    def parse_list_to_config(self, list_: list[str]) -> str:
        """
        Transforma uma lista de strings do python em uma config (str) com mais
        de um item.
        """
        string_list = (
            str(list_).replace("[", "[\n\t").replace(", ", ",\n\t").replace("'", "")
        )
        return string_list.replace("\\\\", "\\")

    def _write(self, sect: str, key: str, val: str):
        """Escreve a combinacao de `key` e `val` na seção `sect`"""
        try:
            if not self.conf.has_section(sect):
                self.conf.add_section(sect)

            self.conf.set(sect, key, val)
            with open(self.config_file, "w") as newconfig:
                self.conf.write(newconfig)
            self.conf.read(self.config_file, "iso 8859-1")
            self.logger.info(
                f"Valor atualizado em {self.config_file}: [{sect}] {key} = {val}"
            )

        except Exception as xpt:
            self.logger.error(f"Erro escrevendo [{sect}] {key}={val}: {str(xpt)}")
            raise xpt

    def _read(
        self,
        sect: str,
        key: str,
        convert_to: Literal[None, "bool", "int", "list"] = None,
    ):
        try:
            if not convert_to:
                return self.conf[sect][key]
            elif convert_to == "bool":
                return self.conf.getboolean(sect, key)
            elif convert_to == "int":
                return self.conf.getint(sect, key)
            elif convert_to == "list":
                return self.parse_list_from_config(self.conf.get(sect, key))

        except KeyError:
            return None
        except configparser.NoSectionError:
            return None
        except configparser.NoOptionError:
            return None

    def _add_to_list(self, sect: str, key: str, val: str):
        current_list = self.parse_list_from_config(self.conf[sect][key])
        if val in current_list:
            self.logger.warning(
                f"{val} não foi adicionado à [{sect}] {key}, item já presente."
            )
            return
        new_list = current_list + [val]

        self.conf.set(sect, key, self.parse_list_to_config(new_list))
        with open(self.config_file, "w") as newconfig:
            self.conf.write(newconfig)
        self.conf.read(self.config_file, "iso 8859-1")

    def _rm_from_list(self, sect: str, key: str, idx: int):
        """Retira o `idx`-esimo item da lista, não faz nada se `idx` for inválido."""
        try:
            idx = int(idx)
        except ValueError:
            return

        current_list = self.parse_list_from_config(self.conf[sect][key])
        n = len(current_list)

        if (idx + 1) > n:
            self.logger.error(f"{idx} fora dos limites, deve ser menor que {n}")

        _ = current_list.pop(idx)
        self.conf.set(sect, key, self.parse_list_to_config(current_list))
        with open(self.config_file, "w") as newconfig:
            self.conf.write(newconfig)
        self.conf.read(self.config_file, "iso 8859-1")


class PreferencesHandler(SettingsHandler):
    def __init__(self, configname="prefs"):
        super().__init__(configname)

        # set defaults
        if self.read_last_transacs_limit() is None:
            self.write_last_transacs_limit(1000)

        if self.read_highest_balaces_limit() is None:
            self.write_highest_balaces_limit(10)

        if self.read_main_state() is None:
            self.write_main_state("AC")

        if self.read_main_city() is None:
            self.write_main_city("")

    def write_last_transacs_limit(self, val: int):
        """
        Controla um limite de transações a ser exibidas na tabela
        'Últimas transações'.
        """
        val = int(val)
        self._write("default", "last_transacs_limit", str(val))

    def write_highest_balaces_limit(self, val: str):
        """
        Controla um limite de contas a ser exibidas na tabela
        'Maiores saldos'.
        """
        val = int(val)
        self._write("default", "highest_balaces_limit", str(val))

    def write_main_state(self, val: str):
        """Controla o UF padrão exibido no formulário 'Criar conta'"""
        self._write("default", "main_state", val)

    def write_main_city(self, val: str):
        """Controla a cidade padrão exibida no formulário 'Criar conta'"""
        self._write("default", "main_city", val)

    def read_last_transacs_limit(self) -> int | None:
        return self._read("default", "last_transacs_limit", convert_to="int")

    def read_highest_balaces_limit(self) -> int | None:
        return self._read("default", "highest_balaces_limit", convert_to="int")

    def read_main_state(self) -> str | None:
        return self._read("default", "main_state")

    def read_main_city(self) -> str | None:
        return self._read("default", "main_city")


class BackupPrefsHandler(SettingsHandler):
    def __init__(self, configname="backup"):
        super().__init__(configname)

        if self.read_backup_places() is None:
            self._write("default", "backup_places", "[]")

        if self.read_backup_on_exit() is None:
            self._write("default", "backup_on_exit", "true")

    def read_backup_places(self) -> list | None:
        return self._read("default", "backup_places", convert_to="list")

    def read_backup_on_exit(self) -> bool | None:
        return self._read("default", "backup_on_exit", convert_to="bool")

    def read_dbsize(self) -> int | None:
        return self._read("data", "dbsize", convert_to="int")

    def write_dbsize(self, val: int) -> None:
        val = int(val)
        self._write("data", "dbsize", str(val))

    def write_backup_on_exit(self, val: bool) -> None:
        val = str(val).lower()
        self._write("default", "backup_on_exit", val)

    def add_backup_place(self, place: str) -> None:
        self._add_to_list("default", "backup_places", place)

    def rm_backup_place(self, idx: int) -> None:
        self._rm_from_list("default", "backup_places", idx)


###########################
# init and write defaults #
###########################

settings = PreferencesHandler()
