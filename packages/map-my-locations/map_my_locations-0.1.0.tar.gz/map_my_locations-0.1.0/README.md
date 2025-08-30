# Map-My-Locations

A lightweight, command-line tool and Python package for plotting GPS “stay” locations on an interactive map. Read your JSON file of location stays, extract coordinates from any nested path or key, draw numbered markers and straight-line routes, and save a self-contained HTML map you can view offline.

## Features

- No external API calls or plugins—100% powered by [Folium](https://github.com/python-visualization/folium)
- CLI entry point (`map-my-locations`) to run directly from the terminal
- Accepts any JSON structure:
  - Drill into nested arrays via `--array-path` (e.g. `route.stays`)
  - Custom latitude/longitude keys or indices via `--lat-key` / `--lng-key` (e.g. `location[0]`, `latitude`)
- Numbered, styled markers with rich popups showing metadata (start/end times, duration, data points, average speed, radius)
- Straight-line route segments with accurate Haversine distance calculations and on-map labels
- Popup summary of total route distance and stop count
- Automatic map centering and zoom based on coordinate spread
- Self-contained HTML output that works offline

## Installation

```
pip install map-my-locations
```

## Quickstart

```bash
map-my-locations path/to/stays.json
--array-path route.stays
--lat-key location
--lng-key location
--output stays_map.html
```

This command will:

1. Load `stays.json` and drill into `route.stays`  
2. Extract latitude and longitude using the specified keys  
3. Generate `stays_map.html` with numbered markers, route lines, and popups  
4. Automatically open `stays_map.html` in your default browser  

## CLI Usage

```
Usage: map-my-locations [OPTIONS] INPUT

Arguments:
INPUT Path to JSON file containing location data

Options:
-a, --array-path TEXT Dotted path to array of stay objects (default: "")
-x, --lat-key TEXT Key or path for latitude in each object (default: "location")
-y, --lng-key TEXT Key or path for longitude in each object (default: "location")
-o, --output TEXT Output HTML file name (default: "map.html")
-h, --help Show this message and exit.
```


## Example

Given `stays.json`:

```json
{
"route": {
"stays": [
{
"stayNumber": 1,
"location": [38.71303717, -90.26528184],
"start": "2025-08-28 14:11:58",
"end": "2025-08-28 14:16:32",
"duration": "0h 4m (4.57 minutes)",
"dataPoints": 27,
"averageSpeed": "1.69 units",
"searchRadius": "100 meters"
},
{
"stayNumber": 2,
"location": [38.71503717, -90.26728184],
"start": "2025-08-28 15:20:15",
"end": "2025-08-28 16:45:22",
"duration": "1h 25m (85.12 minutes)",
"dataPoints": 156,
"averageSpeed": "0.85 units",
"searchRadius": "100 meters"
}
]
}
}
```


Run:

```bash
map-my-locations path/to/stays.json
--array-path route.stays
--lat-key location
--lng-key location
--output stays_map.html
```

## License

MIT License