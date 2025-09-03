import pytest
from os import path, unlink
from tempfile import (
    TemporaryFile,
    TemporaryDirectory
)
from cashd.prefs import (
    PREFS_CONFIG_FILE,
    SettingsHandler,
    PreferencesHandler,
    BackupPrefsHandler
)


CONFIGS_DIR = path.split(PREFS_CONFIG_FILE)[0]

SETTINGS_TEMPFILE = TemporaryFile(dir=CONFIGS_DIR)
PREFERENCES_TEMPFILE = TemporaryFile(dir=CONFIGS_DIR)
BACKUPPREFS_TEMPFILE = TemporaryFile(dir=CONFIGS_DIR)

settings_handler = SettingsHandler(path.split(SETTINGS_TEMPFILE.name)[1])
prefs_handler = PreferencesHandler(path.split(PREFERENCES_TEMPFILE.name)[1])
backup_prefs_handler = BackupPrefsHandler(path.split(BACKUPPREFS_TEMPFILE.name)[1])

handlers = [settings_handler, prefs_handler, backup_prefs_handler]


@pytest.mark.parametrize(
        "string,expected_list",
        [
            ("[\n\tc:/some/path,\n\tc:\\some\\other\\path]", [r"c:/some/path", r"c:\some\other\path"]),
            ("[\n\t]", []),
            ("[\n\t]", []),
            ("[\n\tA:\\some\\path]", ["A:\\some\\path"])
        ]
)
def test_list_parse(string: str, expected_list: list):
    parsed_from = settings_handler.parse_list_from_config(string)
    parsed_to = settings_handler.parse_list_to_config(expected_list)
    assert parsed_from == expected_list
    assert parsed_to == string


SETTINGS_TEMPFILE.close()
PREFERENCES_TEMPFILE.close()
BACKUPPREFS_TEMPFILE.close()

for handler in handlers:
    unlink(handler.config_file)
    unlink(handler.log_file)
