# blissoda

*blissoda* provides utilities for online data analysis in [BLISS](https://gitlab.esrf.fr/bliss/bliss/).

*blissoda* is mostly used by the BLISS beamline macro's. In this case it needs to be installed
in the BLISS environment.

The actual data processing is done remotely using [ewoksjob](https://gitlab.esrf.fr/workflow/ewoks/ewoksjob).
*blissoda* does not contain any data processing code nor has any scientific libraries as dependencies.

## Install

In the Bliss environment you install with the `client` option

```bash
pip install blissoda[client]
```

Beamline specific clients are installed with the beamline name as option

```bash
pip install blissoda[id11]
```

Project specific clients are installed with the project name as option

```bash
pip install blissoda[streamline]
```

When workflows are not triggered from Bliss but from Redis scan information
in a separate process, you install with the `server` option in the process
environment

```bash
pip install blissoda[server]
```

## Test

```bash
pytest --pyargs blissoda.tests
```

## Documentation

https://blissoda.readthedocs.io/
