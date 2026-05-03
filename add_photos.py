#!/usr/bin/env python3
"""
add_photos.py - Match trail photos to hikes using EXIF GPS metadata.

Usage:
  1. Drop your photos into the photos/ folder.
  2. Run: python add_photos.py
  3. The script matches each photo to the nearest trail and updates index.html.

Requires: Pillow  (pip install Pillow)
"""

import math
import os
import re
import sys

try:
    from PIL import Image
    from PIL.ExifTags import GPSTAGS
except ImportError:
    print("ERROR: Pillow is required. Install it with:  pip install Pillow")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PHOTOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photos")
INDEX_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".tiff", ".tif", ".webp"}

# Trail coordinates mirroring the trails array in index.html.
# Update this list whenever trails are added or their coordinates change.
TRAILS = [
    {"id": 1,  "name": "1. Bessie's Loop",                         "lat": 35.18025, "lng": -83.43328},
    {"id": 2,  "name": "2. William's Pulpit",                      "lat": 35.18025, "lng": -83.43328},
    {"id": 3,  "name": "3. Hickory Knoll Rd. to The Pinnacle",     "lat": 35.07975, "lng": -83.37694},
    {"id": 4,  "name": "4. Mud Creek",                             "lat": 34.99242, "lng": -83.34756},
    {"id": 5,  "name": "5. Queen's Branch",                        "lat": 35.28364, "lng": -83.46750},
    {"id": 6,  "name": "6. Gibson Bottoms",                        "lat": 35.23272, "lng": -83.39133},
    {"id": 7,  "name": "7. Onion Mtn. North",                      "lat": 35.21131, "lng": -83.29542},
    {"id": 8,  "name": "8. Onion Mtn. South",                      "lat": 35.19019, "lng": -83.28244},
    {"id": 9,  "name": "9. Tessentee Bottomland",                  "lat": 35.06889, "lng": -83.37997},
    {"id": 10, "name": "10. Winding Stair Gap to Siler Bald",      "lat": 35.12067, "lng": -83.54708},
    {"id": 11, "name": "11. Winding Stair Gap South",              "lat": 35.11986, "lng": -83.54797},
    {"id": 12, "name": "12. Parker Meadows",                       "lat": 35.15472, "lng": -83.45669},
    {"id": 13, "name": "13. Suli Marsh",                           "lat": 35.19675, "lng": -83.38714},
    {"id": 14, "name": "14. Big Bear Park",                        "lat": 35.18686, "lng": -83.37392},
    {"id": 15, "name": "15. Riverwalk",                            "lat": 35.18533, "lng": -83.37094},
    {"id": 16, "name": "16. Salali Ln",                            "lat": 35.17558, "lng": -83.36992},
    {"id": 17, "name": "17. Tassee Park",                          "lat": 35.17356, "lng": -83.37217},
    {"id": 18, "name": "18. Southwestern CC",                      "lat": 35.15967, "lng": -83.37922},
    {"id": 19, "name": "19. Library",                              "lat": 35.15856, "lng": -83.38178},
    {"id": 20, "name": "20. Cartoogechaye Loop",                   "lat": 35.16733, "lng": -83.43583},
    {"id": 21, "name": "21. Cove Branch (MVI)",                    "lat": 35.16383, "lng": -83.36111},
    {"id": 22, "name": "22. Macon Middle Loop",                    "lat": 35.16136, "lng": -83.35739},
    {"id": 23, "name": "23. South Macon Loop",                     "lat": 35.11281, "lng": -83.40003},
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def haversine(lat1, lon1, lat2, lon2):
    """Return the great-circle distance in miles between two GPS coordinates."""
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def dms_to_decimal(dms, ref):
    """Convert degrees/minutes/seconds tuple + cardinal ref to a decimal degree."""
    degrees = float(dms[0])
    minutes = float(dms[1])
    seconds = float(dms[2])
    decimal = degrees + minutes / 60.0 + seconds / 3600.0
    if ref in ("S", "W"):
        decimal = -decimal
    return decimal


def get_gps_from_exif(image_path):
    """
    Return (latitude, longitude) extracted from a photo's EXIF GPS block,
    or None when GPS data is absent or unreadable.

    Supported formats: JPEG and TIFF are always supported by Pillow.
    HEIC requires the 'pillow-heif' package (pip install pillow-heif).
    WebP support depends on the Pillow build.
    """
    try:
        with Image.open(image_path) as img:
            exif = img.getexif()
        if not exif:
            return None

        # Tag 34853 is the standard EXIF IFD pointer for GPS data
        GPS_IFD_TAG = 34853
        gps_ifd = exif.get_ifd(GPS_IFD_TAG)
        if not gps_ifd:
            return None

        gps_info = {GPSTAGS.get(k, k): v for k, v in gps_ifd.items()}

        if "GPSLatitude" not in gps_info or "GPSLongitude" not in gps_info:
            return None

        lat = dms_to_decimal(
            gps_info["GPSLatitude"],
            gps_info.get("GPSLatitudeRef", "N"),
        )
        lon = dms_to_decimal(
            gps_info["GPSLongitude"],
            gps_info.get("GPSLongitudeRef", "E"),
        )
        return lat, lon

    except Exception as exc:
        print(f"  Warning: Could not read EXIF from {os.path.basename(image_path)}: {exc}")
        return None


def find_nearest_trail(lat, lon):
    """Return (trail_dict, distance_miles) for the closest trail."""
    nearest, min_dist = None, float("inf")
    for trail in TRAILS:
        dist = haversine(lat, lon, trail["lat"], trail["lng"])
        if dist < min_dist:
            min_dist, nearest = dist, trail
    return nearest, min_dist


def update_index_html(trail_id, rel_img_path):
    """
    Insert or replace the img property for the given trail id inside index.html.
    Returns True on success, False if the trail entry could not be located.

    Matches the trail object by id and manipulates the matched string directly,
    so it is not sensitive to the order of other properties in the object.
    """
    with open(INDEX_HTML, "r", encoding="utf-8") as fh:
        content = fh.read()

    # Forward-slash path for use inside the HTML/JS string
    rel_path = rel_img_path.replace(os.sep, "/")

    # Match the whole trail JS object by id. Trail objects contain no nested
    # braces, so matching from `{ id: N,` up to the first `}` is reliable.
    obj_pattern = re.compile(
        r"\{\s*id:\s*" + str(trail_id) + r",[^{]*?\}",
        re.DOTALL,
    )

    match = obj_pattern.search(content)
    if not match:
        print(f"  ERROR: Could not find trail id {trail_id} in index.html")
        return False

    obj_str = match.group(0)

    # Replace an existing img property, or add one before the closing brace
    img_inline = re.compile(r',\s*img:\s*"[^"]*"')
    if img_inline.search(obj_str):
        new_obj = img_inline.sub(f', img: "{rel_path}"', obj_str)
    else:
        new_obj = obj_str[:-1].rstrip() + f', img: "{rel_path}"' + obj_str[-1]

    new_content = content[: match.start()] + new_obj + content[match.end() :]

    with open(INDEX_HTML, "w", encoding="utf-8") as fh:
        fh.write(new_content)

    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not os.path.isdir(PHOTOS_DIR):
        print(f"ERROR: photos/ directory not found at {PHOTOS_DIR}")
        sys.exit(1)

    image_files = sorted(
        f for f in os.listdir(PHOTOS_DIR)
        if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
        and os.path.isfile(os.path.join(PHOTOS_DIR, f))
    )

    if not image_files:
        print("No images found in the photos/ directory.")
        print("Drop your trail photos there and run this script again.")
        return

    print(f"Found {len(image_files)} photo(s) in photos/\n")
    updated = skipped = 0

    for filename in image_files:
        img_path = os.path.join(PHOTOS_DIR, filename)
        rel_img = os.path.join("photos", filename)

        print(f"Processing: {filename}")

        coords = get_gps_from_exif(img_path)
        if not coords:
            print("  No GPS data found in this photo. Skipping.\n")
            skipped += 1
            continue

        lat, lon = coords
        print(f"  GPS coordinates: {lat:.5f}, {lon:.5f}")

        trail, dist = find_nearest_trail(lat, lon)
        print(f"  Nearest trail:   {trail['name']} ({dist:.2f} miles away)")

        answer = input(f"  Add '{filename}' to '{trail['name']}'? [Y/n]: ").strip().lower()
        if answer not in ("", "y", "yes"):
            print("  Skipped.\n")
            skipped += 1
            continue

        if update_index_html(trail["id"], rel_img):
            print(f"  ✓ index.html updated — trail {trail['id']} now shows '{filename}'\n")
            updated += 1
        else:
            skipped += 1

    print(f"Done. {updated} trail(s) updated, {skipped} skipped.")


if __name__ == "__main__":
    main()
