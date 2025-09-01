from functools import total_ordering
from typing import Iterable, Literal


@total_ordering
class Key:
    """
    Represents a single keyboard, mouse, or controller key input. You can access a preset list of
    these events via the `pykeys.key` import, for example:

    >>> from pykeys import key
    >>> key.a # represents the "a" key

    Otherwise, you can use this class to reference keys using a string:

    >>> Key("a") # also represents the "a" key

    - For mouse keys, use `Key("mouse:1")` through `Key("mouse:5")` for buttons 1-5.
    - For numpad keys, use `Key("num:0")` through `Key("num:9")` for keys 0-9.

    For symbol keys, use:

    >>> Key("+") # the + key
    >>> Key("num:+") # the + key on the numpad

    Key objects are comparable, hashable, and equatable.
    """

    id: str

    def __init__(self, input: "str | Key"):
        self.id = input if isinstance(input, str) else input.id

    @property
    def label(self):
        return self.id

    @property
    def is_numpad(self):
        return self.id.startswith("num:")

    def __hash__(self) -> int:
        return hash(self.id)

    def __keystate__(self):
        return self.down

    def __hotkey__(self):
        return self.down.__hotkey__()

    def __invert__(self):
        return KeyInputState(self, "up")

    @property
    def is_mouse(self):
        """
        Whether this key is a mouse key.
        """
        return self.id.startswith("mouse:")

    @property
    def is_keyboard(self):
        """
        Whether this key is a keyboard key.
        """
        return not self.is_mouse

    def __lt__(self, other: "Key") -> bool:
        return self.id < other.id

    @property
    def specificity(self):
        return 1

    def __and__(self, other: "KeysInput"):
        """
        Creates a Hotkey using the left key as a trigger (down event) and the right keys as modifiers.

        >>> from pykeys import key
        >>> hotkey = key.a & key.ctrl + key.shift
        >>> hotkey2 = key.a & [key.ctrl, key.shift]
        >>> hotkey3 = key.a & key.ctrl
        """
        return self.down.modifiers(other)

    @property
    def down(self) -> "KeyInputState":

        return KeyInputState(self, "down")

    @property
    def up(self):
        return KeyInputState(self, "up")

    def __repr__(self) -> str:
        return f"{self.id}"

    def __str__(self) -> str:
        return repr(self)


type KeyStateName = Literal["down", "up"]


@total_ordering
class KeyInputState:
    """
    Represents key up or key down states.
    """

    __match_args__ = ("key", "state")

    @property
    def hotkey(self):
        return self.__hotkey__()

    def __str__(self) -> str:
        """
        A label for the Hotkey's trigger key.
        """
        return f"{self.state_char}{self.key}"

    def __repr__(self) -> str:
        return str(self)

    def __keystate__(self):
        return self

    def __hotkey__(self):
        from ..hotkey import Hotkey, HotkeyInfo

        return Hotkey(
            HotkeyInfo(trigger=self, modifiers=KeySet(), passthrough=False)
        )

    def __invert__(self):
        return KeyInputState(self.key, "up" if self.is_down else "down")

    def __init__(self, key: Key, state: KeyStateName):
        self.key = key
        self.state = state

    def __hash__(self) -> int:
        return hash(self.key) ^ hash(self.state)

    def modifiers(self, modifiers: "KeysInput"):
        from ..hotkey import Hotkey, HotkeyInfo

        """
        Adds modifiers to a Hotkey.
        """
        return Hotkey(
            HotkeyInfo(
                trigger=self,
                modifiers=KeySet(modifiers),
                passthrough=False,
            )
        )

    @property
    def state_char(self) -> str:
        return "↓" if self.state == "down" else "↑"

    def __lt__(self, other: "KeyInputState") -> bool:
        return self.key < other.key and self.state < other.state

    @property
    def specificity(self) -> int:
        return self.key.specificity

    @property
    def is_down(self) -> bool:
        return self.state == "down"

    @property
    def is_up(self) -> bool:
        return self.state == "up"


type KeyInput = "str | Key"

type KeysInput = KeySet | Iterable[Key | KeyInputState]


@total_ordering
class KeySet:
    """
    An unordered collection of `KeyInputState` objects, used as a set of modifiers.
    """

    __match_args__ = ("set",)
    set: dict[Key, KeyInputState]

    def __invert__(self):
        return KeySet(key.__invert__() for key in self.set)

    def __init__(self, input: KeysInput = {}):
        match input:
            case KeySet():
                self.set = input.set
            case _:
                self.set = {
                    key.__keystate__().key: key.__keystate__() for key in input
                }

    def __hash__(self) -> int:
        return hash((x, y) for x, y in self.set.items())

    def __add__(
        self,
        other: "KeyInputState | Key | Iterable[Key | KeyInputState] | KeySet",
    ):
        """
        Combines two keys into a `KeySet`, an unordered collection of keys.
        """
        from keyweave.key_types import KeySet

        match other:
            case KeyInputState():
                return KeySet(self.set | {other.key: other})
            case KeySet():
                return KeySet(self.set | other.set)
            case _:
                raise TypeError(f"Invalid key input: {other}")

    def __bool__(self) -> bool:
        return bool(self.set)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, KeySet) and self.set == other.set

    def __lt__(self, other: "KeySet") -> bool:
        if self.set.keys() != other.set.keys():
            return self.set.keys() < other.set.keys()
        ordered_keys = sorted(self.set.keys())
        for key in ordered_keys:
            if self.set[key] != other.set[key]:
                return self.set[key] < other.set[key]
        return False

    @property
    def specificity(self) -> int:
        return sum(key.specificity for key in self.set)

    def __iter__(self):
        return iter(self.set.values())

    def __contains__(self, key: Key | KeyInputState) -> bool:
        return self.set[key.__keystate__().key] == key.__keystate__()

    def __len__(self) -> int:
        return len(self.set)

    def __repr__(self) -> str:
        if not self.set:
            return ""
        joined = " + ".join(repr(key) for key in self.set)
        return joined

    def __str__(self) -> str:
        if not self.set:
            return "[]"
        joined = ", ".join(str(key) for key in self.set.values())
        return f"{{{joined}}}"
