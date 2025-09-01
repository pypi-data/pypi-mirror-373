from collections.abc import Sequence
import enum
from typing import Annotated, overload

from numpy.typing import ArrayLike


class Vec2:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, x: float, y: float) -> None: ...

    @overload
    def __init__(self, t: tuple) -> None: ...

    @overload
    def __init__(self, l: list) -> None: ...

    @property
    def x(self) -> float: ...

    @x.setter
    def x(self, arg: float, /) -> None: ...

    @property
    def y(self) -> float: ...

    @y.setter
    def y(self, arg: float, /) -> None: ...

class Vec4:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, x: float, y: float, z: float, w: float) -> None: ...

    @overload
    def __init__(self, t: tuple) -> None: ...

    @overload
    def __init__(self, l: list) -> None: ...

    @property
    def x(self) -> float: ...

    @x.setter
    def x(self, arg: float, /) -> None: ...

    @property
    def y(self) -> float: ...

    @y.setter
    def y(self, arg: float, /) -> None: ...

    @property
    def z(self) -> float: ...

    @z.setter
    def z(self, arg: float, /) -> None: ...

    @property
    def w(self) -> float: ...

    @w.setter
    def w(self, arg: float, /) -> None: ...

class WindowFlags(enum.IntFlag):
    NONE = 0

    NO_TITLE_BAR = 1

    NO_RESIZE = 2

    NO_MOVE = 4

    NO_SCROLLBAR = 8

    NO_SCROLL_WITH_MOUSE = 16

    NO_COLLAPSE = 32

    ALWAYS_AUTO_RESIZE = 64

    NO_BACKGROUND = 128

    NO_SAVED_SETTINGS = 256

    NO_MOUSE_INPUTS = 512

    MENU_BAR = 1024

    HORIZONTAL_SCROLLBAR = 2048

    NO_FOCUS_ON_APPEARING = 4096

    NO_BRING_TO_FRONT_ON_FOCUS = 8192

    ALWAYS_VERTICAL_SCROLLBAR = 16384

    ALWAYS_HORIZONTAL_SCROLLBAR = 32768

    NO_NAV_INPUTS = 65536

    NO_NAV_FOCUS = 131072

    UNSAVED_DOCUMENT = 262144

    NO_DOCKING = 524288

    NO_NAV = 196608

    NO_DECORATION = 43

    NO_INPUTS = 197120

    DOCK_NODE_HOST = 8388608

    CHILD_WINDOW = 16777216

    TOOLTIP = 33554432

    POPUP = 67108864

    MODAL = 134217728

    CHILD_MENU = 268435456

    NAV_FLATTENED = 536870912

    ALWAYS_USE_WINDOW_PADDING = 1073741824

class ChildFlags(enum.IntFlag):
    NONE = 0

    BORDERS = 1

    ALWAYS_USE_WINDOW_PADDING = 2

    RESIZE_X = 4

    RESIZE_Y = 8

    AUTO_RESIZE_X = 16

    AUTO_RESIZE_Y = 32

    ALWAYS_AUTO_RESIZE = 64

    FRAME_STYLE = 128

    NAV_FLATTENED = 256

    BORDER = 1

class ItemFlags(enum.IntFlag):
    NONE = 0

    NO_TAB_STOP = 1

    NO_NAV = 2

    NO_NAV_DEFAULT_FOCUS = 4

    BUTTON_REPEAT = 8

    AUTO_CLOSE_POPUPS = 16

    ALLOW_DUPLICATE_ID = 32

class InputTextFlags(enum.IntFlag):
    NONE = 0

    CHARS_DECIMAL = 1

    CHARS_HEXADECIMAL = 2

    CHARS_SCIENTIFIC = 4

    CHARS_UPPERCASE = 8

    CHARS_NO_BLANK = 16

    ALLOW_TAB_INPUT = 32

    ENTER_RETURNS_TRUE = 64

    ESCAPE_CLEARS_ALL = 128

    CTRL_ENTER_FOR_NEW_LINE = 256

    READ_ONLY = 512

    PASSWORD = 1024

    ALWAYS_OVERWRITE = 2048

    AUTO_SELECT_ALL = 4096

    PARSE_EMPTY_REF_VAL = 8192

    DISPLAY_EMPTY_REF_VAL = 16384

    NO_HORIZONTAL_SCROLL = 32768

    NO_UNDO_REDO = 65536

    ELIDE_LEFT = 131072

    CALLBACK_COMPLETION = 262144

    CALLBACK_HISTORY = 524288

    CALLBACK_ALWAYS = 1048576

    CALLBACK_CHAR_FILTER = 2097152

    CALLBACK_RESIZE = 4194304

    CALLBACK_EDIT = 8388608

class TreeNodeFlags(enum.IntFlag):
    NONE = 0

    SELECTED = 1

    FRAMED = 2

    ALLOW_OVERLAP = 4

    NO_TREE_PUSH_ON_OPEN = 8

    NO_AUTO_OPEN_ON_LOG = 16

    DEFAULT_OPEN = 32

    OPEN_ON_DOUBLE_CLICK = 64

    OPEN_ON_ARROW = 128

    LEAF = 256

    BULLET = 512

    FRAME_PADDING = 1024

    SPAN_AVAIL_WIDTH = 2048

    SPAN_FULL_WIDTH = 4096

    SPAN_LABEL_WIDTH = 8192

    SPAN_ALL_COLUMNS = 16384

    LABEL_SPAN_ALL_COLUMNS = 32768

    NAV_LEFT_JUMPS_TO_PARENT = 131072

    COLLAPSING_HEADER = 26

    DRAW_LINES_NONE = 262144

    DRAW_LINES_FULL = 524288

    DRAW_LINES_TO_NODES = 1048576

    NAV_LEFT_JUMPS_BACK_HERE = 131072

    SPAN_TEXT_WIDTH = 8192

    ALLOW_ITEM_OVERLAP = 4

class PopupFlags(enum.IntFlag):
    NONE = 0

    MOUSE_BUTTON_LEFT = 0

    MOUSE_BUTTON_RIGHT = 1

    MOUSE_BUTTON_MIDDLE = 2

    NO_REOPEN = 32

    NO_OPEN_OVER_EXISTING_POPUP = 128

    NO_OPEN_OVER_ITEMS = 256

    ANY_POPUP_ID = 1024

    ANY_POPUP_LEVEL = 2048

    ANY_POPUP = 3072

class SelectableFlags(enum.IntFlag):
    NONE = 0

    NO_AUTO_CLOSE_POPUPS = 1

    SPAN_ALL_COLUMNS = 2

    ALLOW_DOUBLE_CLICK = 4

    DISABLED = 8

    ALLOW_OVERLAP = 16

    HIGHLIGHT = 32

    DONT_CLOSE_POPUPS = 1

    ALLOW_ITEM_OVERLAP = 16

class ComboFlags(enum.IntFlag):
    NONE = 0

    POPUP_ALIGN_LEFT = 1

    HEIGHT_SMALL = 2

    HEIGHT_REGULAR = 4

    HEIGHT_LARGE = 8

    HEIGHT_LARGEST = 16

    NO_ARROW_BUTTON = 32

    NO_PREVIEW = 64

    WIDTH_FIT_PREVIEW = 128

class TabBarFlags(enum.IntFlag):
    NONE = 0

    REORDERABLE = 1

    AUTO_SELECT_NEW_TABS = 2

    TAB_LIST_POPUP_BUTTON = 4

    NO_CLOSE_WITH_MIDDLE_MOUSE_BUTTON = 8

    NO_TAB_LIST_SCROLLING_BUTTONS = 16

    NO_TOOLTIP = 32

    DRAW_SELECTED_OVERLINE = 64

    FITTING_POLICY_MIXED = 128

    FITTING_POLICY_SHRINK = 256

    FITTING_POLICY_SCROLL = 512

    FITTING_POLICY_RESIZE_DOWN = 256

class TabItemFlags(enum.IntFlag):
    NONE = 0

    UNSAVED_DOCUMENT = 1

    SET_SELECTED = 2

    NO_CLOSE_WITH_MIDDLE_MOUSE_BUTTON = 4

    NO_PUSH_ID = 8

    NO_TOOLTIP = 16

    NO_REORDER = 32

    LEADING = 64

    TRAILING = 128

    NO_ASSUMED_CLOSURE = 256

class FocusedFlags(enum.IntFlag):
    NONE = 0

    CHILD_WINDOWS = 1

    ROOT_WINDOW = 2

    ANY_WINDOW = 4

    NO_POPUP_HIERARCHY = 8

    DOCK_HIERARCHY = 16

    ROOT_AND_CHILD_WINDOWS = 3

class HoveredFlags(enum.IntFlag):
    NONE = 0

    CHILD_WINDOWS = 1

    ROOT_WINDOW = 2

    ANY_WINDOW = 4

    NO_POPUP_HIERARCHY = 8

    DOCK_HIERARCHY = 16

    ALLOW_WHEN_BLOCKED_BY_POPUP = 32

    ALLOW_WHEN_BLOCKED_BY_ACTIVE_ITEM = 128

    ALLOW_WHEN_OVERLAPPED_BY_ITEM = 256

    ALLOW_WHEN_OVERLAPPED_BY_WINDOW = 512

    ALLOW_WHEN_DISABLED = 1024

    NO_NAV_OVERRIDE = 2048

    ALLOW_WHEN_OVERLAPPED = 768

    RECT_ONLY = 928

    ROOT_AND_CHILD_WINDOWS = 3

    FOR_TOOLTIP = 4096

    STATIONARY = 8192

    DELAY_NONE = 16384

    DELAY_SHORT = 32768

    DELAY_NORMAL = 65536

    NO_SHARED_DELAY = 131072

