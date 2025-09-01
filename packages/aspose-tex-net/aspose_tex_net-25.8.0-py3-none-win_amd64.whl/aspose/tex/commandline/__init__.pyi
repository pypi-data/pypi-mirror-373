import aspose.tex
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class Base64Exec(aspose.tex.commandline.Executable):
    
    def __init__(self):
        ...
    
    ...

class Executable:
    
    def execute(self, args: list[str]) -> None:
        ...
    
    @property
    def command_name(self) -> str:
        ...
    
    ...

class ExecutablesList:
    
    def add(self, exec: aspose.tex.commandline.Executable) -> None:
        ...
    
    def remove(self, command_name: str) -> None:
        ...
    
    ...

class Write18Exception(RuntimeError):
    
    def __init__(self, message: str):
        ...
    
    ...

