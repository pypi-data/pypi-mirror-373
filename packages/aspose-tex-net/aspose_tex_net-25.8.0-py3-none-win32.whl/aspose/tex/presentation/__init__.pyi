from aspose.tex.presentation import image
from aspose.tex.presentation import pdf
from aspose.tex.presentation import svg
from aspose.tex.presentation import xps
import aspose.tex
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class Device:
    
    @property
    def page_count(self) -> int:
        ...
    
    ...

class GlyphData:
    
    def __init__(self):
        ...
    
    @property
    def natural_width(self) -> float:
        ...
    
    @natural_width.setter
    def natural_width(self, value: float):
        ...
    
    @property
    def advance_width(self) -> float:
        ...
    
    @advance_width.setter
    def advance_width(self, value: float):
        ...
    
    @property
    def u_offset(self) -> float:
        ...
    
    @u_offset.setter
    def u_offset(self, value: float):
        ...
    
    @property
    def v_offset(self) -> float:
        ...
    
    @v_offset.setter
    def v_offset(self, value: float):
        ...
    
    ...

class SaveOptions:
    
    @property
    def subset_fonts(self) -> bool:
        ...
    
    @subset_fonts.setter
    def subset_fonts(self, value: bool):
        ...
    
    @property
    def rasterize_formulas(self) -> bool:
        ...
    
    @rasterize_formulas.setter
    def rasterize_formulas(self, value: bool):
        ...
    
    @property
    def rasterize_included_graphics(self) -> bool:
        ...
    
    @rasterize_included_graphics.setter
    def rasterize_included_graphics(self, value: bool):
        ...
    
    ...