class DockNodeFlags(enum.IntFlag):
    NONE = 0

    KEEP_ALIVE_ONLY = 1

    NO_DOCKING_OVER_CENTRAL_NODE = 4

    PASSTHRU_CENTRAL_NODE = 8

    NO_DOCKING_SPLIT = 16

    NO_RESIZE = 32

    AUTO_HIDE_TAB_BAR = 64

    NO_UNDOCKING = 128

    NO_SPLIT = 16

    NO_DOCKING_IN_CENTRAL_NODE = 4

class DragDropFlags(enum.IntFlag):
    NONE = 0

    SOURCE_NO_PREVIEW_TOOLTIP = 1

    SOURCE_NO_DISABLE_HOVER = 2

    SOURCE_NO_HOLD_TO_OPEN_OTHERS = 4

    SOURCE_ALLOW_NULL_ID = 8

    SOURCE_EXTERN = 16

    PAYLOAD_AUTO_EXPIRE = 32

    PAYLOAD_NO_CROSS_CONTEXT = 64

    PAYLOAD_NO_CROSS_PROCESS = 128

    ACCEPT_BEFORE_DELIVERY = 1024

    ACCEPT_NO_DRAW_DEFAULT_RECT = 2048

    ACCEPT_NO_PREVIEW_TOOLTIP = 4096

    ACCEPT_PEEK_ONLY = 3072

    SOURCE_AUTO_EXPIRE_PAYLOAD = 32

class DataType(enum.IntEnum):
    S8 = 0

    U8 = 1

    S16 = 2

    U16 = 3

    S32 = 4

    U32 = 5

    S64 = 6

    U64 = 7

    FLOAT = 8

    DOUBLE = 9

    BOOL = 10

    STRING = 11

class Dir(enum.IntEnum):
    NONE = -1

    LEFT = 0

    RIGHT = 1

    UP = 2

    DOWN = 3

class SortDirection(enum.IntEnum):
    NONE = 0

    ASCENDING = 1

    DESCENDING = 2

class Key(enum.IntEnum):
    NONE = 0

    NAMED_KEY__B_E_G_I_N = 512

    TAB = 512

    LEFT_ARROW = 513

    RIGHT_ARROW = 514

    UP_ARROW = 515

    DOWN_ARROW = 516

    PAGE_UP = 517

    PAGE_DOWN = 518

    HOME = 519

    END = 520

    INSERT = 521

    DELETE = 522

    BACKSPACE = 523

    SPACE = 524

    ENTER = 525

    ESCAPE = 526

    LEFT_CTRL = 527

    LEFT_SHIFT = 528

    LEFT_ALT = 529

    LEFT_SUPER = 530

    RIGHT_CTRL = 531

    RIGHT_SHIFT = 532

    RIGHT_ALT = 533

    RIGHT_SUPER = 534

    MENU = 535

    KEY_0 = 536

    KEY_1 = 537

    KEY_2 = 538

    KEY_3 = 539

    KEY_4 = 540

    KEY_5 = 541

    KEY_6 = 542

    KEY_7 = 543

    KEY_8 = 544

    KEY_9 = 545

    A = 546

    B = 547

    C = 548

    D = 549

    E = 550

    F = 551

    G = 552

    H = 553

    I = 554

    J = 555

    K = 556

    L = 557

    M = 558

    N = 559

    O = 560

    P = 561

    Q = 562

    R = 563

    S = 564

    T = 565

    U = 566

    V = 567

    W = 568

    X = 569

    Y = 570

    Z = 571

    F1 = 572

    F2 = 573

    F3 = 574

    F4 = 575

    F5 = 576

    F6 = 577

    F7 = 578

    F8 = 579

    F9 = 580

    F10 = 581

    F11 = 582

    F12 = 583

    F13 = 584

    F14 = 585

    F15 = 586

    F16 = 587

    F17 = 588

    F18 = 589

    F19 = 590

    F20 = 591

    F21 = 592

    F22 = 593

    F23 = 594

    F24 = 595

    APOSTROPHE = 596

    COMMA = 597

    MINUS = 598

    PERIOD = 599

    SLASH = 600

    SEMICOLON = 601

    EQUAL = 602

    LEFT_BRACKET = 603

    BACKSLASH = 604

    RIGHT_BRACKET = 605

    GRAVE_ACCENT = 606

    CAPS_LOCK = 607

    SCROLL_LOCK = 608

    NUM_LOCK = 609

    PRINT_SCREEN = 610

    PAUSE = 611

    KEYPAD0 = 612

    KEYPAD1 = 613

    KEYPAD2 = 614

    KEYPAD3 = 615

    KEYPAD4 = 616

    KEYPAD5 = 617

    KEYPAD6 = 618

    KEYPAD7 = 619

    KEYPAD8 = 620

    KEYPAD9 = 621

    KEYPAD_DECIMAL = 622

    KEYPAD_DIVIDE = 623

    KEYPAD_MULTIPLY = 624

    KEYPAD_SUBTRACT = 625

    KEYPAD_ADD = 626

    KEYPAD_ENTER = 627

    KEYPAD_EQUAL = 628

    APP_BACK = 629

    APP_FORWARD = 630

    OEM102 = 631

    GAMEPAD_START = 632

    GAMEPAD_BACK = 633

    GAMEPAD_FACE_LEFT = 634

    GAMEPAD_FACE_RIGHT = 635

    GAMEPAD_FACE_UP = 636

    GAMEPAD_FACE_DOWN = 637

    GAMEPAD_DPAD_LEFT = 638

    GAMEPAD_DPAD_RIGHT = 639

    GAMEPAD_DPAD_UP = 640

    GAMEPAD_DPAD_DOWN = 641

    GAMEPAD_L1 = 642

    GAMEPAD_R1 = 643

    GAMEPAD_L2 = 644

    GAMEPAD_R2 = 645

    GAMEPAD_L3 = 646

    GAMEPAD_R3 = 647

    GAMEPAD_L_STICK_LEFT = 648

    GAMEPAD_L_STICK_RIGHT = 649

    GAMEPAD_L_STICK_UP = 650

    GAMEPAD_L_STICK_DOWN = 651

    GAMEPAD_R_STICK_LEFT = 652

    GAMEPAD_R_STICK_RIGHT = 653

    GAMEPAD_R_STICK_UP = 654

    GAMEPAD_R_STICK_DOWN = 655

    MOUSE_LEFT = 656

    MOUSE_RIGHT = 657

    MOUSE_MIDDLE = 658

    MOUSE_X1 = 659

    MOUSE_X2 = 660

    MOUSE_WHEEL_X = 661

    MOUSE_WHEEL_Y = 662

    RESERVED_FOR_MOD_CTRL = 663

    RESERVED_FOR_MOD_SHIFT = 664

    RESERVED_FOR_MOD_ALT = 665

    RESERVED_FOR_MOD_SUPER = 666

    NAMED_KEY__E_N_D = 667

    MOD_CTRL = 4096

    MOD_SHIFT = 8192

    MOD_ALT = 16384

    MOD_SUPER = 32768

class InputFlags(enum.IntFlag):
    NONE = 0

    REPEAT = 1

    ROUTE_ACTIVE = 1024

    ROUTE_FOCUSED = 2048

    ROUTE_GLOBAL = 4096

    ROUTE_ALWAYS = 8192

    ROUTE_OVER_FOCUSED = 16384

    ROUTE_OVER_ACTIVE = 32768

    ROUTE_UNLESS_BG_FOCUSED = 65536

    ROUTE_FROM_ROOT_WINDOW = 131072

    TOOLTIP = 262144

class ConfigFlags(enum.IntFlag):
    NONE = 0

    NAV_ENABLE_KEYBOARD = 1

    NAV_ENABLE_GAMEPAD = 2

    NO_MOUSE = 16

    NO_MOUSE_CURSOR_CHANGE = 32

    NO_KEYBOARD = 64

    DOCKING_ENABLE = 128

    VIEWPORTS_ENABLE = 1024

    IS_S_R_G_B = 1048576

    IS_TOUCH_SCREEN = 2097152

    NAV_ENABLE_SET_MOUSE_POS = 4

    NAV_NO_CAPTURE_KEYBOARD = 8

    DPI_ENABLE_SCALE_FONTS = 16384

    DPI_ENABLE_SCALE_VIEWPORTS = 32768

class BackendFlags(enum.IntFlag):
    NONE = 0

    HAS_GAMEPAD = 1

    HAS_MOUSE_CURSORS = 2

    HAS_SET_MOUSE_POS = 4

    RENDERER_HAS_VTX_OFFSET = 8

    RENDERER_HAS_TEXTURES = 16

    PLATFORM_HAS_VIEWPORTS = 1024

    HAS_MOUSE_HOVERED_VIEWPORT = 2048

    RENDERER_HAS_VIEWPORTS = 4096

