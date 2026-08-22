#!/usr/bin/env python3
"""
Route Service for Chennai Bike Ride-Sharing
Integrates OpenStreetMap (OSM), OSRM Road Routing, and Chennai Commuter Geo-Database
with exact door-level addresses, landmarks, metro stations, tech parks, and pincodes.
"""

import math
import requests
import json
import re
from typing import Dict, List, Optional, Tuple, Any

class RouteService:
    """Service for Chennai road geocoding, distance, time, and corridor matching"""
    
    # 70+ Curated Chennai IT Parks, Tech Hubs, SEZs, Metro Stations & Residential Commuter Areas
    CHENNAI_HUBS: Dict[str, Dict[str, Any]] = {
        # --- IT Parks, SEZs & Tech Hubs ---
        'ELCOT SEZ IT Park (Sholinganallur)': {
            'lat': 12.9062, 'lng': 80.2185, 'area': 'Sholinganallur', 'pincode': '600119',
            'address': 'ELCOT SEZ Main Road, Sholinganallur, Chennai - 600119', 'type': 'it_park'
        },
        'CKC / HCL Technologies (ELCOT SEZ)': {
            'lat': 12.9062, 'lng': 80.2185, 'area': 'Sholinganallur', 'pincode': '600119',
            'address': 'ELCOT SEZ Unit-II, SDB2, Sholinganallur - Medavakkam High Rd, Chennai - 600119', 'type': 'it_park'
        },
        'Olympia Tech Park': {
            'lat': 13.0135, 'lng': 80.2030, 'area': 'Guindy / Ekkatuthangal', 'pincode': '600032',
            'address': 'No. 1, SIDCO Industrial Estate, Guindy, Chennai - 600032', 'type': 'it_park'
        },
        'DLF IT Park / Cybercity': {
            'lat': 13.0298, 'lng': 80.1654, 'area': 'Porur / Manapakkam', 'pincode': '600089',
            'address': '1/124, Mount Poonamallee Road, Manapakkam, Porur, Chennai - 600089', 'type': 'it_park'
        },
        'Tidel Park': {
            'lat': 12.9892, 'lng': 80.2483, 'area': 'Taramani / OMR', 'pincode': '600113',
            'address': 'No. 4, Rajiv Gandhi Salai (OMR), Taramani, Chennai - 600113', 'type': 'it_park'
        },
        'Ramanujan IT City': {
            'lat': 12.9868, 'lng': 80.2447, 'area': 'Taramani / OMR', 'pincode': '600113',
            'address': 'TRIL Infopark, Rajiv Gandhi Salai, Taramani, Chennai - 600113', 'type': 'it_park'
        },
        'Ascendas IT Park (International Tech Park)': {
            'lat': 12.9880, 'lng': 80.2460, 'area': 'Taramani', 'pincode': '600113',
            'address': 'CSIR Road, Taramani, Chennai - 600113', 'type': 'it_park'
        },
        'Siruseri SIPCOT IT Park': {
            'lat': 12.8252, 'lng': 80.2185, 'area': 'Siruseri / OMR', 'pincode': '603103',
            'address': 'SIPCOT IT Park, Siruseri, OMR, Chennai - 603103', 'type': 'it_park'
        },
        'TCS Siruseri Signature Tower': {
            'lat': 12.8280, 'lng': 80.2210, 'area': 'Siruseri / OMR', 'pincode': '603103',
            'address': 'SIPCOT IT Park Phase 2, Siruseri, Chennai - 603103', 'type': 'it_park'
        },
        'One Indiabulls Park': {
            'lat': 13.1028, 'lng': 80.1678, 'area': 'Ambattur Industrial Estate', 'pincode': '600058',
            'address': 'Ambattur Industrial Estate 3rd Main Rd, Chennai - 600058', 'type': 'it_park'
        },
        'Ambattur Industrial Estate': {
            'lat': 13.0982, 'lng': 80.1620, 'area': 'Ambattur', 'pincode': '600058',
            'address': 'Sidco Industrial Estate, Ambattur, Chennai - 600058', 'type': 'industrial'
        },
        'Prince Info City / Suntech': {
            'lat': 12.9620, 'lng': 80.2450, 'area': 'Kandanchavadi', 'pincode': '600096',
            'address': 'Rajiv Gandhi Salai (OMR), Kandanchavadi, Chennai - 600096', 'type': 'it_park'
        },
        'RMZ Millenia Business Park': {
            'lat': 12.9698, 'lng': 80.2465, 'area': 'Perungudi / OMR', 'pincode': '600096',
            'address': 'No. 143, Dr. MGR Road, Kandanchavadi, Perungudi, Chennai - 600096', 'type': 'it_park'
        },
        'World Trade Center Chennai (WTC)': {
            'lat': 12.9645, 'lng': 80.2460, 'area': 'Perungudi / OMR', 'pincode': '600096',
            'address': 'Rajiv Gandhi Salai, Perungudi, Chennai - 600096', 'type': 'it_park'
        },
        'Commerzone Porur': {
            'lat': 13.0320, 'lng': 80.1580, 'area': 'Porur', 'pincode': '600116',
            'address': 'Mount Poonamallee High Rd, Porur, Chennai - 600116', 'type': 'it_park'
        },
        'ASV Suntech Park': {
            'lat': 12.9345, 'lng': 80.2312, 'area': 'Thoraipakkam', 'pincode': '600097',
            'address': 'No. 148, Rajiv Gandhi Salai, Thoraipakkam, Chennai - 600097', 'type': 'it_park'
        },
        'MEPZ Tambaram (Special Economic Zone)': {
            'lat': 12.9380, 'lng': 80.1280, 'area': 'Tambaram Sanatorium', 'pincode': '600045',
            'address': 'GST Road, Tambaram Sanatorium, Chennai - 600045', 'type': 'it_park'
        },
        'Mahindra World City': {
            'lat': 12.7380, 'lng': 80.0070, 'area': 'Chengalpattu / GST Road', 'pincode': '603002',
            'address': 'GST Road, Paranur, Chengalpattu - 603002', 'type': 'it_park'
        },
        
        # --- Major Commuter Neighborhoods & Junctions ---
        'Maduravoyal': {
            'lat': 13.0645, 'lng': 80.1658, 'area': 'West Chennai', 'pincode': '600095',
            'address': 'Poonamallee High Road / PH Road, Maduravoyal, Chennai - 600095', 'type': 'hub'
        },
        'Maduravoyal Grade Separator / Flyover': {
            'lat': 13.0606, 'lng': 80.1660, 'area': 'Maduravoyal', 'pincode': '600095',
            'address': 'NH4 - Chennai Bypass Junction, Maduravoyal, Chennai - 600095', 'type': 'junction'
        },
        'Vadapalani (100ft Road / Arcot Rd)': {
            'lat': 13.0500, 'lng': 80.2121, 'area': 'Central Chennai', 'pincode': '600026',
            'address': '100 Feet Road / Arcot Road, Vadapalani, Chennai - 600026', 'type': 'hub'
        },
        'Vadapalani Metro Station / Forum Vijaya Mall': {
            'lat': 13.0500, 'lng': 80.2121, 'area': 'Vadapalani', 'pincode': '600026',
            'address': 'Arcot Road, Nexus Vijaya Mall, Vadapalani, Chennai - 600026', 'type': 'transit'
        },
        'Koyambedu CMBT (Bus Terminus)': {
            'lat': 13.0694, 'lng': 80.1948, 'area': 'Koyambedu', 'pincode': '600107',
            'address': 'Chennai Mofussil Bus Terminus (CMBT), Koyambedu, Chennai - 600107', 'type': 'transit'
        },
        'Tambaram (GST Road / Railway Station)': {
            'lat': 12.9249, 'lng': 80.1260, 'area': 'South Chennai', 'pincode': '600045',
            'address': 'Grand Southern Trunk (GST) Road, Tambaram, Chennai - 600045', 'type': 'hub'
        },
        'Chromepet (GST Road / MIT)': {
            'lat': 12.9516, 'lng': 80.1462, 'area': 'South Chennai', 'pincode': '600044',
            'address': 'GST Road, Chromepet, Chennai - 600044', 'type': 'residential'
        },
        'Pallavaram': {
            'lat': 12.9675, 'lng': 80.1491, 'area': 'South Chennai', 'pincode': '600043',
            'address': 'GST Road / 200ft Radial Rd, Pallavaram, Chennai - 600043', 'type': 'residential'
        },
        'Perungalathur Junction': {
            'lat': 12.9036, 'lng': 80.0890, 'area': 'South Chennai', 'pincode': '600063',
            'address': 'GST Road, Perungalathur Bus Stand, Chennai - 600063', 'type': 'transit'
        },
        'Sholinganallur Junction (OMR)': {
            'lat': 12.9006, 'lng': 80.2279, 'area': 'OMR', 'pincode': '600119',
            'address': 'OMR - Medavakkam Link Road Junction, Sholinganallur, Chennai - 600119', 'type': 'hub'
        },
        'Thoraipakkam (200ft Radial Rd Junction)': {
            'lat': 12.9370, 'lng': 80.2340, 'area': 'OMR', 'pincode': '600097',
            'address': 'Rajiv Gandhi Salai (OMR) Toll Plaza, Thoraipakkam, Chennai - 600097', 'type': 'hub'
        },
        'Perungudi Toll Plaza (OMR)': {
            'lat': 12.9690, 'lng': 80.2450, 'area': 'OMR', 'pincode': '600096',
            'address': 'Rajiv Gandhi Salai, Perungudi, Chennai - 600096', 'type': 'hub'
        },
        'Kandanchavadi Signal (OMR)': {
            'lat': 12.9620, 'lng': 80.2450, 'area': 'OMR', 'pincode': '600096',
            'address': 'OMR, Kandanchavadi, Chennai - 600096', 'type': 'hub'
        },
        'Navalur (Vivira Mall / OMR)': {
            'lat': 12.8465, 'lng': 80.2255, 'area': 'OMR', 'pincode': '603103',
            'address': 'Rajiv Gandhi Salai, Navalur, OMR, Chennai - 603103', 'type': 'residential'
        },
        'Velachery Vijaya Nagar': {
            'lat': 12.9750, 'lng': 80.2200, 'area': 'South Chennai', 'pincode': '600042',
            'address': 'Vijaya Nagar Bus Terminus, Velachery Main Rd, Chennai - 600042', 'type': 'hub'
        },
        'Guindy Kathipara Junction': {
            'lat': 13.0067, 'lng': 80.2070, 'area': 'South Chennai', 'pincode': '600032',
            'address': 'Kathipara Cloverleaf Flyover, Guindy, Chennai - 600032', 'type': 'transit'
        },
        'Alandur Metro Station': {
            'lat': 13.0030, 'lng': 80.2010, 'area': 'Alandur', 'pincode': '600016',
            'address': 'GST Road / Inner Ring Rd, Alandur, Chennai - 600016', 'type': 'transit'
        },
        'Ekkatuthangal Metro Station': {
            'lat': 13.0180, 'lng': 80.2040, 'area': 'Ekkatuthangal', 'pincode': '600032',
            'address': 'Jawaharlal Nehru Road, Ekkatuthangal, Chennai - 600032', 'type': 'transit'
        },
        'Ashok Pillar (100ft Road)': {
            'lat': 13.0360, 'lng': 80.2140, 'area': 'Ashok Nagar', 'pincode': '600083',
            'address': '100 Feet Road / 1st Avenue, Ashok Nagar, Chennai - 600083', 'type': 'residential'
        },
        'KK Nagar (Munusamy Salai)': {
            'lat': 13.0380, 'lng': 80.1980, 'area': 'KK Nagar', 'pincode': '600078',
            'address': 'Munusamy Salai, KK Nagar Bus Terminus, Chennai - 600078', 'type': 'residential'
        },
        'Adyar (L.B. Road / Signal)': {
            'lat': 13.0067, 'lng': 80.2570, 'area': 'South Chennai', 'pincode': '600020',
            'address': 'Lattice Bridge (LB) Road, Adyar, Chennai - 600020', 'type': 'hub'
        },
        'Thiruvanmiyur Signal (ECR / LB Road)': {
            'lat': 12.9830, 'lng': 80.2594, 'area': 'Thiruvanmiyur', 'pincode': '600041',
            'address': 'East Coast Road / LB Road Junction, Thiruvanmiyur, Chennai - 600041', 'type': 'hub'
        },
        'Porur Roundtana': {
            'lat': 13.0382, 'lng': 80.1560, 'area': 'West Chennai', 'pincode': '600116',
            'address': 'Arcot Road / Mount Poonamallee Junction, Porur, Chennai - 600116', 'type': 'hub'
        },
        'Poonamallee Trunk Road': {
            'lat': 13.0489, 'lng': 80.1118, 'area': 'Poonamallee', 'pincode': '600056',
            'address': 'Trunk Road, Poonamallee Bus Stand, Chennai - 600056', 'type': 'hub'
        },
        'Iyyappanthangal Bus Depot': {
            'lat': 13.0395, 'lng': 80.1380, 'area': 'West Chennai', 'pincode': '600056',
            'address': 'Mount Poonamallee Road, Iyyappanthangal, Chennai - 600056', 'type': 'residential'
        },
        'Anna Nagar Roundtana / 2nd Avenue': {
            'lat': 13.0850, 'lng': 80.2101, 'area': 'Anna Nagar', 'pincode': '600040',
            'address': '2nd Avenue / 3rd Avenue, Anna Nagar East, Chennai - 600040', 'type': 'residential'
        },
        'Mogappair West / East': {
            'lat': 13.0845, 'lng': 80.1740, 'area': 'North-West Chennai', 'pincode': '600037',
            'address': 'Ambattur Industrial Estate Extension, Mogappair, Chennai - 600037', 'type': 'residential'
        },
        'T. Nagar (Panagal Park / Pondy Bazaar)': {
            'lat': 13.0418, 'lng': 80.2341, 'area': 'Central Chennai', 'pincode': '600017',
            'address': 'Sir Thyagaraya Road, Pondy Bazaar, T. Nagar, Chennai - 600017', 'type': 'commercial'
        },
        'Saidapet (Anna Salai)': {
            'lat': 13.0210, 'lng': 80.2230, 'area': 'Central Chennai', 'pincode': '600015',
            'address': 'Anna Salai (Mount Road), Saidapet, Chennai - 600015', 'type': 'hub'
        },
        'Nungambakkam High Road': {
            'lat': 13.0569, 'lng': 80.2425, 'area': 'Central Chennai', 'pincode': '600034',
            'address': 'Uthamar Gandhi Salai, Nungambakkam, Chennai - 600034', 'type': 'commercial'
        },
        'Chennai Central Railway Station': {
            'lat': 13.0827, 'lng': 80.2707, 'area': 'Central Chennai', 'pincode': '600003',
            'address': 'Poonamallee High Road, Park Town, Chennai - 600003', 'type': 'transit'
        },
        'Chennai Egmore Railway Station': {
            'lat': 13.0784, 'lng': 80.2608, 'area': 'Central Chennai', 'pincode': '600008',
            'address': 'Gandhi Irwin Road, Egmore, Chennai - 600008', 'type': 'transit'
        },
        'Medavakkam Koot Road': {
            'lat': 12.9180, 'lng': 80.1920, 'area': 'South Chennai', 'pincode': '600100',
            'address': 'Tambaram - Velachery Main Road, Medavakkam, Chennai - 600100', 'type': 'hub'
        },
        'Keelkattalai Junction': {
            'lat': 12.9550, 'lng': 80.1870, 'area': 'South Chennai', 'pincode': '600117',
            'address': 'Radial Road / Medavakkam Main Rd, Keelkattalai, Chennai - 600117', 'type': 'residential'
        },
        'Madipakkam Koot Road': {
            'lat': 12.9640, 'lng': 80.1980, 'area': 'South Chennai', 'pincode': '600091',
            'address': 'Bazaar Road, Madipakkam, Chennai - 600091', 'type': 'residential'
        },
        'Nanganallur (1st Main Road)': {
            'lat': 12.9840, 'lng': 80.1932, 'area': 'Nanganallur', 'pincode': '600061',
            'address': '1st Main Road, Nanganallur, Chennai - 600061', 'type': 'residential'
        },
        'Ambattur OT (Old Town)': {
            'lat': 13.1143, 'lng': 80.1548, 'area': 'North Chennai', 'pincode': '600053',
            'address': 'CTH Road, Ambattur OT, Chennai - 600053', 'type': 'hub'
        },
        'Avadi (Bus Stand / Railway Station)': {
            'lat': 13.1147, 'lng': 80.1006, 'area': 'North Chennai', 'pincode': '600054',
            'address': 'CTH Road, Avadi, Chennai - 600054', 'type': 'hub'
        },
        'Mylapore (Luz Corner / Kapaleeshwarar)': {
            'lat': 13.0368, 'lng': 80.2676, 'area': 'Mylapore', 'pincode': '600004',
            'address': 'Royapettah High Road / Luz Church Rd, Mylapore, Chennai - 600004', 'type': 'cultural'
        },
        'Perambur (Paper Mills Road)': {
            'lat': 13.1102, 'lng': 80.2426, 'area': 'Perambur', 'pincode': '600011',
            'address': 'Paper Mills Road, Perambur, Chennai - 600011', 'type': 'transit'
        },
        'Vandalur (GST Road / Zoo)': {
            'lat': 12.8900, 'lng': 80.0810, 'area': 'South Suburb', 'pincode': '600048',
            'address': 'GST Road, Vandalur, Chennai - 600048', 'type': 'transit'
        },
        'Guduvanchery (GST Road)': {
            'lat': 12.8440, 'lng': 80.0610, 'area': 'South Suburb', 'pincode': '603202',
            'address': 'GST Road, Guduvanchery, Chengalpattu Dist - 603202', 'type': 'residential'
        },
        'Kelambakkam (OMR Junction)': {
            'lat': 12.7870, 'lng': 80.2220, 'area': 'OMR Suburb', 'pincode': '603103',
            'address': 'OMR - Vandalur Road Junction, Kelambakkam - 603103', 'type': 'hub'
        },
        'Padur (Hindustan University)': {
            'lat': 12.8050, 'lng': 80.2250, 'area': 'Padur / OMR', 'pincode': '603103',
            'address': 'Hindustan University, OMR, Padur - 603103', 'type': 'residential'
        },
        'Egattur (Marina Mall)': {
            'lat': 12.8290, 'lng': 80.2270, 'area': 'OMR', 'pincode': '603103',
            'address': 'The Marina Mall, OMR, Egattur, Navalur, Chennai - 603103', 'type': 'commercial'
        },
        'Semmancheri (Sathyabama University)': {
            'lat': 12.8710, 'lng': 80.2210, 'area': 'OMR', 'pincode': '600119',
            'address': 'Rajiv Gandhi Salai, Semmancheri, Chennai - 600119', 'type': 'hub'
        },
        'Karapakkam (OMR)': {
            'lat': 12.9180, 'lng': 80.2310, 'area': 'OMR', 'pincode': '600097',
            'address': 'OMR, Karapakkam, Chennai - 600097', 'type': 'hub'
        },
        'Chennai International Airport (MAA)': {
            'lat': 12.9800, 'lng': 80.1630, 'area': 'Meenambakkam', 'pincode': '600027',
            'address': 'GST Road, Meenambakkam, Chennai - 600027', 'type': 'transit'
        }
    }
    
    @classmethod
    def get_coordinates(cls, location_name: str) -> Optional[Tuple[float, float]]:
        """
        Get (lat, lng) for a location name.
        Checks pre-seeded database first, then tries fuzzy match, then Nominatim OSM.
        """
        if not location_name:
            return None
        
        name_clean = location_name.strip()
        name_lower = name_clean.lower()
        
        # 0. Check if raw coordinates passed (e.g. '13.0500,80.2121' or 'Chennai (13.0500, 80.2121)')
        coord_match = re.search(r'([0-9]{1,2}\.[0-9]+)\s*,\s*([0-9]{1,3}\.[0-9]+)', name_clean)
        if coord_match:
            try:
                lat = float(coord_match.group(1))
                lng = float(coord_match.group(2))
                if 12.0 <= lat <= 14.0 and 79.0 <= lng <= 81.0:
                    return (lat, lng)
            except Exception:
                pass
        
        # 1. Exact match in pre-seeded hubs
        for hub_name, data in cls.CHENNAI_HUBS.items():
            if hub_name.lower() == name_lower:
                return (data['lat'], data['lng'])
        
        # 2. Substring match in pre-seeded hubs
        for hub_name, data in cls.CHENNAI_HUBS.items():
            if name_lower in hub_name.lower() or hub_name.lower() in name_lower:
                return (data['lat'], data['lng'])
            if data.get('area', '').lower() in name_lower or name_lower in data.get('area', '').lower():
                return (data['lat'], data['lng'])
            if data.get('address', '').lower() in name_lower or name_lower in data.get('address', '').lower():
                return (data['lat'], data['lng'])
            if data.get('pincode', '') and data.get('pincode', '') in name_clean:
                return (data['lat'], data['lng'])
        
        # 3. Live Nominatim OSM Geocoding (bounded to Chennai)
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': f"{name_clean}, Chennai, Tamil Nadu, India",
                'format': 'json',
                'limit': 1,
                'countrycodes': 'in',
                'viewbox': '79.8,13.4,80.4,12.7'
            }
            headers = {'User-Agent': 'ChennaiSmartRideMatcher/2.0 (contact@smartride.in)'}
            response = requests.get(url, params=params, headers=headers, timeout=4)
            if response.status_code == 200:
                results = response.json()
                if results and len(results) > 0:
                    lat = float(results[0]['lat'])
                    lng = float(results[0]['lon'])
                    # Cache in memory
                    cls.CHENNAI_HUBS[name_clean] = {
                        'lat': lat,
                        'lng': lng,
                        'area': 'Chennai',
                        'pincode': '',
                        'address': results[0].get('display_name', name_clean),
                        'type': 'geocoded'
                    }
                    return (lat, lng)
        except Exception as e:
            print(f"[WARN] Geocoding request failed for {name_clean}: {e}")
        
        # Default fallback to Chennai Central coordinates
        return (13.0827, 80.2707)

    @classmethod
    def reverse_geocode(cls, lat: float, lng: float) -> Dict[str, Any]:
        """
        Reverse geocode GPS coordinates to exact Chennai street address, locality and pincode.
        """
        # 1. First check if within 400m of any pre-seeded Chennai hub
        closest_hub = None
        min_d = 999.0
        for name, data in cls.CHENNAI_HUBS.items():
            d = cls._haversine(lat, lng, data['lat'], data['lng'])
            if d < min_d:
                min_d = d
                closest_hub = (name, data)
                
        if closest_hub and min_d <= 0.4:
            hub_name, hub_data = closest_hub
            return {
                'success': True,
                'name': hub_name,
                'address': hub_data.get('address', f"{hub_name}, Chennai"),
                'pincode': hub_data.get('pincode', ''),
                'lat': lat,
                'lng': lng,
                'area': hub_data.get('area', 'Chennai')
            }
            
        # 2. Query Nominatim reverse API with server-side User-Agent
        try:
            url = f"https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': lat,
                'lon': lng,
                'format': 'json',
                'addressdetails': 1
            }
            headers = {'User-Agent': 'ChennaiSmartRideMatcher/2.0 (contact@smartride.in)'}
            res = requests.get(url, params=params, headers=headers, timeout=4)
            if res.status_code == 200:
                data = res.json()
                addr = data.get('address', {})
                display_name = data.get('display_name', '')
                postcode = addr.get('postcode', '')
                
                title = (
                    addr.get('building') or
                    addr.get('amenity') or
                    addr.get('office') or
                    addr.get('road') or
                    addr.get('suburb') or
                    addr.get('neighbourhood') or
                    'Chennai'
                )
                
                # Format clean address
                parts = []
                if addr.get('house_number'):
                    parts.append(f"#{addr['house_number']}")
                if addr.get('road'):
                    parts.append(addr['road'])
                if addr.get('suburb') or addr.get('neighbourhood'):
                    parts.append(addr.get('suburb') or addr.get('neighbourhood'))
                parts.append('Chennai')
                if postcode:
                    parts.append(f"- {postcode}")
                    
                clean_address = ", ".join(parts) if parts else display_name
                
                # Cache in memory
                display_title = f"{title}, {addr.get('suburb', 'Chennai')}" if addr.get('suburb') and title != addr.get('suburb') else title
                cls.CHENNAI_HUBS[display_title] = {
                    'lat': lat,
                    'lng': lng,
                    'area': addr.get('suburb') or 'Chennai',
                    'pincode': postcode,
                    'address': clean_address,
                    'type': 'gps'
                }
                
                return {
                    'success': True,
                    'name': display_title,
                    'address': clean_address,
                    'pincode': postcode,
                    'lat': lat,
                    'lng': lng,
                    'area': addr.get('suburb') or 'Chennai'
                }
        except Exception as e:
            print(f"[WARN] Reverse geocoding failed: {e}")
            
        # Fallback to closest known hub
        if closest_hub:
            hub_name, hub_data = closest_hub
            return {
                'success': True,
                'name': f"Near {hub_name}",
                'address': hub_data.get('address', f"Near {hub_name}, Chennai"),
                'pincode': hub_data.get('pincode', ''),
                'lat': lat,
                'lng': lng,
                'area': hub_data.get('area', 'Chennai')
            }
            
        return {
            'success': True,
            'name': f"Chennai ({lat:.4f}, {lng:.4f})",
            'address': f"Chennai Coordinates ({lat:.4f}, {lng:.4f})",
            'pincode': '600001',
            'lat': lat,
            'lng': lng,
            'area': 'Chennai'
        }

    @classmethod
    def get_locations_list(cls, query: str = '') -> List[Dict[str, Any]]:
        """
        Return list of Chennai locations matching query for autocomplete with exact
        door numbers, roads, tech park buildings, suburbs, and 6-digit pincodes.
        """
        results = []
        q = query.strip().lower()
        
        # 1. Search in curated Chennai Hubs
        for name, data in cls.CHENNAI_HUBS.items():
            match = False
            if not q:
                match = True
            elif q in name.lower():
                match = True
            elif q in data.get('area', '').lower():
                match = True
            elif q in data.get('address', '').lower():
                match = True
            elif data.get('pincode', '') and q in data.get('pincode', ''):
                match = True
            elif q in data.get('type', '').lower():
                match = True
                
            if match:
                results.append({
                    'name': name,
                    'lat': data['lat'],
                    'lng': data['lng'],
                    'area': data.get('area', 'Chennai'),
                    'pincode': data.get('pincode', ''),
                    'address': data.get('address', f"{name}, Chennai"),
                    'type': data.get('type', 'hub')
                })
        
        # 2. If query is longer and few local matches, perform live OSM Nominatim query
        if len(q) >= 3 and len(results) < 5:
            try:
                url = "https://nominatim.openstreetmap.org/search"
                params = {
                    'q': f"{query}, Chennai",
                    'format': 'json',
                    'addressdetails': 1,
                    'limit': 5,
                    'countrycodes': 'in',
                    'viewbox': '79.8,13.4,80.4,12.7'
                }
                headers = {'User-Agent': 'ChennaiSmartRideMatcher/2.0 (contact@smartride.in)'}
                response = requests.get(url, params=params, headers=headers, timeout=3)
                if response.status_code == 200:
                    for item in response.json():
                        addr = item.get('address', {})
                        display_name = item.get('display_name', '')
                        lat = float(item.get('lat', 13.0827))
                        lng = float(item.get('lon', 80.2707))
                        postcode = addr.get('postcode', '')
                        
                        # Extract clean title
                        title = (
                            addr.get('building') or
                            addr.get('amenity') or
                            addr.get('office') or
                            addr.get('road') or
                            addr.get('suburb') or
                            item.get('name') or
                            query.title()
                        )
                        
                        # Avoid duplicates
                        if not any(r['name'].lower() == title.lower() for r in results):
                            results.append({
                                'name': title,
                                'lat': lat,
                                'lng': lng,
                                'area': addr.get('suburb') or addr.get('neighbourhood') or 'Chennai',
                                'pincode': postcode,
                                'address': display_name,
                                'type': 'location'
                            })
            except Exception as e:
                pass

        return results[:15]

    @classmethod
    def calculate_road_route(cls, from_location: str, to_location: str) -> Dict[str, Any]:
        """
        Calculate actual driving road route using OSRM API.
        Returns exact distance (km), duration (mins), and GeoJSON route coordinates polyline.
        """
        from_coords = cls.get_coordinates(from_location)
        to_coords = cls.get_coordinates(to_location)
        
        if not from_coords or not to_coords:
            return cls._generate_fallback_route(from_location, to_location, (13.0418, 80.1435), (13.0135, 80.2030))
        
        from_lat, from_lng = from_coords
        to_lat, to_lng = to_coords
        
        # OSRM Driving API URL
        osrm_url = f"https://router.project-osrm.org/route/v1/driving/{from_lng},{from_lat};{to_lng},{to_lat}?overview=full&geometries=geojson"
        
        try:
            response = requests.get(osrm_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 'Ok' and len(data.get('routes', [])) > 0:
                    route = data['routes'][0]
                    distance_km = round(route['distance'] / 1000, 1)
                    duration_mins = max(1, round(route['duration'] / 60))
                    
                    # Convert [lng, lat] to [lat, lng] for Leaflet
                    raw_coords = route['geometry']['coordinates']
                    leaflet_coords = [[coord[1], coord[0]] for coord in raw_coords]
                    
                    return {
                        'success': True,
                        'distance_km': distance_km,
                        'duration_mins': duration_mins,
                        'coordinates': leaflet_coords,
                        'from_coords': {'lat': from_lat, 'lng': from_lng},
                        'to_coords': {'lat': to_lat, 'lng': to_lng},
                        'source': 'osrm'
                    }
        except Exception as e:
            print(f"[WARN] OSRM routing failed ({from_location} -> {to_location}): {e}")
        
        # Mathematical fallback
        return cls._generate_fallback_route(from_location, to_location, from_coords, to_coords)

    @classmethod
    def _generate_fallback_route(cls, from_name: str, to_name: str, from_c: Tuple[float, float], to_c: Tuple[float, float]) -> Dict[str, Any]:
        """Generate smooth geometric road approximation when OSRM is offline"""
        lat1, lng1 = from_c
        lat2, lng2 = to_c
        
        # Haversine straight-line distance * 1.35 road factor
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        straight_km = 6371 * c
        road_km = round(straight_km * 1.35, 1)
        duration_mins = max(1, round(road_km * 2.2)) # ~25-30 km/h Chennai traffic
        
        # Generate 20 intermediate curved polyline points
        steps = 20
        coords = []
        for i in range(steps + 1):
            t = i / steps
            inter_lat = lat1 + (lat2 - lat1) * t
            inter_lng = lng1 + (lng2 - lng1) * t
            # Subtle curvature
            curve = math.sin(t * math.pi) * 0.006
            coords.append([inter_lat + curve, inter_lng + curve])
            
        return {
            'success': True,
            'distance_km': max(road_km, 1.0),
            'duration_mins': max(duration_mins, 3),
            'coordinates': coords,
            'from_coords': {'lat': lat1, 'lng': lng1},
            'to_coords': {'lat': lat2, 'lng': lng2},
            'source': 'geometric_fallback'
        }

    @classmethod
    def calculate_corridor_overlap(cls, rider_route_coords: List[List[float]], passenger_pickup: Tuple[float, float], passenger_drop: Tuple[float, float]) -> Dict[str, Any]:
        """
        Check if passenger's pickup and drop-off points fall along the rider's travel corridor.
        """
        if not rider_route_coords or len(rider_route_coords) == 0:
            return {'on_route': False, 'min_pickup_dist_km': 99.0, 'detour_mins': 99}
        
        p_lat, p_lng = passenger_pickup
        d_lat, d_lng = passenger_drop
        
        min_p_dist = min([cls._haversine(p_lat, p_lng, c[0], c[1]) for c in rider_route_coords])
        min_d_dist = min([cls._haversine(d_lat, d_lng, c[0], c[1]) for c in rider_route_coords])
        
        on_route = (min_p_dist <= 2.2) and (min_d_dist <= 2.5)
        detour_mins = max(0, round((min_p_dist + min_d_dist) * 2.0))
        
        return {
            'on_route': on_route,
            'min_pickup_dist_km': round(min_p_dist, 2),
            'min_drop_dist_km': round(min_d_dist, 2),
            'detour_mins': detour_mins
        }

    @staticmethod
    def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate straight line distance in km between two coordinates"""
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
