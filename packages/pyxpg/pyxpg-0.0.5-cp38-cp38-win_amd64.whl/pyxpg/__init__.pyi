import enum
from typing import Callable, List, Optional, Sequence, Tuple, Union

from . import imgui as imgui, slang as slang


class LogCapture:
    def __init__(self, arg: Callable[[LogLevel, str, str], None], /) -> None: ...

class LogLevel(enum.Enum):
    TRACE = 0

    DEBUG = 1

    INFO = 2

    WARN = 3

    ERROR = 4

    DISABLED = 5

def set_log_level(level: LogLevel) -> None: ...

class SwapchainOutOfDateError(Exception):
    pass

class MemoryHeapFlags(enum.Flag):
    VK_MEMORY_HEAP_DEVICE_LOCAL = 1

    VK_MEMORY_HEAP_MULTI_INSTANCE = 2

class MemoryPropertyFlags(enum.Flag):
    DEVICE_LOCAL = 1

    HOST_VISIBLE = 2

    HOST_COHERENT = 4

    HOST_CACHED = 8

    LAZILY_ALLOCATED = 16

    PROTECTED = 32

    DEVICE_COHERENT = 64

    DEVICE_UNCACHED = 128

    RDMA_CAPABLE = 256

class MemoryHeap:
    @property
    def size(self) -> int: ...

    @property
    def flags(self) -> MemoryHeapFlags: ...

    def __repr__(self) -> str: ...

class MemoryType:
    @property
    def heap_index(self) -> int: ...

    @property
    def property_flags(self) -> MemoryPropertyFlags: ...

    def __repr__(self) -> str: ...

class MemoryProperties:
    @property
    def memory_heaps(self) -> List[MemoryHeap]: ...

    @property
    def memory_types(self) -> List[MemoryType]: ...

    def __repr__(self) -> str: ...

class HeapStatistics:
    @property
    def block_count(self) -> int: ...

    @property
    def allocation_count(self) -> int: ...

    @property
    def block_bytes(self) -> int: ...

    @property
    def allocation_bytes(self) -> int: ...

    @property
    def usage(self) -> int: ...

    @property
    def budget(self) -> int: ...

    def __repr__(self) -> str: ...

class DeviceFeatures(enum.IntFlag):
    NONE = 0

    DYNAMIC_RENDERING = 1

    SYNCHRONIZATION_2 = 2

    DESCRIPTOR_INDEXING = 4

    SCALAR_BLOCK_LAYOUT = 8

    RAY_QUERY = 16

    RAY_PIPELINE = 32

    EXTERNAL_RESOURCES = 64

    HOST_QUERY_RESET = 128

    CALIBRATED_TIMESTAMPS = 256

    TIMELINE_SEMAPHORES = 512

    WIDE_LINES = 1024

class PhysicalDeviceType(enum.Enum):
    OTHER = 0

    INTEGRATED_GPU = 1

    DISCRETE_GPU = 2

    VIRTUAL_GPU = 3

    CPU = 4

class DeviceSparseProperties:
    @property
    def residency_standard_2d_block_shape(self) -> bool: ...

    @property
    def residency_standard_2d_multisample_block_shape(self) -> bool: ...

    @property
    def residency_standard_3d_block_shape(self) -> bool: ...

    @property
    def residency_aligned_mip_size(self) -> bool: ...

    @property
    def residency_non_resident_strict(self) -> bool: ...

class DeviceLimits:
    @property
    def max_image_dimension_1d(self) -> int: ...

    @property
    def max_image_dimension_2d(self) -> int: ...

    @property
    def max_image_dimension_3d(self) -> int: ...

    @property
    def max_image_dimension_cube(self) -> int: ...

    @property
    def max_image_array_layers(self) -> int: ...

    @property
    def max_texel_buffer_elements(self) -> int: ...

    @property
    def max_uniform_buffer_range(self) -> int: ...

    @property
    def max_storage_buffer_range(self) -> int: ...

    @property
    def max_push_constants_size(self) -> int: ...

    @property
    def max_memory_allocation_count(self) -> int: ...

    @property
    def max_sampler_allocation_count(self) -> int: ...

    @property
    def buffer_image_granularity(self) -> int: ...

    @property
    def sparse_address_space_size(self) -> int: ...

    @property
    def max_bound_descriptor_sets(self) -> int: ...

    @property
    def max_per_stage_descriptor_samplers(self) -> int: ...

    @property
    def max_per_stage_descriptor_uniform_buffers(self) -> int: ...

    @property
    def max_per_stage_descriptor_storage_buffers(self) -> int: ...

    @property
    def max_per_stage_descriptor_sampled_images(self) -> int: ...

    @property
    def max_per_stage_descriptor_storage_images(self) -> int: ...

    @property
    def max_per_stage_descriptor_input_attachments(self) -> int: ...

    @property
    def max_per_stage_resources(self) -> int: ...

    @property
    def max_descriptor_set_samplers(self) -> int: ...

    @property
    def max_descriptor_set_uniform_buffers(self) -> int: ...

    @property
    def max_descriptor_set_uniform_buffers_dynamic(self) -> int: ...

    @property
    def max_descriptor_set_storage_buffers(self) -> int: ...

    @property
    def max_descriptor_set_storage_buffers_dynamic(self) -> int: ...

    @property
    def max_descriptor_set_sampled_images(self) -> int: ...

    @property
    def max_descriptor_set_storage_images(self) -> int: ...

    @property
    def max_descriptor_set_input_attachments(self) -> int: ...

    @property
    def max_vertex_input_attributes(self) -> int: ...

    @property
    def max_vertex_input_bindings(self) -> int: ...

    @property
    def max_vertex_input_attribute_offset(self) -> int: ...

    @property
    def max_vertex_input_binding_stride(self) -> int: ...

    @property
    def max_vertex_output_components(self) -> int: ...

    @property
    def max_tessellation_generation_level(self) -> int: ...

    @property
    def max_tessellation_patch_size(self) -> int: ...

    @property
    def max_tessellation_control_per_vertex_input_components(self) -> int: ...

    @property
    def max_tessellation_control_per_vertex_output_components(self) -> int: ...

    @property
    def max_tessellation_control_per_patch_output_components(self) -> int: ...

    @property
    def max_tessellation_control_total_output_components(self) -> int: ...

    @property
    def max_tessellation_evaluation_input_components(self) -> int: ...

    @property
    def max_tessellation_evaluation_output_components(self) -> int: ...

    @property
    def max_geometry_shader_invocations(self) -> int: ...

    @property
    def max_geometry_input_components(self) -> int: ...

    @property
    def max_geometry_output_components(self) -> int: ...

    @property
    def max_geometry_output_vertices(self) -> int: ...

    @property
    def max_geometry_total_output_components(self) -> int: ...

    @property
    def max_fragment_input_components(self) -> int: ...

    @property
    def max_fragment_output_attachments(self) -> int: ...

    @property
    def max_fragment_dual_src_attachments(self) -> int: ...

    @property
    def max_fragment_combined_output_resources(self) -> int: ...

    @property
    def max_compute_shared_memory_size(self) -> int: ...

    @property
    def max_compute_work_group_count(self) -> tuple: ...

    @property
    def max_compute_work_group_invocations(self) -> int: ...

    @property
    def max_compute_work_group_size(self) -> tuple: ...

    @property
    def sub_pixel_precision_bits(self) -> int: ...

    @property
    def sub_texel_precision_bits(self) -> int: ...

    @property
    def mipmap_precision_bits(self) -> int: ...

    @property
    def max_draw_indexed_index_value(self) -> int: ...

    @property
    def max_draw_indirect_count(self) -> int: ...

    @property
    def max_sampler_lod_bias(self) -> float: ...

    @property
    def max_sampler_anisotropy(self) -> float: ...

    @property
    def max_viewports(self) -> int: ...

    @property
    def max_viewport_dimensions(self) -> tuple: ...

    @property
    def viewport_bounds_range(self) -> tuple: ...

    @property
    def viewport_sub_pixel_bits(self) -> int: ...

    @property
    def min_memory_map_alignment(self) -> int: ...

    @property
    def min_texel_buffer_offset_alignment(self) -> int: ...

    @property
    def min_uniform_buffer_offset_alignment(self) -> int: ...

    @property
    def min_storage_buffer_offset_alignment(self) -> int: ...

    @property
    def min_texel_offset(self) -> int: ...

    @property
    def max_texel_offset(self) -> int: ...

    @property
    def min_texel_gather_offset(self) -> int: ...

    @property
    def max_texel_gather_offset(self) -> int: ...

    @property
    def min_interpolation_offset(self) -> float: ...

    @property
    def max_interpolation_offset(self) -> float: ...

    @property
    def sub_pixel_interpolation_offset_bits(self) -> int: ...

    @property
    def max_framebuffer_width(self) -> int: ...

    @property
    def max_framebuffer_height(self) -> int: ...

    @property
    def max_framebuffer_layers(self) -> int: ...

    @property
    def framebuffer_color_sample_counts(self) -> int: ...

    @property
    def framebuffer_depth_sample_counts(self) -> int: ...

    @property
    def framebuffer_stencil_sample_counts(self) -> int: ...

    @property
    def framebuffer_no_attachments_sample_counts(self) -> int: ...

    @property
    def max_color_attachments(self) -> int: ...

    @property
    def sampled_image_color_sample_counts(self) -> int: ...

    @property
    def sampled_image_integer_sample_counts(self) -> int: ...

    @property
    def sampled_image_depth_sample_counts(self) -> int: ...

    @property
    def sampled_image_stencil_sample_counts(self) -> int: ...

    @property
    def storage_image_sample_counts(self) -> int: ...

    @property
    def max_sample_mask_words(self) -> int: ...

    @property
    def timestamp_compute_and_graphics(self) -> int: ...

    @property
    def timestamp_period(self) -> float: ...

    @property
    def max_clip_distances(self) -> int: ...

    @property
    def max_cull_distances(self) -> int: ...

    @property
    def max_combined_clip_and_cull_distances(self) -> int: ...

    @property
    def discrete_queue_priorities(self) -> int: ...

    @property
    def point_size_range(self) -> tuple: ...

    @property
    def line_width_range(self) -> tuple: ...

    @property
    def point_size_granularity(self) -> float: ...

    @property
    def line_width_granularity(self) -> float: ...

    @property
    def strict_lines(self) -> int: ...

    @property
    def standard_sample_locations(self) -> int: ...

    @property
    def optimal_buffer_copy_offset_alignment(self) -> int: ...

    @property
    def optimal_buffer_copy_row_pitch_alignment(self) -> int: ...

    @property
    def non_coherent_atom_size(self) -> int: ...