class Col(enum.IntEnum):
    TEXT = 0

    TEXT_DISABLED = 1

    WINDOW_BG = 2

    CHILD_BG = 3

    POPUP_BG = 4

    BORDER = 5

    BORDER_SHADOW = 6

    FRAME_BG = 7

    FRAME_BG_HOVERED = 8

    FRAME_BG_ACTIVE = 9

    TITLE_BG = 10

    TITLE_BG_ACTIVE = 11

    TITLE_BG_COLLAPSED = 12

    MENU_BAR_BG = 13

    SCROLLBAR_BG = 14

    SCROLLBAR_GRAB = 15

    SCROLLBAR_GRAB_HOVERED = 16

    SCROLLBAR_GRAB_ACTIVE = 17

    CHECK_MARK = 18

    SLIDER_GRAB = 19

    SLIDER_GRAB_ACTIVE = 20

    BUTTON = 21

    BUTTON_HOVERED = 22

    BUTTON_ACTIVE = 23

    HEADER = 24

    HEADER_HOVERED = 25

    HEADER_ACTIVE = 26

    SEPARATOR = 27

    SEPARATOR_HOVERED = 28

    SEPARATOR_ACTIVE = 29

    RESIZE_GRIP = 30

    RESIZE_GRIP_HOVERED = 31

    RESIZE_GRIP_ACTIVE = 32

    INPUT_TEXT_CURSOR = 33

    TAB_HOVERED = 34

    TAB = 35

    TAB_SELECTED = 36

    TAB_SELECTED_OVERLINE = 37

    TAB_DIMMED = 38

    TAB_DIMMED_SELECTED = 39

    TAB_DIMMED_SELECTED_OVERLINE = 40

    DOCKING_PREVIEW = 41

    DOCKING_EMPTY_BG = 42

    PLOT_LINES = 43

    PLOT_LINES_HOVERED = 44

    PLOT_HISTOGRAM = 45

    PLOT_HISTOGRAM_HOVERED = 46

    TABLE_HEADER_BG = 47

    TABLE_BORDER_STRONG = 48

    TABLE_BORDER_LIGHT = 49

    TABLE_ROW_BG = 50

    TABLE_ROW_BG_ALT = 51

    TEXT_LINK = 52

    TEXT_SELECTED_BG = 53

    TREE_LINES = 54

    DRAG_DROP_TARGET = 55

    NAV_CURSOR = 56

    NAV_WINDOWING_HIGHLIGHT = 57

    NAV_WINDOWING_DIM_BG = 58

    MODAL_WINDOW_DIM_BG = 59

    TAB_ACTIVE = 36

    TAB_UNFOCUSED = 38

    TAB_UNFOCUSED_ACTIVE = 39

    NAV_HIGHLIGHT = 56

class StyleVar(enum.IntEnum):
    ALPHA = 0

    DISABLED_ALPHA = 1

    WINDOW_PADDING = 2

    WINDOW_ROUNDING = 3

    WINDOW_BORDER_SIZE = 4

    WINDOW_MIN_SIZE = 5

    WINDOW_TITLE_ALIGN = 6

    CHILD_ROUNDING = 7

    CHILD_BORDER_SIZE = 8

    POPUP_ROUNDING = 9

    POPUP_BORDER_SIZE = 10

    FRAME_PADDING = 11

    FRAME_ROUNDING = 12

    FRAME_BORDER_SIZE = 13

    ITEM_SPACING = 14

    ITEM_INNER_SPACING = 15

    INDENT_SPACING = 16

    CELL_PADDING = 17

    SCROLLBAR_SIZE = 18

    SCROLLBAR_ROUNDING = 19

    GRAB_MIN_SIZE = 20

    GRAB_ROUNDING = 21

    IMAGE_BORDER_SIZE = 22

    TAB_ROUNDING = 23

    TAB_BORDER_SIZE = 24

    TAB_MIN_WIDTH_BASE = 25

    TAB_MIN_WIDTH_SHRINK = 26

    TAB_BAR_BORDER_SIZE = 27

    TAB_BAR_OVERLINE_SIZE = 28

    TABLE_ANGLED_HEADERS_ANGLE = 29

    TABLE_ANGLED_HEADERS_TEXT_ALIGN = 30

    TREE_LINES_SIZE = 31

    TREE_LINES_ROUNDING = 32

    BUTTON_TEXT_ALIGN = 33

    SELECTABLE_TEXT_ALIGN = 34

    SEPARATOR_TEXT_BORDER_SIZE = 35

    SEPARATOR_TEXT_ALIGN = 36

    SEPARATOR_TEXT_PADDING = 37

    DOCKING_SEPARATOR_SIZE = 38

class ButtonFlags(enum.IntFlag):
    NONE = 0

    MOUSE_BUTTON_LEFT = 1

    MOUSE_BUTTON_RIGHT = 2

    MOUSE_BUTTON_MIDDLE = 4

    ENABLE_NAV = 8

class ColorEditFlags(enum.IntFlag):
    NONE = 0

    NO_ALPHA = 2

    NO_PICKER = 4

    NO_OPTIONS = 8

    NO_SMALL_PREVIEW = 16

    NO_INPUTS = 32

    NO_TOOLTIP = 64

    NO_LABEL = 128

    NO_SIDE_PREVIEW = 256

    NO_DRAG_DROP = 512

    NO_BORDER = 1024

    ALPHA_OPAQUE = 2048

    ALPHA_NO_BG = 4096

    ALPHA_PREVIEW_HALF = 8192

    ALPHA_BAR = 65536

    H_D_R = 524288

    DISPLAY_R_G_B = 1048576

    DISPLAY_H_S_V = 2097152

    DISPLAY_HEX = 4194304

    UINT8 = 8388608

    FLOAT = 16777216

    PICKER_HUE_BAR = 33554432

    PICKER_HUE_WHEEL = 67108864

    INPUT_R_G_B = 134217728

    INPUT_H_S_V = 268435456

    ALPHA_PREVIEW = 0

class SliderFlags(enum.IntFlag):
    NONE = 0

    LOGARITHMIC = 32

    NO_ROUND_TO_FORMAT = 64

    NO_INPUT = 128

    WRAP_AROUND = 256

    CLAMP_ON_INPUT = 512

    CLAMP_ZERO_RANGE = 1024

    NO_SPEED_TWEAKS = 2048

    ALWAYS_CLAMP = 1536

class MouseButton(enum.IntEnum):
    LEFT = 0

    RIGHT = 1

    MIDDLE = 2

class MouseCursor(enum.IntEnum):
    NONE = -1

    ARROW = 0

    TEXT_INPUT = 1

    RESIZE_ALL = 2

    RESIZE_N_S = 3

    RESIZE_E_W = 4

    RESIZE_N_E_S_W = 5

    RESIZE_N_W_S_E = 6

    HAND = 7

    WAIT = 8

    PROGRESS = 9

    NOT_ALLOWED = 10

class MouseSource(enum.IntEnum):
    MOUSE = 0

    TOUCH_SCREEN = 1

    PEN = 2

class Cond(enum.IntEnum):
    NONE = 0

    ALWAYS = 1

    ONCE = 2

    FIRST_USE_EVER = 4

    APPEARING = 8

class TableFlags(enum.IntFlag):
    NONE = 0

    RESIZABLE = 1

    REORDERABLE = 2

    HIDEABLE = 4

    SORTABLE = 8

    NO_SAVED_SETTINGS = 16

    CONTEXT_MENU_IN_BODY = 32

    ROW_BG = 64

    BORDERS_INNER_H = 128

    BORDERS_OUTER_H = 256

    BORDERS_INNER_V = 512

    BORDERS_OUTER_V = 1024

    BORDERS_H = 384

    BORDERS_V = 1536

    BORDERS_INNER = 640

    BORDERS_OUTER = 1280

    BORDERS = 1920

    NO_BORDERS_IN_BODY = 2048

    NO_BORDERS_IN_BODY_UNTIL_RESIZE = 4096

    SIZING_FIXED_FIT = 8192

    SIZING_FIXED_SAME = 16384

    SIZING_STRETCH_PROP = 24576

    SIZING_STRETCH_SAME = 32768

    NO_HOST_EXTEND_X = 65536

    NO_HOST_EXTEND_Y = 131072

    NO_KEEP_COLUMNS_VISIBLE = 262144

    PRECISE_WIDTHS = 524288

    NO_CLIP = 1048576

    PAD_OUTER_X = 2097152

    NO_PAD_OUTER_X = 4194304

    NO_PAD_INNER_X = 8388608

    SCROLL_X = 16777216

    SCROLL_Y = 33554432

    SORT_MULTI = 67108864

    SORT_TRISTATE = 134217728

    HIGHLIGHT_HOVERED_COLUMN = 268435456

class TableColumnFlags(enum.IntFlag):
    NONE = 0

    DISABLED = 1

    DEFAULT_HIDE = 2

    DEFAULT_SORT = 4

    WIDTH_STRETCH = 8

    WIDTH_FIXED = 16

    NO_RESIZE = 32

    NO_REORDER = 64

    NO_HIDE = 128

    NO_CLIP = 256

    NO_SORT = 512

    NO_SORT_ASCENDING = 1024

    NO_SORT_DESCENDING = 2048

    NO_HEADER_LABEL = 4096

    NO_HEADER_WIDTH = 8192

    PREFER_SORT_ASCENDING = 16384

    PREFER_SORT_DESCENDING = 32768

    INDENT_ENABLE = 65536

    INDENT_DISABLE = 131072

    ANGLED_HEADER = 262144

    IS_ENABLED = 16777216

    IS_VISIBLE = 33554432

    IS_SORTED = 67108864

    IS_HOVERED = 134217728

class TableRowFlags(enum.IntFlag):
    NONE = 0

    HEADERS = 1

class TableBgTarget(enum.IntEnum):
    NONE = 0

    ROW_BG0 = 1

    ROW_BG1 = 2

    CELL_BG = 3

class MultiSelectFlags(enum.IntFlag):
    NONE = 0

    SINGLE_SELECT = 1

    NO_SELECT_ALL = 2

    NO_RANGE_SELECT = 4

    NO_AUTO_SELECT = 8

    NO_AUTO_CLEAR = 16

    NO_AUTO_CLEAR_ON_RESELECT = 32

    BOX_SELECT1D = 64

    BOX_SELECT2D = 128

    BOX_SELECT_NO_SCROLL = 256

    CLEAR_ON_ESCAPE = 512

    CLEAR_ON_CLICK_VOID = 1024

    SCOPE_WINDOW = 2048

    SCOPE_RECT = 4096

    SELECT_ON_CLICK = 8192

    SELECT_ON_CLICK_RELEASE = 16384

    NAV_WRAP_X = 65536

class SelectionRequestType(enum.IntEnum):
    NONE = 0

    SET_ALL = 1

    SET_RANGE = 2

