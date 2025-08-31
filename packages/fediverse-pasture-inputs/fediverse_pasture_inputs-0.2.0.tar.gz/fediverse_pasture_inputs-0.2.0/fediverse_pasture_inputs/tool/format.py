import json

from fediverse_pasture_inputs.types import InputData

from .transformer import ExampleTransformer


def write_json(fp, data):
    fp.write("```json\n")
    fp.write(json.dumps(data, indent=2, sort_keys=True))
    fp.write("\n```\n\n")


async def page_from_inputs(fp, inputs: InputData):
    transformer = ExampleTransformer()

    fp.write(f"# {inputs.title}\n\n")
    fp.write(inputs.frontmatter)

    if inputs.support_table:
        fp.write("\n\n## Support Table Preview\n\n")
        fp.write("| Short | Object | Activity |\n")
        fp.write("| --- | --- | --- | \n")
        for idx, ex in enumerate(inputs.examples):
            activity = await transformer.create_activity(ex)
            transformed = inputs.support_result["activity"](activity)
            fp.write(
                f"| {transformed} | [Object](#object-{idx + 1}) | [Activity](#activity-{idx + 1}) |\n"
            )

    fp.write("\n\n## Objects \n\n")

    for idx, ex in enumerate(inputs.examples):
        fp.write(f"\n### Object {idx + 1}\n\n")
        write_json(fp, await transformer.create_object(ex))

    fp.write("\n\n## Activities \n\n")

    for idx, ex in enumerate(inputs.examples):
        fp.write(f"\n### Activity {idx + 1}\n\n")
        write_json(fp, await transformer.create_activity(ex))


def add_dict_to_zip(zipcontainer, data: dict, filename: str):
    formatted = json.dumps(data, indent=2).encode("utf-8")
    with zipcontainer.open(filename, "w") as f:
        f.write(formatted)


async def add_samples_to_zip(zipcontainer, inputs: InputData):
    transformer = ExampleTransformer()

    base = inputs.filename.removesuffix(".md")

    for idx, ex in enumerate(inputs.examples):
        add_dict_to_zip(
            zipcontainer,
            await transformer.create_activity(ex),
            f"activity/{base}_{idx}.json",
        )
        add_dict_to_zip(
            zipcontainer,
            await transformer.create_object(ex),
            f"object/{base}_{idx}.json",
        )