class DeviceProperties:
    @property
    def limits(self) -> DeviceLimits: ...

    @property
    def sparse_properties(self) -> DeviceSparseProperties: ...

    @property
    def api_version(self) -> int: ...

    @property
    def driver_version(self) -> int: ...

    @property
    def vendor_id(self) -> int: ...

    @property
    def device_id(self) -> int: ...

    @property
    def device_type(self) -> PhysicalDeviceType: ...

    @property
    def device_name(self) -> str: ...

    @property
    def pipeline_cache_uuid(self) -> bytes: ...

class Context:
    def __init__(self, version: Tuple[int, int] = (1, 1), required_features: DeviceFeatures = DeviceFeatures.SYNCHRONIZATION_2|DYNAMIC_RENDERING, optional_features: DeviceFeatures = DeviceFeatures.NONE, presentation: bool = True, preferred_frames_in_flight: int = 2, vsync: bool = True, force_physical_device_index: int = 4294967295, prefer_discrete_gpu: bool = True, enable_debug_utils: bool = False, enable_validation_layer: bool = False, enable_gpu_based_validation: bool = False, enable_synchronization_validation: bool = False) -> None: ...

    def sync_commands(self) -> CommandsManager: ...

    @property
    def sync_command_buffer(self) -> CommandBuffer: ...

    def submit_sync(self) -> None: ...

    def wait_idle(self) -> None: ...

    @property
    def instance_version(self) -> tuple: ...

    @property
    def version(self) -> tuple: ...

    @property
    def device_features(self) -> DeviceFeatures: ...

    @property
    def device_properties(self) -> DeviceProperties: ...

    @property
    def memory_properties(self) -> MemoryProperties: ...

    @property
    def heap_statistics(self) -> List[HeapStatistics]: ...

    @property
    def has_compute_queue(self) -> bool: ...

    @property
    def has_transfer_queue(self) -> bool: ...

    @property
    def graphics_queue_family_index(self) -> int: ...

    @property
    def compute_queue_family_index(self) -> int: ...

    @property
    def transfer_queue_family_index(self) -> int: ...

    @property
    def timestamp_period_ns(self) -> float: ...

    def reset_query_pool(self, arg: QueryPool, /) -> None: ...

    def get_calibrated_timestamps(self) -> Tuple[int, int]: ...

    @property
    def queue(self) -> Queue: ...

    @property
    def compute_queue(self) -> Queue: ...

    @property
    def transfer_queue(self) -> Queue: ...

class CommandsManager:
    def __enter__(self) -> CommandBuffer: ...

    def __exit__(self, exc_type: Optional[object], exc_val: Optional[object], exc_tb: Optional[object]) -> None: ...

class Frame:
    @property
    def command_buffer(self) -> CommandBuffer: ...

    @property
    def image(self) -> Image: ...

    def compute_commands(self, wait_semaphores: Sequence[Tuple[Semaphore, PipelineStageFlags]] = [], wait_timeline_values: Sequence[int] = [], signal_semaphores: Sequence[Semaphore] = [], signal_timeline_values: Sequence[int] = []) -> CommandsManager: ...

    @property
    def compute_command_buffer(self) -> Optional[CommandBuffer]: ...

    def transfer_commands(self, wait_semaphores: Sequence[Tuple[Semaphore, PipelineStageFlags]] = [], wait_timeline_values: Sequence[int] = [], signal_semaphores: Sequence[Semaphore] = [], signal_timeline_values: Sequence[int] = []) -> CommandsManager: ...

    @property
    def transfer_command_buffer(self) -> Optional[CommandBuffer]: ...

class Window:
    def __init__(self, ctx: Context, title: str, width: int, height: int, x: Optional[int] = None, y: Optional[int] = None) -> None: ...

    def should_close(self) -> bool: ...

    def get_modifiers_state(self) -> Modifiers: ...

    def set_callbacks(self, draw: Callable[[], None], mouse_move_event: Callable[[Tuple[int, int]], None] | None = None, mouse_button_event: Callable[[Tuple[int, int], MouseButton, Action, Modifiers], None] | None = None, mouse_scroll_event: Callable[[Tuple[int, int], Tuple[int, int]], None] | None = None, key_event: Callable[[Key, Action, Modifiers], None] | None = None) -> None: ...

    def reset_callbacks(self) -> None: ...

    def update_swapchain(self) -> SwapchainStatus: ...

    def begin_frame(self) -> Frame: ...

    def end_frame(self, frame: Frame, additional_wait_semaphores: Sequence[Tuple[Semaphore, PipelineStageFlags]] = [], additional_wait_timeline_values: Sequence[int] = [], additional_signal_semaphores: Sequence[Semaphore] = [], additional_signal_timeline_values: Sequence[int] = []) -> None: ...

    def frame(self, additional_wait_semaphores: Sequence[Tuple[Semaphore, PipelineStageFlags]] = [], additional_wait_timeline_values: Sequence[int] = [], additional_signal_semaphores: Sequence[Semaphore] = [], additional_signal_timeline_values: Sequence[int] = []) -> WindowFrame: ...

    def post_empty_event(self) -> None: ...

    @property
    def swapchain_format(self) -> Format: ...

    @property
    def num_swapchain_images(self) -> int: ...

    @property
    def fb_width(self) -> int: ...

    @property
    def fb_height(self) -> int: ...

    @property
    def num_frames(self) -> int: ...

class WindowFrame:
    def __enter__(self) -> Frame: ...

    def __exit__(self, exc_type: Optional[object], exc_val: Optional[object], exc_tb: Optional[object]) -> None: ...

class GuiFrame:
    def __enter__(self) -> None: ...

    def __exit__(self, exc_type: Optional[object], exc_val: Optional[object], exc_tb: Optional[object]) -> None: ...

class Gui:
    def __init__(self, window: Window) -> None: ...

    def begin_frame(self) -> None: ...

    def end_frame(self) -> None: ...

    def render(self, frame: CommandBuffer) -> None: ...

    def frame(self) -> GuiFrame: ...

    def set_ini_filename(self, arg: str, /) -> None: ...

class Action(enum.Enum):
    NONE = 4294967295

    RELEASE = 0

    PRESS = 1

    REPEAT = 2

