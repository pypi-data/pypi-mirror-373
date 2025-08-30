#!/usr/bin/env python
import argparse
import json
import sys
from map_my_locations.mapper import SimpleLocationMapper

def get_nested(data, path: str):
    """Drill into dict/list by dotted/key[index] path, e.g. 'route.stays' or 'location[0]'."""
    import re
    node = data
    for part in path.split('.'):
        if not part:
            continue
        # handle index e.g. location[0]
        m = re.match(r'^([a-zA-Z0-9_]+)(?:\[(\d+)\])?$', part)
        if not m:
            raise ValueError(f"Invalid path segment: {part}")
        key, idx = m.group(1), m.group(2)
        node = node[key]
        if idx is not None:
            node = node[int(idx)]
    return node

def main():
    parser = argparse.ArgumentParser(
        prog="geostay",
        description="Plot GPS stays on a map"
    )
    parser.add_argument("input", help="Path to JSON file")
    parser.add_argument(
        "-a", "--array-path",
        default="",
        help="Dotted path to stays array (e.g. 'route.stays')"
    )
    parser.add_argument(
        "-x", "--lat-key",
        default="location[0]",
        help="Key or path for latitude in each object"
    )
    parser.add_argument(
        "-y", "--lng-key",
        default="location[1]",
        help="Key or path for longitude in each object"
    )
    parser.add_argument(
        "-o", "--output",
        default="map.html",
        help="Output HTML file name"
    )
    args = parser.parse_args()

    try:
        with open(args.input, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Drill into array if requested
    raw = data
    if args.array_path:
        try:
            raw = get_nested(data, args.array_path)
        except Exception as e:
            print(f"❌ Invalid array path '{args.array_path}': {e}", file=sys.stderr)
            sys.exit(1)

    if not isinstance(raw, list):
        print(f"❌ Extracted object is not a list ({type(raw).__name__})", file=sys.stderr)
        sys.exit(1)

    # Prepare stays list with lat/lng keys replaced
    stays = []
    for i, item in enumerate(raw, start=1):
        try:
            lat = get_nested(item, args.lat_key)
            lng = get_nested(item, args.lng_key)
        except Exception as e:
            print(f"❌ Failed to extract coords for stay {i}: {e}", file=sys.stderr)
            sys.exit(1)
        # override location fields for uniformity
        item["lat"] = lat
        item["lng"] = lng
        stays.append(item)

    mapper = SimpleLocationMapper()
    html = mapper.create_map(stays, save_path=args.output)
    if html:
        mapper.open_map(html)

if __name__ == "__main__":
    main()
