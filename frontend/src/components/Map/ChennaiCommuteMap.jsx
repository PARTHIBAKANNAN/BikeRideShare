import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';

// Custom SVG Markers
const createCustomIcon = (color, label = '') => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36" width="36" height="36">
      <defs>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="rgba(0,0,0,0.5)"/>
        </filter>
      </defs>
      <path fill="${color}" filter="url(#shadow)" d="M18 3C11.37 3 6 8.37 6 15c0 8.25 12 18 12 18s12-9.75 12-18c0-6.63-5.37-12-12-12z"/>
      <circle cx="18" cy="15" r="5" fill="#ffffff"/>
      <circle cx="18" cy="15" r="2.5" fill="${color}"/>
    </svg>
  `;
  return L.divIcon({
    html: svg,
    className: 'custom-leaflet-marker',
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -32],
  });
};

const createBikeIcon = () => {
  const svg = `
    <div style="background:#10b981; border:2px solid #ffffff; border-radius:50%; width:32px; height:32px; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 12px rgba(16,185,129,0.5);">
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="18.5" cy="17.5" r="3.5"/><circle cx="5.5" cy="17.5" r="3.5"/><circle cx="15" cy="5" r="1"/><path d="M12 17.5V14l-3-3 4-3 2 3h2"/>
      </svg>
    </div>
  `;
  return L.divIcon({
    html: svg,
    className: 'custom-bike-marker',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16]
  });
};

const greenIcon = createCustomIcon('#10b981'); // Start / Origin
const redIcon = createCustomIcon('#ef4444');   // Destination
const amberIcon = createCustomIcon('#f59e0b'); // Pickup Point
const bikeIcon = createBikeIcon();

// Auto-fit map viewport to polyline / points
function AutoFitBounds({ coordinates, fromCoords, toCoords }) {
  const map = useMap();
  useEffect(() => {
    if (coordinates && coordinates.length > 1) {
      const bounds = L.latLngBounds(coordinates);
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15, animate: true });
    } else if (fromCoords && toCoords) {
      const bounds = L.latLngBounds([
        [fromCoords.lat, fromCoords.lng],
        [toCoords.lat, toCoords.lng]
      ]);
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14, animate: true });
    }
  }, [coordinates, fromCoords, toCoords, map]);
  return null;
}

// Click listener for selecting on map
function MapClickHandler({ onLocationSelect }) {
  useMapEvents({
    click(e) {
      if (onLocationSelect) {
        onLocationSelect(e.latlng.lat, e.latlng.lng);
      }
    }
  });
  return null;
}

export default function ChennaiCommuteMap({
  fromCoords = null,
  toCoords = null,
  pickupCoords = null,
  routeCoordinates = [],
  availableRides = [],
  onSelectRide = null,
  onLocationSelect = null,
  interactive = true,
  height = '420px',
  activeRidePolylineColor = '#10b981'
}) {
  const defaultChennaiCenter = [13.0418, 80.2030]; // Central Chennai

  return (
    <div className="relative w-full rounded-2xl overflow-hidden shadow-2xl border border-slate-800 z-0 isolate" style={{ height }}>
      <MapContainer
        center={defaultChennaiCenter}
        zoom={12}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        {/* Dark Modern OpenStreetMap CartoDB Tiles */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          maxZoom={19}
        />

        {/* Dynamic Map Bounds Adjuster */}
        <AutoFitBounds 
          coordinates={routeCoordinates} 
          fromCoords={fromCoords} 
          toCoords={toCoords} 
        />

        {/* Click-to-pick Handler */}
        {onLocationSelect && <MapClickHandler onLocationSelect={onLocationSelect} />}

        {/* Active Route Polyline */}
        {routeCoordinates && routeCoordinates.length > 1 && (
          <>
            {/* Polyline Outer Glow / Border */}
            <Polyline
              positions={routeCoordinates}
              pathOptions={{
                color: '#064e3b',
                weight: 8,
                opacity: 0.6,
                lineCap: 'round',
                lineJoin: 'round'
              }}
            />
            {/* Polyline Main Line */}
            <Polyline
              positions={routeCoordinates}
              pathOptions={{
                color: activeRidePolylineColor,
                weight: 5,
                opacity: 0.95,
                lineCap: 'round',
                lineJoin: 'round'
              }}
            />
          </>
        )}

        {/* Start / Origin Marker */}
        {fromCoords && (
          <Marker position={[fromCoords.lat, fromCoords.lng]} icon={greenIcon}>
            <Popup>
              <div className="text-xs p-1">
                <span className="font-bold text-emerald-400">🟢 Start Point</span>
                <p className="text-slate-200 mt-0.5">{fromCoords.name || 'Origin'}</p>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Destination Marker */}
        {toCoords && (
          <Marker position={[toCoords.lat, toCoords.lng]} icon={redIcon}>
            <Popup>
              <div className="text-xs p-1">
                <span className="font-bold text-rose-400">🔴 Destination</span>
                <p className="text-slate-200 mt-0.5">{toCoords.name || 'Destination'}</p>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Suggested Pickup Nodal Marker */}
        {pickupCoords && (
          <Marker position={[pickupCoords.lat, pickupCoords.lng]} icon={amberIcon}>
            <Popup>
              <div className="text-xs p-1">
                <span className="font-bold text-amber-400">📍 Suggested Pickup Point</span>
                <p className="text-slate-200 mt-0.5">{pickupCoords.name || 'Pickup Junction'}</p>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Available Community Rides Markers */}
        {availableRides && availableRides.map((ride, idx) => {
          const rFrom = ride.from_coords || (ride.route && ride.route.from_coords);
          if (!rFrom) return null;
          return (
            <Marker 
              key={ride.id || idx} 
              position={[rFrom.lat, rFrom.lng]} 
              icon={bikeIcon}
              eventHandlers={{
                click: () => onSelectRide && onSelectRide(ride)
              }}
            >
              <Popup>
                <div className="text-xs p-2 min-w-[160px]">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-emerald-400">🏍️ {ride.rider_name || 'Rider'}</span>
                    <span className="bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded font-mono font-semibold">
                      ₹{ride.cost_per_person || (ride.booking && ride.booking.cost_per_person) || 50}
                    </span>
                  </div>
                  <p className="text-slate-300 font-medium">{ride.from_location} ➔ {ride.to_location}</p>
                  <p className="text-slate-400 text-[11px] mt-1">🕒 {ride.departure_time || (ride.timing && ride.timing.departure_time)}</p>
                  {ride.ai_match_score && (
                    <div className="mt-2 pt-1.5 border-t border-slate-700 flex justify-between items-center">
                      <span className="text-slate-400">Match:</span>
                      <span className="text-emerald-400 font-bold">{ride.ai_match_score}%</span>
                    </div>
                  )}
                  {onSelectRide && (
                    <button
                      onClick={() => onSelectRide(ride)}
                      className="mt-2 w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-1 px-2 rounded text-[11px] transition-colors"
                    >
                      View & Request Ride
                    </button>
                  )}
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {/* Chennai Commute Overlay Badge */}
      <div className="absolute top-3 right-3 z-10 bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-700/60 shadow-lg text-xs flex items-center gap-2 pointer-events-none">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
        <span className="text-slate-200 font-semibold">Chennai Live Road Network</span>
      </div>
    </div>
  );
}