class DrawFlags(enum.IntFlag):
    NONE = 0

    CLOSED = 1

    ROUND_CORNERS_TOP_LEFT = 16

    ROUND_CORNERS_TOP_RIGHT = 32

    ROUND_CORNERS_BOTTOM_LEFT = 64

    ROUND_CORNERS_BOTTOM_RIGHT = 128

    ROUND_CORNERS_NONE = 256

    ROUND_CORNERS_TOP = 48

    ROUND_CORNERS_BOTTOM = 192

    ROUND_CORNERS_LEFT = 80

    ROUND_CORNERS_RIGHT = 160

    ROUND_CORNERS_ALL = 240

class DrawListFlags(enum.IntFlag):
    NONE = 0

    ANTI_ALIASED_LINES = 1

    ANTI_ALIASED_LINES_USE_TEX = 2

    ANTI_ALIASED_FILL = 4

    ALLOW_VTX_OFFSET = 8

class TextureFormat(enum.IntEnum):
    R_G_B_A32 = 0

    ALPHA8 = 1

class TextureStatus(enum.IntEnum):
    O_K = 0

    DESTROYED = 1

    WANT_CREATE = 2

    WANT_UPDATES = 3

    WANT_DESTROY = 4

class FontAtlasFlags(enum.IntFlag):
    NONE = 0

    NO_POWER_OF_TWO_HEIGHT = 1

    NO_MOUSE_CURSORS = 2

    NO_BAKED_LINES = 4

class FontFlags(enum.IntFlag):
    NONE = 0

    NO_LOAD_ERROR = 2

    NO_LOAD_GLYPHS = 4

    LOCK_BAKED_SIZES = 8

class ViewportFlags(enum.IntFlag):
    NONE = 0

    IS_PLATFORM_WINDOW = 1

    IS_PLATFORM_MONITOR = 2

    OWNED_BY_APP = 4

    NO_DECORATION = 8

    NO_TASK_BAR_ICON = 16

    NO_FOCUS_ON_APPEARING = 32

    NO_FOCUS_ON_CLICK = 64

    NO_INPUTS = 128

    NO_RENDERER_CLEAR = 256

    NO_AUTO_MERGE = 512

    TOP_MOST = 1024

    CAN_HOST_OTHER_WINDOWS = 2048

    IS_MINIMIZED = 4096

    IS_FOCUSED = 8192

