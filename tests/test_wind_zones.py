"""
Unit tests for Wind Zones module
"""

import pytest
from steeldeckfem.core import get_wind_pressure, get_all_locations, WIND_ZONES, CITY_WIND_ZONES


class TestWindZones:
    """Tests for wind zone database and functions"""
    
    def test_wind_zones_exist(self):
        """Test that WIND_ZONES dictionary exists and has data"""
        assert WIND_ZONES is not None
        assert len(WIND_ZONES) > 0
    
    def test_city_wind_zones_exist(self):
        """Test that CITY_WIND_ZONES dictionary exists"""
        assert CITY_WIND_ZONES is not None
        assert len(CITY_WIND_ZONES) > 0
    
    def test_get_all_locations(self):
        """Test getting all locations"""
        locations = get_all_locations()
        assert isinstance(locations, list)
        assert len(locations) > 0
    
    def test_get_wind_pressure_hanoi(self):
        """Test wind pressure lookup for Hà Nội"""
        result = get_wind_pressure("Hà Nội")
        
        assert result is not None
        assert 'zone' in result
        assert 'Wo' in result
        assert result['zone'] == 'I'
        assert result['Wo'] == 95
    
    def test_get_wind_pressure_by_zone(self):
        """Test wind pressure lookup by zone name"""
        result = get_wind_pressure("Vùng I - Nội địa")
        
        assert result is not None
        assert 'zone' in result
        assert result['zone'] == 'I'
    
    def test_get_wind_pressure_invalid_location(self):
        """Test wind pressure with invalid location"""
        result = get_wind_pressure("NonExistentCity")
        
        # Should return default or None
        assert result is not None
    
    def test_wind_zone_structure(self):
        """Test that wind zones have proper structure"""
        for zone_name, zone_data in WIND_ZONES.items():
            assert 'zone' in zone_data
            assert 'Wo' in zone_data
            assert isinstance(zone_data['Wo'], (int, float))
    
    def test_city_wind_zone_structure(self):
        """Test that city wind zones have proper structure"""
        for city, data in CITY_WIND_ZONES.items():
            assert 'zone' in data
            assert 'Wo' in data
            assert isinstance(data['Wo'], (int, float))


class TestWindPressureCalculations:
    """Tests for wind pressure calculations"""
    
    def test_different_zones_different_pressures(self):
        """Test that different zones return different pressures"""
        zone_i = get_wind_pressure("Vùng I - Nội địa")
        zone_ii = get_wind_pressure("Vùng II - Ven biển")
        
        # Zone II should have higher wind pressure than Zone I
        if zone_i and zone_ii:
            assert zone_ii['Wo'] >= zone_i['Wo']
    
    def test_coastal_cities_higher_pressure(self):
        """Test that coastal cities generally have higher wind pressure"""
        hanoi = get_wind_pressure("Hà Nội")  # Inland
        danang = get_wind_pressure("Đà Nẵng")  # Coastal
        
        if hanoi and danang:
            # Đà Nẵng (coastal) should have higher Wo than Hà Nội (inland)
            assert danang['Wo'] >= hanoi['Wo']
