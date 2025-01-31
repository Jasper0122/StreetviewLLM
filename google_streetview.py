import os
import google_streetview.api
import requests


def download_and_save_streetview_image(lat, lon, folder='streetview'):
    api_key = 'YOUR_API_KEY'  # Be sure to replace 'YOUR_API_KEY' with your actual Google Maps API key
    """
    Download and save a streetview image for given latitude and longitude inside a specified folder.

    Parameters:
    - lat: float. Latitude for the location.
    - lon: float. Longitude for the location.
    - folder: str. Folder to save the image in.
    """
    # Ensure the directory exists
    os.makedirs(folder, exist_ok=True)

    # Define parameters for API request
    params = [{
        'size': '640x640',  # Change size as necessary
        'location': f'{lat},{lon}',
        'heading': '151.78',
        'pitch': '-0.76',
        'key': api_key
    }]

    # Create a results object
    results = google_streetview.api.results(params)

    # Get the URL of the image
    links = results.links
    if not links:
        print("No street view images found at this location.")
        return

    # Download the image from the URL
    image_response = requests.get(links[0])
    if image_response.status_code == 200:
        # Generate filename based on latitude and longitude
        filename = f"{lat}_{lon}.jpg"
        full_path = os.path.join(folder, filename)

        # Save the image
        with open(full_path, 'wb') as file:
            file.write(image_response.content)
        print(f"Image saved as {full_path}")
    else:
        print("Failed to download the image.")


# Example usage:
download_and_save_streetview_image(46.414382, 10.013988)
