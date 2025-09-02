import logging
from pathlib import Path
from typing import Any, Final

from yaml import safe_load
from yaml.parser import ParserError

from dagtool.utils import hash_sha256

DAG_FILENAME_PREFIX: Final[str] = "dag"
VARIABLE_FILENAME: Final[str] = "variables"
ASSET_DIR: Final[str] = "assets"

logger = logging.getLogger("dagtool.conf")


class YamlConf:
    """Core Config object that use to find and map data from the current path.

    Attributes:
        path (Path): A filepath of template.
    """

    def __init__(self, path: Path | str) -> None:
        self.path: Path = Path(path)

    def read_vars(self) -> dict[str, Any]:
        """Get Variable value with an input stage name."""
        search_files: list[Path] = list(
            self.path.rglob(f"{VARIABLE_FILENAME}.y*ml")
        )
        if not search_files:
            raise FileNotFoundError("Does not found variables file.")
        try:
            raw_data = safe_load(
                min(
                    search_files,
                    key=lambda f: len(str(f.absolute())),
                ).open(mode="rt", encoding="utf-8")
            )
            if not raw_data:
                raise ValueError("Variable file does not contain any content.")
            elif isinstance(raw_data, list):
                raise TypeError(
                    "Variable file should contain only mapping data not list "
                    "of data."
                )
            return raw_data
        except ParserError:
            raise

    def read_conf(self) -> list[dict[str, Any]]:
        """Read DAG template config from the path argument and reload to the
        conf.

        Returns:
            list[dict[str, Any]]: A list of model data before validate step.
        """
        conf: list[dict[str, Any]] = []
        for file in self.path.rglob("*"):
            if (
                file.is_file()
                and file.stem != VARIABLE_FILENAME
                and file.stem.startswith(DAG_FILENAME_PREFIX)
                and file.suffix in (".yml", ".yaml")
            ):
                try:
                    raw_data: str = file.read_text(encoding="utf-8")
                    data: dict[str, Any] | list[Any] = safe_load(raw_data)
                except ParserError:
                    logger.error(f"YAML file does not parsing, {file}.")
                    continue
                except Exception as e:
                    logger.error(f"YAML file got error, {e}, {file}.")
                    continue

                # VALIDATE: Does not support for empty data or list of template
                #   config.
                if not data or isinstance(data, list):
                    continue

                try:
                    if (
                        "name" not in data
                        or data.get("type", "NOTSET") != "dag"
                    ):
                        continue

                    file_stats = file.stat()
                    model: dict[str, Any] = {
                        "filename": file.name,
                        "parent_dir": file.parent,
                        "created_dt": file_stats.st_ctime,
                        "updated_dt": file_stats.st_mtime,
                        "raw_data": raw_data,
                        "raw_data_hash": hash_sha256(raw_data),
                        **data,
                    }
                    logger.info(f"Load DAG Template data: {model['name']!r}")
                    conf.append(model)
                except AttributeError:
                    # NOTE: Except case data is not be `dict` type.
                    continue

        if len(conf) == 0:
            logger.warning(
                "Read config file from this domain path does not exists"
            )
        return conf

    def read_assets(self, filename: str) -> str:
        """Read the asset file from the template config path."""
        search_files: list[Path] = list(
            self.path.rglob(f"{ASSET_DIR}/{filename}")
        )
        if not search_files:
            raise FileNotFoundError(f"Asset file: {filename} does not found.")
        return search_files[0].read_text(encoding="utf-8")