class IO:
    @property
    def config_flags(self) -> int: ...

    @config_flags.setter
    def config_flags(self, arg: int, /) -> None: ...

    @property
    def backend_flags(self) -> int: ...

    @backend_flags.setter
    def backend_flags(self, arg: int, /) -> None: ...

    @property
    def display_size(self) -> Vec2: ...

    @display_size.setter
    def display_size(self, arg: Vec2, /) -> None: ...

    @property
    def display_framebuffer_scale(self) -> Vec2: ...

    @display_framebuffer_scale.setter
    def display_framebuffer_scale(self, arg: Vec2, /) -> None: ...

    @property
    def delta_time(self) -> float: ...

    @delta_time.setter
    def delta_time(self, arg: float, /) -> None: ...

    @property
    def ini_saving_rate(self) -> float: ...

    @ini_saving_rate.setter
    def ini_saving_rate(self, arg: float, /) -> None: ...

    @property
    def font_allow_user_scaling(self) -> bool: ...

    @font_allow_user_scaling.setter
    def font_allow_user_scaling(self, arg: bool, /) -> None: ...

    @property
    def config_nav_swap_gamepad_buttons(self) -> bool: ...

    @config_nav_swap_gamepad_buttons.setter
    def config_nav_swap_gamepad_buttons(self, arg: bool, /) -> None: ...

    @property
    def config_nav_move_set_mouse_pos(self) -> bool: ...

    @config_nav_move_set_mouse_pos.setter
    def config_nav_move_set_mouse_pos(self, arg: bool, /) -> None: ...

    @property
    def config_nav_capture_keyboard(self) -> bool: ...

    @config_nav_capture_keyboard.setter
    def config_nav_capture_keyboard(self, arg: bool, /) -> None: ...

    @property
    def config_nav_escape_clear_focus_item(self) -> bool: ...

    @config_nav_escape_clear_focus_item.setter
    def config_nav_escape_clear_focus_item(self, arg: bool, /) -> None: ...

    @property
    def config_nav_escape_clear_focus_window(self) -> bool: ...

    @config_nav_escape_clear_focus_window.setter
    def config_nav_escape_clear_focus_window(self, arg: bool, /) -> None: ...

    @property
    def config_nav_cursor_visible_auto(self) -> bool: ...

    @config_nav_cursor_visible_auto.setter
    def config_nav_cursor_visible_auto(self, arg: bool, /) -> None: ...

    @property
    def config_nav_cursor_visible_always(self) -> bool: ...

    @config_nav_cursor_visible_always.setter
    def config_nav_cursor_visible_always(self, arg: bool, /) -> None: ...

    @property
    def config_docking_no_split(self) -> bool: ...

    @config_docking_no_split.setter
    def config_docking_no_split(self, arg: bool, /) -> None: ...

    @property
    def config_docking_with_shift(self) -> bool: ...

    @config_docking_with_shift.setter
    def config_docking_with_shift(self, arg: bool, /) -> None: ...

    @property
    def config_docking_always_tab_bar(self) -> bool: ...

    @config_docking_always_tab_bar.setter
    def config_docking_always_tab_bar(self, arg: bool, /) -> None: ...

    @property
    def config_docking_transparent_payload(self) -> bool: ...

    @config_docking_transparent_payload.setter
    def config_docking_transparent_payload(self, arg: bool, /) -> None: ...

    @property
    def config_viewports_no_auto_merge(self) -> bool: ...

    @config_viewports_no_auto_merge.setter
    def config_viewports_no_auto_merge(self, arg: bool, /) -> None: ...

    @property
    def config_viewports_no_task_bar_icon(self) -> bool: ...

    @config_viewports_no_task_bar_icon.setter
    def config_viewports_no_task_bar_icon(self, arg: bool, /) -> None: ...

    @property
    def config_viewports_no_decoration(self) -> bool: ...

    @config_viewports_no_decoration.setter
    def config_viewports_no_decoration(self, arg: bool, /) -> None: ...

    @property
    def config_viewports_no_default_parent(self) -> bool: ...

    @config_viewports_no_default_parent.setter
    def config_viewports_no_default_parent(self, arg: bool, /) -> None: ...

    @property
    def config_viewport_platform_focus_sets_im_gui_focus(self) -> bool: ...

    @config_viewport_platform_focus_sets_im_gui_focus.setter
    def config_viewport_platform_focus_sets_im_gui_focus(self, arg: bool, /) -> None: ...

    @property
    def config_dpi_scale_fonts(self) -> bool: ...

    @config_dpi_scale_fonts.setter
    def config_dpi_scale_fonts(self, arg: bool, /) -> None: ...

    @property
    def config_dpi_scale_viewports(self) -> bool: ...

    @config_dpi_scale_viewports.setter
    def config_dpi_scale_viewports(self, arg: bool, /) -> None: ...

    @property
    def mouse_draw_cursor(self) -> bool: ...

    @mouse_draw_cursor.setter
    def mouse_draw_cursor(self, arg: bool, /) -> None: ...

    @property
    def config_mac_o_s_x_behaviors(self) -> bool: ...

    @config_mac_o_s_x_behaviors.setter
    def config_mac_o_s_x_behaviors(self, arg: bool, /) -> None: ...

    @property
    def config_input_trickle_event_queue(self) -> bool: ...

    @config_input_trickle_event_queue.setter
    def config_input_trickle_event_queue(self, arg: bool, /) -> None: ...

    @property
    def config_input_text_cursor_blink(self) -> bool: ...

    @config_input_text_cursor_blink.setter
    def config_input_text_cursor_blink(self, arg: bool, /) -> None: ...

    @property
    def config_input_text_enter_keep_active(self) -> bool: ...

    @config_input_text_enter_keep_active.setter
    def config_input_text_enter_keep_active(self, arg: bool, /) -> None: ...

    @property
    def config_drag_click_to_input_text(self) -> bool: ...

    @config_drag_click_to_input_text.setter
    def config_drag_click_to_input_text(self, arg: bool, /) -> None: ...

    @property
    def config_windows_resize_from_edges(self) -> bool: ...

    @config_windows_resize_from_edges.setter
    def config_windows_resize_from_edges(self, arg: bool, /) -> None: ...

    @property
    def config_windows_move_from_title_bar_only(self) -> bool: ...

    @config_windows_move_from_title_bar_only.setter
    def config_windows_move_from_title_bar_only(self, arg: bool, /) -> None: ...

    @property
    def config_windows_copy_contents_with_ctrl_c(self) -> bool: ...

    @config_windows_copy_contents_with_ctrl_c.setter
    def config_windows_copy_contents_with_ctrl_c(self, arg: bool, /) -> None: ...

    @property
    def config_scrollbar_scroll_by_page(self) -> bool: ...

    @config_scrollbar_scroll_by_page.setter
    def config_scrollbar_scroll_by_page(self, arg: bool, /) -> None: ...

    @property
    def config_memory_compact_timer(self) -> float: ...

    @config_memory_compact_timer.setter
    def config_memory_compact_timer(self, arg: float, /) -> None: ...

    @property
    def mouse_double_click_time(self) -> float: ...

    @mouse_double_click_time.setter
    def mouse_double_click_time(self, arg: float, /) -> None: ...

    @property
    def mouse_double_click_max_dist(self) -> float: ...

    @mouse_double_click_max_dist.setter
    def mouse_double_click_max_dist(self, arg: float, /) -> None: ...

    @property
    def mouse_drag_threshold(self) -> float: ...

    @mouse_drag_threshold.setter
    def mouse_drag_threshold(self, arg: float, /) -> None: ...

    @property
    def key_repeat_delay(self) -> float: ...

    @key_repeat_delay.setter
    def key_repeat_delay(self, arg: float, /) -> None: ...

    @property
    def key_repeat_rate(self) -> float: ...

    @key_repeat_rate.setter
    def key_repeat_rate(self, arg: float, /) -> None: ...

    @property
    def config_error_recovery(self) -> bool: ...

    @config_error_recovery.setter
    def config_error_recovery(self, arg: bool, /) -> None: ...

    @property
    def config_error_recovery_enable_assert(self) -> bool: ...

    @config_error_recovery_enable_assert.setter
    def config_error_recovery_enable_assert(self, arg: bool, /) -> None: ...

    @property
    def config_error_recovery_enable_debug_log(self) -> bool: ...

    @config_error_recovery_enable_debug_log.setter
    def config_error_recovery_enable_debug_log(self, arg: bool, /) -> None: ...

    @property
    def config_error_recovery_enable_tooltip(self) -> bool: ...

    @config_error_recovery_enable_tooltip.setter
    def config_error_recovery_enable_tooltip(self, arg: bool, /) -> None: ...

    @property
    def config_debug_is_debugger_present(self) -> bool: ...

    @config_debug_is_debugger_present.setter
    def config_debug_is_debugger_present(self, arg: bool, /) -> None: ...

    @property
    def config_debug_highlight_id_conflicts(self) -> bool: ...

    @config_debug_highlight_id_conflicts.setter
    def config_debug_highlight_id_conflicts(self, arg: bool, /) -> None: ...

    @property
    def config_debug_highlight_id_conflicts_show_item_picker(self) -> bool: ...

    @config_debug_highlight_id_conflicts_show_item_picker.setter
    def config_debug_highlight_id_conflicts_show_item_picker(self, arg: bool, /) -> None: ...

    @property
    def config_debug_begin_return_value_once(self) -> bool: ...

    @config_debug_begin_return_value_once.setter
    def config_debug_begin_return_value_once(self, arg: bool, /) -> None: ...

    @property
    def config_debug_begin_return_value_loop(self) -> bool: ...

    @config_debug_begin_return_value_loop.setter
    def config_debug_begin_return_value_loop(self, arg: bool, /) -> None: ...

    @property
    def config_debug_ignore_focus_loss(self) -> bool: ...

    @config_debug_ignore_focus_loss.setter
    def config_debug_ignore_focus_loss(self, arg: bool, /) -> None: ...

    @property
    def config_debug_ini_settings(self) -> bool: ...

    @config_debug_ini_settings.setter
    def config_debug_ini_settings(self, arg: bool, /) -> None: ...

    @property
    def want_capture_mouse(self) -> bool: ...

    @want_capture_mouse.setter
    def want_capture_mouse(self, arg: bool, /) -> None: ...

    @property
    def want_capture_keyboard(self) -> bool: ...

    @want_capture_keyboard.setter
    def want_capture_keyboard(self, arg: bool, /) -> None: ...

    @property
    def want_text_input(self) -> bool: ...

    @want_text_input.setter
    def want_text_input(self, arg: bool, /) -> None: ...

    @property
    def want_set_mouse_pos(self) -> bool: ...

    @want_set_mouse_pos.setter
    def want_set_mouse_pos(self, arg: bool, /) -> None: ...

    @property
    def want_save_ini_settings(self) -> bool: ...

    @want_save_ini_settings.setter
    def want_save_ini_settings(self, arg: bool, /) -> None: ...

    @property
    def nav_active(self) -> bool: ...

    @nav_active.setter
    def nav_active(self, arg: bool, /) -> None: ...

    @property
    def nav_visible(self) -> bool: ...

    @nav_visible.setter
    def nav_visible(self, arg: bool, /) -> None: ...

    @property
    def framerate(self) -> float: ...

    @framerate.setter
    def framerate(self, arg: float, /) -> None: ...

    @property
    def metrics_render_vertices(self) -> int: ...

    @metrics_render_vertices.setter
    def metrics_render_vertices(self, arg: int, /) -> None: ...

    @property
    def metrics_render_indices(self) -> int: ...

    @metrics_render_indices.setter
    def metrics_render_indices(self, arg: int, /) -> None: ...

    @property
    def metrics_render_windows(self) -> int: ...

    @metrics_render_windows.setter
    def metrics_render_windows(self, arg: int, /) -> None: ...

    @property
    def metrics_active_windows(self) -> int: ...

    @metrics_active_windows.setter
    def metrics_active_windows(self, arg: int, /) -> None: ...

    @property
    def mouse_delta(self) -> Vec2: ...

    @mouse_delta.setter
    def mouse_delta(self, arg: Vec2, /) -> None: ...

    @property
    def mouse_pos(self) -> Vec2: ...

    @mouse_pos.setter
    def mouse_pos(self, arg: Vec2, /) -> None: ...

    @property
    def mouse_wheel(self) -> float: ...

    @mouse_wheel.setter
    def mouse_wheel(self, arg: float, /) -> None: ...

    @property
    def mouse_wheel_h(self) -> float: ...

    @mouse_wheel_h.setter
    def mouse_wheel_h(self, arg: float, /) -> None: ...

    @property
    def mouse_source(self) -> MouseSource: ...

    @mouse_source.setter
    def mouse_source(self, arg: MouseSource, /) -> None: ...

    @property
    def mouse_hovered_viewport(self) -> int: ...

    @mouse_hovered_viewport.setter
    def mouse_hovered_viewport(self, arg: int, /) -> None: ...

    @property
    def key_ctrl(self) -> bool: ...

    @key_ctrl.setter
    def key_ctrl(self, arg: bool, /) -> None: ...

    @property
    def key_shift(self) -> bool: ...

    @key_shift.setter
    def key_shift(self, arg: bool, /) -> None: ...

    @property
    def key_alt(self) -> bool: ...

    @key_alt.setter
    def key_alt(self, arg: bool, /) -> None: ...

    @property
    def key_super(self) -> bool: ...

    @key_super.setter
    def key_super(self, arg: bool, /) -> None: ...

    @property
    def key_mods(self) -> int: ...

    @key_mods.setter
    def key_mods(self, arg: int, /) -> None: ...

    @property
    def want_capture_mouse_unless_popup_close(self) -> bool: ...

    @want_capture_mouse_unless_popup_close.setter
    def want_capture_mouse_unless_popup_close(self, arg: bool, /) -> None: ...

    @property
    def mouse_pos_prev(self) -> Vec2: ...

    @mouse_pos_prev.setter
    def mouse_pos_prev(self, arg: Vec2, /) -> None: ...

    @property
    def mouse_wheel_request_axis_swap(self) -> bool: ...

    @mouse_wheel_request_axis_swap.setter
    def mouse_wheel_request_axis_swap(self, arg: bool, /) -> None: ...

    @property
    def mouse_ctrl_left_as_right_click(self) -> bool: ...

    @mouse_ctrl_left_as_right_click.setter
    def mouse_ctrl_left_as_right_click(self, arg: bool, /) -> None: ...

    @property
    def pen_pressure(self) -> float: ...

    @pen_pressure.setter
    def pen_pressure(self, arg: float, /) -> None: ...

    @property
    def app_focus_lost(self) -> bool: ...

    @app_focus_lost.setter
    def app_focus_lost(self, arg: bool, /) -> None: ...

    @property
    def app_accepting_events(self) -> bool: ...

    @app_accepting_events.setter
    def app_accepting_events(self, arg: bool, /) -> None: ...

    @property
    def input_queue_surrogate(self) -> int: ...

    @input_queue_surrogate.setter
    def input_queue_surrogate(self, arg: int, /) -> None: ...

    @property
    def font_global_scale(self) -> float: ...

    @font_global_scale.setter
    def font_global_scale(self, arg: float, /) -> None: ...

def get_style() -> "ImGuiStyle": ...

def show_demo_window(p_open: bool | None = None) -> bool | None: ...

def show_metrics_window(p_open: bool | None = None) -> bool | None: ...

def show_debug_log_window(p_open: bool | None = None) -> bool | None: ...

def show_id_stack_tool_window(p_open: bool | None = None) -> bool | None: ...

def show_about_window(p_open: bool | None = None) -> bool | None: ...

def show_style_editor(ref: "ImGuiStyle" | None = None) -> None: ...

def show_style_selector(label: str) -> bool: ...

def show_font_selector(label: str) -> None: ...

def show_user_guide() -> None: ...

def get_version() -> str: ...

def style_colors_dark(dst: "ImGuiStyle" | None = None) -> None: ...

def style_colors_light(dst: "ImGuiStyle" | None = None) -> None: ...

def style_colors_classic(dst: "ImGuiStyle" | None = None) -> None: ...

def begin(name: str, p_open: bool | None = None, flags: int = 0) -> tuple: ...

def end() -> None: ...

def begin_child(str_id: str, size: Vec2 = (0, 0), child_flags: int = 0, window_flags: int = 0) -> bool: ...

def end_child() -> None: ...

def is_window_appearing() -> bool: ...

def is_window_collapsed() -> bool: ...

def is_window_focused(flags: int = 0) -> bool: ...

def is_window_hovered(flags: int = 0) -> bool: ...

def get_window_draw_list() -> DrawList: ...

def get_window_dpi_scale() -> float: ...

def get_window_pos() -> Vec2: ...

def get_window_size() -> Vec2: ...

def get_window_width() -> float: ...

def get_window_height() -> float: ...

def get_window_viewport() -> "ImGuiViewport": ...

def set_next_window_pos(pos: Vec2, cond: int = 0, pivot: Vec2 = (0, 0)) -> None: ...

