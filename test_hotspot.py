import pandas as pd
import ast
import folium
from folium.plugins import HeatMap
from scipy.stats import gaussian_kde
import numpy as np

# Load the dataset
file_path = r"C:/Users/ASUS/OneDrive/Documents/Skripsi_Megi/skripsi_baru/kuliner_makassar_clean.csv"
data = pd.read_csv(file_path)

# Extract latitude and longitude from the 'Lokasi' column
data['Lat'] = data['Lokasi'].apply(lambda x: ast.literal_eval(x)['lat'])
data['Lng'] = data['Lokasi'].apply(lambda x: ast.literal_eval(x)['lng'])

def create_kde_heatmap(filtered_data, map_object, layer_name):
    """
    Create KDE-based heatmap for filtered data
    """
    if len(filtered_data) < 3:  # Need at least 3 points for KDE
        return
    
    # Prepare coordinates for filtered data
    filter_coordinates = filtered_data[['Lat', 'Lng']].values
    
    # Create KDE model
    kde = gaussian_kde(filter_coordinates.T, bw_method=0.025)
    
    # Create grid for density estimation
    lat_min, lat_max = filter_coordinates[:, 0].min(), filter_coordinates[:, 0].max()
    lng_min, lng_max = filter_coordinates[:, 1].min(), filter_coordinates[:, 1].max()
    
    # Add padding to grid
    lat_padding = (lat_max - lat_min) * 0.15
    lng_padding = (lng_max - lng_min) * 0.15
    
    lat_values = np.linspace(lat_min - lat_padding, lat_max + lat_padding, 80)
    lng_values = np.linspace(lng_min - lng_padding, lng_max + lng_padding, 80)
    lat_grid, lng_grid = np.meshgrid(lat_values, lng_values)
    
    # Evaluate KDE on the grid
    density = kde(np.vstack([lat_grid.ravel(), lng_grid.ravel()]))
    density = density.reshape(lat_grid.shape)
    
    # Normalize density
    density_normalized = (density - density.min()) / (density.max() - density.min())
    
    # Create heatmap data
    heat_data = []
    for lat, lng, d in zip(lat_grid.ravel(), lng_grid.ravel(), density_normalized.ravel()):
        if d > 0.03:  # Filter out very low-density areas
            heat_data.append([lat, lng, d])
    
    # Create heatmap layer with minimal parameters
    heatmap_layer = folium.FeatureGroup(name=layer_name, show=False)  # Default hidden
    HeatMap(heat_data, radius=20, blur=25).add_to(heatmap_layer)
    
    heatmap_layer.add_to(map_object)

def get_marker_color_by_ratings(user_ratings_total):
    """
    Determine marker color based on user_ratings_total
    """
    if user_ratings_total >= 500:
        return 'red'      # Merah: >= 500 ratings
    elif user_ratings_total >= 100:
        return 'orange'   # Orange: 100-499 ratings
    else:
        return 'lightblue'     # Biru: < 100 ratings

def get_price_label(price_level):
    """
    Convert price level number to descriptive text
    """
    price_mapping = {
        0: 'Murah',
        1: 'Terjangkau', 
        2: 'Sedang',
        3: 'Mahal'
    }
    return price_mapping.get(price_level, 'Tidak Diketahui')

def get_price_color(price_level):
    """
    Get color for price level display
    """
    color_mapping = {
        0: '#28a745',  # Green untuk murah
        1: '#ffc107',  # Yellow untuk terjangkau
        2: '#fd7e14',  # Orange untuk sedang
        3: '#dc3545'   # Red untuk mahal
    }
    return color_mapping.get(price_level, '#6c757d')

def get_marker_icon_color(color_name):
    """
    Convert Folium color names to hex colors
    """
    color_map = {
        'red': '#d63031',
        'orange': '#e17055', 
        'lightblue': '#74b9ff'
    }
    return color_map.get(color_name, '#74b9ff')

def create_custom_icon(color):
    """
    Create custom icon with smaller size using CSS scaling
    """
    return folium.DivIcon(
        html=f'''
        <div style="
            transform: scale(0.75);
            transform-origin: center bottom;
        ">
            <i class="fa fa-map-marker" style="
                color: {color};
                font-size: 30px;
                text-shadow: 1px 1px 1px rgba(0,0,0,0.5);
            "></i>
        </div>
        ''',
        icon_size=(25, 35),
        icon_anchor=(12, 35),
        class_name='custom-marker'
    )

def create_google_maps_url(lat, lng, place_name):
    """
    Create Google Maps URL for navigation
    """
    place_name_encoded = place_name.replace(' ', '+').replace(',', '')
    return f"https://www.google.com/maps/search/?api=1&query={lat},{lng}+{place_name_encoded}"

