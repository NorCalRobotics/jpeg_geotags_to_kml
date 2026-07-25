const cookie_var_name = 'user_config';
const cookie_secs = 60 * 60 * 24 * 365; // 1 year
const cookie_delim = ';';
const cookie_assignment = '=';
const cookie_path = '/';

const default_ids = {
    'parent': 'form-holder',
    'textarea': 'cloud-settings',
    'validate': 'validate-btn',
    'save': 'save-btn'
};

var validated_json = null;
var is_valid_json = false;

function cookiesToDict() {
    const cookieDict = {};

    for (const currentCookie of document.cookie.split(cookie_delim)) {
        const [name, ...valueParts] = currentCookie.split(cookie_assignment);
        const cookieName = name.trim();
        if (!cookieName) {
            continue;
        }

        cookieDict[cookieName] = valueParts.join(cookie_assignment);
    }

    return cookieDict;
}

function loadUserConfigFromCookie() {
    const cookies = cookiesToDict();
    const cookieValue = cookies[cookie_var_name];

    if (!cookieValue) {
        return null;
    }

    try {
        return decodeURIComponent(cookieValue);
    } catch (e) {
        console.warn('Unable to parse user config cookie:', e);
        return null;
    }
}

function saveUserConfigToCookie(config) {
    var cookie_s = `${cookie_var_name}${cookie_assignment}` + encodeURIComponent(config);
    cookie_s += `${cookie_delim} path${cookie_assignment}${cookie_path}`;
    cookie_s += `${cookie_delim} max-age${cookie_assignment}${cookie_secs}`;
    document.cookie = cookie_s;
}

async function setCloudConfig(config) {
    while (!(typeof window.sync_cloud_config === 'function')) {
        await new Promise(resolve => setTimeout(resolve, 50));
    }
    window.config = config;
    window.sync_cloud_config();
}

function saveUserConfig(id = default_ids) {
    var textAreaElement = document.getElementById(id['textarea']);
    var validateButton = document.getElementById(id['validate']);
    var saveButton = document.getElementById(id['save']);
    var json = textAreaElement.value;
    var settings = JSON.parse(json);

    saveUserConfigToCookie(json);
    setCloudConfig(json);
    validateButton.disabled = true;
    saveButton.disabled = true;
}

function validateUserConfig(id = default_ids) {
    var textAreaElement = document.getElementById(id['textarea']);
    var validateButton = document.getElementById(id['validate']);
    var saveButton = document.getElementById(id['save']);
    var validation = window.validate_cloud_config(textAreaElement.value);

    is_valid_json = validation.ok;
    if(!is_valid_json){
        textAreaElement.after.innerHTML = `<br/><p style="color:red;">${validation.error}</p>`;
        validateButton.disabled = false;
        saveButton.disabled = true;
        return;
    } 

    textAreaElement.after.innerHTML = `<br/><p style="color:green;">OK!</p>`;
    validated_json = textAreaElement.value;
    validateButton.disabled = true;
    saveButton.disabled = false;
}

function create_config_form(id = default_ids) {
    var parentElement = document.getElementById(id['parent']);
    var textAreaElement = document.getElementById(id['textarea']);
    var validateButton = document.getElementById(id['validate']);
    var saveButton = document.getElementById(id['save']);

    textAreaElement.value = validated_json;
    is_valid_json = true;

    validateButton.disabled = true;
    saveButton.disabled = true;

    textAreaElement.addEventListener('input', () => {
        is_valid_json = validated_json == textAreaElement.value
        validateButton.disabled = is_valid_json;
        saveButton.disabled = true;
    });
}

async function initialize() {
    var cookie_config;

    if(cookie_config = loadUserConfigFromCookie()) {
        validated_json = cookie_config;
        var settings = JSON.parse(cookie_config);
        await setCloudConfig(cookie_config);
    } else {
        validated_json = await fetch("cloud.json").then(res => res.text());
    }

    window.saveUserConfig = saveUserConfig;
    window.validateUserConfig = validateUserConfig;

    if(document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            create_config_form();
        });
    } else {
        create_config_form();
    }
}

initialize();