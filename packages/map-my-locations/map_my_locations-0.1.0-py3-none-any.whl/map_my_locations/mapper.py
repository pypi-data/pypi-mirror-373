# location_mapper/mapper.py

import json
import folium
import webbrowser
import os
import math
from typing import List, Dict, Any, Optional, Tuple

class SimpleLocationMapper:
    """
    Simple mapper for plotting location stays with straight-line routes.
    """

    def __init__(self):
        self.map: Optional[folium.Map] = None

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers."""
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return 6371 * c

    @staticmethod
    def calculate_map_bounds(coordinates: List[Tuple[float, float]]) -> Dict[str, Any]:
        """Return center and zoom level based on coordinates spread."""
        if not coordinates:
            return {"center": [0, 0], "zoom": 2}

        lats, lngs = zip(*coordinates)
        center = [sum(lats)/len(lats), sum(lngs)/len(lngs)]
        lat_range = max(lats) - min(lats) if len(coordinates) > 1 else 0
        lng_range = max(lngs) - min(lngs) if len(coordinates) > 1 else 0
        span = max(lat_range, lng_range)
        if span > 10:
            zoom = 5
        elif span > 1:
            zoom = 9
        elif span > 0.1:
            zoom = 12
        elif span > 0.01:
            zoom = 14
        else:
            zoom = 16
        return {"center": center, "zoom": zoom}

    @staticmethod
    def make_popup_html(index: int, lat: float, lng: float, data: Dict[str, Any], color: str) -> str:
        """Return HTML string for marker popup."""
        html = [
            f"<div style='font-family:Arial;min-width:200px;'>",
            f"<h3 style='color:{color};margin:0 0 8px;'>📍 Location #{index}</h3>",
            f"<p><strong>Coords:</strong> {lat:.6f}, {lng:.6f}</p>"
        ]
        for key in ("stayNumber","start","end","duration","dataPoints","averageSpeed","searchRadius"):
            if key in data:
                label = key.replace("stayNumber","Stay #") \
                           .replace("dataPoints","Points") \
                           .replace("averageSpeed","Avg Speed") \
                           .replace("searchRadius","Radius")
                html.append(f"<p><strong>{label}:</strong> {data[key]}</p>")
        html.append("</div>")
        return "".join(html)

    @staticmethod
    def make_distance_label(distance: float) -> str:
        """Return HTML for distance label."""
        return (
            f"<div style='"
            "background:#ff4757;color:#fff;padding:4px 8px;"
            "border-radius:4px;font-size:12px;font-weight:bold;"
            "font-family:Arial;'>"
            f"{distance:.1f} km"
            "</div>"
        )

    def create_map(
        self,
        stays: List[Dict[str, Any]],
        save_path: str = "map.html"
    ) -> Optional[str]:
        """
        Create and save an HTML map from list of stay dicts.
        Each dict must have 'lat' and 'lng' keys.
        """
        coords = [(s["lat"], s["lng"]) for s in stays]
        if not coords:
            print("❌ No valid coordinates provided.")
            return None

        bounds = self.calculate_map_bounds(coords)
        m = folium.Map(location=bounds["center"], zoom_start=bounds["zoom"], tiles="OpenStreetMap")

        colors = [
            "red","blue","green","purple","orange","darkred","lightred",
            "beige","darkblue","darkgreen","cadetblue","darkpurple",
            "pink","lightblue","lightgreen","gray","black"
        ]

        # Add markers
        for i, (lat, lng) in enumerate(coords, start=1):
            color = colors[(i-1) % len(colors)]
            popup = folium.Popup(
                self.make_popup_html(i, lat, lng, stays[i-1], color),
                max_width=300
            )
            folium.Marker(
                [lat, lng],
                popup=popup,
                tooltip=f"Location #{i}",
                icon=folium.Icon(color=color, icon="info-sign")
            ).add_to(m)
            folium.Marker(
                [lat, lng],
                icon=folium.DivIcon(html=f"<div style='"
                    f"background:{color};color:#fff;"
                    "border-radius:50%;width:24px;height:24px;"
                    "display:flex;align-items:center;justify-content:center;"
                    "font-weight:bold;font-size:14px;"
                    "border:2px solid #fff;"
                    "box-shadow:0 2px 4px rgba(0,0,0,0.3);"
                f"'>{i}</div>")
            ).add_to(m)

        # Add straight-line route + labels
        if len(coords) > 1:
            total = 0.0
            for i in range(len(coords)-1):
                a,b = coords[i], coords[i+1]
                dist = self.haversine_distance(a[0],a[1],b[0],b[1])
                total += dist
                folium.PolyLine([a,b], color="#ff4757", weight=4, opacity=0.8,
                    popup=f"Segment {i+1}->{i+2}: {dist:.1f} km").add_to(m)
                latm, lngm = (a[0]+b[0])/2, (a[1]+b[1])/2
                folium.Marker(
                    [latm,lngm],
                    icon=folium.DivIcon(html=self.make_distance_label(dist))
                ).add_to(m)

            # Summary at first point
            # summary = (
            #     f"<div style='font-family:Arial;min-width:180px;'>"
            #     f"<h4 style='color:green;margin:0 0 8px;'>🗺 Route</h4>"
            #     f"<p><strong>Total:</strong> {total:.1f} km</p>"
            #     f"<p><strong>Points:</strong> {len(coords)}</p>"
            #     f"<p style='font-size:11px;color:#666;'>"
            #     "Straight-line only</p></div>"
            # )
            # folium.Marker(
            #     coords[0],
            #     popup=folium.Popup(summary, max_width=250),
            #     icon=folium.Icon(color="green", icon="road", prefix="fa")
            # ).add_to(m)

        m.save(save_path)
        print(f"✅ Map saved to {save_path}")
        self.map = m
        return save_path

    def open_map(self, path: str):
        """Open the generated map in the default web browser."""
        url = f"file://{os.path.abspath(path)}"
        webbrowser.open(url)
        print(f"🌐 Opening {url}")
