from cashd.db import DB_ENGINE
from cashd.prefs import BackupPrefsHandler

import sqlite3
from os import path, rename
from pathlib import Path
from datetime import datetime
import shutil
import configparser
import logging


####################
# GLOBAL VARS
####################

SCRIPT_PATH = Path(path.split(path.realpath(__file__))[0])
BACKUP_PATH = Path(SCRIPT_PATH, "data", "backup")
CONFIG_FILE = Path(SCRIPT_PATH, "configs", "backup.ini")
LOG_FILE = Path(SCRIPT_PATH, "logs", "backup.log")
DB_FILE = Path(SCRIPT_PATH, "data", "database.db")

BACKUP_PATH.mkdir(exist_ok=True, parents=True)


settings = BackupPrefsHandler()

logger = logging.getLogger("cashd.backup")
logger.setLevel(logging.DEBUG)
logger.propagate = False

log_fmt = logging.Formatter("%(asctime)s :: %(levelname)s %(message)s")
log_handler = logging.FileHandler(LOG_FILE)
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(log_fmt)

logger.addHandler(log_handler)


####################
# UTILS
####################


def copy_file(source_path, target_dir, _raise: bool = False):
    logger.debug("function call: copy_file")
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
    try:
        filename = f"backup_{now}.db"
        shutil.copyfile(source_path, Path(target_dir, filename))
        logger.info(f"Copia de '{source_path}' criada em '{target_dir}'")
    except FileNotFoundError as xpt:
        logger.error(f"Erro realizando copia: {xpt}.", exc_info=1)
        if _raise:
            raise xpt


def rename_on_db_folder(current: str, new: str, _raise: bool = False):
    """
    Renomeia um arquivo na mesma pasta em que `DB_FILE` se encontra, se a
    operacao falhar porque o arquivo esta em uso, faz uma copia com o novo
    nome em vez de renomear.

    Levanta o ultimo erro que recebeu se ambas as operacoes falharem.
    """
    logger.debug("function call: rename_on_db_folder")
    current, new = str(current), str(new)

    db_folder = Path(DB_FILE).parent
    path_to_current = path.join(db_folder, current)
    path_to_new = path.join(db_folder, new)

    try:
        rename(path_to_current, path_to_new)
        logger.info(f"{path_to_current} renomeado como {path_to_new}")
    except WindowsError:
        shutil.copy(path_to_current, path_to_new)
    except Exception as xpt:
        logger.error(f"Erro renomeando {path_to_current}: {xpt}", exc_info=1)
        if _raise:
            raise xpt


def check_sqlite(file: str, _raise: bool = False):
    """Checa se o full path para o arquivo `file` representa um banco de dados sqlite."""
    logger.debug("function call: check_sqlite")

    if not path.isfile(file):
        xpt = FileExistsError(f"Arquivo {file} invalido.")
        logger.error(str(xpt))
        if _raise:
            raise xpt

    con = sqlite3.connect(file)
    cursor = con.cursor()
    stmt = f"PRAGMA schema_version;"
    try:
        _ = cursor.execute(stmt).fetchone()
        if _ == (0,):
            raise sqlite3.DatabaseError()
        return True
    except sqlite3.DatabaseError:
        return False
    except Exception as xpt:
        logger.critical(f"Erro inesperado validando {file}", exc_info=1)
        if _raise:
            raise xpt
    finally:
        con.close()


def read_db_size(file_path: str = DB_FILE) -> int:
    logger.debug("function call: read_db_size")
    try:
        return path.getsize(file_path)
    except Exception as xpt:
        logger.error(f"Erro lendo tamanho do arquivo: {str(xpt)}")
        return


####################
# LEITURAS
####################


def read_last_recorded_size(config_file: str = CONFIG_FILE):
    logger.debug("function call: read_last_recorded_size")
    config = configparser.ConfigParser()
    config.read(config_file)

    if "file_sizes" in config:
        return config["file_sizes"].getint("dbsize", fallback=None)
    return 0


####################
# ESCRITAS
####################


def write_current_size(
    current_size: int = read_db_size(), settings: BackupPrefsHandler = settings
) -> None:
    """Writes current database size to `backup.ini`"""
    logger.debug("function call: write_current_size")
    settings.write_dbsize(current_size)


def write_add_backup_place(path: str, settings: BackupPrefsHandler = settings) -> None:
    """Inclui o input `path` na opcao 'backup_places' em `backup.ini`"""
    logger.debug("function call: write_add_backup_place")
    settings.add_backup_place(path)


def write_rm_backup_place(idx: int, settings: BackupPrefsHandler = settings) -> None:
    """Retira o `idx`-esimo item da lista 'backup_places' em `backup.ini`"""
    logger.debug("function call: write_rm_backup_place")
    settings.rm_backup_place(idx)


def load(file: str, _raise: bool = False) -> None:
    """
    Checa se `file` se trata de um banco de dados SQLite valido, e entao o
    carrega como o banco de dados atual no Cashd.

    Se um banco de dados ja estiver presente, vai renomea-lo para um nome
    nao usado pelo Cashd nem por outros arquivos na pasta e o mantera no
    diretorio.
    """
    logger.debug("function call: load")
    db_is_present = path.isfile(DB_FILE)
    file_is_valid = check_sqlite(file)

    if not file_is_valid:
        msg = f"Impossivel carregar arquivo nao SQLite {file}"
        logger.error(msg)
        if _raise:
            raise OSError(msg)

    if db_is_present:
        now = datetime.now()
        dbfilename = path.split(DB_FILE)[1]
        stashfilename = f"stashed{now}.db".replace(":", "-")
        rename_on_db_folder(dbfilename, stashfilename)

    try:
        shutil.copyfile(file, DB_FILE)
    except shutil.SameFileError:
        pass


def run(
    force: bool = False, settings: BackupPrefsHandler = settings, _raise: bool = False
) -> None:
    """
    Vai fazer a copia do arquivo de banco de dados para a pasta local de backup
    e para as pastas listadas na opcao 'backup_places' em `backup.ini`.

    Usar `force = False` so vai fazer uma copia se o arquivo aumentou de
    tamanho, comparado com o registrado em 'file_sizes'.
    """
    backup_places = settings.read_backup_places()
    error_was_raised = False

    current_size = read_db_size()
    previous_size = settings.read_dbsize()
    if not previous_size:
        previous_size = 0

    if not force:
        if current_size <= previous_size:
            return
    settings.write_dbsize(current_size)

    try:
        backup_places = [i for i in [BACKUP_PATH] + backup_places if i != ""]
        for place in backup_places:
            try:
                if path.exists(place):
                    copy_file(DB_FILE, place, _raise=_raise)
                else:
                    raise NotADirectoryError(f"{place} nao existe")
            except Exception as xpt:
                logger.error(f"Nao foi possivel salvar em '{place}': {xpt}", exc_info=1)
                if _raise:
                    error_was_raised = True
    except Exception as xpt:
        logger.error(f"Erro inesperado durante o backup: {xpt}", exc_info=1)
    finally:
        if error_was_raised:
            raise NotADirectoryError(
                f"Erro em alguma etapa do backup, verifique o log: {LOG_FILE}"
            )
