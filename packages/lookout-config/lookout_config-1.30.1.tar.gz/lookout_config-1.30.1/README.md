# Lookout Config

Lookout Config is used to load config stored inside the `~/.config/greenroom` folder.

## Install

* `pip install -e ./packages/lookout_config`
* or...
* `pip install lookout_config` (Public on [PyPi](https://pypi.org/project/lookout-config/))

## Usage

### Reading config

```python
from lookout_config import get_config_io

config_io = get_config_io()
config = config.read()
```

### Generating schemas

After changing the dataclasses, you can generate the schemas with:

```bash
python3 -m lookout_config.generate_schemas
```
