# keyweave

Keyweave is a Python package for creating and managing global keyboard hotkeys.

- Designed to be easy to observe and debug.
- Hotkeys are grouped into a Layout, which can be activated as a context manager.
- Handlers are attached to Commands, which have labels and descriptions.
- Hotkeys are typically defined using decorators on functions or methods.

## Overview

Key-related objects:

- `Key`: Represents a single mouse, keyboard, or controller key.
- `KeyState`: Represents a `Key` together with a state: `up` or `down`.
- `Hotkey`: A trigger `KeyState` and an unordered set of `KeyState` modifiers.

Command-related objects:

- `CommandMeta`: Just the metadata of a command. Has a label and a description.
- `Command`: A metadata object together with a handler (a function).

These are combined using:

- `Binding`: A Hotkey and the Command it’s bound to.
- `Layout`: A collection of `Binding` objects that listens to input events and picks which `Binding` to activate for each event, if any.
- `LayoutClass`: An object-oriented way of defining a `Layout`.

### Key

An object that describes a mouse or keyboard key. You can access most keys using the `key` import:

```python
import key from keyweave
a = key.a
```

Other keys can be constructed using the `Key` class:

```ts
import Key from keyweave
a = Key("a")
```

### KeyState

This describes a `Key` and whether it’s up or down. At any given time, a `KeyState` is either True or False.

KeyStates are used to filter input events as well as global input state. You can construct a `KeyState` using the `Key.down` or `Key.up` properties:

```python
import key from keyweave
a_down = key.a.down
a_up = key.a.up
```

In some cases, you can pass a `Key` instead of a `KeyState`. In that case, `down` is assumed by default.

You can create an Up `KeyState` using the `~` operator on the key:

```python
import key from keyweave
a_up = ~key.a
```

### Hotkey

A `Hotkey` is a filter on input events consisting of two parts:

- A **Trigger** `KeyState` that’s used to hook the input event.
- A set of **Modifiers**: `KeyStates` which need to be True for the Hotkey to fire.

If a `Hotkey` is triggered by an input event, the event is normally swallowed. However, none of the modifiers are swallowed. If they have side-effects, those must be handled separately.

Note that modifiers don’t just refer to classic modifier keys like `Ctrl`. Any key can be a modifier, and the package doesn’t treat these keys differently from others.

You can construct a Hotkey using the `&` operator between:

1. A `Key` or `KeyState`.
2. An iterable of `Key` or `KeyState` objects which are used as modifiers.

```python
import key from keyweave

key.a.down & [key.b]
key.a & [key.b, key.c.up, key.shift.down]
```

In most cases, you can pass a `Key` or `KeyState` directly instead of a `Hotkey`. In that case, the key can be assumed to be `down` and the modifier list is assumed to be empty.

If you want to avoid swallowing the input event, you can modify the Hotkey using its `passthrough` method:

```python
import key from keyweave
key.a.down.hotkey().passthrough
```

### Command

A Command consists of:

- `CommandMeta`: A label, description, and an emoji. Metadata.
- A handler, which is a function that handles the command.

### Layout

A Layout is an object containing lots of `Hotkey` objects bound to `Command` objects.

Layouts are what actually listens to input events. When an input event is received, each Binding’s Hotkey is checked to see if it’s applicable.

If multiple `Binding` objects turn out to be applicable to one input event, **only one of them will be invoked.** The binding that’s invoked is determined by the highest _specificity_ - the total number of keys the Hotkey references.

If the specificity is the same, then the last defined hotkey is used.

So for example, let’s say we register the hotkeys `Ctrl + Shift + A` and `Ctrl + A` under the same `Layout`. Then if `Ctrl + Shift + A` is pressed, the event matches both hotkeys. But one has a specificity of 2 while the other one has 3.

Thus only the `Ctrl + Shift + A` binding is actually invoked.

However, if you have separate Layouts with these bindings, then multiple bindings can be invoked.

### Negative modifiers

A trigger for a hotkey can be either a key down or a key up event.

Modifiers can also contain key up or key down **states**. A key up modifier is a negative modifier – it means the key should not be held down.

Normally, if you define a hotkey for `Ctrl + A`, it would be invoked even if the user presses `Alt + Ctrl + A`. If you don’t want this behavior, you can add the negative/up modifier `Ctrl + A + ~Alt`.

A negative modifier also increase specificity, which can sometimes be desirable.

## Usage

Using this package means **defining Layout objects**. This can be done

## Object-oriented

The main objects used Keyweave are:

- Command: This is metadata involving a

Bindings are partially implemented using [keyboard](https://pypi.org/project/keyboard/) but due to technical issues involving mouse input and key state, it sometimes has to use the win32 API.

- Capturing mouse input
- Getting key states
