import pandas as pd
import ast
import requests
import time
from shapely.geometry import Point, Polygon
import geopandas as gpd
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from functools import partial

def load_data(file_path):
    """
    Load CSV data dan check data kosong
    """
    print("Loading data from CSV...")
    try:
        data = pd.read_csv(file_path)
        print(f"Data loaded: {len(data)} records")
        
        # Check data kosong
        print("\nChecking for empty/null data...")
        null_counts = data.isnull().sum()
        empty_counts = (data == '').sum()
        
        print("Null values per column:")
        for col, count in null_counts.items():
            if count > 0:
                print(f"  {col}: {count} null values")
        
        print("Empty string values per column:")
        for col, count in empty_counts.items():
            if count > 0:
                print(f"  {col}: {count} empty strings")
        
        # Remove rows with critical empty data
        initial_count = len(data)
                                                          
        # Remove rows with empty Nama or Lokasi
        data = data.dropna(subset=['Nama', 'Lokasi'])
        data = data[data['Nama'].str.strip() != '']
        data = data[data['Lokasi'].str.strip() != '']
        
        after_cleaning = len(data)
        removed = initial_count - after_cleaning
        
        if removed > 0:
            print(f"Removed {removed} rows with empty critical data (Nama/Lokasi)")
        
        print(f"Final data count: {len(data)} records")
        return data
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def extract_coordinates(data):
    """
    Extract latitude dan longitude dari kolom Lokasi dengan error handling
    """
    print("Extracting coordinates...")
    
    initial_count = len(data)
    valid_coords = []
    
    for idx, row in data.iterrows():
        try:
            # Parse lokasi string
            lokasi_dict = ast.literal_eval(row['Lokasi'])
            lat = lokasi_dict['lat']
            lng = lokasi_dict['lng']
            
            # Validate coordinates range
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                valid_coords.append(idx)
            else:
                print(f"Invalid coordinates for {row['Nama']}: lat={lat}, lng={lng}")
                
        except Exception as e:
            print(f"Error parsing coordinates for {row['Nama']}: {e}")
    
    # Keep only valid coordinates
    data = data.loc[valid_coords].copy()
    
    # Extract coordinates
    data['Lat'] = data['Lokasi'].apply(lambda x: ast.literal_eval(x)['lat'])
    data['Lng'] = data['Lokasi'].apply(lambda x: ast.literal_eval(x)['lng'])
    
    removed = initial_count - len(data)
    if removed > 0:
        print(f"Removed {removed} rows with invalid coordinates")
    
    print(f"Coordinates extracted for {len(data)} records")
    return data

def create_makassar_boundary():
    """
    Definisi batas administratif Kota Makassar yang lebih akurat
    Menggunakan polygon boundaries yang lebih detail
    """
    print("Creating Makassar city boundary...")
    
    # Batas Kota Makassar yang lebih akurat (polygon)
    # Koordinat ini menghindari area Kabupaten Gowa
    makassar_coords = [
        # Bagian Utara (Pelabuhan, Pantai Losari area)
        (119.374, -5.075),
        (119.425, -5.075),
        (119.465, -5.095),
        
        # Bagian Timur Laut
        (119.480, -5.115),
        (119.485, -5.135),
        
        # Bagian Timur (area UNM, BTP)
        (119.485, -5.155),
        (119.480, -5.175),
        (119.475, -5.190),
        
        # Bagian Tenggara (batas dengan Gowa - hati-hati di sini)
        (119.465, -5.205),
        (119.450, -5.215),
        (119.435, -5.220),
        
        # Bagian Selatan (masih Makassar, belum Gowa)
        (119.420, -5.225),
        (119.405, -5.228),
        (119.390, -5.230),
        
        # Bagian Barat Daya
        (119.380, -5.225),
        (119.375, -5.210),
        
        # Bagian Barat (pesisir)
        (119.374, -5.190),
        (119.374, -5.170),
        (119.374, -5.150),
        (119.374, -5.130),
        (119.374, -5.110),
        (119.374, -5.090),
    ]
    
    # Buat polygon
    makassar_polygon = Polygon(makassar_coords)
    
    print("Makassar boundary created")
    return makassar_polygon

def check_location_validity(lat, lng, boundary_polygon):
    """
    Check apakah koordinat berada dalam batas Kota Makassar
    """
    point = Point(lng, lat)  # Note: Point(lng, lat) bukan Point(lat, lng)
    return boundary_polygon.contains(point)

def filter_by_boundary(data, boundary_polygon):
    """
    Filter data berdasarkan batas administratif
    """
    print("Filtering data by Makassar boundary...")
    
    # Tambah kolom validasi
    data['In_Makassar'] = data.apply(
        lambda row: check_location_validity(row['Lat'], row['Lng'], boundary_polygon), 
        axis=1
    )
    
    # Filter data yang berada di dalam Makassar
    filtered_data = data[data['In_Makassar'] == True].copy()
    
    # Hapus kolom temporary
    filtered_data = filtered_data.drop('In_Makassar', axis=1)
    
    print(f"Data sebelum filtering: {len(data)} records")
    print(f"Data setelah filtering: {len(filtered_data)} records")
    print(f"Data yang dihapus (area Gowa dll): {len(data) - len(filtered_data)} records")
    
    return filtered_data

