# Trail Photos

Drop your trail photos into this folder, then run `add_photos.py` from the repository root to automatically assign each photo to the correct trail.

## Requirements

- Python 3.7+
- Pillow library: `pip install Pillow`

## Steps

1. Copy your photos into this `photos/` folder.
2. Make sure your photos have GPS location data embedded (enabled in your phone's camera settings).
3. From the repository root, run:
   ```
   python add_photos.py
   ```
4. The script will show you which trail it matched each photo to, then ask for confirmation before making any changes.
5. After confirming, `index.html` is updated automatically and the photo will appear on the matching trail card.

## Tips

- Most modern smartphones automatically embed GPS in photos when location services are enabled for the camera app.
- If a photo has no GPS data, the script will skip it and let you know.
- Each trail card displays one photo at a time. Running the script again with a new photo for the same trail will replace the existing one.
- You can also manually assign a photo to a trail by adding `img: "photos/your-file.jpg"` to the matching trail entry in `index.html`.
