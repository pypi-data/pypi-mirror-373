import aspose.tex
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class IFileCollector:
    
    def get_file_names_by_extension(self, extension: str, path: str) -> list[str]:
        ...
    
    ...

class IInputTerminal:
    
    @property
    def reader(self) -> aspose.tex.io.TeXStreamReader:
        ...
    
    ...

class IInputWorkingDirectory:
    
    def get_file(self, file_name: str, search_subdirectories: bool) -> aspose.tex.io.NamedStream:
        ...
    
    ...

class IOutputTerminal:
    
    @property
    def writer(self) -> aspose.tex.io.TeXStreamWriter:
        ...
    
    ...

class IOutputWorkingDirectory:
    
    def get_output_file(self, file_name: str) -> aspose.tex.io.NamedStream:
        ...
    
    ...

class InputConsoleTerminal:
    
    def __init__(self):
        ...
    
    ...

class InputFileSystemDirectory(aspose.tex.io.InputWorkingDirectory):
    
    def __init__(self, base_path: str):
        ...
    
    ...

class InputWorkingDirectory:
    
    @overload
    def get_file(self, file_name: str) -> aspose.tex.io.NamedStream:
        ...
    
    ...

class InputZipDirectory(aspose.tex.io.InputWorkingDirectory):
    
    def __init__(self, zip_stream: io.BytesIO, base_path: str):
        ...
    
    ...

class NamedStream:
    
    def __init__(self, stream: io.BytesIO, full_name: str):
        ...
    
    @property
    def full_name(self) -> str:
        ...
    
    @property
    def stream(self) -> io.BytesIO:
        ...
    
    ...

class NondisposableMemoryStream:
    
    @overload
    def __init__(self):
        ...
    
    @overload
    def __init__(self, stream: io.BytesIO):
        ...
    
    ...

class OutputConsoleTerminal:
    
    def __init__(self):
        ...
    
    ...

class OutputFileSystemDirectory(aspose.tex.io.InputFileSystemDirectory):
    
    def __init__(self, base_path: str):
        ...
    
    ...

class OutputFileTerminal:
    
    def __init__(self, working_directory: aspose.tex.io.IOutputWorkingDirectory):
        ...
    
    ...

class OutputMemoryTerminal:
    
    def __init__(self):
        ...
    
    @property
    def stream(self) -> io.BytesIO:
        ...
    
    ...

class OutputZipDirectory(aspose.tex.io.InputWorkingDirectory):
    
    def __init__(self, zip_stream: io.BytesIO):
        ...
    
    def finish(self) -> None:
        ...
    
    ...

class TeXStreamReader:
    
    @overload
    def read(self) -> int:
        ...
    
    @overload
    def read(self, buffer: list[str], index: int, count: int) -> int:
        ...
    
    def read_to_end(self) -> str:
        ...
    
    def read_line(self) -> str:
        ...
    
    def close(self) -> None:
        ...
    
    ...

class TeXStreamWriter:
    
    @overload
    def write_line(self) -> None:
        ...
    
    @overload
    def write_line(self, value: bool) -> None:
        ...
    
    @overload
    def write_line(self, value: str) -> None:
        ...
    
    @overload
    def write_line(self, value: str) -> None:
        ...
    
    @overload
    def write_line(self, buffer: list[str]) -> None:
        ...
    
    @overload
    def write_line(self, value: decimal.Decimal) -> None:
        ...
    
    @overload
    def write_line(self, value: float) -> None:
        ...
    
    @overload
    def write_line(self, value: float) -> None:
        ...
    
    @overload
    def write_line(self, value: int) -> None:
        ...
    
    @overload
    def write_line(self, value: int) -> None:
        ...
    
    @overload
    def write_line(self, value: int) -> None:
        ...
    
    @overload
    def write_line(self, value: int) -> None:
        ...
    
    @overload
    def write(self, value: bool) -> None:
        ...
    
    @overload
    def write(self, value: str) -> None:
        ...
    
    @overload
    def write(self, value: str) -> None:
        ...
    
    @overload
    def write(self, value: list[str]) -> None:
        ...
    
    @overload
    def write(self, value: decimal.Decimal) -> None:
        ...
    
    @overload
    def write(self, value: float) -> None:
        ...
    
    @overload
    def write(self, value: float) -> None:
        ...
    
    @overload
    def write(self, value: int) -> None:
        ...
    
    @overload
    def write(self, value: int) -> None:
        ...
    
    @overload
    def write(self, value: int) -> None:
        ...
    
    @overload
    def write(self, value: int) -> None:
        ...
    
    def flush(self) -> None:
        ...
    
    def close(self) -> None:
        ...
    
    @property
    def encoding(self) -> str:
        ...
    
    @property
    def new_line(self) -> str:
        ...
    
    ...