class Key(enum.Enum):
    SPACE = 32

    APOSTROPHE = 39

    COMMA = 44

    MINUS = 45

    PERIOD = 46

    SLASH = 47

    N0 = 48

    N1 = 49

    N2 = 50

    N3 = 51

    N4 = 52

    N5 = 53

    N6 = 54

    N7 = 55

    N8 = 56

    N9 = 57

    SEMICOLON = 59

    EQUAL = 61

    A = 65

    B = 66

    C = 67

    D = 68

    E = 69

    F = 70

    G = 71

    H = 72

    I = 73

    J = 74

    K = 75

    L = 76

    M = 77

    N = 78

    O = 79

    P = 80

    Q = 81

    R = 82

    S = 83

    T = 84

    U = 85

    V = 86

    W = 87

    X = 88

    Y = 89

    Z = 90

    LEFT_BRACKET = 91

    BACKSLASH = 92

    RIGHT_BRACKET = 93

    GRAVE_ACCENT = 96

    WORLD_1 = 161

    WORLD_2 = 162

    ESCAPE = 256

    ENTER = 257

    TAB = 258

    BACKSPACE = 259

    INSERT = 260

    DELETE = 261

    RIGHT = 262

    LEFT = 263

    DOWN = 264

    UP = 265

    PAGE_UP = 266

    PAGE_DOWN = 267

    HOME = 268

    END = 269

    CAPS_LOCK = 280

    SCROLL_LOCK = 281

    NUM_LOCK = 282

    PRINT_SCREEN = 283

    PAUSE = 284

    F1 = 290

    F2 = 291

    F3 = 292

    F4 = 293

    F5 = 294

    F6 = 295

    F7 = 296

    F8 = 297

    F9 = 298

    F10 = 299

    F11 = 300

    F12 = 301

    F13 = 302

    F14 = 303

    F15 = 304

    F16 = 305

    F17 = 306

    F18 = 307

    F19 = 308

    F20 = 309

    F21 = 310

    F22 = 311

    F23 = 312

    F24 = 313

    F25 = 314

    KP0 = 320

    KP1 = 321

    KP2 = 322

    KP3 = 323

    KP4 = 324

    KP5 = 325

    KP6 = 326

    KP7 = 327

    KP8 = 328

    KP9 = 329

    KP_DECIMAL = 330

    KP_DIVIDE = 331

    KP_MULTIPLY = 332

    KP_SUBTRACT = 333

    KP_ADD = 334

    KP_ENTER = 335

    KP_EQUAL = 336

    LEFT_SHIFT = 340

    LEFT_CONTROL = 341

    LEFT_ALT = 342

    LEFT_SUPER = 343

    RIGHT_SHIFT = 344

    RIGHT_CONTROL = 345

    RIGHT_ALT = 346

    RIGHT_SUPER = 347

    MENU = 348

class MouseButton(enum.Enum):
    NONE = 4294967295

    LEFT = 0

    RIGHT = 1

    MIDDLE = 2

class Modifiers(enum.IntFlag):
    NONE = 0

    SHIFT = 1

    CTRL = 2

    ALT = 4

    SUPER = 8

class AllocType(enum.Enum):
    HOST = 0

    HOST_WRITE_COMBINING = 1

    DEVICE_MAPPED_WITH_FALLBACK = 2

    DEVICE_MAPPED = 3

    DEVICE = 4

    DEVICE_DEDICATED = 5

class BufferUsageFlags(enum.IntFlag):
    TRANSFER_SRC = 1

    TRANSFER_DST = 2

    UNIFORM = 16

    STORAGE = 32

    INDEX = 64

    VERTEX = 128

    INDIRECT = 256

    ACCELERATION_STRUCTURE_INPUT = 524288

    ACCELERATION_STRUCTURE_STORAGE = 1048576

    SHADER_DEVICE_ADDRESS = 131072

class ImageUsageFlags(enum.IntFlag):
    TRANSFER_SRC = 1

    TRANSFER_DST = 2

    SAMPLED = 4

    STORAGE = 8

    COLOR_ATTACHMENT = 16

    DEPTH_STENCIL_ATTACHMENT = 32

    TRANSIENT_ATTACHMENT = 64

    INPUT_ATTACHMENT = 128

    VIDEO_DECODE_DST = 1024

    VIDEO_DECODE_SRC = 2048

    VIDEO_DECODE_DPB = 4096

    FRAGMENT_DENSITY_MAP = 512

    FRAGMENT_SHADING_RATE_ATTACHMENT = 256

    HOST_TRANSFER = 4194304

    VIDEO_ENCODE_DST = 8192

    VIDEO_ENCODE_SRC = 16384

    VIDEO_ENCODE_DPB = 32768

    ATTACHMENT_FEEDBACK_LOOP = 524288

    INVOCATION_MASK = 262144

    SAMPLE_WEIGHT = 1048576

    SAMPLE_BLOCK_MATCH = 2097152

    SHADING_RATE_IMAGE = 256

class CompareOp(enum.Enum):
    NEVER = 0

    LESS = 1

    EQUAL = 2

    LESS_OR_EQUAL = 3

    GREATER = 4

    NOT_EQUAL = 5

    GREATER_OR_EQUAL = 6

    ALWAYS = 7

class Filter(enum.Enum):
    NEAREST = 0

    LINEAR = 1

    CUBIC = 1000015000

class SamplerMipmapMode(enum.Enum):
    NEAREST = 0

    LINEAR = 1

class SamplerAddressMode(enum.Enum):
    REPEAT = 0

    MIRRORED_REPEAT = 1

    CLAMP_TO_EDGE = 2

    CLAMP_TO_BORDER = 3

    MIRROR_CLAMP_TO_EDGE = 4

class GfxObject:
    @property
    def ctx(self) -> Context: ...

class Queue(GfxObject):
    def __repr__(self) -> str: ...

    def submit(self, command_buffer: CommandBuffer, wait_semaphores: Sequence[Tuple[Semaphore, PipelineStageFlags]] = [], wait_timeline_values: Sequence[int] = [], signal_semaphores: Sequence[Semaphore] = [], signal_timeline_values: Sequence[int] = [], fence: Optional[Fence] = None) -> None: ...

    def begin_label(self, name: str, color: Optional[Tuple[float, float, float, float]] = None) -> None: ...

    def end_label(self) -> None: ...

    def insert_label(self, name: str, color: Optional[Tuple[float, float, float, float]] = None) -> None: ...

class QueryType(enum.Enum):
    OCCLUSION = 0

    PIPELINE_STATISTICS = 1

    TIMESTAMP = 2

    RESULT_STATUS_ONLY = 1000023000

    TRANSFORM_FEEDBACK_STREAM = 1000028004

    PERFORMANCE_QUERY = 1000116000

    ACCELERATION_STRUCTURE_COMPACTED_SIZE = 1000150000

    ACCELERATION_STRUCTURE_SERIALIZATION_SIZE = 1000150001

    VIDEO_ENCODE_FEEDBACK = 1000299000

    MESH_PRIMITIVES_GENERATED = 1000328000

    PRIMITIVES_GENERATED = 1000382000

    ACCELERATION_STRUCTURE_SERIALIZATION_BOTTOM_LEVEL_POINTERS = 1000386000

    ACCELERATION_STRUCTURE_SIZE = 1000386001

    MICROMAP_SERIALIZATION_SIZE = 1000396000

    MICROMAP_COMPACTED_SIZE = 1000396001

class QueryPool(GfxObject):
    def __init__(self, ctx: Context, type: QueryType, count: int, name: Optional[str] = None) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def type(self) -> QueryType: ...

    @property
    def count(self) -> int: ...

    def wait_results(self, first: int, count: int) -> List[int]: ...

class AllocInfo:
    def __repr__(self) -> str: ...

    @property
    def memory_type(self) -> int: ...

    @property
    def offset(self) -> int: ...

    @property
    def size(self) -> int: ...

    @property
    def is_dedicated(self) -> bool: ...

class Buffer(GfxObject):
    def __init__(self, ctx: Context, size: int, usage_flags: BufferUsageFlags, alloc_type: AllocType, name: Optional[str] = None) -> None: ...

    def __repr__(self) -> str: ...

    def destroy(self) -> None: ...

    @staticmethod
    def from_data(ctx: Context, data: object, usage_flags: BufferUsageFlags, alloc_type: AllocType, name: Optional[str] = None) -> Buffer: ...

    @property
    def data(self) -> memoryview: ...

    @property
    def is_mapped(self) -> bool: ...

    @property
    def address(self) -> int: ...

    @property
    def size(self) -> int: ...

    @property
    def alloc(self) -> AllocInfo: ...

class ExternalBuffer(Buffer):
    def __init__(self, ctx: Context, size: int, usage_flags: BufferUsageFlags, alloc_type: AllocType, name: Optional[str] = None) -> None: ...

    def __repr__(self) -> str: ...

    def destroy(self) -> None: ...

    @property
    def handle(self) -> int: ...

class Image(GfxObject):
    def __init__(self, ctx: Context, width: int, height: int, format: Format, usage_flags: ImageUsageFlags, alloc_type: AllocType, samples: int = 1, name: Optional[str] = None) -> None: ...

    def __repr__(self) -> str: ...

    def destroy(self) -> None: ...

    @staticmethod
    def from_data(ctx: Context, data: object, usage: ImageLayout, width: int, height: int, format: Format, usage_flags: ImageUsageFlags, alloc_type: AllocType, samples: int = 1, name: Optional[str] = None) -> Image: ...

    @property
    def width(self) -> int: ...

    @property
    def height(self) -> int: ...

    @property
    def format(self) -> Format: ...

    @property
    def samples(self) -> int: ...

    @property
    def alloc(self) -> AllocInfo: ...

class Sampler(GfxObject):
    def __init__(self, ctx: Context, min_filter: Filter = Filter.NEAREST, mag_filter: Filter = Filter.NEAREST, mipmap_mode: SamplerMipmapMode = SamplerMipmapMode.NEAREST, mip_lod_bias: float = 0.0, min_lod: float = 0.0, max_lod: float = 1000.0, u: SamplerAddressMode = SamplerAddressMode.REPEAT, v: SamplerAddressMode = SamplerAddressMode.REPEAT, w: SamplerAddressMode = SamplerAddressMode.REPEAT, anisotroy_enabled: bool = False, max_anisotropy: float = 0.0, compare_enable: bool = False, compare_op: CompareOp = CompareOp.ALWAYS, name: Optional[str] = None) -> None: ...

    def __repr__(self) -> str: ...

    def destroy(self) -> None: ...

