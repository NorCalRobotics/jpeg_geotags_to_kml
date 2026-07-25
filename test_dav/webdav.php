<?php
// Copyright 2026 NorCalRobotics
// Unmodified use and code review only. No AI/ML training or redistribution rights.

// Standalone WebDAV test script supporting nested directories
// Usage: http://yourserver/webdav.php/subfolder/another_folder/image.jpg

$baseUploadDir = __DIR__ . '/data/';

// Ensure root storage directory exists
if (!file_exists($baseUploadDir)) {
    mkdir($baseUploadDir, 0777, true);
}

$requestMethod = $_SERVER['REQUEST_METHOD'];

// Parse relative path (e.g., "/2026/site_a/image.jpg")
$pathInfo = $_SERVER['PATH_INFO'] ?? '/';

// Clean and sanitize relative path against directory traversal
$relativePath = ltrim(str_replace(['../', '..\\'], '', $pathInfo), '/');
$targetPath = $baseUploadDir . $relativePath;

// Enable CORS so Pyodide / Browser fetch works seamlessly
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, PUT, OPTIONS, PROPFIND, MKCOL, DELETE");
header("Access-Control-Allow-Headers: Authorization, Content-Type, Depth");

// 1. Handle Preflight CORS Check
if ($requestMethod === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// 2. Handle Directory Creation (MKCOL method used by standard WebDAV clients)
if ($requestMethod === 'MKCOL') {
    if (file_exists($targetPath)) {
        http_response_code(405); // Method Not Allowed (Already exists)
        echo "Directory already exists";
        exit;
    }
    if (mkdir($targetPath, 0777, true)) {
        http_response_code(201); // Created
        echo "Directory created successfully";
    } else {
        http_response_code(500);
        echo "Failed to create directory";
    }
    exit;
}

// 3. Handle WebDAV PUT (Image / File Upload)
if ($requestMethod === 'PUT') {
    if (!empty($relativePath)) {
        // Automatically create parent subdirectories if they don't exist yet
        $parentDir = dirname($targetPath);
        if (!file_exists($parentDir)) {
            mkdir($parentDir, 0777, true);
        }

        $input = fopen("php://input", "r");
        $fp = fopen($targetPath, "w");

        if ($input && $fp) {
            while ($data = fread($input, 1024)) {
                fwrite($fp, $data);
            }
            fclose($fp);
            fclose($input);

            http_response_code(201); // Created
            echo "File created successfully";
            exit;
        } else {
            http_response_code(500);
            echo "Failed to write file";
            exit;
        }
    }
}

// 4. Handle GET (Loading images in KML balloons or browsers)
if ($requestMethod === 'GET') {
    if (file_exists($targetPath) && !is_dir($targetPath)) {
        $mime = mime_content_type($targetPath) ?: 'application/octet-stream';
        header("Content-Type: " . $mime);
        readfile($targetPath);
        exit;
    } else {
        http_response_code(404);
        echo "File or path not found";
        exit;
    }
}

// 5. Minimal PROPFIND Stub (Satisfies directory queries from DAV clients)
if ($requestMethod === 'PROPFIND') {
    header('Content-Type: application/xml; charset="utf-8"');
    http_response_code(207); // Multi-Status
    echo '<?xml version="1.0" encoding="utf-8"?><d:multistatus xmlns:d="DAV:"></d:multistatus>';
    exit;
}

http_response_code(405);
echo "Method Not Allowed";
