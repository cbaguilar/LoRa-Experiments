import pandas as pd
import numpy as np
from lxml import etree
import datetime
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import seaborn as sns

import gpxpy
import gpxpy.gpx


# Step 1: Load and collapse signal strength data
signal_df = pd.read_csv('backup.csv', header=None, names=['timestamp', 'signal_strength'])
signal_df['unix_time'] = signal_df['timestamp'].astype(int)
median_signal_df = signal_df.groupby('unix_time')['signal_strength'].median().reset_index()

print(median_signal_df)

# Step 2: Parse GPX data from file
with open('may27.gpx', 'r') as file:
    gpx_data = file.read()

root = etree.fromstring(gpx_data.encode())

print(root)
namespaces = {
    'default': 'http://www.topografix.com/GPX/1/1',
    'geotracker': 'http://ilyabogdanovich.com/gpx/extensions/geotracker'
}

root = etree.fromstring(gpx_data.encode())

gpx_points = []
for trkpt in root.findall('.//default:trkpt', namespaces):
    lat = float(trkpt.get('lat'))
    lon = float(trkpt.get('lon'))
    ele = float(trkpt.find('default:ele', namespaces).text)
    time_str = trkpt.find('default:time', namespaces).text
    time_unix = int(datetime.datetime.fromisoformat(time_str.replace("Z", "+00:00")).timestamp())
    gpx_points.append((time_unix, lat, lon, ele))

gpx_df = pd.DataFrame(gpx_points, columns=['unix_time', 'latitude', 'longitude', 'elevation'])


# Step 3: Join datasets on the unix second
merged_df = pd.merge(median_signal_df, gpx_df, on='unix_time', how='inner')

# Display the merged data
print(merged_df)


# Step 4: Plot the data with color-coded points
plt.figure(figsize=(10, 8))

# Normalize the signal strength for color mapping
norm = plt.Normalize(merged_df['signal_strength'].min(), merged_df['signal_strength'].max())
cmap = plt.cm.get_cmap('coolwarm')

# Scatter plot with color based on signal strength
sc = plt.scatter(merged_df['longitude'], merged_df['latitude'], c=merged_df['signal_strength'], cmap=cmap, norm=norm, s=100, edgecolor='k', alpha=0.7)

# Add colorbar
cbar = plt.colorbar(sc)
cbar.set_label('Signal Strength')

# Labels and title
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Signal Strength Over Different Areas')

plt.show()