class AccelerationStructure(GfxObject):
    def __init__(self, ctx: Context, meshes: Sequence[AccelerationStructureMesh], prefer_fast_build: bool = False, name: Optional[str] = None) -> None: ...

    def __repr__(self) -> str: ...

    def destroy(self) -> None: ...

class Fence(GfxObject):
    def __init__(self, ctx: Context, signaled: bool = False, name: Optional[str] = None) -> None: ...

    def __repr__(self) -> str: ...

    def destroy(self) -> None: ...

    def is_signaled(self) -> bool: ...

    def wait(self) -> None: ...

    def resest(self) -> None: ...

    def wait_and_reset(self) -> None: ...

class Semaphore(GfxObject):
    def __init__(self, ctx: Context, name: Optional[str] = None) -> None: ...

    def __repr__(self) -> str: ...

    def destroy(self) -> None: ...

class TimelineSemaphore(Semaphore):
    def __init__(self, ctx: Context, initial_value: int = 0, name: Optional[str] = None) -> None: ...

    def __repr__(self) -> str: ...

    def get_value(self) -> int: ...

    def signal(self, value: int) -> None: ...

    def wait(self, value: int) -> None: ...

class ExternalSemaphore(Semaphore):
    def __init__(self, ctx: Context, name: Optional[str] = None) -> None: ...

    def __repr__(self) -> str: ...

    def destroy(self) -> None: ...

    @property
    def handle(self) -> int: ...

class ExternalTimelineSemaphore(TimelineSemaphore):
    def __init__(self, ctx: Context, initial_value: int = 0, name: Optional[str] = None) -> None: ...

    def __repr__(self) -> str: ...

    def destroy(self) -> None: ...

    @property
    def handle(self) -> int: ...

class MemoryUsage(enum.Enum):
    NONE = 0

    HOST_WRITE = 1

    TRANSFER_SRC = 2

    TRANSFER_DST = 3

    VERTEX_INPUT = 4

    VERTEX_SHADER_UNIFORM = 5

    GEOMETRY_SHADER_UNIFORM = 6

    FRAGMENT_SHADER_UNIFORM = 7

    COMPUTE_SHADER_UNIFORM = 8

    ANY_SHADER_UNIFORM = 9

    IMAGE = 10

    IMAGE_READ_ONLY = 11

    IMAGE_WRITE_ONLY = 12

    SHADER_READ_ONLY = 13

    COLOR_ATTACHMENT = 14

    COLOR_ATTACHMENT_WRITE_ONLY = 15

    DEPTH_STENCIL_ATTACHMENT = 16

    DEPTH_STENCIL_ATTACHMENT_READ_ONLY = 17

    DEPTH_STENCIL_ATTACHMENT_WRITE_ONLY = 18

    PRESENT = 19

    ALL = 20

class ImageLayout(enum.Enum):
    UNDEFINED = 0

    GENERAL = 1

    COLOR_ATTACHMENT_OPTIMAL = 2

    DEPTH_STENCIL_ATTACHMENT_OPTIMAL = 3

    DEPTH_STENCIL_READ_ONLY_OPTIMAL = 4

    SHADER_READ_ONLY_OPTIMAL = 5

    TRANSFER_SRC_OPTIMAL = 6

    TRANSFER_DST_OPTIMAL = 7

    PREINITIALIZED = 8

    DEPTH_READ_ONLY_STENCIL_ATTACHMENT_OPTIMAL = 1000117000

    DEPTH_ATTACHMENT_STENCIL_READ_ONLY_OPTIMAL = 1000117001

    DEPTH_ATTACHMENT_OPTIMAL = 1000241000

    DEPTH_READ_ONLY_OPTIMAL = 1000241001

    STENCIL_ATTACHMENT_OPTIMAL = 1000241002

    STENCIL_READ_ONLY_OPTIMAL = 1000241003

    READ_ONLY_OPTIMAL = 1000314000

    ATTACHMENT_OPTIMAL = 1000314001

    RENDERING_LOCAL_READ = 1000232000

    PRESENT_SRC = 1000001002

    VIDEO_DECODE_DST = 1000024000

    VIDEO_DECODE_SRC = 1000024001

    VIDEO_DECODE_DPB = 1000024002

    SHARED_PRESENT = 1000111000

    FRAGMENT_DENSITY_MAP_OPTIMAL_EXT = 1000218000

    FRAGMENT_SHADING_RATE_ATTACHMENT_OPTIMAL = 1000164003

    VIDEO_ENCODE_DST = 1000299000

    VIDEO_ENCODE_SRC = 1000299001

    VIDEO_ENCODE_DPB = 1000299002

    ATTACHMENT_FEEDBACK_LOOP_OPTIMAL_EXT = 1000339000

    VIDEO_ENCODE_QUANTIZATION_MAP = 1000553000

    SHADING_RATE_OPTIMAL = 1000164003

class ResolveMode(enum.Enum):
    NONE = 0

    SAMPLE_ZERO = 1

    AVERAGE = 2

    MIN = 4

    MAX = 8

class PipelineStageFlags(enum.IntFlag):
    TOP_OF_PIPE = 1

    DRAW_INDIRECT = 2

    VERTEX_INPUT = 4

    VERTEX_SHADER = 8

    TESSELLATION_CONTROL_SHADER = 16

    TESSELLATION_EVALUATION_SHADER = 32

    GEOMETRY_SHADER = 64

    FRAGMENT_SHADER = 128

    EARLY_FRAGMENT_TESTS = 256

    LATE_FRAGMENT_TESTS = 512

    COLOR_ATTACHMENT_OUTPUT = 1024

    COMPUTE_SHADER = 2048

    TRANSFER = 4096

    BOTTOM_OF_PIPE = 8192

    HOST = 16384

    ALL_GRAPHICS = 32768

    ALL_COMMANDS = 65536

    TRANSFORM_FEEDBACK = 16777216

    CONDITIONAL_RENDERING = 262144

    ACCELERATION_STRUCTURE_BUILD = 33554432

    RAY_TRACING_SHADER = 2097152

    FRAGMENT_DENSITY_PROCESS = 8388608

    FRAGMENT_SHADING_RATE_ATTACHMENT = 4194304

    TASK_SHADER = 524288

    MESH_SHADER = 1048576

class LoadOp(enum.Enum):
    LOAD = 0

    CLEAR = 1

    DONT_CARE = 2

class StoreOp(enum.Enum):
    STORE = 0

    DONT_CARE = 1

    NONE = 1000301000

class RenderingAttachment:
    def __init__(self, image: Image, load_op: LoadOp = LoadOp.LOAD, store_op: StoreOp = StoreOp.STORE, clear: Sequence[float] = [0.0, 0.0, 0.0, 0.0], resolve_image: Optional[Image] = None, resolve_mode: ResolveMode = ResolveMode.NONE) -> None: ...

class DepthAttachment:
    def __init__(self, image: Image, load_op: LoadOp = LoadOp.LOAD, store_op: StoreOp = StoreOp.STORE, clear: float = 0.0) -> None: ...

class RenderingManager:
    def __enter__(self) -> None: ...

    def __exit__(self, exc_type: Optional[object], exc_val: Optional[object], exc_tb: Optional[object]) -> None: ...

class ImageAspectFlags(enum.IntFlag):
    NONE = 0

    COLOR = 1

    DEPTH = 2

    STENCIL = 4

    METADATA = 8

    PLANE_0 = 16

    PLANE_1 = 32

    PLANE_2 = 64

    MEMORY_PLANE_0 = 128

    MEMORY_PLANE_1 = 256

    MEMORY_PLANE_2 = 512

    MEMORY_PLANE_3 = 1024

class IndexType(enum.Enum):
    UINT16 = 0

    UINT32 = 1

    UINT8 = 1000265000

    NONE_KHR = 1000165000

    UINT8_KHR = 1000265000

