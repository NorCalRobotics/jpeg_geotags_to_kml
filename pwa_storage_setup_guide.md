# Custom Storage Endpoint Setup & Configuration Guide

This guide provides technical specifications for configuring custom image storage endpoints to integrate with the Progressive Web App (PWA) geotagged photo and KML generation pipeline.

The PWA is an unopinionated client that offloads image hosting completely to your storage infrastructure. Images are uploaded synchronously via HTTP `PUT` and made available via static, publicly accessible URLs for rendering inside KML maps and Google Earth desktop/web viewers.

---

## 1. Storage Requirements & Architecture

To work properly with the PWA and KML viewers, your storage target must meet two essential criteria:

1. **Upload Protocol:** Accept direct binary image uploads via `HTTP PUT` (with standard headers such as `Authorization` and `Content-Type: image/jpeg`).
2. **KML Direct Asset Access:** Provide a deterministic, public static URL (`url_fmt`) that serves raw JPEG bytes without requiring redirects, JavaScript execution, or authentication headers. KML rendering engines (e.g., Google Earth, ArcGIS, QGIS) cannot handle dynamic login flows or OAuth prompts when loading map overlay callout images.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       PWA STORAGE ARCHITECTURE                          │
│                                                                         │
│  [ PWA Client ] ──── HTTP PUT (Auth Header) ────► [ upload_url ]       │
│                                                          │              │
│                                                    (Stores File)        │
│                                                          │              │
│  [ Google Earth ] ◄── Unauthenticated GET ─────── [ url_fmt ]          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Configuration JSON Reference

The PWA configuration is managed via raw JSON settings in the application UI.

### Example configuration

```json
{
  "hostname": "storage.yourdomain.com",
  "username": "your_username",
  "password": "your_password",
  "upload_dir": "photos/geotagged_kml/user_01",
  "upload_protocol": "HTTP_PUT",
  "upload_url": "https://{0[hostname]}/dav_script.php/{0[upload_dir]}/{photo_path}",
  "url_fmt": "https://{0[hostname]}/public_data/{0[upload_dir]}/{photo_path}",
  "headers": {
    "Authorization": "Basic eW91cl91c2VybmFtZTp5b3VyX3Bhc3N3b3Jk",
    "Content-Type": "image/jpeg"
  }
}
```

### Field Definitions

| Field | Type | Description |
| :--- | :--- | :--- |
| `hostname` | String | Base domain or IP address of your storage host. |
| `username` | String | Storage account username (used for auto-generating Basic Auth). |
| `password` | String | Storage account password (used for auto-generating Basic Auth). |
| `upload_dir` | String | Relative destination directory path on the storage target. |
| `upload_protocol` | String | Upload method. Currently expected to be `HTTP_PUT`. |
| `upload_url` | String | Template string for the HTTP `PUT` destination endpoint. |
| `url_fmt` | String | Template string for the public, unauthenticated image asset URL embedded into KML files. |
| `headers` | Object | Key-value pairs of HTTP headers sent with every upload request. |

### Template Variables
The PWA dynamically evaluates strings in `upload_url` and `url_fmt` using runtime parameter interpolation:
* `{0[hostname]}` — Replaced with the value of the `hostname` field.
* `{0[upload_dir]}` — Replaced with the value of the `upload_dir` field.
* `{photo_path}` — Replaced with the target filename (e.g., `IMG_20260802_171500.jpg`).

---

## 3. PWA Interface & Button Workflows

The PWA configuration panel features three state-managed control buttons to prevent syntax errors and invalid configurations.

```
┌────────────────────────────────────────────────────────────────────────┐
│ Cloud Settings                                                         │
├────────────────────────────────────────────────────────────────────────┤
│ [ JSON Editor Area ]                                                   │
├────────────────────────────────────────────────────────────────────────┤
│  [ Validate ]    [ Save ]    [ Update Authentication Header ]          │
└────────────────────────────────────────────────────────────────────────┘
```

### Button State Logic

* **`Validate`**: Enabled whenever edits are made in the JSON text area.
* **`Save`**: Disabled by default. Enabled **only** after the JSON passes validation via the `Validate` button.
* **`Update Authentication Header`**: Enabled **only** when non-empty `username` and `password` fields are present in the JSON schema.

---

### Workflow A: Editing Configuration Settings

1. Edit the raw JSON string in the UI configuration editor. *(Editing automatically enables the `Validate` button).*
2. Click **`Validate`**. The app parses the JSON and verifies syntax and required fields. *(If valid, the `Save` button becomes enabled).*
3. Click **`Save`** to commit the configuration to application local storage.

---

### Workflow B: Updating the Basic Authentication Header

The `Authorization` header uses standard HTTP Basic Authentication formatting:
$$	{Header Value} = 	{Basic } + 	{Base64}(	{username}:{password})$$

To generate or update this token without using terminal commands:

1. Ensure the `username` and `password` fields in the JSON contain your target credentials. *(The `Update Authentication Header` button becomes enabled).*
2. Click **`Update Authentication Header`**. The PWA encodes `username:password` into Base64 and updates the `headers.Authorization` string automatically.
3. Click **`Validate`** to verify the updated JSON structure.
4. Click **`Save`** to store the updated configuration.

---

## 4. Endpoint Setup Guides

### Guide 1: Nextcloud / OwnCloud (WebDAV)

Nextcloud and OwnCloud natively support WebDAV `PUT` requests, but require public folder sharing so Google Earth can read images without authentication.

#### 1. Setup Storage Directories
1. Log in to your Nextcloud/OwnCloud instance.
2. Create a folder structure: `Photos/geotagged_kml/user_01`.
3. Select the folder, open the **Sharing** panel, and generate a **Public Link** with Read-Only permissions. Note the share token (e.g., `aBcDeF12345`).

