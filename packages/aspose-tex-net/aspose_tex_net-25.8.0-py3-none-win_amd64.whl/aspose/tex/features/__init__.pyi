import aspose.tex
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class FigureRenderer:
    
    def render(self, latex_body: str, stream: io.BytesIO, figure_renderer_options: aspose.tex.features.FigureRendererOptions) -> aspose.pydrawing.SizeF:
        ...
    
    ...

class FigureRendererOptions:
    
    def __init__(self):
        ...
    
    @property
    def preamble(self) -> str:
        ...
    
    @preamble.setter
    def preamble(self, value: str):
        ...
    
    @property
    def scale(self) -> int:
        ...
    
    @scale.setter
    def scale(self, value: int):
        ...
    
    @property
    def background_color(self) -> aspose.pydrawing.Color:
        ...
    
    @background_color.setter
    def background_color(self, value: aspose.pydrawing.Color):
        ...
    
    @property
    def log_stream(self) -> io.BytesIO:
        ...
    
    @log_stream.setter
    def log_stream(self, value: io.BytesIO):
        ...
    
    @property
    def show_terminal(self) -> bool:
        ...
    
    @show_terminal.setter
    def show_terminal(self, value: bool):
        ...
    
    @property
    def error_report(self) -> str:
        ...
    
    @property
    def required_input_directory(self) -> aspose.tex.io.IInputWorkingDirectory:
        ...
    
    @required_input_directory.setter
    def required_input_directory(self, value: aspose.tex.io.IInputWorkingDirectory):
        ...
    
    @property
    def margin(self) -> float:
        ...
    
    @margin.setter
    def margin(self, value: float):
        ...
    
    ...

class IGuessPackageCallback:
    
    def guess_package(self, command_name: str, is_environment: bool) -> str:
        ...
    
    ...

class IRasterRendererOptions:
    
    @property
    def resolution(self) -> int:
        ...
    
    @resolution.setter
    def resolution(self, value: int):
        ...
    
    ...

class LaTeXRepairer:
    
    def __init__(self, path: str, options: aspose.tex.features.LaTeXRepairerOptions):
        ...
    
    def run(self) -> aspose.tex.TeXJobResult:
        ...
    
    ...

class LaTeXRepairerOptions:
    
    def __init__(self):
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
    def guess_package_callback(self) -> aspose.tex.features.IGuessPackageCallback:
        ...
    
    @guess_package_callback.setter
    def guess_package_callback(self, value: aspose.tex.features.IGuessPackageCallback):
        ...
    
    ...

class MathRenderer:
    
    def render(self, formula: str, stream: io.BytesIO, math_renderer_options: aspose.tex.features.MathRendererOptions) -> aspose.pydrawing.SizeF:
        ...
    
    ...

class MathRendererOptions(aspose.tex.features.FigureRendererOptions):
    
    def __init__(self):
        ...
    
    @property
    def text_color(self) -> aspose.pydrawing.Color:
        ...
    
    @text_color.setter
    def text_color(self, value: aspose.pydrawing.Color):
        ...
    
    ...

class PngFigureRenderer(aspose.tex.features.FigureRenderer):
    
    def __init__(self):
        ...
    
    ...

class PngFigureRendererOptions(aspose.tex.features.FigureRendererOptions):
    
    def __init__(self):
        ...
    
    ...

class PngMathRenderer(aspose.tex.features.MathRenderer):
    
    def __init__(self):
        ...
    
    ...

class PngMathRendererOptions(aspose.tex.features.MathRendererOptions):
    
    def __init__(self):
        ...
    
    ...

class SvgFigureRenderer(aspose.tex.features.FigureRenderer):
    
    def __init__(self):
        ...
    
    ...

class SvgFigureRendererOptions(aspose.tex.features.FigureRendererOptions):
    
    def __init__(self):
        ...
    
    ...

class SvgMathRenderer(aspose.tex.features.MathRenderer):
    
    def __init__(self):
        ...
    
    ...

class SvgMathRendererOptions(aspose.tex.features.MathRendererOptions):
    
    def __init__(self):
        ...
    
    ...