class CommandBuffer(GfxObject):
    def __init__(self, ctx: Context, queue_family_index: Optional[int] = None, name: Optional[str] = None) -> None: ...

    def __enter__(self) -> CommandBuffer: ...

    def __exit__(self, exc_type: Optional[object], exc_val: Optional[object], exc_tb: Optional[object]) -> None: ...

    def __repr__(self) -> str: ...

    def destroy(self) -> None: ...

    def begin(self) -> None: ...

    def end(self) -> None: ...

    def memory_barrier(self, src: MemoryUsage, dst: MemoryUsage) -> None: ...

    def buffer_barrier(self, buffer: Buffer, src: MemoryUsage, dst: MemoryUsage, src_queue_family_index: int = 4294967295, dst_queue_family_index: int = 4294967295) -> None: ...

    def image_barrier(self, image: Image, dst_layout: ImageLayout, src_usage: MemoryUsage, dst_usage: MemoryUsage, src_queue_family_index: int = 4294967295, dst_queue_family_index: int = 4294967295, aspect_mask: ImageAspectFlags = ImageAspectFlags.COLOR, undefined: bool = False) -> None: ...

    def begin_rendering(self, render_area: Sequence[int], color_attachments: Sequence[RenderingAttachment], depth: Optional[DepthAttachment] = None) -> None: ...

    def end_rendering(self) -> None: ...

    def rendering(self, render_area: Sequence[int], color_attachments: Sequence[RenderingAttachment], depth: Optional[DepthAttachment] = None) -> RenderingManager: ...

    def set_viewport(self, viewport: Sequence[int]) -> None: ...

    def set_scissors(self, scissors: Sequence[int]) -> None: ...

    def bind_pipeline(self, pipeline: Union[GraphicsPipeline, ComputePipeline]) -> None: ...

    def bind_descriptor_sets(self, pipeline: Union[GraphicsPipeline, ComputePipeline], descriptor_sets: Sequence[DescriptorSet], dynamic_offsets: Sequence[int] = [], first_descriptor_set: int = 0) -> None: ...

    def push_constants(self, pipeline: Union[GraphicsPipeline, ComputePipeline], push_constants: bytes, offset: int = 0) -> None: ...

    def bind_compute_pipeline(self, pipeline: ComputePipeline, descriptor_sets: Sequence[DescriptorSet] = [], dynamic_offsets: Sequence[int] = [], first_descriptor_set: int = 0, push_constants: Optional[bytes] = None, push_constants_offset: int = 0) -> None: ...

    def bind_vertex_buffers(self, vertex_buffers: Sequence[Union[Buffer, Tuple[Buffer, int]]], first_vertex_buffer_binding: int = 0) -> None: ...

    def bind_index_buffers(self, index_buffer: Buffer, index_buffer_offset: int = 0, index_type: IndexType = IndexType.UINT32) -> None: ...

    def bind_graphics_pipeline(self, pipeline: GraphicsPipeline, descriptor_sets: Sequence[DescriptorSet] = [], dynamic_offsets: Sequence[int] = [], first_descriptor_set: int = 0, push_constants: Optional[bytes] = None, push_constants_offset: int = 0, vertex_buffers: Sequence[Union[Buffer, Tuple[Buffer, int]]] = [], first_vertex_buffer_binding: int = 0, index_buffer: Optional[Buffer] = None, index_buffer_offset: int = 0, index_type: IndexType = IndexType.UINT32) -> None: ...

    def dispatch(self, groups_x: int, groups_y: int = 1, groups_z: int = 1) -> None: ...

    def draw(self, num_vertices: int, num_instances: int = 1, first_vertex: int = 0, first_instance: int = 0) -> None: ...

    def draw_indexed(self, num_indices: int, num_instances: int = 1, first_index: int = 0, vertex_offset: int = 0, first_instance: int = 0) -> None: ...

    def copy_buffer(self, src: Buffer, dst: Buffer) -> None: ...

    def copy_buffer_range(self, src: Buffer, dst: Buffer, size: int, src_offset: int = 0, dst_offset: int = 0) -> None: ...

    def copy_image_to_buffer(self, image: Image, buffer: Buffer, buffer_offset_in_bytes: int = 0) -> None: ...

    def copy_buffer_to_image(self, buffer: Buffer, image: Image, buffer_offset_in_bytes: int = 0) -> None: ...

    def copy_buffer_to_image_range(self, buffer: Buffer, image: Image, image_width: int, image_height: int, image_x: int = 0, image_y: int = 0, buffer_offset_in_bytes: int = 0, buffer_row_stride_in_texels: int = 0) -> None: ...

    def clear_color_image(self, image: Image, color: Sequence[float]) -> None: ...

    def clear_depth_stencil_image(self, image: Image, depth: Optional[float] = None, stencil: Optional[int] = None) -> None: ...

    def blit_image(self, src: Image, dst: Image, filter: Filter = Filter.NEAREST, src_aspect: ImageAspectFlags = ImageAspectFlags.COLOR, dst_aspect: ImageAspectFlags = ImageAspectFlags.COLOR) -> None: ...

    def blit_image_range(self, src: Image, src_width: Image, src_height: Filter, dst: int, dst_width: int, dst_height: int, filter: int = Filter.NEAREST, src_x: ImageAspectFlags = 0, src_y: int = 0, src_aspect: int = ImageAspectFlags.COLOR, dst_x: int = 0, dst_y: int = 0, dst_aspect: ImageAspectFlags = ImageAspectFlags.COLOR) -> None: ...

    def resolve_image(self, src: Image, dst: Image, src_aspect: ImageAspectFlags = ImageAspectFlags.COLOR, dst_aspect: ImageAspectFlags = ImageAspectFlags.COLOR) -> None: ...

    def resolve_image_range(self, src: Image, dst: Image, width: int, height: int, src_x: int = 0, src_y: int = 0, src_aspect: ImageAspectFlags = ImageAspectFlags.COLOR, dst_x: int = 0, dst_y: int = 0, dst_aspect: ImageAspectFlags = ImageAspectFlags.COLOR) -> None: ...

    def reset_query_pool(self, pool: QueryPool) -> None: ...

    def write_timestamp(self, pool: QueryPool, index: int, stage: int) -> None: ...

    def begin_label(self, name: str, color: Optional[Tuple[float, float, float, float]] = None) -> None: ...

    def end_label(self) -> None: ...

    def insert_label(self, name: str, color: Optional[Tuple[float, float, float, float]] = None) -> None: ...

    def set_line_width(self, width: float) -> None: ...

class Shader(GfxObject):
    def __init__(self, ctx: Context, code: bytes, name: Optional[str] = None) -> None: ...

    def __repr__(self) -> str: ...

    def destroy(self) -> None: ...

class Stage(enum.IntFlag):
    VERTEX = 1

    TESSELLATION_CONTROL = 2

    TESSELLATION_EVALUATION = 4

    GEOMETRY = 8

    FRAGMENT = 16

    COMPUTE = 32

    RAYGEN = 256

    ANY_HIT = 512

    CLOSEST_HIT = 1024

    MISS = 2048

    INTERSECTION = 4096

    CALLABLE = 8192

    TASK_EXT = 64

    MESH_EXT = 128

class PipelineStage:
    def __init__(self, shader: Shader, stage: Stage, entry: str = 'main') -> None: ...

class VertexInputRate(enum.Enum):
    VERTEX = 0

    INSTANCE = 0

class VertexBinding:
    def __init__(self, binding: int, stride: int, input_rate: VertexInputRate = VertexInputRate.VERTEX) -> None: ...

class FormatInfo:
    @property
    def size(self) -> int: ...

    @property
    def channels(self) -> int: ...

    @property
    def size_of_block_in_bytes(self) -> int: ...

    @property
    def block_side_in_pixels(self) -> int: ...

    def __repr__(self) -> str: ...

def get_format_info(arg: Format, /) -> FormatInfo: ...

