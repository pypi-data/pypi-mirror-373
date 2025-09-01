from dataclasses import dataclass
from typing import Protocol

from keyweave.bindings import Binding
from keyweave.commanding import Command, FuncHotkeyHandler
from keyweave.hotkey import HotkeyEvent


@dataclass(init=False)
class HotkeyInterceptionEvent(HotkeyEvent):
    """
    Represents an intercepted `HotkeyEvent`. Used in the layout hotkey interception API.
    """

    def __str__(self):
        return super().__str__() + " (intercepted)"

    _handled: bool = False

    def __init__(self, event: HotkeyEvent, handler: FuncHotkeyHandler):
        HotkeyEvent.__init__(self, event.binding, event.event)
        self._handler = handler

    def next(self):
        self._handled = True
        result = self._handler(self)
        return result

    def end(self):
        self._handled = True

    @property
    def handled(self):
        return self._handled


class HotkeyInterceptor(Protocol):
    """
    A function that can intercept a hotkey event.
    """

    def __call__(self, action: HotkeyInterceptionEvent): ...


def intercept_binding(target: Binding, *interceptors: HotkeyInterceptor):
    handler = target.handler
    for interceptor in interceptors:
        handler = _wrap_interceptor(interceptor, handler)
    return Binding(
        target.hotkey,
        Command(
            info=target.command.info,
            handler=handler,
        ),
    )


def _wrap_interceptor(
    interceptor: HotkeyInterceptor, handler: FuncHotkeyHandler
) -> FuncHotkeyHandler:
    def _handler(e: HotkeyEvent):
        interception = HotkeyInterceptionEvent(e, handler)
        interceptor(interception)
        if not interception.handled:
            raise ValueError(f"Interceptor {interceptor} did not handle {e}")

    return _handler
