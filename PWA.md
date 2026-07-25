# Progressive Web App Usage

This project can also run as a browser-hosted web app using PyScript/Pyodide.
The web page mode lets users select JPEG photos, generate a KML file, and optionally upload photos via configurable cloud settings.

## What this mode does

- Opens `index.html` as the browser app entry point.
- Uses `pwa.py` to run Python in the browser for KML generation.
- Uses `cloud.js` to display and save cloud upload settings as JSON.
- Generates a browser download link for the KML file.
- Logs progress to the on-screen conversion log.

## Recommended launch

For best results, serve the project over HTTP rather than loading local files directly.
From the repo root, run a simple local server:

```bash
python -m http.server 8000
```

Then open:
[http://localhost:8000/index.html]
This avoids browser restrictions on PyScript, module loading, and other web assets.

Live demo, available on my web site:
[https://www.mobiliscruise.com/jpeg_geotags_to_kml-pwa_wip/]
Note: This demo stores photos on my server by default, but you can change the cloud storage settings.

## Browser UI workflow

1. Click `Choose Files` and select one or more JPEG photos.
2. Enter a `Project Name`.
3. Click `Show Cloud Settings` to review or edit the JSON upload settings.
4. Click `Validate` to confirm the config is valid and `Save` to store it in a browser cookie.
5. Click `Convert to KML`.
6. Download the generated `.kml` file from the download link displayed below the form.

## Cloud settings in the browser

The browser app uses `cloud.json` as the default upload configuration.
When you save cloud settings in the web UI, they are kept in a cookie and synced into the Python runtime.

The JSON editor includes fields such as:

- `hostname`
- `upload_dir`
- `upload_protocol`
- `upload_url`
- `url_fmt`
- `headers`

If photo upload is not needed, you can enter `null` in the cloud settings textbox.

## Important files

- `index.html` — web app entry page and UI.
- `pwa.py` — PyScript Python glue for generating KML and wiring browser logs.
- `cloud.js` — browser-side cloud config editor and runtime sync.
- `photo-picker.css` — web app styling.
- `conv_pys.json` — PyScript configuration for browser Python assets.
- `cloud.json` — default cloud upload JSON.

## Browser requirements

- Modern desktop browser with support for PyScript/Pyodide.
- Network access if the app needs to upload photos to a remote server.

## Notes

- KML generation is done client-side and produces a download link in the browser.
- The upload step only works if the cloud config points to a reachable server and the app can make the required HTTP requests.
- The app may require HTTPS or a secure context for some browser features.
