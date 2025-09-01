import aspose.tex
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class FigureRendererPlugin:
    
    def __init__(self):
        ...
    
    ...

class FigureRendererPluginOptions(aspose.tex.features.FigureRendererOptions):
    
    def add_input_data_source(self, data_source: aspose.tex.plugins.IDataSource) -> None:
        ...
    
    def add_output_data_target(self, data_target: aspose.tex.plugins.IDataSource) -> None:
        ...
    
    @property
    def input_data_collection(self) -> None:
        ...
    
    @property
    def output_data_collection(self) -> None:
        ...
    
    @property
    def operation_name(self) -> str:
        ...
    
    ...

class FigureRendererPluginResult:
    
    @property
    def log(self) -> io.BytesIO:
        ...
    
    @property
    def size(self) -> aspose.pydrawing.SizeF:
        ...
    
    ...

class IDataSource:
    
    @property
    def data_type(self) -> aspose.tex.plugins.DataType:
        ...
    
    ...

class IOperationResult:
    
    def to_file(self) -> str:
        ...
    
    def to_stream(self) -> io.BytesIO:
        ...
    
    @property
    def is_file(self) -> bool:
        ...
    
    @property
    def is_stream(self) -> bool:
        ...
    
    @property
    def is_string(self) -> bool:
        ...
    
    @property
    def is_byte_array(self) -> bool:
        ...
    
    @property
    def data(self) -> object:
        ...
    
    ...

class IPlugin:
    
    def process(self, options: aspose.tex.plugins.IPluginOptions) -> aspose.tex.plugins.ResultContainer:
        ...
    
    ...

class IPluginOptions:
    
    ...

class MathRendererPlugin:
    
    def __init__(self):
        ...
    
    ...

class MathRendererPluginOptions(aspose.tex.features.MathRendererOptions):
    
    def add_input_data_source(self, data_source: aspose.tex.plugins.IDataSource) -> None:
        ...
    
    def add_output_data_target(self, data_target: aspose.tex.plugins.IDataSource) -> None:
        ...
    
    @property
    def input_data_collection(self) -> None:
        ...
    
    @property
    def output_data_collection(self) -> None:
        ...
    
    @property
    def operation_name(self) -> str:
        ...
    
    ...

class MathRendererPluginResult:
    
    @property
    def log(self) -> io.BytesIO:
        ...
    
    @property
    def size(self) -> aspose.pydrawing.SizeF:
        ...
    
    ...

class PngFigureRendererPluginOptions(aspose.tex.plugins.FigureRendererPluginOptions):
    
    def __init__(self):
        ...
    
    ...

class PngMathRendererPluginOptions(aspose.tex.plugins.MathRendererPluginOptions):
    
    def __init__(self):
        ...
    
    ...

class ResultContainer:
    
    @property
    def result_collection(self) -> None:
        ...
    
    ...

class StreamDataSource:
    
    def __init__(self, data: io.BytesIO):
        ...
    
    @property
    def data(self) -> io.BytesIO:
        ...
    
    ...

class StringDataSource:
    
    def __init__(self, data: str):
        ...
    
    @property
    def data(self) -> str:
        ...
    
    ...

class SvgFigureRendererPluginOptions(aspose.tex.plugins.FigureRendererPluginOptions):
    
    def __init__(self):
        ...
    
    ...

class SvgMathRendererPluginOptions(aspose.tex.plugins.MathRendererPluginOptions):
    
    def __init__(self):
        ...
    
    ...

class DataType:
    
    STREAM: int
    STRING: int