def set_next_window_size(size: Vec2, cond: int = 0) -> None: ...

def set_next_window_content_size(size: Vec2) -> None: ...

def set_next_window_collapsed(collapsed: bool, cond: int = 0) -> None: ...

def set_next_window_focus() -> None: ...

def set_next_window_scroll(scroll: Vec2) -> None: ...

def set_next_window_bg_alpha(alpha: float) -> None: ...

def set_window_pos(pos: Vec2, cond: int = 0) -> None: ...

def set_window_size(size: Vec2, cond: int = 0) -> None: ...

def set_window_collapsed(collapsed: bool, cond: int = 0) -> None: ...

def set_window_focus() -> None: ...

def set_window_pos_str(name: str, pos: Vec2, cond: int = 0) -> None: ...

def set_window_size_str(name: str, size: Vec2, cond: int = 0) -> None: ...

def set_window_collapsed_str(name: str, collapsed: bool, cond: int = 0) -> None: ...

def set_window_focus_str(name: str) -> None: ...

def get_scroll_x() -> float: ...

def get_scroll_y() -> float: ...

def set_scroll_x(scroll_x: float) -> None: ...

def set_scroll_y(scroll_y: float) -> None: ...

def get_scroll_max_x() -> float: ...

def get_scroll_max_y() -> float: ...

def set_scroll_here_x(center_x_ratio: float = 0.5) -> None: ...

def set_scroll_here_y(center_y_ratio: float = 0.5) -> None: ...

def set_scroll_from_pos_x(local_x: float, center_x_ratio: float = 0.5) -> None: ...

def set_scroll_from_pos_y(local_y: float, center_y_ratio: float = 0.5) -> None: ...

def push_font_float(font: "ImFont", font_size_base_unscaled: float) -> None: ...

def pop_font() -> None: ...

def get_font() -> "ImFont": ...

def get_font_size() -> float: ...

def get_font_baked() -> "ImFontBaked": ...

def push_style_color(idx: int, col: int) -> None: ...

def push_style_color_im_vec4(idx: int, col: Vec4) -> None: ...

def pop_style_color(count: int = 1) -> None: ...

def push_style_var(idx: int, val: float) -> None: ...

def push_style_var_im_vec2(idx: int, val: Vec2) -> None: ...

def push_style_var_x(idx: int, val_x: float) -> None: ...

def push_style_var_y(idx: int, val_y: float) -> None: ...

def pop_style_var(count: int = 1) -> None: ...

def push_item_flag(option: int, enabled: bool) -> None: ...

def pop_item_flag() -> None: ...

def push_item_width(item_width: float) -> None: ...

def pop_item_width() -> None: ...

def set_next_item_width(item_width: float) -> None: ...

def calc_item_width() -> float: ...

def push_text_wrap_pos(wrap_local_pos_x: float = 0.0) -> None: ...

def pop_text_wrap_pos() -> None: ...

def get_font_tex_uv_white_pixel() -> Vec2: ...

def get_color_u32(idx: int, alpha_mul: float = 1.0) -> int: ...

def get_color_u32_im_vec4(col: Vec4) -> int: ...

def get_color_u32_im_u32(col: int, alpha_mul: float = 1.0) -> int: ...

def get_cursor_screen_pos() -> Vec2: ...

def set_cursor_screen_pos(pos: Vec2) -> None: ...

def get_content_region_avail() -> Vec2: ...

def get_cursor_pos() -> Vec2: ...

def get_cursor_pos_x() -> float: ...

def get_cursor_pos_y() -> float: ...

def set_cursor_pos(local_pos: Vec2) -> None: ...

def set_cursor_pos_x(local_x: float) -> None: ...

def set_cursor_pos_y(local_y: float) -> None: ...

def get_cursor_start_pos() -> Vec2: ...

def separator() -> None: ...

def same_line(offset_from_start_x: float = 0.0, spacing: float = -1.0) -> None: ...

def new_line() -> None: ...

def spacing() -> None: ...

def dummy(size: Vec2) -> None: ...

def indent(indent_w: float = 0.0) -> None: ...

def unindent(indent_w: float = 0.0) -> None: ...

def begin_group() -> None: ...

def end_group() -> None: ...

def align_text_to_frame_padding() -> None: ...

def get_text_line_height() -> float: ...

def get_text_line_height_with_spacing() -> float: ...

def get_frame_height() -> float: ...

def get_frame_height_with_spacing() -> float: ...

def push_id(str_id: str) -> None: ...

def push_id_str(str_id_begin: str, str_id_end: str) -> None: ...

def push_id_int(int_id: int) -> None: ...

def pop_id() -> None: ...

def get_id_int(int_id: int) -> int: ...

def text(fmt: str) -> None: ...

def text_colored(col: Vec4, fmt: str) -> None: ...

def text_disabled(fmt: str) -> None: ...

def text_wrapped(fmt: str) -> None: ...

def label_text(label: str, fmt: str) -> None: ...

def bullet_text(fmt: str) -> None: ...

def separator_text(label: str) -> None: ...

def button(label: str, size: Vec2 = (0, 0)) -> bool: ...

def small_button(label: str) -> bool: ...

def invisible_button(str_id: str, size: Vec2, flags: int = 0) -> bool: ...

def arrow_button(str_id: str, dir: Dir) -> bool: ...

def checkbox(label: str, v: bool) -> tuple: ...

def radio_button(label: str, active: bool) -> bool: ...

def progress_bar(fraction: float, size_arg: Vec2 = (-1.175494351e-38, 0), overlay: str | None = None) -> None: ...

def bullet() -> None: ...

def text_link(label: str) -> bool: ...

def text_link_open_u_r_l(label: str, url: str | None = None) -> bool: ...

def image(tex_ref: "ImTextureRef", image_size: Vec2, uv0: Vec2 = (0, 0), uv1: Vec2 = (1, 1)) -> None: ...

def image_with_bg(tex_ref: "ImTextureRef", image_size: Vec2, uv0: Vec2 = (0, 0), uv1: Vec2 = (1, 1), bg_col: Vec4 = (0, 0, 0, 0), tint_col: Vec4 = (1, 1, 1, 1)) -> None: ...

def image_button(str_id: str, tex_ref: "ImTextureRef", image_size: Vec2, uv0: Vec2 = (0, 0), uv1: Vec2 = (1, 1), bg_col: Vec4 = (0, 0, 0, 0), tint_col: Vec4 = (1, 1, 1, 1)) -> bool: ...

def drag_float(label: str, v: float, v_speed: float = 1.0, v_min: float = 0.0, v_max: float = 0.0, format: str = '%.3f', flags: int = 0) -> tuple: ...

def drag_float2(label: str, v: Sequence[float], v_speed: float = 1.0, v_min: float = 0.0, v_max: float = 0.0, format: str = '%.3f', flags: int = 0) -> tuple: ...

def drag_float3(label: str, v: Sequence[float], v_speed: float = 1.0, v_min: float = 0.0, v_max: float = 0.0, format: str = '%.3f', flags: int = 0) -> tuple: ...

def drag_float4(label: str, v: Sequence[float], v_speed: float = 1.0, v_min: float = 0.0, v_max: float = 0.0, format: str = '%.3f', flags: int = 0) -> tuple: ...

def drag_int(label: str, v: int, v_speed: float = 1.0, v_min: int = 0, v_max: int = 0, format: str = '%d', flags: int = 0) -> tuple: ...

def drag_int2(label: str, v: Sequence[int], v_speed: float = 1.0, v_min: int = 0, v_max: int = 0, format: str = '%d', flags: int = 0) -> tuple: ...

def drag_int3(label: str, v: Sequence[int], v_speed: float = 1.0, v_min: int = 0, v_max: int = 0, format: str = '%d', flags: int = 0) -> tuple: ...

def drag_int4(label: str, v: Sequence[int], v_speed: float = 1.0, v_min: int = 0, v_max: int = 0, format: str = '%d', flags: int = 0) -> tuple: ...

def slider_float(label: str, v: float, v_min: float, v_max: float, format: str = '%.3f', flags: int = 0) -> tuple: ...

def slider_float2(label: str, v: Sequence[float], v_min: float, v_max: float, format: str = '%.3f', flags: int = 0) -> tuple: ...

def slider_float3(label: str, v: Sequence[float], v_min: float, v_max: float, format: str = '%.3f', flags: int = 0) -> tuple: ...

def slider_float4(label: str, v: Sequence[float], v_min: float, v_max: float, format: str = '%.3f', flags: int = 0) -> tuple: ...

def slider_angle(label: str, v_rad: float, v_degrees_min: float = -360.0, v_degrees_max: float = 360.0, format: str = '%.0f deg', flags: int = 0) -> tuple: ...

def slider_int(label: str, v: int, v_min: int, v_max: int, format: str = '%d', flags: int = 0) -> tuple: ...

def slider_int2(label: str, v: Sequence[int], v_min: int, v_max: int, format: str = '%d', flags: int = 0) -> tuple: ...

def slider_int3(label: str, v: Sequence[int], v_min: int, v_max: int, format: str = '%d', flags: int = 0) -> tuple: ...

def slider_int4(label: str, v: Sequence[int], v_min: int, v_max: int, format: str = '%d', flags: int = 0) -> tuple: ...

def v_slider_float(label: str, size: Vec2, v: float, v_min: float, v_max: float, format: str = '%.3f', flags: int = 0) -> tuple: ...

def v_slider_int(label: str, size: Vec2, v: int, v_min: int, v_max: int, format: str = '%d', flags: int = 0) -> tuple: ...

def input_float(label: str, v: float, step: float = 0.0, step_fast: float = 0.0, format: str = '%.3f', flags: int = 0) -> tuple: ...

def input_float2(label: str, v: Sequence[float], format: str = '%.3f', flags: int = 0) -> tuple: ...