class Format(enum.Enum):
    UNDEFINED = 0

    R4G4_UNORM_PACK8 = 1

    R4G4B4A4_UNORM_PACK16 = 2

    B4G4R4A4_UNORM_PACK16 = 3

    R5G6B5_UNORM_PACK16 = 4

    B5G6R5_UNORM_PACK16 = 5

    R5G5B5A1_UNORM_PACK16 = 6

    B5G5R5A1_UNORM_PACK16 = 7

    A1R5G5B5_UNORM_PACK16 = 8

    R8_UNORM = 9

    R8_SNORM = 10

    R8_USCALED = 11

    R8_SSCALED = 12

    R8_UINT = 13

    R8_SINT = 14

    R8_SRGB = 15

    R8G8_UNORM = 16

    R8G8_SNORM = 17

    R8G8_USCALED = 18

    R8G8_SSCALED = 19

    R8G8_UINT = 20

    R8G8_SINT = 21

    R8G8_SRGB = 22

    R8G8B8_UNORM = 23

    R8G8B8_SNORM = 24

    R8G8B8_USCALED = 25

    R8G8B8_SSCALED = 26

    R8G8B8_UINT = 27

    R8G8B8_SINT = 28

    R8G8B8_SRGB = 29

    B8G8R8_UNORM = 30

    B8G8R8_SNORM = 31

    B8G8R8_USCALED = 32

    B8G8R8_SSCALED = 33

    B8G8R8_UINT = 34

    B8G8R8_SINT = 35

    B8G8R8_SRGB = 36

    R8G8B8A8_UNORM = 37

    R8G8B8A8_SNORM = 38

    R8G8B8A8_USCALED = 39

    R8G8B8A8_SSCALED = 40

    R8G8B8A8_UINT = 41

    R8G8B8A8_SINT = 42

    R8G8B8A8_SRGB = 43

    B8G8R8A8_UNORM = 44

    B8G8R8A8_SNORM = 45

    B8G8R8A8_USCALED = 46

    B8G8R8A8_SSCALED = 47

    B8G8R8A8_UINT = 48

    B8G8R8A8_SINT = 49

    B8G8R8A8_SRGB = 50

    A8B8G8R8_UNORM_PACK32 = 51

    A8B8G8R8_SNORM_PACK32 = 52

    A8B8G8R8_USCALED_PACK32 = 53

    A8B8G8R8_SSCALED_PACK32 = 54

    A8B8G8R8_UINT_PACK32 = 55

    A8B8G8R8_SINT_PACK32 = 56

    A8B8G8R8_SRGB_PACK32 = 57

    A2R10G10B10_UNORM_PACK32 = 58

    A2R10G10B10_SNORM_PACK32 = 59

    A2R10G10B10_USCALED_PACK32 = 60

    A2R10G10B10_SSCALED_PACK32 = 61

    A2R10G10B10_UINT_PACK32 = 62

    A2R10G10B10_SINT_PACK32 = 63

    A2B10G10R10_UNORM_PACK32 = 64

    A2B10G10R10_SNORM_PACK32 = 65

    A2B10G10R10_USCALED_PACK32 = 66

    A2B10G10R10_SSCALED_PACK32 = 67

    A2B10G10R10_UINT_PACK32 = 68

    A2B10G10R10_SINT_PACK32 = 69

    R16_UNORM = 70

    R16_SNORM = 71

    R16_USCALED = 72

    R16_SSCALED = 73

    R16_UINT = 74

    R16_SINT = 75

    R16_SFLOAT = 76

    R16G16_UNORM = 77

    R16G16_SNORM = 78

    R16G16_USCALED = 79

    R16G16_SSCALED = 80

    R16G16_UINT = 81

    R16G16_SINT = 82

    R16G16_SFLOAT = 83

    R16G16B16_UNORM = 84

    R16G16B16_SNORM = 85

    R16G16B16_USCALED = 86

    R16G16B16_SSCALED = 87

    R16G16B16_UINT = 88

    R16G16B16_SINT = 89

    R16G16B16_SFLOAT = 90

    R16G16B16A16_UNORM = 91

    R16G16B16A16_SNORM = 92

    R16G16B16A16_USCALED = 93

    R16G16B16A16_SSCALED = 94

    R16G16B16A16_UINT = 95

    R16G16B16A16_SINT = 96

    R16G16B16A16_SFLOAT = 97

    R32_UINT = 98

    R32_SINT = 99

    R32_SFLOAT = 100

    R32G32_UINT = 101

    R32G32_SINT = 102

    R32G32_SFLOAT = 103

    R32G32B32_UINT = 104

    R32G32B32_SINT = 105

    R32G32B32_SFLOAT = 106

    R32G32B32A32_UINT = 107

    R32G32B32A32_SINT = 108

    R32G32B32A32_SFLOAT = 109

    R64_UINT = 110

    R64_SINT = 111

    R64_SFLOAT = 112

    R64G64_UINT = 113

    R64G64_SINT = 114

    R64G64_SFLOAT = 115

    R64G64B64_UINT = 116

    R64G64B64_SINT = 117

    R64G64B64_SFLOAT = 118

    R64G64B64A64_UINT = 119

    R64G64B64A64_SINT = 120

    R64G64B64A64_SFLOAT = 121

    B10G11R11_UFLOAT_PACK32 = 122

    E5B9G9R9_UFLOAT_PACK32 = 123

    D16_UNORM = 124

    X8_D24_UNORM_PACK32 = 125

    D32_SFLOAT = 126

    S8_UINT = 127

    D16_UNORM_S8_UINT = 128

    D24_UNORM_S8_UINT = 129

    D32_SFLOAT_S8_UINT = 130

    BC1_RGB_UNORM_BLOCK = 131

    BC1_RGB_SRGB_BLOCK = 132

    BC1_RGBA_UNORM_BLOCK = 133

    BC1_RGBA_SRGB_BLOCK = 134

    BC2_UNORM_BLOCK = 135

    BC2_SRGB_BLOCK = 136

    BC3_UNORM_BLOCK = 137

    BC3_SRGB_BLOCK = 138

    BC4_UNORM_BLOCK = 139

    BC4_SNORM_BLOCK = 140

    BC5_UNORM_BLOCK = 141

    BC5_SNORM_BLOCK = 142

    BC6H_UFLOAT_BLOCK = 143

    BC6H_SFLOAT_BLOCK = 144

    BC7_UNORM_BLOCK = 145

    BC7_SRGB_BLOCK = 146

    ETC2_R8G8B8_UNORM_BLOCK = 147

    ETC2_R8G8B8_SRGB_BLOCK = 148

    ETC2_R8G8B8A1_UNORM_BLOCK = 149

    ETC2_R8G8B8A1_SRGB_BLOCK = 150

    ETC2_R8G8B8A8_UNORM_BLOCK = 151

    ETC2_R8G8B8A8_SRGB_BLOCK = 152

    EAC_R11_UNORM_BLOCK = 153

    EAC_R11_SNORM_BLOCK = 154

    EAC_R11G11_UNORM_BLOCK = 155

    EAC_R11G11_SNORM_BLOCK = 156

    ASTC_4x4_UNORM_BLOCK = 157

    ASTC_4x4_SRGB_BLOCK = 158

    ASTC_5x4_UNORM_BLOCK = 159

    ASTC_5x4_SRGB_BLOCK = 160

    ASTC_5x5_UNORM_BLOCK = 161

    ASTC_5x5_SRGB_BLOCK = 162

    ASTC_6x5_UNORM_BLOCK = 163

    ASTC_6x5_SRGB_BLOCK = 164

    ASTC_6x6_UNORM_BLOCK = 165

    ASTC_6x6_SRGB_BLOCK = 166

    ASTC_8x5_UNORM_BLOCK = 167

    ASTC_8x5_SRGB_BLOCK = 168

    ASTC_8x6_UNORM_BLOCK = 169

    ASTC_8x6_SRGB_BLOCK = 170

    ASTC_8x8_UNORM_BLOCK = 171

    ASTC_8x8_SRGB_BLOCK = 172

    ASTC_10x5_UNORM_BLOCK = 173

    ASTC_10x5_SRGB_BLOCK = 174

    ASTC_10x6_UNORM_BLOCK = 175

    ASTC_10x6_SRGB_BLOCK = 176

    ASTC_10x8_UNORM_BLOCK = 177

    ASTC_10x8_SRGB_BLOCK = 178

    ASTC_10x10_UNORM_BLOCK = 179

    ASTC_10x10_SRGB_BLOCK = 180

    ASTC_12x10_UNORM_BLOCK = 181

    ASTC_12x10_SRGB_BLOCK = 182

    ASTC_12x12_UNORM_BLOCK = 183

    ASTC_12x12_SRGB_BLOCK = 184

    G8B8G8R8_422_UNORM = 1000156000

    B8G8R8G8_422_UNORM = 1000156001

    G8_B8_R8_3PLANE_420_UNORM = 1000156002

    G8_B8R8_2PLANE_420_UNORM = 1000156003

    G8_B8_R8_3PLANE_422_UNORM = 1000156004

    G8_B8R8_2PLANE_422_UNORM = 1000156005

    G8_B8_R8_3PLANE_444_UNORM = 1000156006

    R10X6_UNORM_PACK16 = 1000156007

    R10X6G10X6_UNORM_2PACK16 = 1000156008

    R10X6G10X6B10X6A10X6_UNORM_4PACK16 = 1000156009

    G10X6B10X6G10X6R10X6_422_UNORM_4PACK16 = 1000156010

    B10X6G10X6R10X6G10X6_422_UNORM_4PACK16 = 1000156011

    G10X6_B10X6_R10X6_3PLANE_420_UNORM_3PACK16 = 1000156012

    G10X6_B10X6R10X6_2PLANE_420_UNORM_3PACK16 = 1000156013

    G10X6_B10X6_R10X6_3PLANE_422_UNORM_3PACK16 = 1000156014

    G10X6_B10X6R10X6_2PLANE_422_UNORM_3PACK16 = 1000156015

    G10X6_B10X6_R10X6_3PLANE_444_UNORM_3PACK16 = 1000156016

    R12X4_UNORM_PACK16 = 1000156017

    R12X4G12X4_UNORM_2PACK16 = 1000156018

    R12X4G12X4B12X4A12X4_UNORM_4PACK16 = 1000156019

    G12X4B12X4G12X4R12X4_422_UNORM_4PACK16 = 1000156020

    B12X4G12X4R12X4G12X4_422_UNORM_4PACK16 = 1000156021

    G12X4_B12X4_R12X4_3PLANE_420_UNORM_3PACK16 = 1000156022

    G12X4_B12X4R12X4_2PLANE_420_UNORM_3PACK16 = 1000156023

    G12X4_B12X4_R12X4_3PLANE_422_UNORM_3PACK16 = 1000156024

    G12X4_B12X4R12X4_2PLANE_422_UNORM_3PACK16 = 1000156025

    G12X4_B12X4_R12X4_3PLANE_444_UNORM_3PACK16 = 1000156026

    G16B16G16R16_422_UNORM = 1000156027

    B16G16R16G16_422_UNORM = 1000156028

    G16_B16_R16_3PLANE_420_UNORM = 1000156029

    G16_B16R16_2PLANE_420_UNORM = 1000156030

    G16_B16_R16_3PLANE_422_UNORM = 1000156031

    G16_B16R16_2PLANE_422_UNORM = 1000156032

    G16_B16_R16_3PLANE_444_UNORM = 1000156033

    G8_B8R8_2PLANE_444_UNORM = 1000330000

    G10X6_B10X6R10X6_2PLANE_444_UNORM_3PACK16 = 1000330001

    G12X4_B12X4R12X4_2PLANE_444_UNORM_3PACK16 = 1000330002

    G16_B16R16_2PLANE_444_UNORM = 1000330003

    A4R4G4B4_UNORM_PACK16 = 1000340000

    A4B4G4R4_UNORM_PACK16 = 1000340001

    ASTC_4x4_SFLOAT_BLOCK = 1000066000

    ASTC_5x4_SFLOAT_BLOCK = 1000066001

    ASTC_5x5_SFLOAT_BLOCK = 1000066002

    ASTC_6x5_SFLOAT_BLOCK = 1000066003

    ASTC_6x6_SFLOAT_BLOCK = 1000066004

    ASTC_8x5_SFLOAT_BLOCK = 1000066005

    ASTC_8x6_SFLOAT_BLOCK = 1000066006

    ASTC_8x8_SFLOAT_BLOCK = 1000066007

    ASTC_10x5_SFLOAT_BLOCK = 1000066008

    ASTC_10x6_SFLOAT_BLOCK = 1000066009

    ASTC_10x8_SFLOAT_BLOCK = 1000066010

    ASTC_10x10_SFLOAT_BLOCK = 1000066011

    ASTC_12x10_SFLOAT_BLOCK = 1000066012

    ASTC_12x12_SFLOAT_BLOCK = 1000066013

    PVRTC1_2BPP_UNORM_BLOCK_IMG = 1000054000

    PVRTC1_4BPP_UNORM_BLOCK_IMG = 1000054001

    PVRTC2_2BPP_UNORM_BLOCK_IMG = 1000054002

    PVRTC2_4BPP_UNORM_BLOCK_IMG = 1000054003

    PVRTC1_2BPP_SRGB_BLOCK_IMG = 1000054004

    PVRTC1_4BPP_SRGB_BLOCK_IMG = 1000054005

    PVRTC2_2BPP_SRGB_BLOCK_IMG = 1000054006

    PVRTC2_4BPP_SRGB_BLOCK_IMG = 1000054007

    R16G16_SFIXED5_NV = 1000464000

    A1B5G5R5_UNORM_PACK16_KHR = 1000470000

    A8_UNORM_KHR = 1000470001

    ASTC_4x4_SFLOAT_BLOCK_EXT = 1000066000

    ASTC_5x4_SFLOAT_BLOCK_EXT = 1000066001

    ASTC_5x5_SFLOAT_BLOCK_EXT = 1000066002

    ASTC_6x5_SFLOAT_BLOCK_EXT = 1000066003

    ASTC_6x6_SFLOAT_BLOCK_EXT = 1000066004

    ASTC_8x5_SFLOAT_BLOCK_EXT = 1000066005

    ASTC_8x6_SFLOAT_BLOCK_EXT = 1000066006

    ASTC_8x8_SFLOAT_BLOCK_EXT = 1000066007

    ASTC_10x5_SFLOAT_BLOCK_EXT = 1000066008

    ASTC_10x6_SFLOAT_BLOCK_EXT = 1000066009

    ASTC_10x8_SFLOAT_BLOCK_EXT = 1000066010

    ASTC_10x10_SFLOAT_BLOCK_EXT = 1000066011

    ASTC_12x10_SFLOAT_BLOCK_EXT = 1000066012

    ASTC_12x12_SFLOAT_BLOCK_EXT = 1000066013

    G8B8G8R8_422_UNORM_KHR = 1000156000

    B8G8R8G8_422_UNORM_KHR = 1000156001

    G8_B8_R8_3PLANE_420_UNORM_KHR = 1000156002

    G8_B8R8_2PLANE_420_UNORM_KHR = 1000156003

    G8_B8_R8_3PLANE_422_UNORM_KHR = 1000156004

    G8_B8R8_2PLANE_422_UNORM_KHR = 1000156005

    G8_B8_R8_3PLANE_444_UNORM_KHR = 1000156006

    R10X6_UNORM_PACK16_KHR = 1000156007

    R10X6G10X6_UNORM_2PACK16_KHR = 1000156008

    R10X6G10X6B10X6A10X6_UNORM_4PACK16_KHR = 1000156009

    G10X6B10X6G10X6R10X6_422_UNORM_4PACK16_KHR = 1000156010

    B10X6G10X6R10X6G10X6_422_UNORM_4PACK16_KHR = 1000156011

    G10X6_B10X6_R10X6_3PLANE_420_UNORM_3PACK16_KHR = 1000156012

    G10X6_B10X6R10X6_2PLANE_420_UNORM_3PACK16_KHR = 1000156013

    G10X6_B10X6_R10X6_3PLANE_422_UNORM_3PACK16_KHR = 1000156014

    G10X6_B10X6R10X6_2PLANE_422_UNORM_3PACK16_KHR = 1000156015

    G10X6_B10X6_R10X6_3PLANE_444_UNORM_3PACK16_KHR = 1000156016

    R12X4_UNORM_PACK16_KHR = 1000156017

    R12X4G12X4_UNORM_2PACK16_KHR = 1000156018

    R12X4G12X4B12X4A12X4_UNORM_4PACK16_KHR = 1000156019

    G12X4B12X4G12X4R12X4_422_UNORM_4PACK16_KHR = 1000156020

    B12X4G12X4R12X4G12X4_422_UNORM_4PACK16_KHR = 1000156021

    G12X4_B12X4_R12X4_3PLANE_420_UNORM_3PACK16_KHR = 1000156022

    G12X4_B12X4R12X4_2PLANE_420_UNORM_3PACK16_KHR = 1000156023

    G12X4_B12X4_R12X4_3PLANE_422_UNORM_3PACK16_KHR = 1000156024

    G12X4_B12X4R12X4_2PLANE_422_UNORM_3PACK16_KHR = 1000156025

    G12X4_B12X4_R12X4_3PLANE_444_UNORM_3PACK16_KHR = 1000156026

    G16B16G16R16_422_UNORM_KHR = 1000156027

    B16G16R16G16_422_UNORM_KHR = 1000156028

    G16_B16_R16_3PLANE_420_UNORM_KHR = 1000156029

    G16_B16R16_2PLANE_420_UNORM_KHR = 1000156030

    G16_B16_R16_3PLANE_422_UNORM_KHR = 1000156031

    G16_B16R16_2PLANE_422_UNORM_KHR = 1000156032

    G16_B16_R16_3PLANE_444_UNORM_KHR = 1000156033

    G8_B8R8_2PLANE_444_UNORM_EXT = 1000330000

    G10X6_B10X6R10X6_2PLANE_444_UNORM_3PACK16_EXT = 1000330001

    G12X4_B12X4R12X4_2PLANE_444_UNORM_3PACK16_EXT = 1000330002

    G16_B16R16_2PLANE_444_UNORM_EXT = 1000330003

    A4R4G4B4_UNORM_PACK16_EXT = 1000340000

    A4B4G4R4_UNORM_PACK16_EXT = 1000340001

    R16G16_S10_5_NV = 1000464000

