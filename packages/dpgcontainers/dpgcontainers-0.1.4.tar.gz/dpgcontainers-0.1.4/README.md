# DPGContainers

## Motivation

[DearPyGUI](https://github.com/hoffstadt/DearPyGui) provides a functional
interface for creating objects - windows, groups, et al.  This library provides
a collection of classes that can be used to create DPG objects as instances.

## Installation

```bash
pip install dpgcontainers
```

## Example usage

```python
from dpgcontainers.containers import Window, Group, Button

window = Window(width=100, height=200)(
    Group(horizontal=True)(
        Button(tag='button_1'),
        Button(tag='button_2'),
    ),
)


window.tagged_entities['button_1'].callback = lambda: print('clicked!')
window.render()
```

Children are captured by calling instances as functions.  The render cycle is
aware of objects that have already been rendered, so the following is fine:

```python
window = Window()

window(Button('button_1'))
window.render()

window(Button('button_2'))
window.render()
```
