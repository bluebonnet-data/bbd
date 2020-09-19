"""
TODO this kind of belongs here because it will be used with get_shapefile,
but it should be moved to it's own utility module if any other code outside
of the census module wants to use it.
"""

import shutil
from pathlib import Path
from typing import Union

from shapefile import Reader, Writer


def trim_shapefile(
    in_path: Union[Path, str],
    join_on: str,
    include: list,
    out_path: Union[Path, str, None] = None,
) -> Path:
    """Trims a shapefile to only include shapes that match the given criteria.

    Shapes will be discarded unless their 'join_on' property is contained in the
    'include' list.
    """

    # Construct new name if it was not provided
    if out_path is None:
        out_path = in_path.with_name(f"{in_path.name}_trimmed{in_path.suffix}")

    with Reader(str(in_path)) as r, Writer(str(out_path)) as w:

        w.fields = r.fields[1:]  # don't copy deletion field

        if join_on not in [f[0] for f in w.fields]:
            raise ValueError(f"'join_on'={join_on} not in shapefile fields: {w.fields}")

        # Copy features if they match the criteria
        for feature in r.iterShapeRecords():
            if feature.record[join_on] in include:
                w.record(*feature.record)
                w.shape(feature.shape)

    # PyShp doesn't manage .prj file, must copy manually.
    in_prj = in_path.with_suffix(".prj")
    if in_prj.exists():
        out_prj = out_path.with_suffix(".prj")
        shutil.copy(in_prj, out_prj)

    return out_path
