# Crystal Projector

![The map of the world, gleaned from the world file.](map.png)

This is a library for manipulating data structures in the video game [Crystal Project](https://store.steampowered.com/app/1637730/Crystal_Project/). This currently can read:

- World files
- Database files
- Texture packs
- Save files
- Mod files

This will hopefully soon be able to modify and write out the above, as well as read additional things, like logfiles.

# Using Crystal Projector as a Set of Schemas

## JSON Files

The [JSON Schema](https://json-schema.org/) formats for each Crystal Project format can be found in [schema/json](schema/json).

## Binary files

The [Kaitai Struct](https://kaitai.io/) formats for Crystal Project's `.dat` and `.sav` files can be found in [schema/ksy](schema/ksy).

# Using Crystal Projector as a Python Library

You will need [Python](https://www.python.org/), version 3.8 or later.

To install Crystal Projector:

```bash
python3 -m pip install --upgrade --pre git+https://github.com/kaitai-io/kaitai_struct_python_runtime.git
python3 -m pip install crystal-projector
```

Then you can invoke it with:

```bash
crystal-projector --help
```

And use it in Python scripts like so:

```py
import crystal_projector

image = crystal_projector.world.visualize_world_map(input("enter your Crystal Project 'Content' folder:"), "field")
image.save("map.png")
```

# Developing Crystal Projector

## Dependencies

### Kaitai Struct

You need [Kaitai Struct](https://kaitai.io/) and its Python bindings, latest nightly.

KSC has some issues with Python:

* No type annotations.
* It imports sub-KSY file dependencies incorrectly; `import X` should be `from . import X`.
* It does not stop keywords from being used as names.

The latter two are fixed by us.

### Quicktype

We use [Quicktype](https://quicktype.io/); you'll need its NPM package. However, Quicktype *also* has issues:

* No support for integer enums; if you omit `type: integer` from such enums, Quicktype crashes.
* Does not support multi-file `$ref`s in a smart manner.

### Python packages

* `kaitaistruct`: Do ***NOT*** pull this from PyPI. Do this instead:
  ```bash
  python3 -m pip install --upgrade --pre git+https://github.com/kaitai-io/kaitai_struct_python_runtime.git
  ```
* `Pillow`: For `PIL`.

For developing and testing:

* `pre-commit`.
* `pyyaml`: For `yaml`.
* `jsonschema`.

## Installing the Project

```bash
python3 -m pip install -e .[dev, test]
pre-commit install
```

## Building the Project

```bash
python3 build_schemas.py
```

## Distributing the Project

```bash
python3 -m build
```