def input_float3(label: str, v: Sequence[float], format: str = '%.3f', flags: int = 0) -> tuple: ...

def input_float4(label: str, v: Sequence[float], format: str = '%.3f', flags: int = 0) -> tuple: ...

def input_int(label: str, v: int, step: int = 1, step_fast: int = 100, flags: int = 0) -> tuple: ...

def input_int2(label: str, v: Sequence[int], flags: int = 0) -> tuple: ...

def input_int3(label: str, v: Sequence[int], flags: int = 0) -> tuple: ...

def input_int4(label: str, v: Sequence[int], flags: int = 0) -> tuple: ...

def color_edit3(label: str, col: Sequence[float], flags: int = 0) -> tuple: ...

def color_edit4(label: str, col: Sequence[float], flags: int = 0) -> tuple: ...

def color_picker3(label: str, col: Sequence[float], flags: int = 0) -> tuple: ...

def color_button(desc_id: str, col: Vec4, flags: int = 0, size: Vec2 = (0, 0)) -> bool: ...

def set_color_edit_options(flags: int) -> None: ...

def tree_node(label: str) -> bool: ...

def tree_node_str(str_id: str, fmt: str) -> bool: ...

def tree_node_ex(label: str, flags: int = 0) -> bool: ...

def tree_node_ex_str(str_id: str, flags: int, fmt: str) -> bool: ...

def tree_push(str_id: str) -> None: ...

def tree_pop() -> None: ...

def get_tree_node_to_label_spacing() -> float: ...

def collapsing_header(label: str, flags: int = 0) -> bool: ...

def set_next_item_open(is_open: bool, cond: int = 0) -> None: ...

def set_next_item_storage_id(storage_id: int) -> None: ...

def selectable(label: str, selected: bool = False, flags: int = 0, size: Vec2 = (0, 0)) -> bool: ...

def begin_multi_select(flags: int, selection_size: int = -1, items_count: int = -1) -> "ImGuiMultiSelectIO": ...

def end_multi_select() -> "ImGuiMultiSelectIO": ...

def set_next_item_selection_user_data(selection_user_data: int) -> None: ...

def is_item_toggled_selection() -> bool: ...

def begin_menu_bar() -> bool: ...

def end_menu_bar() -> None: ...

def begin_main_menu_bar() -> bool: ...

def end_main_menu_bar() -> None: ...

def begin_menu(label: str, enabled: bool = True) -> bool: ...

def end_menu() -> None: ...

def menu_item(label: str, shortcut: str | None = None, selected: bool = False, enabled: bool = True) -> bool: ...

def begin_tooltip() -> bool: ...

def end_tooltip() -> None: ...

def set_tooltip(fmt: str) -> None: ...

def begin_item_tooltip() -> bool: ...

def set_item_tooltip(fmt: str) -> None: ...

def begin_popup(str_id: str, flags: int = 0) -> bool: ...

def begin_popup_modal(name: str, p_open: bool | None = None, flags: int = 0) -> tuple: ...

def end_popup() -> None: ...

def open_popup(str_id: str, popup_flags: int = 0) -> None: ...

def open_popup_on_item_click(str_id: str | None = None, popup_flags: int = 1) -> None: ...

def close_current_popup() -> None: ...

def begin_popup_context_item(str_id: str | None = None, popup_flags: int = 1) -> bool: ...

def begin_popup_context_window(str_id: str | None = None, popup_flags: int = 1) -> bool: ...

def begin_popup_context_void(str_id: str | None = None, popup_flags: int = 1) -> bool: ...

def is_popup_open(str_id: str, flags: int = 0) -> bool: ...

def begin_table(str_id: str, columns: int, flags: int = 0, outer_size: Vec2 = (0.0, 0.0), inner_width: float = 0.0) -> bool: ...

def end_table() -> None: ...

def table_next_row(row_flags: int = 0, min_row_height: float = 0.0) -> None: ...

def table_next_column() -> bool: ...

def table_set_column_index(column_n: int) -> bool: ...

def table_setup_scroll_freeze(cols: int, rows: int) -> None: ...

def table_header(label: str) -> None: ...

def table_headers_row() -> None: ...

def table_angled_headers_row() -> None: ...

def table_get_column_count() -> int: ...

def table_get_column_index() -> int: ...

def table_get_row_index() -> int: ...

def table_get_column_name(column_n: int = -1) -> str: ...

def table_get_column_flags(column_n: int = -1) -> int: ...

def table_set_column_enabled(column_n: int, v: bool) -> None: ...

def table_get_hovered_column() -> int: ...

def table_set_bg_color(target: int, color: int, column_n: int = -1) -> None: ...

def columns(count: int = 1, id: str | None = None, borders: bool = True) -> None: ...

def next_column() -> None: ...

def get_column_index() -> int: ...

def get_column_width(column_index: int = -1) -> float: ...

def set_column_width(column_index: int, width: float) -> None: ...

def get_column_offset(column_index: int = -1) -> float: ...

def set_column_offset(column_index: int, offset_x: float) -> None: ...

def get_columns_count() -> int: ...

def begin_tab_bar(str_id: str, flags: int = 0) -> bool: ...

def end_tab_bar() -> None: ...

def begin_tab_item(label: str, p_open: bool | None = None, flags: int = 0) -> tuple: ...

def end_tab_item() -> None: ...

def tab_item_button(label: str, flags: int = 0) -> bool: ...

def set_tab_item_closed(tab_or_docked_window_label: str) -> None: ...

def dock_space(dockspace_id: int, size: Vec2 = (0, 0), flags: int = 0, window_class: "ImGuiWindowClass" | None = None) -> int: ...

def dock_space_over_viewport(dockspace_id: int = 0, viewport: "ImGuiViewport" | None = None, flags: int = 0, window_class: "ImGuiWindowClass" | None = None) -> int: ...

def set_next_window_dock_id(dock_id: int, cond: int = 0) -> None: ...

def set_next_window_class(window_class: "ImGuiWindowClass") -> None: ...

def get_window_dock_id() -> int: ...

def is_window_docked() -> bool: ...

def log_to_t_t_y(auto_open_depth: int = -1) -> None: ...

def log_to_file(auto_open_depth: int = -1, filename: str | None = None) -> None: ...

def log_to_clipboard(auto_open_depth: int = -1) -> None: ...

def log_finish() -> None: ...

def log_buttons() -> None: ...

def log_text(fmt: str) -> None: ...

def begin_drag_drop_source(flags: int = 0) -> bool: ...

def set_drag_drop_payload(type: str, data: Sequence[int], sz: int, cond: int = 0) -> bool: ...

def end_drag_drop_source() -> None: ...

def begin_drag_drop_target() -> bool: ...

def accept_drag_drop_payload(type: str, flags: int = 0) -> "ImGuiPayload": ...

def end_drag_drop_target() -> None: ...

def get_drag_drop_payload() -> "ImGuiPayload": ...

def begin_disabled(disabled: bool = True) -> None: ...

def end_disabled() -> None: ...

def push_clip_rect(clip_rect_min: Vec2, clip_rect_max: Vec2, intersect_with_current_clip_rect: bool) -> None: ...

def pop_clip_rect() -> None: ...

def set_item_default_focus() -> None: ...

def set_keyboard_focus_here(offset: int = 0) -> None: ...

def set_nav_cursor_visible(visible: bool) -> None: ...

def set_next_item_allow_overlap() -> None: ...

def is_item_hovered(flags: int = 0) -> bool: ...

def is_item_active() -> bool: ...

def is_item_focused() -> bool: ...

def is_item_clicked(mouse_button: int = 0) -> bool: ...

def is_item_visible() -> bool: ...

def is_item_edited() -> bool: ...

def is_item_activated() -> bool: ...

def is_item_deactivated() -> bool: ...

def is_item_deactivated_after_edit() -> bool: ...

def is_item_toggled_open() -> bool: ...

def is_any_item_hovered() -> bool: ...

def is_any_item_active() -> bool: ...

def is_any_item_focused() -> bool: ...

def get_item_id() -> int: ...

def get_item_rect_min() -> Vec2: ...

def get_item_rect_max() -> Vec2: ...

def get_item_rect_size() -> Vec2: ...

def get_main_viewport() -> "ImGuiViewport": ...

def get_background_draw_list(viewport: "ImGuiViewport" | None = None) -> DrawList: ...

def get_foreground_draw_list(viewport: "ImGuiViewport" | None = None) -> DrawList: ...

def is_rect_visible_by_size(size: Vec2) -> bool: ...

def is_rect_visible(rect_min: Vec2, rect_max: Vec2) -> bool: ...

def get_time() -> float: ...

def get_frame_count() -> int: ...

def get_style_color_name(idx: int) -> str: ...

def set_state_storage(storage: "ImGuiStorage") -> None: ...

def get_state_storage() -> "ImGuiStorage": ...

def calc_text_size(text: str, hide_text_after_double_hash: bool = False, wrap_width: float = -1.0) -> Vec2: ...

def color_convert_u32_to_float4(value: int) -> Vec4: ...

def color_convert_float4_to_u32(value: Vec4) -> int: ...

def is_key_down(key: Key) -> bool: ...

def is_key_pressed(key: Key, repeat: bool = True) -> bool: ...

def is_key_released(key: Key) -> bool: ...

def is_key_chord_pressed(key_chord: int) -> bool: ...

def get_key_pressed_amount(key: Key, repeat_delay: float, rate: float) -> int: ...

def get_key_name(key: Key) -> str: ...

def set_next_frame_want_capture_keyboard(want_capture_keyboard: bool) -> None: ...

def shortcut(key_chord: int, flags: int = 0) -> bool: ...

def set_next_item_shortcut(key_chord: int, flags: int = 0) -> None: ...

def set_item_key_owner(key: Key) -> None: ...

