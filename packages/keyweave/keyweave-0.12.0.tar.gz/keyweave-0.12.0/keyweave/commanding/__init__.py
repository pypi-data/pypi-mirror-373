from dataclasses import dataclass, field
import inspect
from typing import Any, Literal, Protocol, TYPE_CHECKING


if TYPE_CHECKING:
    from keyweave.hotkey import Hotkey, HotkeyEvent


@dataclass()
class CommandMeta:
    """
    Metadata about a command. Used for debugging and user feedback.
    """

    label: str | None
    description: str | None = field(default=None, kw_only=True)
    emoji: str | None = field(default=None, kw_only=True)

    def __str__(self):
        return f'Command("{self.label}")'


@dataclass
class Command:
    """
    Represents a command that can be triggered by a hotkey, with an attached handler.
    """

    info: CommandMeta
    handler: "FuncHotkeyHandler"

    def __str__(self):
        return str(self.info)

    def __get__(
        self, instance: object | None = None, owner: type | None = None
    ) -> "Command":
        return self

    def bind(self, hotkey: "Hotkey"):
        from ..bindings import Binding

        return Binding(hotkey.info, self)


class FuncHotkeyHandler(Protocol):
    """
    Represents a non-instance function that handles a hotkey event.
    """

    def __call__(self, event: "HotkeyEvent", /) -> Any: ...


class MethodHotkeyHandler(Protocol):
    """
    Represents an instance method that handles a hotkey event.
    """

    def __call__(self, instance: Any, event: "HotkeyEvent", /) -> Any: ...


type HotkeyHandler = FuncHotkeyHandler | MethodHotkeyHandler


class CommandProducer:
    """
    Represents an object that produces a command with an attached handler. When applied to a method,
    requires additional context to function properly.
    """

    def __str__(self):
        return str(self.cmd)

    def __init__(self, func: HotkeyHandler, cmd: CommandMeta):
        self.func = func
        self.cmd = cmd

    def _make(self, instance: object | None = None):
        def wrapper(event: "HotkeyEvent", /) -> Any:
            arg_count = len(inspect.signature(self.func).parameters)
            match arg_count:
                case 1:
                    return self.func(event)  # type: ignore
                case 2:
                    return self.func.__get__(instance)(event)  # type: ignore
                case _:
                    raise ValueError("Invalid number of arguments")

        return Command(
            info=self.cmd,
            handler=wrapper,
        )

    def __get__(
        self, instance: object | None, owner: type | None = None
    ) -> Command:
        """
        May bind an instance to a command handler so it can be invoked as an instance method.
        """
        return self._make(instance)


type CommandOrProducer = Command | CommandProducer


@dataclass
class command(CommandMeta):
    """
    Use this decorator on a method or function to turn it into a Command.
    """

    def __call__(self, handler: HotkeyHandler) -> "CommandProducer":
        return CommandProducer(handler, cmd=self)
