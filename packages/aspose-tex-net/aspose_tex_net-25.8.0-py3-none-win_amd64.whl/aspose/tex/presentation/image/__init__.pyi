import aspose.tex
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class BmpSaveOptions(aspose.tex.presentation.image.ImageSaveOptions):
    
    def __init__(self):
        ...
    
    ...

class ImageDevice(aspose.tex.presentation.Device):
    
    @overload
    def __init__(self):
        ...
    
    @overload
    def __init__(self, white_background: bool):
        ...
    
    @property
    def result(self) -> list[bytes]:
        ...
    
    ...

class ImageSaveOptions(aspose.tex.presentation.SaveOptions):
    
    @property
    def resolution(self) -> float:
        ...
    
    @resolution.setter
    def resolution(self, value: float):
        ...
    
    @property
    def smoothing_mode(self) -> aspose.pydrawing.Drawing2D.SmoothingMode:
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value: aspose.pydrawing.Drawing2D.SmoothingMode):
        ...
    
    @property
    def interpolation_mode(self) -> aspose.pydrawing.Drawing2D.InterpolationMode:
        ...
    
    @interpolation_mode.setter
    def interpolation_mode(self, value: aspose.pydrawing.Drawing2D.InterpolationMode):
        ...
    
    @property
    def device_writes_images(self) -> bool:
        ...
    
    @device_writes_images.setter
    def device_writes_images(self, value: bool):
        ...
    
    ...

class JpegSaveOptions(aspose.tex.presentation.image.ImageSaveOptions):
    
    def __init__(self):
        ...
    
    ...

class PngSaveOptions(aspose.tex.presentation.image.ImageSaveOptions):
    
    def __init__(self):
        ...
    
    ...

class TiffSaveOptions(aspose.tex.presentation.image.ImageSaveOptions):
    
    def __init__(self):
        ...
    
    @property
    def multipage(self) -> bool:
        ...
    
    @multipage.setter
    def multipage(self, value: bool):
        ...
    
    @property
    def compression(self) -> aspose.tex.presentation.image.TiffCompression:
        ...
    
    @compression.setter
    def compression(self, value: aspose.tex.presentation.image.TiffCompression):
        ...
    
    ...

class TiffCompression:
    
    COMPRESSION_LZW: int
    COMPRESSION_CCITT3: int
    COMPRESSION_CCITT4: int
    COMPRESSION_RLE: int
    COMPRESSION_NONE: int

