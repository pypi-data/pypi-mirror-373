import os
from rfi_fileparser import util

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import geopandas as gpd
import contextily as ctx

def generate_timeline(filepath, title):
    if os.path.isfile(filepath):
        # Load the heatmap.json file
        with open(filepath) as f:
            data = json.load(f)

        # Convert to DataFrame
        df = pd.DataFrame(data)
        # Convert to datetime with UTC
        df['startTime'] = pd.to_datetime(df['startTime'], utc=True)
        df['endTime'] = pd.to_datetime(df['endTime'], utc=True)
        df['eventId_numeric'] = df['eventId'].astype(int)
        df = df.sort_values(by='eventId_numeric')

        # Convert datetimes to matplotlib float format
        df['start_num'] = mdates.date2num(df['startTime'])
        df['end_num'] = mdates.date2num(df['endTime'])
        df['duration_num'] = df['end_num'] - df['start_num']

        # Plot
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.barh(
            y=df['eventId'].astype(str),
            left=df['start_num'],
            width=df['duration_num'],
            color='skyblue'
        )

        # Format x-axis as proper UTC datetime
        ax.xaxis_date()
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%Y-%m-%d UTC'))

        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')

        ax.set_title(title, fontsize=16)
        ax.set_xlabel('Time (UTC)')
        ax.set_ylabel('Event ID')

        plt.tight_layout()
        plt.show()
    else:
        print(f"No such file or directory {filepath}.")


def generate_map(filepath, title):
    if os.path.isfile(filepath):
        # Load the heatmap.json file
        with open(filepath) as f:
            data = json.load(f)

        # Convert to DataFrame
        df = pd.DataFrame(data)
        df['eventId_numeric'] = df['eventId'].astype(int)
        df = df.sort_values(by='eventId_numeric')

        # Convert to GeoDataFrame
        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df['longitude'], df['latitude']),
            crs='EPSG:4326'  # WGS84
        )
        # Reproject to Web Mercator for contextily basemap
        gdf = gdf.to_crs(epsg=3857)
        # Plot
        fig, ax = plt.subplots(figsize=(12, 10))
        gdf.plot(ax=ax, color='red', markersize=50)

        # Annotate eventId
        for i, row in gdf.iterrows():
            ax.annotate(row['eventId'], xy=(row.geometry.x, row.geometry.y), xytext=(3, 3),
                        textcoords="offset points", fontsize=8)

        # Add basemap
        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
        ax.set_title(title)
        ax.axis('off')
        plt.tight_layout()
        plt.show()
    else:
        print(f"No such file or directory {filepath}.")

def plot_jamming(filepath, date):
    if util.is_valid_date(date):
        subpath = date.split("/")
        fullpath = os.path.join(filepath, "jamming", *subpath, 'events.json')
        generate_timeline(fullpath, 'Jamming Event Durations (UTC)')
        generate_map(fullpath, "Jamming Event Locations")


def plot_spoofing(filepath, date):
    if util.is_valid_date(date):
        subpath = date.split("/")
        fullpath = os.path.join(filepath, "spoofing", *subpath, 'events.json')
        generate_timeline(fullpath, 'Spoofing Event Durations (UTC)')
        generate_map(fullpath, "Spoofing Event Locations")

if __name__ == '__main__':
    # plot_jamming("downloaded_json_files", "2025/03/05")
    plot_spoofing("downloaded_json_files", "2025/03/05")