# Create main map with Google Streets as the only basemap
map_center = [data['Lat'].mean(), data['Lng'].mean()]
m = folium.Map(
    location=map_center, 
    zoom_start=12,
    tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
    attr='Google Streets'
)

# Prepare data categories
rating_5_data = data[data['Rating'] == 5.0]
rating_45_49_data = data[(data['Rating'] >= 4.5) & (data['Rating'] < 5.0)]
rating_40_44_data = data[(data['Rating'] >= 4.0) & (data['Rating'] < 4.5)]
rating_below_4_data = data[data['Rating'] < 4.0]
rating_0_data = data[data['Rating'] == 0]

# ============= HEATMAP LAYERS =============
# Create heatmap layers (all hidden by default to avoid overlap)

# All data heatmap - show by default
all_heatmap_layer = folium.FeatureGroup(name='Heatmap - Semua Data', show=True)
create_kde_heatmap(data, m, 'Heatmap - Semua Data')

# Rating-specific heatmaps - hidden by default
if len(rating_5_data) > 0:
    rating_5_heatmap = folium.FeatureGroup(name='Heatmap - Rating 5.0', show=False)
    create_kde_heatmap(rating_5_data, m, 'Heatmap - Rating 5.0')

if len(rating_45_49_data) > 0:
    rating_45_49_heatmap = folium.FeatureGroup(name='Heatmap - Rating 4.5-4.9', show=False)
    create_kde_heatmap(rating_45_49_data, m, 'Heatmap - Rating 4.5-4.9')

if len(rating_40_44_data) > 0:
    rating_40_44_heatmap = folium.FeatureGroup(name='Heatmap - Rating 4.0-4.4', show=False)
    create_kde_heatmap(rating_40_44_data, m, 'Heatmap - Rating 4.0-4.4')

if len(rating_below_4_data) > 0:
    rating_below_4_heatmap = folium.FeatureGroup(name='Heatmap - Rating < 4.0', show=False)
    create_kde_heatmap(rating_below_4_data, m, 'Heatmap - Rating < 4.0')

if len(rating_0_data) > 0:
    rating_0_heatmap = folium.FeatureGroup(name='Heatmap - Rating 0', show=False)
    if len(rating_0_data) >= 3:
        create_kde_heatmap(rating_0_data, m, 'Heatmap - Rating 0')

# ============= MARKER LAYERS =============
# Create marker layers - only show "All Markers" by default
markers_all_layer = folium.FeatureGroup(name='Markers - Semua Data', show=True)
markers_rating_5_layer = folium.FeatureGroup(name='Markers - Rating 5.0', show=False) 
markers_rating_45_49_layer = folium.FeatureGroup(name='Markers - Rating 4.5-4.9', show=False)
markers_rating_40_44_layer = folium.FeatureGroup(name='Markers - Rating 4.0-4.4', show=False)
markers_rating_below_4_layer = folium.FeatureGroup(name='Markers - Rating < 4.0', show=False)
markers_rating_0_layer = folium.FeatureGroup(name='Markers - Rating 0', show=False)

