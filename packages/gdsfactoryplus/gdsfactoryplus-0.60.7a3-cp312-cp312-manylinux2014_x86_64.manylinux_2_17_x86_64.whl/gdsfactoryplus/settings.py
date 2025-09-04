"""Parse the GDSFactory+ settings."""

from __future__ import annotations

import os
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    import numpy as np
    import numpy.typing as npt
    import pydantic as pyd
    import pydantic_settings as pyds

    from gdsfactoryplus import project as gfp_project
else:
    from gdsfactoryplus.core.lazy import lazy_import

    np = lazy_import("numpy")
    pyd = lazy_import("pydantic")
    pyds = lazy_import("pydantic_settings")
    npt = lazy_import("numpy.typing")
    gfp_project = lazy_import("gdsfactoryplus.project")


class LogSettings(pyds.BaseSettings):
    """Logging settings."""

    level: str = "INFO"
    debug_level: str = "DEBUG"


class PdkSettings(pyds.BaseSettings):
    """PDK Settings."""

    name: str = "generic"

    model_config = pyds.SettingsConfigDict(
        extra="ignore",
    )


class DrcSettings(pyds.BaseSettings):
    """DRC Settings."""

    timeout: int = 60
    host: str = "https://dodeck.gdsfactory.com"
    process: str = ""
    pdk: str = ""

    model_config = pyds.SettingsConfigDict(
        extra="ignore",
    )


class ApiSettings(pyds.BaseSettings):
    """API Settings."""

    host: str = pyd.Field(
        default="https://prod.gdsfactory.com/",
        validation_alias="GFP_LANDING_PAGE_BASE_URL",
    )
    key: str = ""

    model_config = pyds.SettingsConfigDict(
        extra="ignore",
    )


class ExternalSettings(pyds.BaseSettings):
    """External Settings."""

    model_config = pyds.SettingsConfigDict(
        extra="ignore",
    )

    axiomatic_api_key: str = ""

    @pyd.model_validator(mode="after")
    def validate_axiomatic_api_key(self) -> Self:
        """Get the axiomatic API key from the environment variable."""
        if "GFP_EXTERNAL_AXIOMATIC_API_KEY" in os.environ:
            self.axiomatic_api_key = os.environ["GFP_EXTERNAL_AXIOMATIC_API_KEY"]
        return self


class KwebSettings(pyds.BaseSettings):
    """Kweb Settings."""

    host: str = "localhost"
    https: bool = False

    model_config = pyds.SettingsConfigDict(
        extra="ignore",
    )


class Linspace(pyds.BaseSettings):
    """A linear spacing definition."""

    min: float = 0.0
    max: float = 1.0
    num: int = 50

    model_config = pyds.SettingsConfigDict(
        extra="ignore",
    )

    @property
    def arr(self) -> npt.NDArray[np.float64]:
        """Create array from linspace definition."""
        return np.linspace(self.min, self.max, self.num, dtype=np.float64)

    @property
    def step(self) -> float:
        """Get step between elements."""
        return float(self.arr[1] - self.arr[0])


class Arange(pyds.BaseSettings):
    """An array range definition."""

    min: float = 0.0
    max: float = 1.0
    step: float = 0.1

    model_config = pyds.SettingsConfigDict(
        extra="ignore",
    )

    @property
    def arr(self) -> npt.NDArray[np.float64]:
        """Create array from arange definition."""
        return np.arange(self.min, self.max, self.step, dtype=np.float64)

    @property
    def num(self) -> int:
        """Get number of elements."""
        return int(self.arr.shape[0])


class SimSettings(pyds.BaseSettings):
    """Simulation Settings."""

    wls: Linspace | Arange = pyd.Field(
        default_factory=lambda: Linspace(min=1.5, max=1.6, num=300)
    )

    model_config = pyds.SettingsConfigDict(
        extra="ignore",
    )


class GptSettings(pyds.BaseSettings):
    """GPT Settings."""

    host: str = "https://doitforme.gdsfactory.com"
    pdk: str = ""

    model_config = pyds.SettingsConfigDict(
        extra="ignore",
    )


