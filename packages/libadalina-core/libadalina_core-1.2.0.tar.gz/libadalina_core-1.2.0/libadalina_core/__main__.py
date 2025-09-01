from collections import namedtuple

import click
from libadalina_core.readers import csv_to_dataframe, geopackage_to_dataframe
from libadalina_core.readers.shapefile import shapefile_to_dataframe
from libadalina_core.writers import dataframe_to_geopackage
from libadalina_core.sedona_utils import to_spark_dataframe
from libadalina_core.sedona_utils import EPSGFormats
from libadalina_core.spatial_operators.multi_table_operators import make_bounding_box_intersection
import pathlib

from libadalina_core.writers.writers import dataframe_to_csv

CONTEXT_SETTINGS = dict(
    obj={
        'datasets':[]
    }
)

DatasetInput = namedtuple("DatasetInput", ["path", "dataset"])

@click.group(context_settings=CONTEXT_SETTINGS, chain=True)
@click.pass_context
def cli(ctx):
    pass

@cli.command(help='Read a CSV file into a Spark DataFrame')
@click.option('--geometry', type=str, default='geometry', help='Name of geometry column in the CSV file')
@click.option('--separator', type=str, default=None, help='CSV separator character')
@click.option('--epsg', type=click.Choice(EPSGFormats, case_sensitive=False), default=EPSGFormats.EPSG4326, help='EPSG code for the coordinate reference system')
@click.argument('dataset', type=click.Path(exists=True, dir_okay=False, readable=True, path_type=pathlib.Path))
@click.pass_context
def read_csv(ctx, dataset: pathlib.Path, geometry: str, separator: str, epsg: EPSGFormats):
    df = csv_to_dataframe(str(dataset), separator)
    df = df.rename(columns={geometry: 'geometry'})
    df = to_spark_dataframe(df, epsg_format=epsg)
    ctx.obj['datasets'].append(DatasetInput(dataset, df))

@cli.command(help='Read a GeoPackage file into a Spark DataFrame')
@click.argument('dataset', type=click.Path(exists=True, dir_okay=False, readable=True, path_type=pathlib.Path))
@click.option('--layer',  type=str, default=None, help='Layer name in the GeoPackage file')
@click.pass_context
def read_geopackage(ctx, dataset: pathlib.Path, layer: str | None):
    df = geopackage_to_dataframe(str(dataset), layer)
    df = to_spark_dataframe(df)
    ctx.obj['datasets'].append(DatasetInput(dataset, df))

@cli.command(help='Read a Shapefile into a Spark DataFrame')
@click.argument('dataset', type=click.Path(exists=True, dir_okay=False, readable=True, path_type=pathlib.Path))
@click.pass_context
def read_shapefile(ctx, dataset: pathlib.Path):
    df = shapefile_to_dataframe(str(dataset))
    df = to_spark_dataframe(df)
    ctx.obj['datasets'].append(DatasetInput(dataset, df))

@cli.command(help='Intersect two datasets based on their bounding boxes and save the results as GeoPackages')
@click.option('--destination', type=click.Path(exists=True, file_okay=False, writable=True, path_type=pathlib.Path),
              help='Path to save the intersected dataset to', default='.')
@click.pass_context
def bounding_box(ctx, destination: pathlib.Path):
    datasets = ctx.obj['datasets']
    if len(datasets) != 2:
        raise click.UsageError("Exactly two datasets are required for intersection.")
    df1, df2 = datasets[0].dataset, datasets[1].dataset
    df1, df2 = make_bounding_box_intersection(df1, df2)

    df1_name: str
    df2_name: str
    df1_name, df2_name = datasets[0].path.stem, datasets[1].path.stem

    dataframe_to_geopackage(df1, str(destination / f"{df1_name}_intersected.gpkg"))
    dataframe_to_geopackage(df2, str(destination / f"{df2_name}_intersected.gpkg"))

@cli.command(help='Save datasets to CSV files')
@click.option('--separator', type=str, default=',', help='CSV separator character')
@click.pass_context
def save_csv(ctx, separator: str):
    for df_input in ctx.obj['datasets']:
        path, df = df_input.path, df_input.dataset
        dataframe_to_csv(df, path.with_suffix('.csv'), separator)

if __name__ == "__main__":
    cli()