# Add markers with improved styling
for _, row in data.iterrows():
    # Determine marker color based on user_ratings_total
    marker_color = get_marker_color_by_ratings(row['User_Ratings_Total'])
    
    # Get price label and color
    price_label = get_price_label(row['Price_Level'])
    price_color = get_price_color(row['Price_Level'])
    
    # Create Google Maps URL
    google_maps_url = create_google_maps_url(row['Lat'], row['Lng'], row['Nama'])
    
    # Create popup content with enhanced price level display
    popup_content = f"""
    <div style="width: 300px; font-family: Arial, sans-serif;">
        <div style="background: #4285f4; color: white; padding: 12px; margin: -9px -9px 12px -9px;">
            <h3 style="margin: 0; font-size: 16px;">{row['Nama']}</h3>
        </div>
        
        <div style="padding: 0 8px;">
            <p style="margin: 8px 0;"><strong>Alamat:</strong><br>{row['Alamat']}</p>
            
            <div style="display: flex; justify-content: space-between; margin: 12px 0;">
                <div style="text-align: center; flex: 1;">
                    <div style="font-size: 20px; font-weight: bold; color: #ff6b6b;">
                        {row['Rating']}
                    </div>
                    <div style="font-size: 12px;">Rating</div>
                </div>
                <div style="text-align: center; flex: 1;">
                    <div style="font-size: 16px; font-weight: bold; color: #4ecdc4;">
                        {row['User_Ratings_Total']}
                    </div>
                    <div style="font-size: 12px;">Reviews</div>
                </div>
                <div style="text-align: center; flex: 1;">
                    <div style="font-size: 16px; font-weight: bold; color: {price_color};">
                        {price_label}
                    </div>
                    <div style="font-size: 12px;">Harga</div>
                </div>
            </div>
            
            <div style="background: #f8f9fa; padding: 8px; border-radius: 5px; margin: 10px 0;">
                <p style="margin: 0; font-size: 12px; color: #666;">
                    <strong>Koordinat:</strong> {row['Lat']:.6f}, {row['Lng']:.6f}
                </p>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 15px;">
            <a href="{google_maps_url}" target="_blank" 
               style="background: #4285f4; color: white; padding: 10px 20px; 
                      text-decoration: none; border-radius: 5px; font-weight: bold;
                      display: inline-block; width: 80%;">
               Buka di Google Maps
            </a>
        </div>
    </div>
    """
    
    # Get marker icon color
    icon_color = get_marker_icon_color(marker_color)
    
    # Create marker for all markers layer
    marker = folium.Marker(
        location=[row['Lat'], row['Lng']],
        popup=folium.Popup(popup_content, max_width=340),
        tooltip=f"{row['Nama']} - Rating: {row['Rating']} - Reviews: {row['User_Ratings_Total']} - Harga: {price_label}",
        icon=create_custom_icon(icon_color)
    )
    marker.add_to(markers_all_layer)
    
    # Add to specific rating layers
    if row['Rating'] == 5.0:
        marker_copy = folium.Marker(
            location=[row['Lat'], row['Lng']],
            popup=folium.Popup(popup_content, max_width=340),
            tooltip=f"{row['Nama']} - Rating: {row['Rating']} - Reviews: {row['User_Ratings_Total']} - Harga: {price_label}",
            icon=create_custom_icon(icon_color)
        )
        marker_copy.add_to(markers_rating_5_layer)
    elif 4.5 <= row['Rating'] < 5.0:
        marker_copy = folium.Marker(
            location=[row['Lat'], row['Lng']],
            popup=folium.Popup(popup_content, max_width=340),
            tooltip=f"{row['Nama']} - Rating: {row['Rating']} - Reviews: {row['User_Ratings_Total']} - Harga: {price_label}",
            icon=create_custom_icon(icon_color)
        )
        marker_copy.add_to(markers_rating_45_49_layer)
    elif 4.0 <= row['Rating'] < 4.5:
        marker_copy = folium.Marker(
            location=[row['Lat'], row['Lng']],
            popup=folium.Popup(popup_content, max_width=340),
            tooltip=f"{row['Nama']} - Rating: {row['Rating']} - Reviews: {row['User_Ratings_Total']} - Harga: {price_label}",
            icon=create_custom_icon(icon_color)
        )
        marker_copy.add_to(markers_rating_40_44_layer)
    elif row['Rating'] < 4.0 and row['Rating'] > 0:
        marker_copy = folium.Marker(
            location=[row['Lat'], row['Lng']],
            popup=folium.Popup(popup_content, max_width=340),
            tooltip=f"{row['Nama']} - Rating: {row['Rating']} - Reviews: {row['User_Ratings_Total']} - Harga: {price_label}",
            icon=create_custom_icon(icon_color)
        )
        marker_copy.add_to(markers_rating_below_4_layer)
    elif row['Rating'] == 0:
        marker_copy = folium.Marker(
            location=[row['Lat'], row['Lng']],
            popup=folium.Popup(popup_content, max_width=340),
            tooltip=f"{row['Nama']} - Rating: {row['Rating']} - Reviews: {row['User_Ratings_Total']} - Harga: {price_label}",
            icon=create_custom_icon(icon_color)
        )
        marker_copy.add_to(markers_rating_0_layer)

# Add all layers to map
markers_all_layer.add_to(m)
markers_rating_5_layer.add_to(m)
markers_rating_45_49_layer.add_to(m)
markers_rating_40_44_layer.add_to(m)
markers_rating_below_4_layer.add_to(m)
markers_rating_0_layer.add_to(m)

