import enum
from typing import List, Sequence, Tuple


class CompilationError(Exception):
    pass

class ImageFormat(enum.Enum):
    UNKNOWN = 0

    RGBA32F = 1

    RGBA16F = 2

    RG32F = 3

    RG16F = 4

    R11F_G11F_B10F = 5

    R32F = 6

    R16F = 7

    RGBA16 = 8

    RGB10_A2 = 9

    RGBA8 = 10

    RG16 = 11

    RG8 = 12

    R16 = 13

    R8 = 14

    RGBA16_SNORM = 15

    RGBA8_SNORM = 16

    RG16_SNORM = 17

    RG8_SNORM = 18

    R16_SNORM = 19

    R8_SNORM = 20

    RGBA32I = 21

    RGBA16I = 22

    RGBA8I = 23

    RG32I = 24

    RG16I = 25

    RG8I = 26

    R32I = 27

    R16I = 28

    R8I = 29

    RGBA32UI = 30

    RGBA16UI = 31

    RGB10_A2UI = 32

    RGBA8UI = 33

    RG32UI = 34

    RG16UI = 35

    RG8UI = 36

    R32UI = 37

    R16UI = 38

    R8UI = 39

    R64UI = 40

    R64I = 41

    BGRA8 = 42

class BindingType(enum.Enum):
    UNKNOWN = 0

    SAMPLER = 1

    TEXTURE = 2

    CONSTANT_BUFFER = 3

    PARAMETER_BLOCK = 4

    TYPED_BUFFER = 5

    RAW_BUFFER = 6

    COMBINED_TEXTURE_SAMPLER = 7

    INPUT_RENDER_TARGET = 8

    INLINE_UNIFORM_DATA = 9

    RAYTRACING_ACCELERATION_STRUCTURE = 10

    VARYING_INPUT = 11

    VARYING_OUTPUT = 12

    EXISTENTIAL_VALUE = 13

    PUSH_CONSTANT = 14

    MUTABLE_TEXTURE = 258

    MUTABLE_TYPED_BUFFER = 261

    MUTABLE_RAW_BUFFER = 262

class ResourceKind(enum.Enum):
    CONSTANT_BUFFER = 0

    STRUCTURED_BUFFER = 1

    TEXTURE_2D = 2

    ACCELERATION_STRUCTURE = 3

    SAMPLER = 4

class Type:
    def __getstate__(self) -> object: ...

    def __setstate__(self, arg: object, /) -> None: ...

class Scalar(Type):
    @property
    def base(self) -> ScalarKind: ...

    def __getstate__(self) -> ScalarKind: ...

    def __setstate__(self, arg: ScalarKind, /) -> None: ...

class Array(Type):
    @property
    def type(self) -> Type: ...

    @property
    def count(self) -> int: ...

    def __getstate__(self) -> Tuple[Type, int]: ...

    def __setstate__(self, arg: Tuple[Type, int], /) -> None: ...

class Vector(Type):
    @property
    def base(self) -> ScalarKind: ...

    @property
    def count(self) -> int: ...

    def __getstate__(self) -> Tuple[ScalarKind, int]: ...

    def __setstate__(self, arg: Tuple[ScalarKind, int], /) -> None: ...

class Matrix(Type):
    @property
    def base(self) -> ScalarKind: ...

    @property
    def rows(self) -> int: ...

    @property
    def columns(self) -> int: ...

    def __getstate__(self) -> Tuple[ScalarKind, int, int]: ...

    def __setstate__(self, arg: Tuple[ScalarKind, int, int], /) -> None: ...

class ResourceAccess(enum.Enum):
    SLANG_RESOURCE_ACCESS_NONE = 0

    SLANG_RESOURCE_ACCESS_READ = 1

    SLANG_RESOURCE_ACCESS_READ_WRITE = 2

    SLANG_RESOURCE_ACCESS_RASTER_ORDERED = 3

    SLANG_RESOURCE_ACCESS_APPEND = 4

    SLANG_RESOURCE_ACCESS_CONSUME = 5

    SLANG_RESOURCE_ACCESS_WRITE = 6

    SLANG_RESOURCE_ACCESS_FEEDBACK = 7

    SLANG_RESOURCE_ACCESS_UNKNOWN = 2147483647

class ResourceShape(enum.Enum):
    NONE = 0

    TEXTURE_1D = 1

    TEXTURE_2D = 2

    TEXTURE_3D = 3

    TEXTURE_CUBE = 4

    TEXTURE_BUFFER = 5

    STRUCTURED_BUFFER = 6

    BYTE_ADDRESS_BUFFER = 7

    RESOURCE_UNKNOWN = 8

    ACCELERATION_STRUCTURE = 9

class Resource(Type):
    @property
    def kind(self) -> ResourceKind: ...

    @property
    def shape(self) -> ResourceShape: ...

    @property
    def access(self) -> ResourceAccess: ...

    @property
    def type(self) -> Type: ...

    @property
    def binding_type(self) -> BindingType: ...

    def __getstate__(self) -> Tuple[ResourceKind, ResourceShape, ResourceAccess, BindingType, Type]: ...

    def __setstate__(self, arg: Tuple[ResourceKind, ResourceShape, ResourceAccess, BindingType, Type], /) -> None: ...

class Field(Type):
    @property
    def name(self) -> str: ...

    @property
    def type(self) -> Type: ...

    @property
    def offset(self) -> int: ...

    @property
    def set(self) -> int: ...

    @property
    def binding(self) -> int: ...

    @property
    def image_format(self) -> ImageFormat: ...

    def __getstate__(self) -> Tuple[str, Type, int, int, int, ImageFormat]: ...

    def __setstate__(self, arg: Tuple[str, Type, int, int, int, ImageFormat], /) -> None: ...

class Struct(Type):
    @property
    def fields(self) -> List[Field]: ...

    def __getstate__(self) -> List[Field]: ...

    def __setstate__(self, arg: Sequence[Field], /) -> None: ...

class Reflection:
    def __getstate__(self) -> Type: ...

    def __setstate__(self, arg: Type, /) -> None: ...

    @property
    def object(self) -> Type: ...

class Shader:
    @property
    def entry(self) -> str: ...

    @property
    def code(self) -> bytes: ...

    @property
    def reflection(self) -> Reflection: ...

    @property
    def dependencies(self) -> list: ...

    def __getstate__(self) -> Tuple[bytes, Reflection, list]: ...

    def __setstate__(self, arg: Tuple[bytes, Reflection, list], /) -> None: ...

def compile(path: str, entry: str = 'main', target: str = 'spirv_1_3') -> Shader: ...

def compile_str(source: str, entry: str = 'main', target: str = 'spirv_1_3', filename: str = '') -> Shader: ...

class ScalarKind(enum.Enum):
    NONE = 0

    VOID = 1

    BOOL = 2

    INT32 = 3

    UINT32 = 4

    INT64 = 5

    UINT64 = 6

    FLOAT16 = 7

    FLOAT32 = 8

    FLOAT64 = 9

    INT8 = 10

    UINT8 = 11

    INT16 = 12

    UINT16 = 13
