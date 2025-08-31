# Inputs for the fediverse-pasture

These inputs are basis for the data on Fediverse interoperability
available at [data.funfedi.dev](https://data.funfedi.dev) and then
[funfedi.dev](https://funfedi.dev). The goal in separating this out
is to be able to separate the varying pieces.

<div class="grid cards" markdown>
- [:material-download: Download Samples](./assets/samples.zip)
- [:material-download: Download Assets](./assets/fediverse_pasture_assets.zip)
</div>

The samples contain all activities and objects that
are generated from the inputs. These are useful for validating
a potential parser. The assets contain objects that are
required to parse certain inputs.

Furthermore, the format of these inputs is quite simple, and so
the hope is that more people will be able to [contribute](#contributing).

## Usage

Most inputs do not make assumptions about the actor being used
to serve the objects. This means that one can use them in general
contexts.

Some inputs such as [Variations of inReplyTo](inputs/in_reply_to.md)
however require assets. This means that one has to download
[the assets](./assets/fediverse_pasture_assets.zip) and serve
them at `http://pasture-one-actor/assets/` to be able to use the
inputs.

The assets are also available as a codeberg package, [here](https://codeberg.org/funfedidev/-/packages/generic/fediverse_pasture_assets/).

## Contributing

Adding new inputs is fairly straightforward. First take a look at
one of the existing files

```python title="fediverse_pasture_inputs/attributed_to.py"
--8<-- "fediverse_pasture_inputs/attributed_to.py"
```

and then at the [corresponding page](inputs/attributed_to.md). I hope one
can guess the relationship between `attributed_to_examples` variable
and the provided examples just by looking at it.

So if you want to modify or add something, one can just do it following
this pattern. Then one can check that everything works correctly by
running

```bash
uv sync --frozen
uv run python -mfediverse_pasture_inputs
uv run mkdocs serve
```

The updated objects can then by viewed at [http://localhost:8000/](http://localhost:8000/). By running `pytest` via

```bash
uv run pytest
```

one can furthermore ensure that the new inputs pass basic sanity checks.

## Installing the package

Available at [pypi](https://pypi.org/project/fediverse-pasture-inputs/) via

```bash
pip install fediverse-pasture-inputs
```

## Funding

This code was created as part of [Fediverse Test Framework](https://nlnet.nl/project/FediverseTestFramework/).

A project funded through the [NGI0 Core](https://nlnet.nl/core) Fund,
a fund established by [NLnet](https://nlnet.nl/) with financial support from
the European Commission's [Next Generation Internet](https://ngi.eu/) programme,
under the aegis of DG Communications Networks, Content and Technology
under grant agreement No 101092990.
