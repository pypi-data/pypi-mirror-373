from dataclasses import dataclass, field
import time
from typing import TYPE_CHECKING

from keyweave.commanding import CommandProducer
from keyweave.key_types import KeyInputState, KeySet, KeysInput

if TYPE_CHECKING:
    from keyweave.commanding import Command
    from keyweave.bindings import Binding


@dataclass(order=True, eq=True, frozen=True, unsafe_hash=True)
class HotkeyInfo:
    """
    Represents declarative information about a hotkey, including its trigger key, event type, and modifiers.
    """

    __match_args__ = ("trigger", "type", "modifiers", "passthrough")
    trigger: KeyInputState
    modifiers: KeySet = field(default=KeySet())
    passthrough: bool = field(default=False, compare=False)

    @property
    def specificity(self) -> int:
        """
        The specificity of a Hotkey. Used to decide which Hotkey to invoke when multiple are applicable.
        """
        return self.trigger.specificity + self.modifiers.specificity

    @property
    def trigger_label(self) -> str:
        """
        A label for the Hotkey's trigger key.
        """
        return str(self.trigger)

    def __str__(self) -> str:
        if not self.modifiers:
            return str(self.trigger)
        else:
            return f"{self.trigger_label} & {self.modifiers}"

    def __hotkey__(self):
        return Hotkey(self)


@dataclass(order=True, eq=True, frozen=True, unsafe_hash=True)
class Hotkey:
    """
    Represents a hotkey that can be transformed and bound to a command.
    """

    info: HotkeyInfo

    def __hotkey__(self):
        return Hotkey(self.info)

    def passthrough(self, enable: bool = True):
        """
        Whether the Hotkey should emit the Trigger key event.
        """
        return Hotkey(
            HotkeyInfo(
                trigger=self.info.trigger,
                modifiers=self.info.modifiers,
                passthrough=enable,
            )
        )

    @property
    def is_down(self) -> bool:
        """
        Whether the hotkey is triggered by a key press event.
        """
        return self.info.trigger.is_down

    def __call__(self, cmd: "Command | CommandProducer"):
        """
        Binds a command or command producer to the hotkey. Typically used as a decorator.
        """
        from ..bindings import BindingProducer

        return BindingProducer(cmd, self)

    @property
    def is_up(self) -> bool:
        """
        Whether the hotkey is triggered by a key release event.
        """
        return self.info.trigger.is_up

    def __and__(self, other: KeysInput):
        """
        Adds modifiers to a Hotkey.
        """
        return self.modifiers(other)

    def modifiers(self, modifiers: KeysInput):
        """
        Adds modifiers to a Hotkey.
        """
        return Hotkey(
            HotkeyInfo(
                trigger=self.info.trigger,
                modifiers=self.info.modifiers + modifiers,
                passthrough=self.info.passthrough,
            )
        )


type HotkeyInput = Hotkey | HotkeyInfo


@dataclass
class InputEvent:
    """
    Represents a low-level input event, such as a key press or release.
    """

    timestamp: float | None = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class HotkeyEvent:
    """
    Represents a high-level event triggered by a hotkey, with a matching Command.
    """

    binding: "Binding"
    event: InputEvent

    @property
    def hotkey(self) -> "HotkeyInfo":
        return self.binding.hotkey

    def command(self) -> "Command":
        return self.binding.command

    def __str__(self):
        dt = time.strftime("%H:%M:%S", time.localtime(self.event.timestamp))
        return f"<HotkeyEvent {dt} :: {self.binding}>"
