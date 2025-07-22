import requests
import json
import csv
import random

def query_osm_makassar():
    """
    Query OpenStreetMap untuk data UMKM kuliner di Makassar dengan coverage area yang diperluas
    """
    print("Mengambil data UMKM kuliner dari OpenStreetMap (Extended Coverage)...")
    
    # Overpass API endpoint
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Query khusus untuk UMKM kuliner di Makassar
    # Fokus pada tempat makan dan minuman, tanpa pub
    # Format: south, west, north, east
    # Coverage: (-5.28,119.35,-5.05,119.55) - mencakup seluruh Kota Makassar
    query = """
    [out:json][timeout:90];
    (
      node["amenity"="restaurant"](-5.28,119.35,-5.05,119.55);
      node["amenity"="cafe"](-5.28,119.35,-5.05,119.55);
      node["amenity"="food_court"](-5.28,119.35,-5.05,119.55);
      node["amenity"="fast_food"](-5.28,119.35,-5.05,119.55);
      node["amenity"="bar"](-5.28,119.35,-5.05,119.55);
      node["amenity"="ice_cream"](-5.28,119.35,-5.05,119.55);
      node["amenity"="juice_bar"](-5.28,119.35,-5.05,119.55);
      node["shop"="bakery"](-5.28,119.35,-5.05,119.55);
      node["shop"="confectionery"](-5.28,119.35,-5.05,119.55);
      node["shop"="coffee"](-5.28,119.35,-5.05,119.55);
      node["shop"="tea"](-5.28,119.35,-5.05,119.55);
      node["shop"="pastry"](-5.28,119.35,-5.05,119.55);
      node["shop"="chocolate"](-5.28,119.35,-5.05,119.55);
      node["shop"="dairy"](-5.28,119.35,-5.05,119.55);
      way["amenity"="restaurant"](-5.28,119.35,-5.05,119.55);
      way["amenity"="cafe"](-5.28,119.35,-5.05,119.55);
      way["amenity"="food_court"](-5.28,119.35,-5.05,119.55);
      way["amenity"="fast_food"](-5.28,119.35,-5.05,119.55);
      way["amenity"="bar"](-5.28,119.35,-5.05,119.55);
      way["amenity"="ice_cream"](-5.28,119.35,-5.05,119.55);
      way["amenity"="juice_bar"](-5.28,119.35,-5.05,119.55);
      way["shop"="bakery"](-5.28,119.35,-5.05,119.55);
      way["shop"="confectionery"](-5.28,119.35,-5.05,119.55);
      way["shop"="coffee"](-5.28,119.35,-5.05,119.55);
      way["shop"="tea"](-5.28,119.35,-5.05,119.55);
      way["shop"="pastry"](-5.28,119.35,-5.05,119.55);
      way["shop"="chocolate"](-5.28,119.35,-5.05,119.55);
    );
    out center geom;
    """
    
    try:
        response = requests.post(overpass_url, data=query, timeout=150)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Berhasil mengambil {len(data['elements'])} tempat kuliner dari OSM")
            print("Jenis UMKM kuliner yang diambil:")
            print("- Restaurant, Cafe, Food Court")
            print("- Fast Food, Bar")
            print("- Ice Cream, Juice Bar")
            print("- Bakery, Confectionery, Coffee Shop")
            print("- Tea Shop, Pastry, Chocolate Shop")
            print("- Dairy Shop")
            return data['elements']
        else:
            print(f"Error HTTP {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error mengambil data: {e}")
        return []

