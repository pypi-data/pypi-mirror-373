# Memory-FS

Memory-FS is a fully tested, type-safe file system abstraction implemented entirely in memory.  It originated from the `OSBot_Cloud_FS` prototype and has evolved through multiple architectural iterations documented in [docs/tech_debriefs](docs/tech_debriefs).  The library exposes a small, composable API for creating, loading and editing file objects while remaining agnostic of the underlying storage provider.

## Key Features

- **In-Memory Storage** – extremely fast read/write operations via an in‑memory provider.
- **Type Safety** – all APIs use `osbot_utils` `Type_Safe` models ensuring runtime validation.
- **Two-File Pattern** – metadata (`.config` / `.metadata`) and content are stored separately.
- **Pluggable Path Strategies** – configurable path handlers (latest, temporal, versioned, etc.).
- **Extensible File Types** – JSON, Markdown, binary and custom formats through schema classes.
- **100% Code Coverage** – every line of production code is tested as of version `v0.11.1`.

## Architecture Overview

The current design (introduced in the [June 18 2025 debrief](docs/tech_debriefs/on-18-jun-2025.md)) is composed of two layers:

1. **File_FS Layer** – high level file operations
   - `File_FS` object plus `File_FS__*` action classes
   - `Target_FS` factory for creating file objects from existing paths
2. **Storage_FS Layer** – low level storage providers
   - `Storage_FS` interface and in‑memory implementation `Storage_FS__Memory`
   - Provider pattern enabling future backends (local disk, SQLite, zip, S3)

This separation yields a small surface area for extending or replacing storage while keeping file logic consistent.  The project’s [tech debrief README](docs/tech_debriefs/README.md) describes this architecture as:

```
1. **File_FS Layer**: High-level file operations
2. **Storage_FS Layer**: Low-level storage operations
   - Provider pattern for pluggable storage backends
```

### File Naming

Files are organised using a predictable naming scheme:

1. **Content File** – `{file_id}.{extension}`
2. **Config File** – `{file_id}.{extension}.config`
3. **Metadata File** – `{file_id}.{extension}.metadata`


### Coverage Guarantee

Memory-FS maintains comprehensive tests.  As recorded in the debriefs:

```
As of June 18, 2025 (v0.11.0), Memory-FS has achieved **100% code coverage**:
- Every line of production code is tested
- All edge cases are covered
- No dead or unused code remains
- Comprehensive test suite with 200+ test methods
```

## Installation

```bash
pip install memory-fs
```

or install from source:

```bash
pip install -e .
```

## Quick Example

Below is a minimal example using the high‑level API.  It stores JSON content via the in‑memory provider:

```python
from memory_fs.file_fs.File_FS                              import File_FS
from memory_fs.file_types.Memory_FS__File__Type__Json       import Memory_FS__File__Type__Json
from memory_fs.schemas.Schema__Memory_FS__File__Config      import Schema__Memory_FS__File__Config
from memory_fs.path_handlers.Path__Handler__Latest          import Path__Handler__Latest
from memory_fs.storage.Memory_FS__Storage                   import Memory_FS__Storage
from memory_fs.storage_fs.providers.Storage_FS__Memory      import Storage_FS__Memory

# set up in-memory storage
storage      = Memory_FS__Storage(storage_fs=Storage_FS__Memory())

# configuration describing where/how the file should be stored
config = Schema__Memory_FS__File__Config(
    path_handlers  = [Path__Handler__Latest()],
    default_handler=Path__Handler__Latest,
    file_type      = Memory_FS__File__Type__Json(),
)

# create a file object and save some data
file = File_FS(file_config=config, storage=storage)
file.create()
file.create__content(b'{"hello": "world"}')

# reload using the factory
from memory_fs.target_fs.Target_FS__Create import Target_FS__Create
loaded_target = Target_FS__Create(storage=storage).from_path__config(file.file_fs__paths().paths__config()[0])
print(loaded_target.file_fs().content())  # -> b'{"hello": "world"}'
```

## Documentation

Extensive documentation is kept under the `docs` folder.  The [tech_debriefs](docs/tech_debriefs) directory captures the project evolution, while [architecture](docs/architecture/technical_architecture_debrief.md) provides a detailed design overview.  Developers should also review [docs/dev](docs/dev/README.md) for coding conventions, bug lists and TODO items.

## Project History

The debrief timeline in `docs/tech_debriefs/README.md` summarises all key milestones from the initial design on May 26 2025 through the storage abstraction layer, Target_FS introduction and the 100% coverage refactor.  The current release is `v0.11.1`.

Memory-FS serves both as a lightweight in‑memory storage engine and as a reference implementation for future backends such as S3 or SQLite.  Its small, type‑safe API and complete test coverage make it an ideal starting point for new contributors or for embedding a fast, pluggable file system into your own projects.