class VertexAttribute:
    def __init__(self, location: int, binding: int, format: Format, offset: int = 0) -> None: ...

class PrimitiveTopology(enum.Enum):
    POINT_LIST = 0

    LINE_LIST = 1

    LINE_STRIP = 2

    TRIANGLE_LIST = 3

    TRIANGLE_STRIP = 4

    TRIANGLE_FAN = 5

    LINE_LIST_WITH_ADJACENCY = 6

    LINE_STRIP_WITH_ADJACENCY = 7

    TRIANGLE_LIST_WITH_ADJACENCY = 8

    TRIANGLE_STRIP_WITH_ADJACENCY = 9

    PATCH_LIST = 10

class InputAssembly:
    def __init__(self, primitive_topology: PrimitiveTopology = PrimitiveTopology.TRIANGLE_LIST, primitive_restart_enable: bool = False) -> None: ...

class PolygonMode(enum.Enum):
    FILL = 0

    LINE = 1

    POINT = 2

    FILL_RECTANGLE = 1000153000

class CullMode(enum.IntFlag):
    NONE = 0

    FRONT = 1

    BACK = 2

    FRONT_AND_BACK = 3

class FrontFace(enum.Enum):
    COUNTER_CLOCKWISE = 0

    CLOCKWISE = 1

