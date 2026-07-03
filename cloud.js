import { createJSONEditor, createAjvValidator } from 'https://cdn.jsdelivr.net/npm/vanilla-jsoneditor@3.12.0/index.js'

var json_promise = fetch('cloud.json');
var schema_promise = fetch('cloud.schema.json');
var configuration = null;
var config_schema = null;

const cookie_var_name = 'user_config';
const cookie_secs = 60 * 60 * 24 * 365; // 1 year
const cookie_delim = ';';
const cookie_assignment = '=';
const cookie_path = '/';

async function initialize(){
    configuration = await json_promise.json();
    config_schema = await schema_promise.json();

    const cookieConfig = loadUserConfigFromCookie();
    if (cookieConfig !== null) {
        configuration = cookieConfig;
    }

    create_config_form();
}

function parseCookies() {
    return document.cookie.split(cookie_delim).reduce((cookies, rawCookie) => {
        const [name, ...valueParts] = rawCookie.split(cookie_assignment);
        const cookieName = name.trim();
        if (!cookieName) {
            return cookies;
        }

        cookies[cookieName] = valueParts.join(cookie_assignment);
        return cookies;
    }, {});
}

function loadUserConfigFromCookie() {
    const cookies = parseCookies();
    const cookieValue = cookies[cookie_var_name];

    if (!cookieValue) {
        return null;
    }

    try {
        return JSON.parse(decodeURIComponent(cookieValue));
    } catch (e) {
        console.warn('Unable to parse user config cookie:', e);
        return null;
    }
}

function create_config_form(parentElementId = "form-holder"){
    var parentElement = document.getElementById(parentElementId);
    var schema_validator = createAjvValidator({ schema: config_schema });
    var editor_properties = {
        content: {
            json: configuration
        },
        validator: schema_validator,
        onChange: (updatedContent) => {
            if (updatedContent && updatedContent.json !== undefined) {
                configuration = updatedContent.json;
                saveUserConfigToCookie(configuration);
            }
        }
    };
    var editor_kwargs = {
        target: parentElement,
        props: editor_properties
    };

    var editor = createJSONEditor(editor_kwargs);

    // Expose editor globally so your main pipeline button can read from it later
    window.currentFormEditor = editor;
}

function saveUserConfigToCookie(config) {
    var cookie_s = `${cookie_var_name}${cookie_assignment}` + encodeURIComponent(JSON.stringify(config));
    cookie_s += `${cookie_delim} path${cookie_assignment}${cookie_path}`;
    cookie_s += `${cookie_delim} max-age${cookie_assignment}${cookie_secs}`;
    document.cookie = cookie_s;
}

function getUploadUrl(file) {
    if (!configuration) {
        throw new Error('Upload configuration is not loaded');
    }

    if (configuration.url_fmt && configuration.url_fmt.includes('{photo_path}')) {
        return configuration.url_fmt.replace('{photo_path}', encodeURIComponent(file.name));
    }

    if (configuration.upload_url) {
        var baseUrl = configuration.upload_url;
        var separator = baseUrl.endsWith('/') ? '' : '/';
        return `${baseUrl}${separator}${encodeURIComponent(file.name)}`;
    }

    throw new Error('No upload URL configured in cloud.json');
}

async function uploadImageFile(file) {
    var uploadUrl = getUploadUrl(file);
    var headers = (configuration && configuration.headers) ? configuration.headers : {};

    var response = await fetch(uploadUrl, {
        method: 'PUT',
        headers: headers,
        body: file
    });

    if (!response.ok) {
        throw new Error(`Upload failed for ${file.name}: ${response.status} ${response.statusText}`);
    }

    return response;
}

async function uploadPendingPhotoFiles() {
    var photoPicker = document.getElementById('photo-picker');
    if (!photoPicker || !photoPicker.files) {
        throw new Error('photo-picker element not found or has no files');
    }

    var pendingFiles = Array.from(photoPicker.files);
    var uploadResults = [];

    for (var i = 0; i < pendingFiles.length; i++) {
        var file = pendingFiles[i];
        var result = await uploadImageFile(file);
        uploadResults.push({ file: file, status: result.status });
    }

    return uploadResults;
}

window.uploadPendingPhotoFiles = uploadPendingPhotoFiles;

initialize();