def generate_rating_by_type(amenity_type, shop_type=None):
    """
    Generate rating berdasarkan jenis UMKM kuliner
    """
    # Rating rata-rata untuk setiap jenis UMKM kuliner
    rating_map = {
        'restaurant': (3.5, 4.8),
        'cafe': (3.8, 4.7),
        'food_court': (3.2, 4.2),
        'fast_food': (3.0, 4.0),
        'bar': (3.3, 4.5),
        'ice_cream': (3.6, 4.5),
        'juice_bar': (3.4, 4.3),
        'bakery': (3.8, 4.6),
        'confectionery': (3.9, 4.7),
        'coffee': (3.7, 4.5),
        'tea': (3.5, 4.4),
        'pastry': (3.8, 4.6),
        'chocolate': (4.0, 4.8),
        'dairy': (3.3, 4.2),
    }
    
    # Pilih range rating
    if amenity_type in rating_map:
        min_rating, max_rating = rating_map[amenity_type]
    elif shop_type in rating_map:
        min_rating, max_rating = rating_map[shop_type]
    else:
        min_rating, max_rating = (3.0, 4.5)
    
    # Generate rating random dalam range
    rating = random.uniform(min_rating, max_rating)
    
    # Round ke 1 desimal
    return round(rating, 1)

def generate_user_ratings(rating, place_type):
    """
    Generate jumlah user ratings berdasarkan rating dan jenis UMKM kuliner
    """
    # Base multiplier berdasarkan jenis UMKM kuliner
    type_multipliers = {
        'restaurant': (80, 400),
        'cafe': (50, 250),
        'food_court': (100, 500),
        'fast_food': (120, 600),
        'bar': (30, 180),
        'ice_cream': (40, 200),
        'juice_bar': (30, 150),
        'bakery': (40, 200),
        'confectionery': (35, 180),
        'coffee': (60, 300),
        'tea': (25, 120),
        'pastry': (30, 150),
        'chocolate': (20, 100),
        'dairy': (15, 80),
    }
    
    min_base, max_base = type_multipliers.get(place_type, (20, 150))
    
    # Rating multiplier
    if rating >= 4.5:
        multiplier = random.uniform(1.8, 3.5)
    elif rating >= 4.0:
        multiplier = random.uniform(1.2, 2.2)
    elif rating >= 3.5:
        multiplier = random.uniform(0.8, 1.5)
    else:
        multiplier = random.uniform(0.3, 1.0)
    
    base_count = random.randint(min_base, max_base)
    final_count = int(base_count * multiplier)
    
    # Cap maksimum di 999
    return min(final_count, 999)

def generate_price_level(place_type):
    """
    Generate price level berdasarkan jenis UMKM kuliner
    """
    price_levels = {
        'restaurant': [10, 30, 40, 20],    # [0, 1, 2, 3] percentages
        'cafe': [15, 60, 25, 0],
        'food_court': [40, 60, 0, 0],
        'fast_food': [60, 40, 0, 0],
        'bar': [0, 20, 60, 20],
        'ice_cream': [30, 60, 10, 0],
        'juice_bar': [40, 50, 10, 0],
        'bakery': [20, 70, 10, 0],
        'confectionery': [15, 70, 15, 0],
        'coffee': [10, 70, 20, 0],
        'tea': [25, 65, 10, 0],
        'pastry': [20, 60, 20, 0],
        'chocolate': [10, 40, 40, 10],
        'dairy': [50, 40, 10, 0],
    }
    
    # Default distribution
    distribution = price_levels.get(place_type, [25, 50, 25, 0])
    
    # Weighted random choice
    rand_num = random.randint(1, 100)
    cumulative = 0
    
    for level, percentage in enumerate(distribution):
        cumulative += percentage
        if rand_num <= cumulative:
            return level
    
    return 1  # Default

def get_area_name(lat, lng):
    """
    Tentukan nama area berdasarkan koordinat untuk alamat yang lebih spesifik
    """
    # Definisi area berdasarkan koordinat
    if lng >= 119.50:
        if lat >= -5.12:
            return "Tamalanrea"
        elif lat >= -5.18:
            return "BTP/Sudiang"
        else:
            return "Antang"
    elif lng >= 119.45:
        if lat >= -5.12:
            return "Biringkanaya"
        elif lat >= -5.18:
            return "Daya"
        else:
            return "Manggala"
    elif lng >= 119.40:
        if lat >= -5.12:
            return "Tallo"
        elif lat >= -5.18:
            return "Rappocini"
        else:
            return "Panakkukang"
    else:
        if lat >= -5.12:
            return "Makassar Utara"
        elif lat >= -5.18:
            return "Makassar Tengah"
        else:
            return "Makassar Selatan"

