# Language Independent Interface Types For INSIGHT

The proto files can be consumed as GIT submodules or copied and built directly in the consumer project.

The compiled files are published to central repositories (Maven, ...).

## Generate gRPC Client Libraries

To generate the raw gRPC client libraries, use `make gen-${LANGUAGE}`. Currently supported languages are:

* python
* golang

# Using local build

When testing you can build the python version locally using `make build-python`. This will build a version of 0.0.1-dev,
this can then be installed using `pip install`.

```bash
make build-python
pip install build/python

## or using the egg
pip install build/python/dist/insight_proto-0.0.1.dev0-py3-none-any.whl
```
Due to this being a dev build sometimes pip gets confused so you might need to run uninstall.
```bash
pip uninstall insight-proto
```

# Releasing

To release this we use GitHub Actions when a new release is tagged via GitHub.
