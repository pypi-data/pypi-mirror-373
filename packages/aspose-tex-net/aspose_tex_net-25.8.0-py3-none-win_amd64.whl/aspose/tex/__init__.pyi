from aspose.tex import commandline
from aspose.tex import features
from aspose.tex import io
from aspose.tex import plugins
from aspose.tex import presentation
from aspose.tex import resourceproviders
import aspose.tex
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable
from typing import Any

def get_pyinstaller_hook_dirs() -> Any:
  """Function required by PyInstaller. Returns paths to module
  PyInstaller hooks. Not intended to be called explicitly."""

class BuildVersionInfo:
    
    def __init__(self):
        ...
    
    ASSEMBLY_VERSION: str
    
    PRODUCT: str
    
    FILE_VERSION: str
    
    ...

class License:
    
    def __init__(self):
        ...
    
    @overload
    def set_license(self, license_name: str) -> None:
        ...
    
    @overload
    def set_license(self, stream: io.BytesIO) -> None:
        ...
    
    @property
    def embedded(self) -> bool:
        ...
    
    @embedded.setter
    def embedded(self, value: bool):
        ...
    
    ...

class Metered:
    
    def __init__(self):
        ...
    
    def set_metered_key(self, public_key: str, private_key: str) -> None:
        ...
    
    @staticmethod
    def get_consumption_quantity(self) -> decimal.Decimal:
        ...
    
    @staticmethod
    def get_consumption_credit(self) -> decimal.Decimal:
        ...
    
    ...

class TeXConfig:
    
    @overload
    @staticmethod
    def object_tex(self) -> aspose.tex.TeXConfig:
        ...
    
    @overload
    @staticmethod
    def object_tex(self, format_provider: aspose.tex.resourceproviders.FormatProvider) -> aspose.tex.TeXConfig:
        ...
    
    object_ini_tex: aspose.tex.TeXConfig
    
    object_latex: aspose.tex.TeXConfig
    
    ...

class TeXExtension:
    
    OBJECT_TEX: aspose.tex.TeXExtension
    
    ...

class TeXJob:
    
    @overload
    def __init__(self, stream: io.BytesIO, device: aspose.tex.presentation.Device, options: aspose.tex.TeXOptions):
        ...
    
    @overload
    def __init__(self, path: str, device: aspose.tex.presentation.Device, options: aspose.tex.TeXOptions):
        ...
    
    @overload
    def __init__(self, device: aspose.tex.presentation.Device, options: aspose.tex.TeXOptions):
        ...
    
    def run(self) -> aspose.tex.TeXJobResult:
        ...
    
    @staticmethod
    def create_format(self, path: str, options: aspose.tex.TeXOptions) -> None:
        ...
    
    ...

class TeXOptions:
    
    @staticmethod
    def console_app_options(self, config: aspose.tex.TeXConfig) -> aspose.tex.TeXOptions:
        ...
    
    @property
    def job_name(self) -> str:
        ...
    
    @job_name.setter
    def job_name(self, value: str):
        ...
    
    @property
    def terminal_in(self) -> aspose.tex.io.IInputTerminal:
        ...
    
    @terminal_in.setter
    def terminal_in(self, value: aspose.tex.io.IInputTerminal):
        ...
    
    @property
    def terminal_out(self) -> aspose.tex.io.IOutputTerminal:
        ...
    
    @terminal_out.setter
    def terminal_out(self, value: aspose.tex.io.IOutputTerminal):
        ...
    
    @property
    def input_working_directory(self) -> aspose.tex.io.IInputWorkingDirectory:
        ...
    
    @input_working_directory.setter
    def input_working_directory(self, value: aspose.tex.io.IInputWorkingDirectory):
        ...
    
    @property
    def output_working_directory(self) -> aspose.tex.io.IOutputWorkingDirectory:
        ...
    
    @output_working_directory.setter
    def output_working_directory(self, value: aspose.tex.io.IOutputWorkingDirectory):
        ...
    
    @property
    def required_input_directory(self) -> aspose.tex.io.IInputWorkingDirectory:
        ...
    
    @required_input_directory.setter
    def required_input_directory(self, value: aspose.tex.io.IInputWorkingDirectory):
        ...
    
    @property
    def interaction(self) -> aspose.tex.Interaction:
        ...
    
    @interaction.setter
    def interaction(self, value: aspose.tex.Interaction):
        ...
    
    @property
    def ignore_missing_packages(self) -> bool:
        ...
    
    @ignore_missing_packages.setter
    def ignore_missing_packages(self, value: bool):
        ...
    
    @property
    def save_options(self) -> aspose.tex.presentation.SaveOptions:
        ...
    
    @save_options.setter
    def save_options(self, value: aspose.tex.presentation.SaveOptions):
        ...
    
    @property
    def date_time(self) -> datetime.datetime:
        ...
    
    @date_time.setter
    def date_time(self, value: datetime.datetime):
        ...
    
    @property
    def repeat(self) -> bool:
        ...
    
    @repeat.setter
    def repeat(self, value: bool):
        ...
    
    @property
    def no_ligatures(self) -> bool:
        ...
    
    @no_ligatures.setter
    def no_ligatures(self, value: bool):
        ...
    
    @property
    def full_input_file_names(self) -> bool:
        ...
    
    @full_input_file_names.setter
    def full_input_file_names(self, value: bool):
        ...
    
    @property
    def shell_mode(self) -> aspose.tex.ShellMode:
        ...
    
    @shell_mode.setter
    def shell_mode(self, value: aspose.tex.ShellMode):
        ...
    
    @property
    def executables(self) -> aspose.tex.commandline.ExecutablesList:
        ...
    
    ...

class Interaction:
    
    BATCH_MODE: int
    NONSTOP_MODE: int
    SCROLL_MODE: int
    ERROR_STOP_MODE: int
    FORMAT_DEFINED: int

class ShellMode:
    
    NO_SHELL_ESCAPE: int
    SHELL_RESTRICTED: int

class TeXJobResult:
    
    SPOTLESS: int
    WARNING_ISSUED: int
    ERROR_MESSAGE_ISSUED: int
    FATAL_ERROR_STOP: int