def is_mouse_down(button: int) -> bool: ...

def is_mouse_clicked(button: int, repeat: bool = False) -> bool: ...

def is_mouse_released(button: int) -> bool: ...

def is_mouse_double_clicked(button: int) -> bool: ...

def is_mouse_released_with_delay(button: int, delay: float) -> bool: ...

def get_mouse_clicked_count(button: int) -> int: ...

def is_mouse_hovering_rect(r_min: Vec2, r_max: Vec2, clip: bool = True) -> bool: ...

def is_any_mouse_down() -> bool: ...

def get_mouse_pos() -> Vec2: ...

def get_mouse_pos_on_opening_current_popup() -> Vec2: ...

def is_mouse_dragging(button: int, lock_threshold: float = -1.0) -> bool: ...

def get_mouse_drag_delta(button: int = 0, lock_threshold: float = -1.0) -> Vec2: ...

def reset_mouse_drag_delta(button: int = 0) -> None: ...

def get_mouse_cursor() -> int: ...

def set_mouse_cursor(cursor_type: int) -> None: ...

def set_next_frame_want_capture_mouse(want_capture_mouse: bool) -> None: ...

def get_clipboard_text() -> str: ...

def set_clipboard_text(text: str) -> None: ...

def load_ini_settings_from_disk(ini_filename: str) -> None: ...

def save_ini_settings_to_disk(ini_filename: str) -> None: ...

def debug_text_encoding(text: str) -> None: ...

def debug_flash_style_color(idx: int) -> None: ...

def debug_start_item_picker() -> None: ...

def debug_check_version_and_data_layout(version_str: str, sz_io: int, sz_style: int, sz_vec2: int, sz_vec4: int, sz_drawvert: int, sz_drawidx: int) -> bool: ...

def debug_log(fmt: str) -> None: ...

def find_viewport_by_id(id: int) -> "ImGuiViewport": ...

class DrawList:
    def push_clip_rect(self, clip_rect_min: Vec2, clip_rect_max: Vec2, intersect_with_current_clip_rect: bool = False) -> None: ...

    def push_clip_rect_full_screen(self) -> None: ...

    def pop_clip_rect(self) -> None: ...

    def push_texture(self, tex_ref: "ImTextureRef") -> None: ...

    def pop_texture(self) -> None: ...

    def get_clip_rect_min(self) -> Vec2: ...

    def get_clip_rect_max(self) -> Vec2: ...

    def add_line(self, p1: Vec2, p2: Vec2, col: int, thickness: float = 1.0) -> None: ...

    def add_rect(self, p_min: Vec2, p_max: Vec2, col: int, rounding: float = 0.0, flags: int = 0, thickness: float = 1.0) -> None: ...

    def add_rect_filled(self, p_min: Vec2, p_max: Vec2, col: int, rounding: float = 0.0, flags: int = 0) -> None: ...

    def add_rect_filled_multi_color(self, p_min: Vec2, p_max: Vec2, col_upr_left: int, col_upr_right: int, col_bot_right: int, col_bot_left: int) -> None: ...

    def add_quad(self, p1: Vec2, p2: Vec2, p3: Vec2, p4: Vec2, col: int, thickness: float = 1.0) -> None: ...

    def add_quad_filled(self, p1: Vec2, p2: Vec2, p3: Vec2, p4: Vec2, col: int) -> None: ...

    def add_triangle(self, p1: Vec2, p2: Vec2, p3: Vec2, col: int, thickness: float = 1.0) -> None: ...

    def add_triangle_filled(self, p1: Vec2, p2: Vec2, p3: Vec2, col: int) -> None: ...

    def add_circle(self, center: Vec2, radius: float, col: int, num_segments: int = 0, thickness: float = 1.0) -> None: ...

    def add_circle_filled(self, center: Vec2, radius: float, col: int, num_segments: int = 0) -> None: ...

    def add_ngon(self, center: Vec2, radius: float, col: int, num_segments: int, thickness: float = 1.0) -> None: ...

    def add_ngon_filled(self, center: Vec2, radius: float, col: int, num_segments: int) -> None: ...

    def add_ellipse(self, center: Vec2, radius: Vec2, col: int, rot: float = 0.0, num_segments: int = 0, thickness: float = 1.0) -> None: ...

    def add_ellipse_filled(self, center: Vec2, radius: Vec2, col: int, rot: float = 0.0, num_segments: int = 0) -> None: ...

    def add_text(self, pos: Vec2, col: int, text: str) -> None: ...

    def add_bezier_cubic(self, p1: Vec2, p2: Vec2, p3: Vec2, p4: Vec2, col: int, thickness: float, num_segments: int = 0) -> None: ...

    def add_bezier_quadratic(self, p1: Vec2, p2: Vec2, p3: Vec2, col: int, thickness: float, num_segments: int = 0) -> None: ...

    def add_polyline(self, points: Vec2, num_points: int, col: int, flags: int, thickness: float) -> None: ...

    def add_convex_poly_filled(self, points: Vec2, num_points: int, col: int) -> None: ...

    def add_concave_poly_filled(self, points: Vec2, num_points: int, col: int) -> None: ...

    def add_image(self, tex_ref: "ImTextureRef", p_min: Vec2, p_max: Vec2, uv_min: Vec2 = (0, 0), uv_max: Vec2 = (1, 1), col: int = 4294967295) -> None: ...

    def add_image_quad(self, tex_ref: "ImTextureRef", p1: Vec2, p2: Vec2, p3: Vec2, p4: Vec2, uv1: Vec2 = (0, 0), uv2: Vec2 = (1, 0), uv3: Vec2 = (1, 1), uv4: Vec2 = (0, 1), col: int = 4294967295) -> None: ...

    def add_image_rounded(self, tex_ref: "ImTextureRef", p_min: Vec2, p_max: Vec2, uv_min: Vec2, uv_max: Vec2, col: int, rounding: float, flags: int = 0) -> None: ...

    def path_clear(self) -> None: ...

    def path_line_to(self, pos: Vec2) -> None: ...

    def path_line_to_merge_duplicate(self, pos: Vec2) -> None: ...

    def path_fill_convex(self, col: int) -> None: ...

    def path_fill_concave(self, col: int) -> None: ...

    def path_stroke(self, col: int, flags: int = 0, thickness: float = 1.0) -> None: ...

    def path_arc_to(self, center: Vec2, radius: float, a_min: float, a_max: float, num_segments: int = 0) -> None: ...

    def path_arc_to_fast(self, center: Vec2, radius: float, a_min_of_12: int, a_max_of_12: int) -> None: ...

    def path_elliptical_arc_to(self, center: Vec2, radius: Vec2, rot: float, a_min: float, a_max: float, num_segments: int = 0) -> None: ...

    def path_bezier_cubic_curve_to(self, p2: Vec2, p3: Vec2, p4: Vec2, num_segments: int = 0) -> None: ...

    def path_bezier_quadratic_curve_to(self, p2: Vec2, p3: Vec2, num_segments: int = 0) -> None: ...

    def path_rect(self, rect_min: Vec2, rect_max: Vec2, rounding: float = 0.0, flags: int = 0) -> None: ...

    def add_draw_cmd(self) -> None: ...

    def clone_output(self) -> DrawList: ...

    def channels_split(self, count: int) -> None: ...

    def channels_merge(self) -> None: ...

    def channels_set_current(self, n: int) -> None: ...

    def prim_reserve(self, idx_count: int, vtx_count: int) -> None: ...

    def prim_unreserve(self, idx_count: int, vtx_count: int) -> None: ...

    def prim_rect(self, a: Vec2, b: Vec2, col: int) -> None: ...

    def prim_write_vtx(self, pos: Vec2, uv: Vec2, col: int) -> None: ...

    def prim_write_idx(self, idx: int) -> None: ...

    def prim_vtx(self, pos: Vec2, uv: Vec2, col: int) -> None: ...

    def push_texture_id(self, tex_ref: "ImTextureRef") -> None: ...

    def pop_texture_id(self) -> None: ...

    def add_rect_batch(self, p_min: Annotated[ArrayLike, dict(dtype='float32', shape=(None, 2))], p_max: Annotated[ArrayLike, dict(dtype='float32', shape=(None, 2))], color: Annotated[ArrayLike, dict(dtype='uint32', shape=(None))], rounding: Annotated[ArrayLike, dict(dtype='float32', shape=(None))], thickness: Annotated[ArrayLike, dict(dtype='float32', shape=(None))]) -> None: ...

    def add_rect_filled_batch(self, p_min: Annotated[ArrayLike, dict(dtype='float32', shape=(None, 2))], p_max: Annotated[ArrayLike, dict(dtype='float32', shape=(None, 2))], color: Annotated[ArrayLike, dict(dtype='uint32', shape=(None))], rounding: Annotated[ArrayLike, dict(dtype='float32', shape=(None))]) -> None: ...

def push_font(font: "ImFont") -> None: ...

def set_window_font_scale(scale: float) -> None: ...

def image_im_vec4(tex_ref: "ImTextureRef", image_size: Vec2, uv0: Vec2, uv1: Vec2, tint_col: Vec4, border_col: Vec4) -> None: ...

def push_button_repeat(repeat: bool) -> None: ...

def pop_button_repeat() -> None: ...

def push_tab_stop(tab_stop: bool) -> None: ...

def pop_tab_stop() -> None: ...

def get_content_region_max() -> Vec2: ...

def get_window_content_region_min() -> Vec2: ...

def get_window_content_region_max() -> Vec2: ...

def begin_child_frame(id: int, size: Vec2, window_flags: int = 0) -> bool: ...

def end_child_frame() -> None: ...

def show_stack_tool_window(p_open: bool | None = None) -> bool | None: ...

def set_item_allow_overlap() -> None: ...

def get_io() -> IO: ...
