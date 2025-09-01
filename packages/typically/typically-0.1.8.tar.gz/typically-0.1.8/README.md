# typically

## Overview

When adding comprehensive type annotations to python projects, you often have to choose where to import identical types.

For instance, you might want to use a `TypedDict`, so you would naturally import:

```python
from typing import TypedDict
```

The issue is that now if you use your typed dictionary in a pydantic model, you will get an exception. This is because you actually "should have" imported:

```python
from typing_extensions import TypedDict
```

There's also `types`, `collections`, `collections.abc`, `annotated_types`, etc.

This package is intended to create a single source of core types for python projects with very few required dependencies, and maybe at most a few optional ones (eg: `pydantic`).

Suggested pattern:

```python
import typically as t
```

## Installation

With pip:

```sh
pip install typically
```

Or with `uv`:

```sh
uv add typically
```

## Notes

- Type annotations really shouldn't impose any overhead. Of course, that's possible to avoid, but I'm still aiming to keep the extra import time less than 100 ms. The goal is (maybe) to pack as much commonly used stuff into a single import without incurring overhead.
- All members of `builtins` are explicitly imported in the `__init__` file, as sometimes one might like to override them, but also be able to access original builtin type. 
- Various type variables are included. These are always named `T_...` where the ellipses is the type the type variable is bound to, if any.


## TODO

- [ ] Implement paramspec objects for functools caching.
- [ ] Add pydantic as submodule, as it imposes overhead and should be optional.
- [ ] Add improved decimal type.