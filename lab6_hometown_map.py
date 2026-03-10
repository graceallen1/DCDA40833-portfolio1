import pandas as pd
import requests
import folium
from urllib.parse import quote

# =====================================================
# LAB 6 - HOMETOWN INTERACTIVE MAP
# Grace Allen
# =====================================================

# -----------------------------
# MAPBOX SETTINGS
# -----------------------------
ACCESS_TOKEN = "pk.eyJ1IjoiZ3JhY2UtYWxsZW4iLCJhIjoiY21tMHZjOXpuMDM0bjJwcHJhY3N3NGo0ZCJ9.-4aVRpJL842xmrqxNs7mEA"

# Your Mapbox style info
USERNAME = "grace-allen"
STYLE_ID = "cmm3r0tut00i501qz31ix4mt3"

# File names
CSV_FILE = "hometown_locations.csv"
OUTPUT_HTML = "lab6_hometown_map.html"

# Mapbox custom tiles URL for Folium
tiles_url = f"https://api.mapbox.com/styles/v1/{USERNAME}/{STYLE_ID}/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={ACCESS_TOKEN}"


# -----------------------------
# FUNCTION: GEOCODE ADDRESS
# -----------------------------
def geocode_address(address, access_token):
    """
    Sends an address to the Mapbox Geocoding API
    and returns latitude and longitude.
    """
    encoded_address = quote(address)
    url = f"https://api.mapbox.com/search/geocode/v6/forward?q={encoded_address}&access_token={access_token}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        features = data.get("features", [])
        if features:
            # Mapbox gives coordinates in [longitude, latitude] order
            longitude, latitude = features[0]["geometry"]["coordinates"]
            return latitude, longitude
        else:
            print(f"Could not geocode: {address}")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"Error geocoding {address}: {e}")
        return None, None


# -----------------------------
# READ CSV
# -----------------------------
df = pd.read_csv(CSV_FILE)

print("CSV loaded successfully.")
print(df.head())


# -----------------------------
# GEOCODE ALL LOCATIONS
# -----------------------------
latitudes = []
longitudes = []

for address in df["Address"]:
    lat, lon = geocode_address(address, ACCESS_TOKEN)
    latitudes.append(lat)
    longitudes.append(lon)

df["Latitude"] = latitudes
df["Longitude"] = longitudes

# Remove any rows that failed to geocode
df = df.dropna(subset=["Latitude", "Longitude"])

print("\nGeocoding complete.")
print(df[["Name", "Latitude", "Longitude"]])


# -----------------------------
# ICON STYLES BY LOCATION TYPE
# -----------------------------
# These match the types in your CSV
icon_styles = {
    "School": {"color": "blue", "icon": "education"},
    "Restaurant": {"color": "red", "icon": "cutlery"},
    "Workout": {"color": "orange", "icon": "heart"},
    "Cafe": {"color": "green", "icon": "coffee"},
    "Shopping": {"color": "purple", "icon": "shopping-cart"},
    "Park": {"color": "darkgreen", "icon": "tree-conifer"},
    "Recreation": {"color": "cadetblue", "icon": "star"},
    "Museam": {"color": "darkpurple", "icon": "camera"}
}

# default style in case a type is missing from dictionary
default_style = {"color": "gray", "icon": "info-sign"}


# -----------------------------
# CREATE BASE MAP
# -----------------------------
# Center the map based on average coordinates
center_lat = df["Latitude"].mean()
center_lon = df["Longitude"].mean()

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=11,
    tiles=None
)

# Add your custom Mapbox basemap
folium.TileLayer(
    tiles=tiles_url,
    attr="Map data © OpenStreetMap contributors | Imagery © Mapbox",
    name="Grace Allen Custom Basemap",
    overlay=False,
    control=True
).add_to(m)


# -----------------------------
# ADD MARKERS + POPUPS
# -----------------------------
for _, row in df.iterrows():
    location_type = row["Type"]
    style = icon_styles.get(location_type, default_style)

    popup_html = f"""
    <div style="width:260px;">
        <h3 style="margin-bottom:8px;">{row['Name']}</h3>
        <p><strong>Type:</strong> {row['Type']}</p>
        <p>{row['Description']}</p>
        <img src="{row['Image_URL']}" alt="{row['Name']}" style="width:100%; border-radius:8px; margin-top:8px;">
    </div>
    """

    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        tooltip=row["Name"],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(
            color=style["color"],
            icon=style["icon"],
            prefix="glyphicon"
        )
    ).add_to(m)


# -----------------------------
# ADD LAYER CONTROL
# -----------------------------
folium.LayerControl().add_to(m)


# -----------------------------
# SAVE MAP
# -----------------------------
m.save(OUTPUT_HTML)

print(f"\nMap created successfully and saved as: {OUTPUT_HTML}")



