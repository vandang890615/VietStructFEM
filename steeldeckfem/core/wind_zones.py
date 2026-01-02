# -*- coding: utf-8 -*-
"""
Vietnam Wind Zone Database
Based on TCVN 2737:2023 - Wind loads for structures
"""

# Wind zone data for major cities and provinces in Vietnam
WIND_ZONES = {
    # Vùng I (Inland) - Wo = 95 kg/m²
    "Vùng I - Nội địa": {
        "zone": "I",
        "Wo": 95,  # kg/m²
        "description": "Vùng nội địa, cách biển >30km",
        "cities": ["Hà Nội", "Hòa Bình", "Cao Bằng", "Lạng Sơn", "Yên Bái"]
    },
    
    # Vùng II (Near coast) - Wo = 110 kg/m²
    "Vùng II - Ven biển": {
        "zone": "II",
        "Wo": 110,
        "description": "Vùng ven biển, cách biển 5-30km",
        "cities": ["Hải Phòng", "Nam Định", "Ninh Bình", "Thanh Hóa", "Nghệ An"]
    },
    
    # Vùng IIA (Coastal) - Wo = 125 kg/m²
    "Vùng IIA - Sát biển": {
        "zone": "IIA",
        "Wo": 125,
        "description": "Vùng sát biển, cách biển <5km",
        "cities": ["Quảng Ninh", "Huế", "Đà Nẵng", "Quy Nhơn", "Nha Trang"]
    },
    
    # Vùng IIIA (High wind - North coast) - Wo = 145 kg/m²
    "Vùng IIIA - Bão miền Bắc": {
        "zone": "IIIA",
        "Wo": 145,
        "description": "Vùng bão miền Bắc, các tỉnh ven biển phía Bắc",
        "cities": ["Móng Cái", "Cửa Ông", "Tiên Yên", "Vân Đồn"]
    },
    
    # Vùng IIIB (High wind - Central coast) - Wo = 155 kg/m²
    "Vùng IIIB - Bão miền Trung": {
        "zone": "IIIB",
        "Wo": 155,
        "description": "Vùng bão miền Trung, từ Quảng Bình đến Phú Yên",
        "cities": ["Quảng Bình", "Quảng Trị", "Quảng Nam", "Bình Định"]
    },
    
    # Vùng IV (High wind - South coast) - Wo = 135 kg/m²
    "Vùng IV - Bão miền Nam": {
        "zone": "IV",
        "Wo": 135,
        "description": "Vùng bão miền Nam, các tỉnh Nam Bộ ven biển",
        "cities": ["TP Hồ Chí Minh", "Vũng Tàu", "Bình Thuận", "Kiên Giang"]
    },
    
    # Vùng đặc biệt (Islands) - Wo = 165 kg/m²
    "Vùng Đảo - Hoàng Sa, Trường Sa": {
        "zone": "ISLAND",
        "Wo": 165,
        "description": "Các đảo xa bờ, Hoàng Sa, Trường Sa",
        "cities": ["Hoàng Sa", "Trường Sa", "Phú Quý", "Côn Đảo"]
    }
}

# Specific cities mapping
CITY_WIND_ZONES = {
    # Major cities - detailed mapping
    "Hà Nội": {"zone": "I", "Wo": 95},
    "TP Hồ Chí Minh": {"zone": "IV", "Wo": 135},
    "Đà Nẵng": {"zone": "IIA", "Wo": 125},
    "Hải Phòng": {"zone": "II", "Wo": 110},
    "Cần Thơ": {"zone": "I", "Wo": 95},
    
    # Northern region
    "Hạ Long": {"zone": "IIIA", "Wo": 145},
    "Móng Cái": {"zone": "IIIA", "Wo": 145},
    "Lạng Sơn": {"zone": "I", "Wo": 95},
    "Cao Bằng": {"zone": "I", "Wo": 95},
    "Lào Cai": {"zone": "I", "Wo": 95},
    
    # Central region
    "Vinh": {"zone": "II", "Wo": 110},
    "Huế": {"zone": "IIA", "Wo": 125},
    "Quảng Ngãi": {"zone": "IIIB", "Wo": 155},
    "Quy Nhơn": {"zone": "IIA", "Wo": 125},
    "Nha Trang": {"zone": "IIA", "Wo": 125},
    "Phan Thiết": {"zone": "IV", "Wo": 135},
    
    # Southern region
    "Vũng Tàu": {"zone": "IV", "Wo": 135},
    "Long Xuyên": {"zone": "I", "Wo": 95},
    "Rạch Giá": {"zone": "IV", "Wo": 135},
    "Cà Mau": {"zone": "IV", "Wo": 135},
    
    # Islands
    "Phú Quốc": {"zone": "IV", "Wo": 135},
    "Côn Đảo": {"zone": "ISLAND", "Wo": 165},
    "Phú Quý": {"zone": "ISLAND", "Wo": 165}
}


def get_wind_pressure(location_name: str) -> dict:
    """
    Get wind pressure for a specific location
    
    Args:
        location_name: City or zone name
        
    Returns:
        Dictionary with zone info and wind pressure
    """
    # Try exact city match first
    if location_name in CITY_WIND_ZONES:
        return CITY_WIND_ZONES[location_name]
    
    # Try zone match
    for zone_name, zone_data in WIND_ZONES.items():
        if location_name in zone_name or location_name in zone_data.get('cities', []):
            return {
                "zone": zone_data["zone"],
                "Wo": zone_data["Wo"]
            }
    
    # Default to Zone I if not found
    return {"zone": "I", "Wo": 95}


def get_all_locations():
    """Get sorted list of all available locations"""
    locations = []
    
    # Add zones
    for zone_name in WIND_ZONES.keys():
        locations.append(zone_name)
    
    # Add cities
    locations.extend(sorted(CITY_WIND_ZONES.keys()))
    
    return locations
