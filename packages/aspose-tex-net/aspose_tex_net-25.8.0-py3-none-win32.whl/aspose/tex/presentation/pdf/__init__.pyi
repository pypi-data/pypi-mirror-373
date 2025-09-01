import aspose.tex
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class PdfDevice(aspose.tex.presentation.Device):
    
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

class PdfEncryptionDetails:
    
    def __init__(self, user_password: str, owner_password: str, permissions: int, encryption_algorithm: aspose.tex.presentation.pdf.PdfEncryptionAlgorithm):
        ...
    
    @property
    def user_password(self) -> str:
        ...
    
    @user_password.setter
    def user_password(self, value: str):
        ...
    
    @property
    def owner_password(self) -> str:
        ...
    
    @owner_password.setter
    def owner_password(self, value: str):
        ...
    
    @property
    def permissions(self) -> int:
        ...
    
    @permissions.setter
    def permissions(self, value: int):
        ...
    
    @property
    def encryption_algorithm(self) -> aspose.tex.presentation.pdf.PdfEncryptionAlgorithm:
        ...
    
    @encryption_algorithm.setter
    def encryption_algorithm(self, value: aspose.tex.presentation.pdf.PdfEncryptionAlgorithm):
        ...
    
    ...

class PdfSaveOptions(aspose.tex.presentation.SaveOptions):
    
    def __init__(self):
        ...
    
    @property
    def jpeg_quality_level(self) -> int:
        ...
    
    @jpeg_quality_level.setter
    def jpeg_quality_level(self, value: int):
        ...
    
    @property
    def outline_tree_height(self) -> int:
        ...
    
    @outline_tree_height.setter
    def outline_tree_height(self, value: int):
        ...
    
    @property
    def outline_tree_expansion_level(self) -> int:
        ...
    
    @outline_tree_expansion_level.setter
    def outline_tree_expansion_level(self, value: int):
        ...
    
    @property
    def text_compression(self) -> aspose.tex.presentation.pdf.PdfTextCompression:
        ...
    
    @text_compression.setter
    def text_compression(self, value: aspose.tex.presentation.pdf.PdfTextCompression):
        ...
    
    @property
    def image_compression(self) -> aspose.tex.presentation.pdf.PdfImageCompression:
        ...
    
    @image_compression.setter
    def image_compression(self, value: aspose.tex.presentation.pdf.PdfImageCompression):
        ...
    
    @property
    def encryption_details(self) -> aspose.tex.presentation.pdf.PdfEncryptionDetails:
        ...
    
    @encryption_details.setter
    def encryption_details(self, value: aspose.tex.presentation.pdf.PdfEncryptionDetails):
        ...
    
    ...

class PdfEncryptionAlgorithm:
    
    RC4_40: int
    RC4_128: int

class PdfImageCompression:
    
    AUTO: int
    NONE: int
    RLE: int
    FLATE: int
    LZW_BASELINE_PREDICTOR: int
    LZW_OPTIMIZED_PREDICTOR: int
    JPEG: int

class PdfTextCompression:
    
    NONE: int
    RLE: int
    LZW: int
    FLATE: int

