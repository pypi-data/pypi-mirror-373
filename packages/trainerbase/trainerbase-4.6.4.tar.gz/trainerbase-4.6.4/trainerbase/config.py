from pathlib import Path
from tomllib import load as load_toml
from typing import Any, Final

from pydantic import AliasChoices, BaseModel, Field


CONFIG_FILE: Final[Path] = Path("./trainerbase.toml")

DEFAULT_VENDOR_FOLDER_PATHS: Final[list[Path]] = [
    Path(__file__).resolve().parent.parent / "trainerbase_vendor",
    Path().resolve() / "trainerbase_vendor",
]


class Process(BaseModel):
    names: list[str] = Field(validation_alias=AliasChoices("names", "process_names"))
    exact_match: bool = True
    ignore_case: bool = False


class SpeedhackConfig(BaseModel):
    offset_x64: int = 0x47098
    offset_x32: int = 0x40058


class Vendor(BaseModel):
    extra_search_paths: list[Path] | None = None
    speedhack: SpeedhackConfig = SpeedhackConfig()

    @property
    def folder(self) -> Path:
        search_paths = DEFAULT_VENDOR_FOLDER_PATHS.copy()

        if self.extra_search_paths is not None:
            search_paths.extend(self.extra_search_paths)

        try:
            path = next(filter(Path.is_dir, search_paths))
        except StopIteration as e:
            raise ValueError("Failed to find Trainer Base vendor folder") from e

        return path.resolve()


class Config(BaseModel):
    process: Process = Field(validation_alias=AliasChoices("process", "pymem"))
    vendor: Vendor = Vendor()
    logging: dict[str, Any] | None = None  # Must be managed by logging.dictConfig


with CONFIG_FILE.resolve().open("rb") as trainerbase_toml:
    trainerbase_config = load_toml(trainerbase_toml)


config = Config.model_validate(trainerbase_config)
