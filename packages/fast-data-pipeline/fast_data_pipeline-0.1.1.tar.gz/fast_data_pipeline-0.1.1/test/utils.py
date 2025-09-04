from pathlib import Path

from h5rdmtoolbox.layout import Layout
from h5rdmtoolbox.database import hdfdb
import polars as pl
import yaml

def create_h5_layout_from_yaml(filepath: Path, enforce_units: bool = True):

    layout = Layout()

    with open(filepath, "r") as f:
        layout_spec = yaml.safe_load(f)

    for mapping in layout_spec["mapping"]:
        if isinstance(mapping["target_name"], str):
            mapping["target_name"] = [mapping["target_name"]]
        if mapping.get("description") is None:
            mapping["description"] = "No description available"

    layout_spec_df = pl.DataFrame(layout_spec["mapping"])

    print(layout_spec_df.head())

    for row in layout_spec_df.iter_rows(named=True):
        layout.add(
            hdfdb.FileDB.find,
            flt={"$name": row["target_name"]},
            objfilter="dataset",
            n=1,
        )
    if enforce_units is True:
        layout.add(
            hdfdb.FileDB.find,
            flt={'units': {'$exists': True}},
            recursive=True,
            objfilter='dataset',
            description='Units must exist',
            n={'$gt': 0}
        )

    return layout
