# Ghoshell Container

IoC container for [GhostInShells](https://github.com/GhostInShells).

## IoC Container

`GhostInShells` follows the concept of `interface-oriented programming` to build the project.
Most modules are divided into `interface` and `implementation`.
Register and get implementations by IoC Container.

About IoC: [Inverse of Control](https://en.wikipedia.org/wiki/Inversion_of_control)

## Installation

`pip install ghoshell-container`

## Features

* `set` and `get`, and type check by `fetch`, `force_fetch`
* `alias`: set alias for contract
* `bind` with factory function, subclass, instance e.t.c
* dict interface
* factory class `Provider` registrar
* `boostrap` and `shutdown`
* container bloodline inheritance
* `make`: recursively dependencies injection for class
* `call`: recursively dependencies injection for function
* `get_container` and `set_container` by contextvars
* `depends`: function decorator
* `Inject` : class property injection
* `DeclaredContainer`: auto bindings by property

see them in [examples](tests/examples)