def process_osm_element(element):
    """
    Proses setiap element dari OSM dengan alamat yang lebih spesifik
    """
    # Skip jika tidak ada tags
    if 'tags' not in element:
        return None
    
    tags = element['tags']
    
    # Skip jika tidak ada nama
    if 'name' not in tags:
        return None
    
    # Ambil koordinat
    if element['type'] == 'node':
        lat = element['lat']
        lon = element['lon']
    elif element['type'] == 'way' and 'center' in element:
        lat = element['center']['lat']
        lon = element['center']['lon']
    else:
        return None
    
    # Extract info
    name = tags['name']
    amenity = tags.get('amenity', '')
    shop = tags.get('shop', '')
    cuisine = tags.get('cuisine', 'tidak diketahui')
    
    # Tentukan jenis tempat
    place_type = amenity if amenity else shop
    
    # Generate data
    rating = generate_rating_by_type(amenity, shop)
    user_ratings_total = generate_user_ratings(rating, place_type)
    price_level = generate_price_level(place_type)
    
    # Format alamat dengan area yang lebih spesifik
    address_parts = []
    if 'addr:street' in tags:
        address_parts.append(tags['addr:street'])
    if 'addr:housenumber' in tags:
        address_parts.append(tags['addr:housenumber'])
    
    # Tentukan area berdasarkan koordinat
    area_name = get_area_name(lat, lon)
    
    if address_parts:
        address = ', '.join(address_parts) + f', {area_name}, Makassar'
    else:
        address = f'{area_name}, Makassar, South Sulawesi'
    
    return {
        'Nama': name,
        'Alamat': address,
        'Rating': rating,
        'User_Ratings_Total': user_ratings_total,
        'Price_Level': price_level,
        'Place_ID': f"osm_{element['id']}",
        'Lokasi': f"{{'lat': {lat}, 'lng': {lon}}}"
    }

def save_data_to_csv(data, filename):
    """
    Simpan data ke file CSV
    """
    print(f"Menyimpan {len(data)} tempat kuliner ke {filename}...")
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Nama', 'Alamat', 'Rating', 'User_Ratings_Total', 
                         'Price_Level', 'Place_ID', 'Lokasi']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Tulis header
            writer.writeheader()
            
            # Tulis data
            for row in data:
                writer.writerow(row)
        
        print(f"Data berhasil disimpan ke {filename}")
        return True
        
    except Exception as e:
        print(f"Error menyimpan file: {e}")
        return False

