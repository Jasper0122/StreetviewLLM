import pandas as pd
import folium
from folium import plugins

def plot_on_map(csv_file_path):
    # Read the CSV file
    data = pd.read_csv(csv_file_path)

    # Extract latitude, longitude, and the difference
    latitudes = data['latitude']
    longitudes = data['longitude']
    differences = data['Difference']

    # Ensure differences are within the range 0 to 10
    differences = differences.clip(0, 10)

    coordinates = list(zip(latitudes, longitudes))

    # Create a folium map centered around the average latitude and longitude
    m = folium.Map(location=[latitudes.mean(), longitudes.mean()], zoom_start=12, tiles='CartoDB positron')

    # Create a color map: smaller differences are greener, larger differences are redder
    colormap = folium.LinearColormap(colors=['green', 'yellow', 'red'], vmin=0.0, vmax=10.0)
    colormap.caption = 'Difference'

    # Add circle markers to the map
    for coord, diff in zip(coordinates, differences):
        color = colormap(diff)
        folium.CircleMarker(
            location=coord,
            radius=7,
            color='none',
            fill=True,
            fill_color=color,
            fill_opacity=0.75
        ).add_to(m)

    # Add the colormap to the map
    m.add_child(colormap)

    # Save the map to an HTML file
    output_file_path = csv_file_path.replace('.csv', '_map.html')
    m.save(output_file_path)
    print(f"Map saved to: {output_file_path}")

# Example usage
csv_file_path = 'results/Hongkong_population density_withoutCOT_3.5Tuning_bias.csv'
plot_on_map(csv_file_path)