class Rasterization:
    def __init__(self, polygon_mode: PolygonMode = PolygonMode.FILL, cull_mode: CullMode = CullMode.NONE, front_face: FrontFace = FrontFace.COUNTER_CLOCKWISE, depth_bias_enable: bool = False, depth_clamp_enable: bool = False, dynamic_line_width: bool = False, line_width: float = 1.0) -> None: ...

class DescriptorType(enum.Enum):
    SAMPLER = 0

    COMBINED_IMAGE_SAMPLER = 1

    SAMPLED_IMAGE = 2

    STORAGE_IMAGE = 3

    UNIFORM_TEXEL_BUFFER = 4

    STORAGE_TEXEL_BUFFER = 5

    UNIFORM_BUFFER = 6

    STORAGE_BUFFER = 7

    UNIFORM_BUFFER_DYNAMIC = 8

    STORAGE_BUFFER_DYNAMIC = 9

    INPUT_ATTACHMENT = 10

    INLINE_UNIFORM_BLOCK = 1000138000

    ACCELERATION_STRUCTURE = 1000150000

    SAMPLE_WEIGHT_IMAGE = 1000440000

    BLOCK_MATCH_IMAGE = 1000440001

    MUTABLE = 1000351000

class DescriptorSetEntry:
    def __init__(self, count: int, type: DescriptorType) -> None: ...

class DescriptorBindingFlags(enum.IntFlag):
    UPDATE_AFTER_BIND = 1

    UPDATE_UNUSED_WHILE_PENDING = 2

    PARTIALLY_BOUND = 4

    VARIABLE_DESCRIPTOR_COUNT = 8

class DescriptorSet(GfxObject):
    def __init__(self, ctx: Context, entries: Sequence[DescriptorSetEntry], flags: DescriptorBindingFlags = DescriptorBindingFlags.0, name: Optional[str] = None) -> None: ...

    def __repr__(self) -> str: ...

    def destroy(self) -> None: ...

    def write_buffer(self, buffer: Buffer, type: DescriptorType, binding: int, element: int = 0, offset: int = 0, size: int = 18446744073709551615) -> None: ...

    def write_image(self, image: Image, layout: ImageLayout, type: DescriptorType, binding: int, element: int = 0) -> None: ...

    def write_sampler(self, sampler: Sampler, binding: int, element: int = 0) -> None: ...

    def write_acceleration_structure(self, acceleration_structure: AccelerationStructure, binding: int, element: int = 0) -> None: ...

class BlendFactor(enum.Enum):
    VK_BLEND_FACTOR_ZERO = 0

    VK_BLEND_FACTOR_ONE = 1

    VK_BLEND_FACTOR_SRC_COLOR = 2

    VK_BLEND_FACTOR_ONE_MINUS_SRC_COLOR = 3

    VK_BLEND_FACTOR_DST_COLOR = 4

    VK_BLEND_FACTOR_ONE_MINUS_DST_COLOR = 5

    VK_BLEND_FACTOR_SRC_ALPHA = 6

    VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA = 7

    VK_BLEND_FACTOR_DST_ALPHA = 8

    VK_BLEND_FACTOR_ONE_MINUS_DST_ALPHA = 9

    VK_BLEND_FACTOR_CONSTANT_COLOR = 10

    VK_BLEND_FACTOR_ONE_MINUS_CONSTANT_COLOR = 11

    VK_BLEND_FACTOR_CONSTANT_ALPHA = 12

    VK_BLEND_FACTOR_ONE_MINUS_CONSTANT_ALPHA = 13

    VK_BLEND_FACTOR_SRC_ALPHA_SATURATE = 14

    VK_BLEND_FACTOR_SRC1_COLOR = 15

    VK_BLEND_FACTOR_ONE_MINUS_SRC1_COLOR = 16

    VK_BLEND_FACTOR_SRC1_ALPHA = 17

    VK_BLEND_FACTOR_ONE_MINUS_SRC1_ALPHA = 18

class BlendOp(enum.Enum):
    OP_ADD = 0

    OP_SUBTRACT = 1

    OP_REVERSE_SUBTRACT = 2

    OP_MIN = 3

    OP_MAX = 4

    OP_ZERO = 1000148000

    OP_SRC = 1000148001

    OP_DST = 1000148002

    OP_SRC_OVER = 1000148003

    OP_DST_OVER = 1000148004

    OP_SRC_IN = 1000148005

    OP_DST_IN = 1000148006

    OP_SRC_OUT = 1000148007

    OP_DST_OUT = 1000148008

    OP_SRC_ATOP = 1000148009

    OP_DST_ATOP = 1000148010

    OP_XOR = 1000148011

    OP_MULTIPLY = 1000148012

    OP_SCREEN = 1000148013

    OP_OVERLAY = 1000148014

    OP_DARKEN = 1000148015

    OP_LIGHTEN = 1000148016

    OP_COLORDODGE = 1000148017

    OP_COLORBURN = 1000148018

    OP_HARDLIGHT = 1000148019

    OP_SOFTLIGHT = 1000148020

    OP_DIFFERENCE = 1000148021

    OP_EXCLUSION = 1000148022

    OP_INVERT = 1000148023

    OP_INVERT_RGB = 1000148024

    OP_LINEARDODGE = 1000148025

    OP_LINEARBURN = 1000148026

    OP_VIVIDLIGHT = 1000148027

    OP_LINEARLIGHT = 1000148028

    OP_PINLIGHT = 1000148029

    OP_HARDMIX = 1000148030

    OP_HSL_HUE = 1000148031

    OP_HSL_SATURATION = 1000148032

    OP_HSL_COLOR = 1000148033

    OP_HSL_LUMINOSITY = 1000148034

    OP_PLUS = 1000148035

    OP_PLUS_CLAMPED = 1000148036

    OP_PLUS_CLAMPED_ALPHA = 1000148037

    OP_PLUS_DARKER = 1000148038

    OP_MINUS = 1000148039

    OP_MINUS_CLAMPED = 1000148040

    OP_CONTRAST = 1000148041

    OP_INVERT_OVG = 1000148042

    OP_RED = 1000148043

    OP_GREEN = 1000148044

    OP_BLUE = 1000148045

class ColorComponentFlags(enum.IntFlag):
    R = 1

    G = 2

    B = 4

    A = 8

class Attachment:
    def __init__(self, format: Format, blend_enable: bool = False, src_color_blend_factor: BlendFactor = BlendFactor.VK_BLEND_FACTOR_ZERO, dst_color_blend_factor: BlendFactor = BlendFactor.VK_BLEND_FACTOR_ZERO, color_blend_op: BlendOp = BlendOp.OP_ADD, src_alpha_blend_factor: BlendFactor = BlendFactor.VK_BLEND_FACTOR_ZERO, dst_alpha_blend_factor: BlendFactor = BlendFactor.VK_BLEND_FACTOR_ZERO, alpha_blend_op: BlendOp = BlendOp.OP_ADD, color_write_mask: int = 15) -> None: ...

class PushConstantsRange:
    def __init__(self, size: int, offset: int = 0, stages: Stage = Stage.1073741824|536870912|268435456|134217728|67108864|33554432|16777216|8388608|4194304|2097152|1048576|524288|262144|131072|65536|32768|16384|CALLABLE|INTERSECTION|MISS|CLOSEST_HIT|ANY_HIT|RAYGEN|MESH_EXT|TASK_EXT|COMPUTE|FRAGMENT|GEOMETRY|TESSELLATION_EVALUATION|TESSELLATION_CONTROL|VERTEX) -> None: ...

class AccelerationStructureMesh:
    def __init__(self, vertices_address: int, vertices_stride: int, vertices_count: int, vertices_format: Format, indices_address: int, indices_type: IndexType, primitive_count: int, transform: Sequence[float]) -> None: ...

class Depth:
    def __init__(self, format: Format = Format.UNDEFINED, test: bool = False, write: bool = False, op: CompareOp = CompareOp.LESS) -> None: ...

class ComputePipeline(GfxObject):
    def __init__(self, ctx: Context, shader: Shader, entry: str = 'main', push_constants_ranges: Sequence[PushConstantsRange] = [], descriptor_sets: Sequence[DescriptorSet] = [], name: Optional[str] = None) -> None: ...

    def __repr__(self) -> str: ...

    def destroy(self) -> None: ...

class GraphicsPipeline(GfxObject):
    def __init__(self, ctx: Context, stages: Sequence[PipelineStage] = [], vertex_bindings: Sequence[VertexBinding] = [], vertex_attributes: Sequence[VertexAttribute] = [], input_assembly: InputAssembly = ..., rasterization: Rasterization = ..., push_constants_ranges: Sequence[PushConstantsRange] = [], descriptor_sets: Sequence[DescriptorSet] = [], samples: int = 1, attachments: Sequence[Attachment] = [], depth: Depth = ..., name: Optional[str] = None) -> None: ...

    def __repr__(self) -> str: ...

    def destroy(self) -> None: ...

class SwapchainStatus(enum.Enum):
    READY = 0

    RESIZED = 1

    MINIMIZED = 2

def process_events(wait: bool) -> None: ...
