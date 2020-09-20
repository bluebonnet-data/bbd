import shutil
from pathlib import Path
from typing import Union

from shapefile import Reader, Writer

from .utils import resolve_shapefile_path


def trim_shapefile(
    in_path: Union[Path, str],
    join_on: str,
    include: list,
    out_path: Union[Path, str, None] = None,
) -> Union[Path, str]:
    """Trims a shapefile to only include shapes that match the given criteria.

    Shapes will be discarded unless their 'join_on' property is contained in the
    'include' list.
    """

    # Resolve the shapefile path (allows in_path to point to directory with same
    # name as nested shapefile)
    in_path = resolve_shapefile_path(in_path)

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