#### 2. Configure JSON

```json
{
  "hostname": "cloud.yourdomain.com",
  "username": "your_nextcloud_user",
  "password": "your_app_password",
  "upload_dir": "Photos/geotagged_kml/user_01",
  "upload_protocol": "HTTP_PUT",
  "upload_url": "https://{0[hostname]}/remote.php/dav/files/{0[username]}/{0[upload_dir]}/{photo_path}",
  "url_fmt": "https://{0[hostname]}/s/aBcDeF12345/download?path=&files={photo_path}",
  "headers": {
    "Authorization": "Basic eW91cl9uZXh0Y2xvdWRfdXNlcjp5b3VyX2FwcF9wYXNzd29yZA==",
    "Content-Type": "image/jpeg"
  }
}
```

> **Security Note:** It is strongly recommended to use a dedicated **App Password** generated under Nextcloud Security Settings rather than your primary account password.

---

### Guide 2: Amazon S3 / Cloudflare R2 / MinIO / S3-Compatible Storage

S3-compatible object storage offers high scalability and zero infrastructure maintenance.

#### 1. Bucket Permissions & CORS Configuration
1. Create a public read bucket or attach a public policy to the target prefix/directory:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "PublicReadForKML",
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::your-bucket-name/photos/*"
       }
     ]
   }
   ```
2. Configure **CORS** on your bucket to allow the PWA browser origin to execute `PUT` requests:
   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["PUT", "GET", "HEAD"],
       "AllowedOrigins": ["https://your-pwa-domain.com"],
       "ExposeHeaders": []
     }
   ]
   ```

#### 2. Configure JSON (Using API Gateway or Direct REST PUT)

```json
{
  "hostname": "your-bucket-name.s3.us-west-2.amazonaws.com",
  "username": "AKIAIOSFODNN7EXAMPLE",
  "password": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "upload_dir": "photos/geotagged_kml/user_01",
  "upload_protocol": "HTTP_PUT",
  "upload_url": "https://{0[hostname]}/{0[upload_dir]}/{photo_path}",
  "url_fmt": "https://{0[hostname]}/{0[upload_dir]}/{photo_path}",
  "headers": {
    "Authorization": "Basic QUtJQTIzNDU2Nzg5OkVYQU1QTEVLRVk=",
    "Content-Type": "image/jpeg"
  }
}
```

*(Note: If using presigned PUT endpoints or custom Cloudflare Workers, set `upload_url` to the ingest endpoint and `url_fmt` to the public CDN/R2 distribution URL).*

---

### Guide 3: Custom Apache / Nginx WebDAV or PHP Receiver

If running a traditional Linux VPS (e.g., Debian/Ubuntu with Apache or Nginx), you can route incoming `PUT` requests to a WebDAV script or PHP handler while serving uploaded files statically via a fast web server alias.

#### 1. Web Server Directory Structure
* **Write Directory (Auth Required):** `/var/www/webdav/Photos/geotagged_kml/user_01`
* **Public Static Alias (No Auth):** `/var/www/html/data/Photos/geotagged_kml/user_01`

#### 2. Apache VirtualHost Configuration Snippet

```apache
# Enable WebDAV on /test_dav/webdav.php
Alias /test_dav/data /var/www/webdav

<Directory /var/www/webdav>
    Dav On
    AuthType Basic
    AuthName "PWA Storage Access"
    AuthUserFile /etc/apache2/.htpasswd
    Require valid-user

    # Allow HTTP PUT method
    <Limit PUT POST DELETE>
        Require valid-user
    </Limit>
</Directory>

# Public read-only access for KML map viewing
<Location /test_dav/data>
    Require all granted
    Satisfy Any
</Location>
```

#### 3. Configure JSON

```json
{
  "hostname": "www.yourdomain.com",
  "username": "user01",
  "password": "pw01",
  "upload_dir": "Photos/jpeg_geotags_to_kml_photos/user_user01",
  "upload_protocol": "HTTP_PUT",
  "upload_url": "https://{0[hostname]}/test_dav/webdav.php/{0[upload_dir]}/{photo_path}",
  "url_fmt": "https://{0[hostname]}/test_dav/data/{0[upload_dir]}/{photo_path}",
  "headers": {
    "Authorization": "Basic dXNlcjAxOnB3MDE=",
    "Content-Type": "image/jpeg"
  }
}
```

---

## 5. Deployment Verification Checklist

Before deploying your storage endpoint for live PWA uploads and KML generation, perform these three verification steps:

1. **Verify HTTP PUT via cURL:**
   ```bash
   curl -X PUT      -H "Authorization: Basic YOUR_BASE64_HEADER"      -H "Content-Type: image/jpeg"      --data-binary "@test_image.jpg"      "https://yourdomain.com/upload_endpoint/photos/test_image.jpg"
   ```
   *Expected Result:* HTTP status code `200 OK` or `201 Created`.

2. **Verify Public KML Asset URL:**
   Open a browser incognito window (or use `curl -I`) and request the compiled `url_fmt` link:
   ```bash
   curl -I "https://yourdomain.com/public_data/photos/test_image.jpg"
   ```
   *Expected Result:* HTTP status code `200 OK` returning `Content-Type: image/jpeg` with **no redirect** to a login screen or 401/403 status.

3. **Google Earth Callout Verification:**
   In Google Earth (Desktop or Web), import a test KML file containing an `<href>` link pointing to your `url_fmt` string. Verify that clicking the geotagged map pin renders the inline photo popup instantly.