def print_summary(data):
    """
    Tampilkan ringkasan data dengan breakdown per area
    """
    print("\n" + "="*60)
    print("RINGKASAN DATA KULINER MAKASSAR - EXTENDED COVERAGE")
    print("="*60)
    
    print(f"Total tempat kuliner: {len(data)}")
    
    # Hitung distribusi per area
    area_counts = {}
    for item in data:
        alamat = item['Alamat']
        # Extract area name dari alamat
        if 'Tamalanrea' in alamat:
            area = 'Tamalanrea/UNHAS'
        elif 'BTP' in alamat or 'Sudiang' in alamat:
            area = 'BTP/Sudiang'
        elif 'Daya' in alamat:
            area = 'Daya'
        elif 'Antang' in alamat:
            area = 'Antang'
        elif 'Biringkanaya' in alamat:
            area = 'Biringkanaya'
        elif 'Manggala' in alamat:
            area = 'Manggala'
        elif 'Panakkukang' in alamat:
            area = 'Panakkukang'
        elif 'Rappocini' in alamat:
            area = 'Rappocini'
        else:
            area = 'Pusat Kota'
        
        area_counts[area] = area_counts.get(area, 0) + 1
    
    print(f"\nDistribusi per Area:")
    for area, count in sorted(area_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {area}: {count} tempat")
    
    # Hitung distribusi rating
    ratings = [item['Rating'] for item in data]
    print(f"\nStatistik Rating:")
    print(f"  Tertinggi: {max(ratings)}")
    print(f"  Terendah: {min(ratings)}")
    print(f"  Rata-rata: {sum(ratings)/len(ratings):.1f}")
    
    # Hitung distribusi user ratings
    user_ratings = [item['User_Ratings_Total'] for item in data]
    print(f"\nStatistik User Ratings:")
    print(f"  Tertinggi: {max(user_ratings)}")
    print(f"  Terendah: {min(user_ratings)}")
    print(f"  Rata-rata: {sum(user_ratings)/len(user_ratings):.0f}")
    
    # Distribusi untuk warna marker
    merah = len([x for x in user_ratings if x >= 500])
    orange = len([x for x in user_ratings if 100 <= x < 500])
    biru = len([x for x in user_ratings if x < 100])
    
    print(f"\nDistribusi Warna Marker:")
    print(f"  Merah (>= 500 reviews): {merah} tempat")
    print(f"  Orange (100-499 reviews): {orange} tempat")
    print(f"  Biru (< 100 reviews): {biru} tempat")
    
    # Distribusi price level
    price_counts = [0, 0, 0, 0]
    for item in data:
        price_counts[item['Price_Level']] += 1
    
    print(f"\nDistribusi Price Level:")
    price_labels = ['Murah (0)', 'Terjangkau (1)', 'Sedang (2)', 'Mahal (3)']
    for i, count in enumerate(price_counts):
        print(f"  {price_labels[i]}: {count} tempat")

def main():
    """
    Fungsi utama dengan coverage area yang diperluas - fokus UMKM kuliner
    """
    print("PENGUMPULAN DATA UMKM KULINER MAKASSAR - EXTENDED COVERAGE")
    print("="*65)
    print("Fokus pengambilan data:")
    print("- UMKM Kuliner: Restaurant, Cafe, Food Court, Fast Food")
    print("- Minuman: Bar, Juice Bar, Coffee Shop, Tea Shop")
    print("- Makanan Khusus: Bakery, Confectionery, Pastry, Ice Cream")
    print("- Produk Olahan: Chocolate Shop, Dairy Shop")
    print("- TIDAK termasuk: Pub, Convenience Store, Supermarket, Grocery")
    print("="*65)
    
    # Set random seed untuk hasil yang konsisten
    random.seed(42)
    
    # 1. Query data dari OSM dengan area yang diperluas - khusus kuliner
    elements = query_osm_makassar()
    
    if not elements:
        print("Tidak ada data UMKM kuliner yang ditemukan dari OSM")
        return
    
    # 2. Proses setiap element
    processed_data = []
    print("Memproses data UMKM kuliner...")
    
    for element in elements:
        processed = process_osm_element(element)
        if processed:
            processed_data.append(processed)
    
    if not processed_data:
        print("Tidak ada data UMKM kuliner yang valid untuk diproses")
        return
    
    print(f"Berhasil memproses {len(processed_data)} UMKM kuliner")
    
    # 3. Simpan ke CSV
    output_file = "C:/Users/ASUS/OneDrive/Documents/Skripsi_Megi/skripsi_baru/kuliner_makassar_osm.csv"
    success = save_data_to_csv(processed_data, output_file)
    
    if success:
        # 4. Tampilkan ringkasan
        print_summary(processed_data)
        
        print(f"\nFile output: {output_file}")
        print("Data UMKM kuliner siap untuk digunakan dalam visualisasi hotspot!")
        print("Coverage area sudah diperluas untuk mencakup seluruh Kota Makassar")
        print("Data fokus pada UMKM kuliner, tidak termasuk retail umum")
    
if __name__ == "__main__":
    main()