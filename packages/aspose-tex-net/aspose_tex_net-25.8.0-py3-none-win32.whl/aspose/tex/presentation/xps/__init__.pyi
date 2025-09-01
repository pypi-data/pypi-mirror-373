import aspose.tex
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class XpsDevice(aspose.tex.presentation.Device):
    
    @overload
    def __init__(self):
        ...
    
    @overload
    def __init__(self, stream: io.BytesIO):
        ...
    
    def add_bookmark(self, name: str, position: aspose.pydrawing.PointF) -> None:
        ...
    
    def start_fragment(self) -> None:
        ...
    
    def end_fragment(self) -> None:
        ...
    
    ...

class XpsSaveOptions(aspose.tex.presentation.SaveOptions):
    
    def __init__(self):
        ...
    
    ...