# Add collapsible legend with close/open functionality
legend_html = '''
<div id="legend-container" style="position: fixed; 
            top: 15px; right: 15px; z-index: 9999;">
    
    <!-- Collapsed state button -->
    <div id="legend-collapsed" style="
        width: 50px; height: 50px; 
        background-color: white; border: 2px solid #333; 
        border-radius: 6px; box-shadow: 0 3px 6px rgba(0,0,0,0.2);
        display: none; cursor: pointer;
        justify-content: center; align-items: center;
        font-size: 20px; font-weight: bold; color: #333;">
        📍
    </div>
    
    <!-- Expanded legend -->
    <div id="legend-expanded" style="
        width: 220px; height: auto; 
        background-color: white; border: 2px solid #333; 
        font-size: 12px; padding: 12px;
        border-radius: 6px; box-shadow: 0 3px 6px rgba(0,0,0,0.2);">
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h3 style="margin: 0; color: #333; font-size: 14px;">Legenda Warna Marker</h3>
            <button id="close-legend" style="
                background: none; border: none; font-size: 16px; 
                cursor: pointer; color: #666; padding: 0;
                width: 20px; height: 20px; display: flex;
                justify-content: center; align-items: center;">
                ✕
            </button>
        </div>

        <div style="margin: 5px 0;">
            <span style="color: red; font-size: 14px;">●</span> 
            <strong>≥ 500 reviews</strong> - Sangat Populer
        </div>
        <div style="margin: 5px 0;">
            <span style="color: orange; font-size: 14px;">●</span> 
            <strong>100-499 reviews</strong> - Populer
        </div>
        <div style="margin: 5px 0;">
            <span style="color: lightblue; font-size: 14px;">●</span> 
            <strong>< 100 reviews</strong> - Kurang Populer
        </div>

        <hr style="margin: 10px 0; border: 1px solid #ddd;">

        <div style="background: #f8f9fa; padding: 8px; border-radius: 4px;">
            <p style="margin: 0; font-size: 10px; color: #666;">
                <strong>Hotspot:</strong> Berdasarkan Algoritma KDE<br>
                <strong>Basemap:</strong> Google Street Maps<br>
                <strong>Filter:</strong> Per kategori rating
            </p>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const legendCollapsed = document.getElementById('legend-collapsed');
    const legendExpanded = document.getElementById('legend-expanded');
    const closeButton = document.getElementById('close-legend');
    
    // Close legend function
    closeButton.addEventListener('click', function() {
        legendExpanded.style.display = 'none';
        legendCollapsed.style.display = 'flex';
    });
    
    // Open legend function
    legendCollapsed.addEventListener('click', function() {
        legendCollapsed.style.display = 'none';
        legendExpanded.style.display = 'block';
    });
});
</script>
'''

# Add legend and standard layer control
m.get_root().html.add_child(folium.Element(legend_html))

# Add layer control with improved settings
folium.LayerControl(
    collapsed=False,
    position='topleft'
).add_to(m)

# Print enhanced statistics
print("="*60)
print("VISUALISASI HOTSPOT UMKM MAKASSAR - GOOGLE STREET MAPS")
print("="*60)
print(f"Total UMKM: {len(data)}")
print(f"Rating 5.0: {len(rating_5_data)} UMKM")
print(f"Rating 4.5-4.9: {len(rating_45_49_data)} UMKM") 
print(f"Rating 4.0-4.4: {len(rating_40_44_data)} UMKM")
print(f"Rating < 4.0: {len(rating_below_4_data)} UMKM")
print(f"Rating 0: {len(rating_0_data)} UMKM")

print(f"\nDistribusi Warna Marker (berdasarkan jumlah reviews):")
merah = len(data[data['User_Ratings_Total'] >= 500])
orange = len(data[(data['User_Ratings_Total'] >= 100) & (data['User_Ratings_Total'] < 500)])
biru = len(data[data['User_Ratings_Total'] < 100])
print(f"Merah (≥500 reviews): {merah} UMKM")
print(f"Orange (100-499 reviews): {orange} UMKM")
print(f"Biru (<100 reviews): {biru} UMKM")

# Enhanced statistics - Price Level Distribution
print(f"\nDistribusi Level Harga:")
murah = len(data[data['Price_Level'] == 0])
terjangkau = len(data[data['Price_Level'] == 1])
sedang = len(data[data['Price_Level'] == 2])
mahal = len(data[data['Price_Level'] == 3])
print(f"Murah: {murah} UMKM ({murah/len(data)*100:.1f}%)")
print(f"Terjangkau: {terjangkau} UMKM ({terjangkau/len(data)*100:.1f}%)")
print(f"Sedang: {sedang} UMKM ({sedang/len(data)*100:.1f}%)")
print(f"Mahal: {mahal} UMKM ({mahal/len(data)*100:.1f}%)")

# Save the map
output_file = "hotspot_umkm_makassar_final.html"
m.save(output_file)

print(f"\nPeta berhasil disimpan sebagai '{output_file}'")