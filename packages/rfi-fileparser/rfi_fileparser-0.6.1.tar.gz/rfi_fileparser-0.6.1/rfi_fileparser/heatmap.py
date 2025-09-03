import os
from rfi_fileparser import util

import json
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from h3 import h3_to_geo_boundary
from shapely.geometry import Polygon

def generate_heatmap(filepath, title):
    if os.path.isfile(filepath):
        # Load the heatmap.json file
        with open(filepath) as f:
            data = json.load(f)
        # Convert to DataFrame
        df = pd.DataFrame(data)
        # Filter out rows with totalAircraftCount = 0 to avoid divide-by-zero
        df = df[df['totalAircraftCount'] > 0].copy()
        # Compute ratio: lowQualityCount / totalAircraftCount
        df['low_quality_ratio'] = df['lowQualityCount'] / df['totalAircraftCount']

        # Convert H3 hexagons to polygons
        def h3_to_polygon(h3_index):
            boundary = h3_to_geo_boundary(h3_index, geo_json=True)
            return Polygon(boundary)

        # Create geometry column
        df['geometry'] = df['h3Index'].apply(h3_to_polygon)
        # Convert to GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
        # Create full-screen figure and axis
        fig, ax = plt.subplots(figsize=(20, 12))
        gdf.plot(
            column='low_quality_ratio',
            cmap='viridis',
            edgecolor='none',
            ax=ax,
            legend=True,
            legend_kwds={
                'shrink': 0.4,  # Shrink the colorbar to 40% height
                'label': 'Low NIC Ratio',
                'orientation': 'vertical',
                'pad': 0.02
            }
        )
        # Customize title and layout
        ax.set_title(title, fontsize=16)
        ax.set_axis_off()  # Hide axes for cleaner map
        plt.tight_layout()
        plt.show()

    else:
        # print("Looking for:", os.path.abspath(fullpath))
        print(f"No such file or directory {filepath}.")


def plot_daily_heatmap(filepath, date):
    if util.is_valid_date(date):
        subpath = date.split("/")
        fullpath = os.path.join(filepath, "jamming", *subpath, 'heatmap.json')
        generate_heatmap(fullpath, 'Daily Low NIC Flight Percentage Heatmap')


def plot_hourly_heatmap(filepath, date):
    if util.is_valid_date(date):
        subpath = date.split("/")
        allhours = [f"{hour:02}00" for hour in range(24)]
        fullpath = [os.path.join(filepath, "jamming", *subpath, hourpath, 'heatmap.json') for hourpath in allhours]
        for file in fullpath:
            generate_heatmap(file, 'Hourly Low NIC Flight Percentage Heatmap')


if __name__ == '__main__':
    plot_daily_heatmap("..\downloaded_json_files", "2025/03/24")
    # plot_hourly_heatmap("downloaded_json_files", "2025/03/05")