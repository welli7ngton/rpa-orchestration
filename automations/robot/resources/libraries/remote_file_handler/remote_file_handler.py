import fnmatch
import httpx

from robot.api import logger
from robot.api.deco import keyword, library

from selenium.webdriver.common.options import BaseOptions
from selenium.webdriver import ChromeOptions, FirefoxOptions

from base64 import decodebytes
from io import BytesIO
from os import rename, getenv
from os.path import join
from zipfile import ZipFile

FileMap = dict[str, bool]


class API:
    def __init__(self) -> None:
        self._BASE_URL = getenv("REMOTE_GRID_URL", "http://localhost:4444")
        self._API_ENDPOINT = self._BASE_URL + "/session/{session_id}/se/files"
        logger.debug(f"Using '{self._BASE_URL}'")

    @property
    def API_ENDPOINT(self) -> str:
        return self._API_ENDPOINT

    def download_file_name(self, session_id: str, file_name: str):
        with httpx.Client(timeout=5.0) as client:
            response = client.post(
                self.API_ENDPOINT.format(session_id=session_id),
                json={"name": file_name},
            )
            response.raise_for_status()
            resultado = response.json()
            value = resultado["value"]
            return value

    def get_file_names(self, session_id: str) -> list[str]:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(
                self._API_ENDPOINT.format(session_id=session_id)
            )
            response.raise_for_status()
            resultado: dict = response.json()
            names = self._extract_names_from_json(resultado)

        logger.info(f"'{len(names)}' Arquivos disponíveis para download", also_console=True)
        return names

    def _extract_names_from_json(self, json: dict) -> list[str]:
        assert isinstance(json, dict)

        value = json.get("value", {})
        assert isinstance(value, dict)

        names = value.get("names", [])
        assert isinstance(names, list)

        return names


class FileHandler:
    def save_file_as_zip(self, payload, dest: str):
        encoded_file = payload['contents']
        file_name = payload["filename"]
        name_without_extension = self.__remove_extension(file_name)
        decoded = decodebytes(encoded_file.encode("utf-8"))
        # gerar .zip
        file_path = join(dest, f"{name_without_extension}.zip")
        with open(file_path, "wb") as file:
            file.write(decoded)

    def __remove_extension(self, file_name: str) -> str:
        return file_name.rsplit(".", 1).pop(0)

    def save_extracted_files(self, payload, dest: str, extracted_name: str | None = None):
        content = payload["contents"]
        encoded = content.encode("utf-8")
        decoded = decodebytes(encoded)

        # criar arquivo descompactado
        with ZipFile(BytesIO(decoded)) as zf:
            names = zf.namelist()
            logger.info(f"Arquivos: {names}", also_console=True)
            if (count := len(names)) > 1:
                logger.warn(f"Mais de 1 arquivo esperado (contém {count})!")

            for name in names:
                extracted_path = zf.extract(name, dest)
                if extracted_name:
                    extension = name.rsplit(".", 1)[1]
                    result_name = join(dest, f"{extracted_name}.{extension}")
                    rename(extracted_path, result_name)


class DownloadMap:
    def __init__(self) -> None:
        self._file_map: FileMap = {}

    def list_undownloaded_files(self):
        return [key for key, value in self._file_map.items() if value is False]

    def insert_unregistered_files(self, filenames: list[str]):
        for file in filenames:
            if file not in self._file_map:
                self._file_map[file] = False
                logger.debug(f"Inserting file '{file}'.")

    def mark_file_as_downloaded(self, filename: str):
        if filename not in self._file_map:
            logger.warn(f"File '{filename}' not in file_map but marked as downloaded.")

        self._file_map[filename] = True
        logger.debug(f"File '{filename}' marked as downloaded.")


_DOWNLOAD_PREFERENCES = {
    "download.prompt_for_download": "false",
    "browser.helperApps.neverAsk.saveToDisk": "application/csv,application/xml,application/txt",
    "download.default_directory": "/home/seluser/Downloads",
}


def set_downloadsEnabled_option(options: BaseOptions) -> BaseOptions:
    """Adiciona às opções que o browser deve permitir download de arquivos"""
    assert isinstance(options, BaseOptions)

    options.set_capability("se:downloadsEnabled", True)

    if isinstance(options, FirefoxOptions):
        _set_firefox_options(options)
        logger.info("set FirefoxOptions", also_console=True)

    elif isinstance(options, ChromeOptions):
        _set_chrome_options(options)
        logger.info("set ChromeOptions", also_console=True)

    else:
        logger.warn(f"Unexpected option type '{options.__class__.__name__}' ")

    logger.debug("Este robô requer um nó que permita download")
    return options


def _set_firefox_options(options: FirefoxOptions):
    for name, value in _DOWNLOAD_PREFERENCES.items():
        options.set_preference(name, value)


def _set_chrome_options(options: ChromeOptions):
    options.add_experimental_option("prefs", _DOWNLOAD_PREFERENCES)


@library(scope='GLOBAL', version='0.1')
class RemoteFileHandler:
    def __init__(self) -> None:
        self._file_map = DownloadMap()
        self._API = API()
        self._FILE_HANDLER = FileHandler()
        self.temp_file_patterns = ['.com.google.Chrome*', '*.crdownload', '*.tmp']

    @keyword
    def set_downloadsEnabled_option(self, options: BaseOptions) -> BaseOptions:
        """Adiciona às opções que o browser deve permitir download de arquivos"""

        options = set_downloadsEnabled_option(options)
        return options

    @keyword
    def list_download_files(self, session_id: str, pattern: str | None = None) -> "list[str]":
        assert isinstance(session_id, str)
        assert isinstance(pattern, (str, type(None)))

        names = self._API.get_file_names(session_id)
        if pattern:
            names = fnmatch.filter(names, pattern)

        self._file_map.insert_unregistered_files(names)
        return names

    @keyword
    def list_undownloaded_files(self) -> list[str]:
        return self._file_map.list_undownloaded_files()

    @keyword
    def retrieve_download_files(self, session_id: str, filename: str):
        assert isinstance(session_id, str)
        assert isinstance(filename, str)

        value = self._API.download_file_name(session_id, filename)
        self._file_map.mark_file_as_downloaded(filename)
        return value

    @keyword
    def save_file_as_zip(self, value, dest: str):
        file_name = value["filename"]
        logger.info(f"Obteve arquivo(s) '{file_name}'", also_console=True)
        self._FILE_HANDLER.save_file_as_zip(value, dest)

    @keyword
    def save_extracted_file(self, value, dest: str, extracted_name: str | None = None):
        self._FILE_HANDLER.save_extracted_files(value, dest, extracted_name)
