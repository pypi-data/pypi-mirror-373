from dataclasses import dataclass, field
import inspect
from typing import Any, Iterable, Iterator, overload

from keyweave.commanding import (
    Command,
    CommandProducer,
    FuncHotkeyHandler,
)
from keyweave.key_types import Key, KeyInputState
from keyweave.hotkey import (
    Hotkey,
    HotkeyEvent,
    HotkeyInfo,
    HotkeyInput,
    InputEvent,
)


@dataclass(match_args=True)
class Binding:
    hotkey: HotkeyInfo
    command: Command
    _number_of_args: int = field(init=False)

    def __str__(self):
        return f"⛓️‍💥{self.hotkey} → ⚡{self.command.info.label}"

    @property
    def handler(self) -> FuncHotkeyHandler:
        return self.command.handler

    def __post_init__(self):
        self._number_of_args = len(inspect.signature(self.handler).parameters)
        if not callable(self.handler):
            raise ValueError(f"handler must be a callable, got {self.handler}")
        if self._number_of_args != 1:
            raise ValueError(
                f"handler must accept 1 argument, got {self._number_of_args}"
            )

    def __call__(self, event: InputEvent, /):
        handler = self.handler
        triggered_key_event = HotkeyEvent(self, event)
        handler(triggered_key_event)


class BindingCollection(Iterable["KeyBindingCollection"]):
    _map: dict[Key, "KeyBindingCollection"]
    _handler_map: dict[KeyInputState, Any]

    def __init__(self, input: dict[Key, "KeyBindingCollection"] = {}):
        self._map = input

    def __add__(self, input: Binding):
        trigger_key = input.hotkey.trigger.key
        new_map = self._map.copy()
        trigger_collection = new_map.get(
            trigger_key, KeyBindingCollection(trigger_key)
        )
        trigger_collection = trigger_collection.set(input)
        new_map[trigger_key] = trigger_collection
        return BindingCollection(new_map)

    @property
    def keys(self) -> set[Key]:
        return set(self._map.keys())

    @property
    def bindings(self) -> Iterable[Binding]:
        return (binding for collection in self for binding in collection)

    @property
    def pairs(self) -> Iterable[tuple[Key, "KeyBindingCollection"]]:
        return self._map.items()

    @overload
    def __getitem__(self, key: Key) -> "KeyBindingCollection": ...

    @overload
    def __getitem__(self, key: Hotkey) -> Binding: ...

    def __getitem__(
        self, key: Key | HotkeyInfo | Hotkey | KeyInputState
    ) -> "KeyBindingCollection | Binding":
        match key:
            case HotkeyInfo():
                return self._map[key.trigger.key][key]
            case Key() | KeyInputState():
                return self._map[key.__keystate__().key]
            case Hotkey():
                return self._map[key.info.trigger.key][key]

    def __iter__(self) -> Iterator["KeyBindingCollection"]:
        return iter(self._map.values())

    def __len__(self) -> int:
        return len(self._map)

    def __repr__(self) -> str:
        return repr(self._map)


class KeyBindingCollection:
    key: Key
    _map: dict[HotkeyInfo, Binding]

    def __init__(self, trigger: Key, bindings: dict[HotkeyInfo, Binding] = {}):
        self.key = trigger
        self._map = bindings

    def __getitem__(self, key: HotkeyInput) -> Binding:

        return self._map[key.__hotkey__().info]

    def set(self, binding: Binding):
        return KeyBindingCollection(
            self.key, {**self._map, binding.hotkey: binding}
        )

    def __len__(self) -> int:
        return len(self._map)

    def __iter__(self) -> Iterator[Binding]:
        return iter(self._map.values())

    def __add__(self, binding: Binding):
        return self.set(binding)


@dataclass
class BindingProducer:
    cmd: "Command | CommandProducer"
    hotkey: Hotkey

    def __get__(self, instance: object, owner: type) -> "Binding":
        r_cmd = self.cmd.__get__(instance, owner)

        return r_cmd.bind(self.hotkey)
