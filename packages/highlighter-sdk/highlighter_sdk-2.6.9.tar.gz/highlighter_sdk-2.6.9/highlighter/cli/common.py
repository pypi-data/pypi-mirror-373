from pathlib import Path

import click


def _to_pathlib_make_dir(ctx, param, value):
    if value is None:
        return value

    value = Path(value)
    value.mkdir(parents=True, exist_ok=True)
    return value


def _to_pathlib(ctx, param, value):
    if value is None:
        return value

    if isinstance(value, tuple):
        value = [Path(v) for v in value]
        return value

    if isinstance(value, str):
        value = Path(value)
        return value

    raise ValueError(f"Invalid path input: {v}")


class CommonOptions:
    annotations_dir = click.option(
        "-a",
        "--annotations-dir",
        type=click.Path(file_okay=False),
        required=True,
        help=("Directory to save the annotation files to. If it does not exist " "one will be created"),
        callback=_to_pathlib_make_dir,
    )

    data_file_dir = click.option(
        "-o",
        "--data-file-dir",
        type=click.Path(file_okay=False),
        required=False,
        default=None,
        help=("Directory to save the data_files to. Images with the same " "filename will be skipped"),
        callback=_to_pathlib_make_dir,
    )