class Settings(pyds.BaseSettings):
    """Settings."""

    name: str = ""
    ignore: list[str] = pyd.Field(default_factory=list)
    pdk: PdkSettings = pyd.Field(default_factory=PdkSettings)
    api: ApiSettings = pyd.Field(default_factory=ApiSettings)
    drc: DrcSettings = pyd.Field(default_factory=DrcSettings)
    sim: SimSettings = pyd.Field(default_factory=SimSettings)
    gpt: GptSettings = pyd.Field(default_factory=GptSettings)
    kweb: KwebSettings = pyd.Field(default_factory=KwebSettings)
    log: LogSettings = pyd.Field(default_factory=LogSettings)
    external: ExternalSettings = pyd.Field(default_factory=ExternalSettings)

    model_config = pyds.SettingsConfigDict(
        pyproject_toml_table_header=("tool", "gdsfactoryplus"),
        env_prefix="GFP_",
        env_nested_delimiter="_",
        extra="ignore",
    )

    def is_a_pdk(self) -> bool:
        """Check if the settings are for a pdk or a project."""
        return self.name == self.pdk.name

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[pyds.BaseSettings],
        init_settings: pyds.PydanticBaseSettingsSource,
        env_settings: pyds.PydanticBaseSettingsSource,
        dotenv_settings: pyds.PydanticBaseSettingsSource,
        file_secret_settings: pyds.PydanticBaseSettingsSource,
    ) -> tuple[pyds.PydanticBaseSettingsSource, ...]:
        """Add global gdsfactoryplus.toml and local pyproject.toml to the sources."""
        sources = [init_settings, env_settings, dotenv_settings, file_secret_settings]
        sources.append(
            pyds.PyprojectTomlConfigSettingsSource(
                settings_cls=settings_cls,
                toml_file=Path("~").expanduser().resolve()
                / ".gdsfactory"
                / "gdsfactoryplus.toml",
            )
        )
        project_dir = gfp_project.maybe_find_project_dir()
        if project_dir is not None:
            sources.append(
                pyds.PyprojectTomlConfigSettingsSource(
                    settings_cls=settings_cls,
                    toml_file=Path(project_dir).resolve() / "pyproject.toml",
                )
            )
        return tuple(sources)

    def _validate_ignore(self) -> Self:
        # expand glob patterns in ignore list
        """Expand glob patterns in ignore list."""
        repodir = Path(gfp_project.maybe_find_project_dir() or ".").resolve()
        picsdir = repodir / self.name
        new = []
        ignore = [
            *self.ignore,
            "**/.virtual_documents/**/*",
            "**/.ipynb_checkpoints/**/*",
        ]
        for pattern in ignore:
            for path in picsdir.glob(pattern):
                fn = str(path.resolve().relative_to(picsdir))
                new.append(fn)
        self.ignore = new
        return self

    def _validate_name(self) -> Self:
        """Get the name from the pyproject.toml [project] section."""
        if self.name:
            return self
        project_settings = ProjectSettings()
        self.name = project_settings.name
        return self

    @pyd.model_validator(mode="after")
    def _validate(self) -> Self:
        """Run validations after all fields are set."""
        # order is important here.
        self._validate_name()
        self._validate_ignore()
        return self


class ProjectSettings(pyds.BaseSettings):
    """Settings."""

    # FIXME: it seems like global config overrules local config?!

    name: str = "pics"
    model_config = pyds.SettingsConfigDict(
        pyproject_toml_table_header=("project",),
        env_prefix="GFP_PROJECT_",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[pyds.BaseSettings],
        init_settings: pyds.PydanticBaseSettingsSource,
        env_settings: pyds.PydanticBaseSettingsSource,
        dotenv_settings: pyds.PydanticBaseSettingsSource,
        file_secret_settings: pyds.PydanticBaseSettingsSource,
    ) -> tuple[pyds.PydanticBaseSettingsSource, ...]:
        """Read the [project] section of the pyproject.toml."""
        sources = [init_settings, env_settings, dotenv_settings, file_secret_settings]
        project_dir = gfp_project.maybe_find_project_dir()
        if project_dir is not None:
            sources.append(
                pyds.PyprojectTomlConfigSettingsSource(
                    settings_cls=settings_cls,
                    toml_file=Path(project_dir).resolve() / "pyproject.toml",
                )
            )
        return tuple(sources)


@cache
def get_settings() -> Settings:
    """Get the gdsfactoryplus settings."""
    return Settings()


def get_wls() -> Linspace | Arange:
    """Get the wavelengths used in the project."""
    return get_settings().sim.wls


def get_pdk_name() -> str:
    """Get the name of the pdk used in the project.

    Returns:
        str: Name of the PDK.

    Raises:
        RuntimeError: If the PDK name is not set in the project settings.
    """
    try:
        pdk_name = get_settings().pdk.name
    except Exception:  # noqa: BLE001
        return "generic"
    if not pdk_name:
        return "generic"
    return pdk_name


def get_project_dir() -> Path:
    """Get the project root directory."""
    return Path(gfp_project.maybe_find_project_dir() or Path.cwd()).resolve()


def get_pics_dir() -> Path:
    """Get the PICs directory."""
    project_dir = get_project_dir()
    settings = get_settings()
    return project_dir / settings.name


def get_build_dir() -> Path:
    """Get the build directory."""
    return get_project_dir() / "build"


def ignored_paths() -> list[Path]:
    """Get paths to ignore."""
    settings = get_settings()
    return [get_pics_dir() / path for path in settings.ignore]


def get_gds_dir() -> Path:
    """Get the output GDS directory."""
    path = get_build_dir() / "gds"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_db_path() -> Path:
    """Get the path to the database."""
    build_dir = get_build_dir()
    build_dir.mkdir(exist_ok=True)
    return build_dir / "gfp.db"


def get_log_dir() -> Path:
    """Get the log directory."""
    log_dir = get_build_dir() / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir
