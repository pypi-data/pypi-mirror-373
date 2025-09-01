import click

from ..client import ObjectClass, read_object_classes


@click.group("object-class")
@click.pass_context
def object_class_group(ctx):
    pass


def _read_object_classes(client, name: str):
    gen = read_object_classes(client, name=name)
    for obj_cls in gen:
        yield obj_cls.dict()


@object_class_group.command("read")
@click.option(
    "-i",
    "--ids",
    type=str,
    required=False,
    multiple=True,
)
@click.option(
    "-n",
    "--names",
    type=str,
    required=False,
    multiple=True,
)
@click.pass_context
def read(ctx, names, ids):
    client = ctx.obj["client"]

    result = []
    if len(ids) > 0:
        for id in ids:
            result.append(
                client.objectClass(
                    return_type=ObjectClass,
                    id=id,
                ).dict()
            )
    elif len(names) > 0:
        for name in names:
            result.extend([o for o in _read_object_classes(client, name)])

    print(result)