def reverse_geocode_check(lat, lng, max_retries=3):
    """
    Double check menggunakan reverse geocoding
    untuk memastikan alamat benar-benar di Kota Makassar
    """
    for attempt in range(max_retries):
        try:
            # Menggunakan Nominatim API
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=10&addressdetails=1"
            
            headers = {
                'User-Agent': 'Makassar_UMKM_Cleaner/1.0'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'address' in data:
                    address = data['address']
                    
                    # Check berbagai level administratif
                    city = address.get('city', '').lower()
                    county = address.get('county', '').lower()
                    state = address.get('state', '').lower()
                    municipality = address.get('municipality', '').lower()
                    city_district = address.get('city_district', '').lower()
                    suburb = address.get('suburb', '').lower()
                    
                    # Gabungkan semua informasi lokasi
                    location_text = f"{city} {county} {state} {municipality} {city_district} {suburb}".lower()
                    
                    # Check apakah benar-benar di Kota Makassar
                    if 'makassar' in location_text and 'kota' in location_text:
                        return True, f"Kota Makassar"
                    elif 'makassar' in city or city == 'makassar':
                        return True, f"Kota Makassar"
                    else:
                        # Bukan Kota Makassar - bisa Gowa, Maros, Takalar, dll
                        detected_location = ""
                        if 'gowa' in location_text:
                            detected_location = "Kabupaten Gowa"
                        elif 'maros' in location_text:
                            detected_location = "Kabupaten Maros"
                        elif 'takalar' in location_text:
                            detected_location = "Kabupaten Takalar"
                        elif 'bantaeng' in location_text:
                            detected_location = "Kabupaten Bantaeng"
                        elif 'jeneponto' in location_text:
                            detected_location = "Kabupaten Jeneponto"
                        elif 'pangkep' in location_text or 'pangkajene' in location_text:
                            detected_location = "Kabupaten Pangkep"
                        elif 'barru' in location_text:
                            detected_location = "Kabupaten Barru"
                        elif 'bone' in location_text:
                            detected_location = "Kabupaten Bone"
                        elif 'pare' in location_text and 'pare' in location_text:
                            detected_location = "Kota Parepare"
                        else:
                            detected_location = f"Area lain: {location_text.strip()}"
                        
                        return False, detected_location
            
            # Rate limiting dengan jitter untuk parallelization
            time.sleep(1 + (attempt * 0.5))
            
        except Exception as e:
            print(f"Geocoding attempt {attempt + 1} failed for {lat},{lng}: {e}")
            time.sleep(2 + attempt)
    
    return None, "Geocoding failed"

def process_single_row(row_data):
    """
    Process single row for parallel geocoding
    """
    idx, row = row_data
    is_makassar, location_info = reverse_geocode_check(row['Lat'], row['Lng'])
    
    return {
        'idx': idx,
        'name': row['Nama'],
        'is_makassar': is_makassar,
        'location_info': location_info
    }

def full_parallel_cleaning(data, max_workers=10):
    """
    Parallel reverse geocoding untuk SEMUA data tanpa boundary filter
    Langsung proses semua data dengan parallelization
    """
    print(f"\nMemulai parallel geocoding untuk SEMUA {len(data)} data...")
    print(f"Menggunakan {max_workers} workers parallel")
    print("Estimasi waktu: 3-5 menit\n")
    
    confirmed_makassar = []
    confirmed_outside = []
    unclear = []
    outside_locations = {}
    
    # Lock untuk thread-safe operations
    results_lock = threading.Lock()
    
    # Prepare data for parallel processing
    row_data = [(idx, row) for idx, row in data.iterrows()]
    
    # Progress tracking
    completed = 0
    total = len(row_data)
    start_time = time.time()
    
    # Parallel processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_data = {executor.submit(process_single_row, rd): rd for rd in row_data}
        
        # Collect results as they complete
        for future in as_completed(future_to_data):
            try:
                result = future.result()
                
                with results_lock:
                    completed += 1
                    
                    # Progress update setiap 25 data atau milestone
                    if completed % 25 == 0 or completed == total:
                        elapsed = time.time() - start_time
                        rate = completed / elapsed if elapsed > 0 else 0
                        eta = (total - completed) / rate if rate > 0 else 0
                        print(f"Progress: {completed}/{total} ({completed/total*100:.1f}%) - Rate: {rate:.1f}/s - ETA: {eta:.0f}s")
                
                idx = result['idx']
                name = result['name']
                is_makassar = result['is_makassar']
                location_info = result['location_info']
                
                if is_makassar == True:
                    confirmed_makassar.append(idx)
                elif is_makassar == False:
                    confirmed_outside.append(idx)
                    print(f"  OUTSIDE: {name} -> {location_info}")
                    
                    # Track location statistics (thread-safe)
                    with results_lock:
                        if location_info in outside_locations:
                            outside_locations[location_info] += 1
                        else:
                            outside_locations[location_info] = 1
                else:
                    unclear.append(idx)
                    
            except Exception as e:
                print(f"Error processing row: {e}")
    
    total_time = time.time() - start_time
    print(f"\nParallel processing completed in {total_time:.1f} seconds")
    
    print(f"\nHasil parallel geocoding:")
    print(f"Confirmed Kota Makassar: {len(confirmed_makassar)}")
    print(f"Confirmed di luar Kota Makassar: {len(confirmed_outside)}")
    print(f"Unclear/Failed: {len(unclear)}")
    
    # Show distribution of outside locations
    if outside_locations:
        print(f"\nDistribusi lokasi di luar Kota Makassar:")
        for location, count in sorted(outside_locations.items(), key=lambda x: x[1], reverse=True):
            print(f"  {location}: {count} tempat")
    
    # Remove data outside Makassar
    if confirmed_outside:
        print(f"\nMenghapus {len(confirmed_outside)} data yang terdeteksi di luar Kota Makassar...")
        data_clean = data.drop(confirmed_outside).copy()
        
        # Also remove unclear data for safety
        if unclear:
            print(f"Menghapus {len(unclear)} data yang unclear untuk keamanan...")
            data_clean = data_clean.drop(unclear, errors='ignore').copy()
        
        return data_clean
    
    return data

def print_cleaning_summary(original_data, cleaned_data):
    """
    Print summary hasil cleaning
    """
    print("\n" + "="*60)
    print("HASIL DATA CLEANING - KOTA MAKASSAR")
    print("="*60)
    
    print(f"Data asli: {len(original_data)} records")
    print(f"Data setelah cleaning: {len(cleaned_data)} records")
    print(f"Data yang dihapus: {len(original_data) - len(cleaned_data)} records")
    print(f"Persentase data tersisa: {(len(cleaned_data)/len(original_data)*100):.1f}%")
    
    # Area coverage check
    print(f"\nCoverage area setelah cleaning:")
    print(f"Latitude range: {cleaned_data['Lat'].min():.6f} to {cleaned_data['Lat'].max():.6f}")
    print(f"Longitude range: {cleaned_data['Lng'].min():.6f} to {cleaned_data['Lng'].max():.6f}")
    
    # Rating distribution
    print(f"\nDistribusi rating setelah cleaning:")
    rating_counts = cleaned_data['Rating'].value_counts().sort_index()
    for rating, count in rating_counts.head().items():
        print(f"Rating {rating}: {count} tempat")
    
    # User ratings distribution for marker colors
    user_ratings = cleaned_data['User_Ratings_Total']
    merah = len(user_ratings[user_ratings >= 500])
    orange = len(user_ratings[(user_ratings >= 100) & (user_ratings < 500)])
    biru = len(user_ratings[user_ratings < 100])
    
    print(f"\nDistribusi warna marker:")
    print(f"Merah (>=500 reviews): {merah} tempat")
    print(f"Orange (100-499 reviews): {orange} tempat")
    print(f"Biru (<100 reviews): {biru} tempat")

def save_cleaned_data(data, output_file):
    """
    Simpan data yang sudah dibersihkan
    """
    print(f"\nMenyimpan data bersih ke {output_file}...")
    
    try:
        # Hapus kolom Lat dan Lng sementara (karena sudah ada di kolom Lokasi)
        data_to_save = data.drop(['Lat', 'Lng'], axis=1)
        
        data_to_save.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Data berhasil disimpan ke {output_file}")
        return True
        
    except Exception as e:
        print(f"Error menyimpan data: {e}")
        return False

def main():
    """
    Fungsi utama untuk cleaning data
    """
    print("DATA CLEANING - PARALLEL PROCESSING SEMUA DATA")
    print("="*55)
    
    # File paths
    input_file = "C:/Users/ASUS/OneDrive/Documents/Skripsi_Megi/skripsi_baru/kuliner_makassar_osm.csv"
    output_file = "C:/Users/ASUS/OneDrive/Documents/Skripsi_Megi/skripsi_baru/kuliner_makassar_clean.csv"
    
    # 1. Load data dan check data kosong
    data = load_data(input_file)
    if data is None:
        return
    
    # 2. Extract coordinates dengan validation
    data = extract_coordinates(data)
    
    # 3. Langsung parallel processing SEMUA data (skip boundary filter)
    print("\nMenggunakan parallel processing untuk SEMUA data...")
    print("Tidak menggunakan boundary filter - langsung reverse geocoding")
    
    cleaned_data = full_parallel_cleaning(data, max_workers=10)
    
    # 4. Print summary
    print_cleaning_summary(data, cleaned_data)
    
    # 5. Save cleaned data
    success = save_cleaned_data(cleaned_data, output_file)
    
    if success:
        print(f"\nData cleaning selesai!")
        print(f"File output: {output_file}")

if __name__ == "__main__":
    main()