import threading
from typing import Any
from keyweave.bindings import KeyBindingCollection
from keyweave.hotkey import InputEvent
from keyweave.key_types import Key, KeyInputState, KeySet
from keyboard import KeyboardEvent, hook_key, is_pressed, unhook

from win32api import GetAsyncKeyState  # type: ignore
from keyweave._util.logging import keyweaveLogger

from keyweave.scheduling import Scheduler

keyweaveHookLogger = keyweaveLogger.getChild("KeyHook")


class KeyHook:
    _internal_handler: Any
    _lock = threading.Lock()

    @property
    def _logger(self):
        return keyweaveHookLogger.getChild(f"{self.trigger}")

    def __init__(
        self,
        key: Key,
        collection: KeyBindingCollection,
        scheduler: Scheduler,
    ):
        self.trigger = key
        self._collection = collection
        self._scheduler = scheduler
        self.manufactured_handler = self._get_handler()

    def __enter__(self):
        self._logger.info("INSTALLING HOOK")
        self._internal_handler = hook_key(
            _get_keyboard_hook_id(self.trigger),
            self.manufactured_handler,
            suppress=True,
        )
        return self

    def __exit__(self):
        unhook(self._internal_handler)
        return self

    def _get_handler(self):
        def get_best_binding(event: KeyboardEvent):
            only_matching = [
                binding
                for binding in self._collection
                if binding.hotkey.trigger.key.is_numpad == event.is_keypad
                and _is_key_set_active(binding.hotkey.modifiers)
                and event.event_type == binding.hotkey.trigger.state
            ]

            by_specificity = sorted(
                only_matching,
                key=lambda binding: binding.hotkey.specificity,
                reverse=True,
            )
            return by_specificity[0] if by_specificity else None

        def handler(info: KeyboardEvent):
            binding = get_best_binding(info)
            event_state = _state_from_event(info)
            if not binding:
                self._logger.debug(
                    f"RECEIVED {event_state}; NO MATCHING BINDING"
                )

                return True
            self._logger.debug(f"RECEIVED {event_state}; MATCHED {binding}")

            def binding_invoker():
                binding(InputEvent(info.time))

            self._scheduler(binding_invoker)
            return False

        return handler


def _get_keyboard_hook_id(key: Key) -> str:
    match key.id:
        case "num:enter":
            return "enter"
        case "num:dot" | "num:.":
            return "."
        case "num:star" | "num:*" | "num:multiply":
            return "*"
        case "num:plus" | "num:+":
            return "+"
        case "num:minus" | "num:-":
            return "-"
        case "num:slash" | "num:/":
            return "/"
        case "mouse:1":
            return "left"
        case "mouse:2":
            return "right"
        case "mouse:3":
            return "middlemouse"
        case "mouse:4":
            return "x"
        case "mouse:5":
            return "x2"
        case _:
            return key.id.replace("num:", "num ")


def _get_windows_id_for_mouse_key(key: Key) -> int:
    if key.is_mouse:
        return int(key.id.replace("mouse:", ""))
    raise ValueError("Key is not a mouse key")


def _is_pressed(key: Key):
    if key.is_mouse:
        id = _get_windows_id_for_mouse_key(key)
        pr: Any = GetAsyncKeyState(id) & 0x8000
        return pr
    else:
        hook_id = _get_keyboard_hook_id(key)
        return is_pressed(hook_id)


def _is_state_active(state: KeyInputState):
    match state.state:
        case "down":
            return _is_pressed(state.key)
        case "up":
            return not _is_pressed(state.key)
        case _:
            raise ValueError(f"Unknown key state: {state.state}")


def _is_key_set_active(key_set: KeySet):
    return all(_is_state_active(key_state) for key_state in key_set)


def _state_from_event(event: KeyboardEvent) -> KeyInputState:
    return KeyInputState(
        key=Key(event.name or ""), state=event.event_type or "down"
    )
