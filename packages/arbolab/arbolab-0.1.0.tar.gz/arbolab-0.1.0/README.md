# arbolab

Core utilities for ArboLab providing configuration, logging, database management, plotting helpers and a small metadata layer.

## Installation
```bash
pip install -e .
```

### Extras
Optional dependencies can be installed via extras:

```bash
pip install -e ".[plot]"       # seaborn, plotly
pip install -e ".[ml]"         # scipy, scikit-learn
pip install -e ".[latex]"      # jinja2, pylatexenc
pip install -e ".[linescale]"  # arbolab-linescale, pyserial
pip install -e ".[treeqinetic]" # arbolab-treeqinetic, pyserial
pip install -e ".[treecablecalc]" # arbolab-treecablecalc, pyserial
pip install -e ".[treemotion]" # arbolab-treemotion, pyserial
pip install -e ".[wind]"       # arbolab-wind, requests, beautifulsoup4, pandas, numpy
pip install -e ".[all]"        # install every optional dependency
```

The wind extras can also be installed from PyPI:

```bash
pip install arbolab[wind]
```

## Usage
The package exposes a small user-facing API centered around the :class:`Lab` container. Import it from the top-level package and either create a new laboratory configuration with ``setup`` or load an existing one with ``load``:

```python
from arbolab import Lab

# create a new lab and persist its config/database
lab = Lab.setup(load_plugins=True)

# later, reload the same lab (defaults to a file named after the working directory)
lab = Lab.load("lab.duckdb")

# attached sensor adapters are available via lab.sensors
print(lab.sensors.keys())
```

Adapter plugins are discovered via the ``arbolab.adapters`` entry point group and loaded automatically when ``load_plugins`` is ``True``.

### Custom sensor packages
Third-party sensors integrate by implementing the :class:`~arbolab.adapter.Adapter` protocol and exposing an entry point:

```toml
[project.entry-points."arbolab.adapters"]
"mysensor" = "my_package:MyAdapter"
```

Installing such a package makes it discoverable by :meth:`Lab.setup` when ``load_plugins`` is ``True``.

Domain entities such as :class:`Project` or :class:`Series` live in ``arbolab.classes`` and operate on the active ``Lab`` instance. Measurements captured from sensors are represented by :class:`Measurement` objects. Each measurement stores additional metadata fields like ``unit`` (physical unit of the recorded values), ``sample_rate`` (in Hz) and ``sensor_type``. These fields provide defaults and are validated via Pydantic to ensure consistency. The database representation of a laboratory is called :class:`LabEntry` to avoid confusion with the user-facing container.

Entities deriving from :class:`BaseEntity` can store identifiers from external systems in a JSON mapping. Use :meth:`set_external_id` to register a value such as ``{"sensor_serial": "1234"}`` and :meth:`get_external_id` to retrieve it later.

## Configuration
Configuration values can be supplied via environment variables or a YAML file. The ``Config`` class and its nested sections are implemented using [Pydantic](https://docs.pydantic.dev/) models which provide validation and type coercion. The configuration layout looks as follows:

```yaml
# config.yaml
working_dir: /tmp/lab           # defaults to the current directory
db_url: duckdb:///lab.duckdb    # optional database URL (defaults to duckdb:///<working_dir_name>.duckdb)
logging:
  level: INFO                   # log level, use "NONE" to disable logging
  use_colors: true
  save_to_file: false
  tune_matplotlib: false
```

Load the configuration with:

```python
from arbolab import Config

cfg = Config.from_file("config.yaml")
```

The same fields can be provided via environment variables named ``ARBOLAB_WORKING_DIR``, ``ARBOLAB_DB_URL``, ``ARBOLAB_LOGGING__LEVEL``, ``ARBOLAB_LOGGING__USE_COLORS``, ``ARBOLAB_LOGGING__SAVE_TO_FILE`` and ``ARBOLAB_LOGGING__TUNE_MATPLOTLIB``.

### Database table prefix
To avoid name clashes between sensor packages, database tables can be prefixed via the ``ARBOLAB_DB__TABLE_PREFIX`` environment variable. For example, setting ``ARBOLAB_DB__TABLE_PREFIX=ls_`` will create tables like ``ls_measurements`` and ``ls_sensors``. All foreign keys and sequences use the same prefix.

### Updating configuration
Use ``Lab.update_config`` to adjust settings at runtime. It applies changes via Pydantic's ``model_copy`` and dispatches reconfiguration hooks based on the fields that changed so logging, database connections, plotting defaults and persistence refresh independently.

### Path parameters
Functions that accept file system paths support both strings and [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path) instances. This applies to helpers such as :meth:`Config.from_file` and :meth:`Lab.load` as well as to :class:`Config` itself:

```python
from pathlib import Path
from arbolab import Config

Config(working_dir="/tmp/lab")
Config(working_dir=Path("/tmp/lab"))
```

## Development
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```
