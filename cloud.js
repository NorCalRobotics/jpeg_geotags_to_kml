import { createJSONEditor, createAjvValidator } from 'https://cdn.jsdelivr.net/npm/vanilla-jsoneditor@3.12.0/index.js'

var schema_promise = fetch('cloud.schema.json');

/*
const cookie_var_name = 'user_config';
const cookie_secs = 60 * 60 * 24 * 365; // 1 year
const cookie_delim = ';';
const cookie_assignment = '=';
const cookie_path = '/';

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

function saveUserConfigToCookie(config) {
    var cookie_s = `${cookie_var_name}${cookie_assignment}` + encodeURIComponent(JSON.stringify(config));
    cookie_s += `${cookie_delim} path${cookie_assignment}${cookie_path}`;
    cookie_s += `${cookie_delim} max-age${cookie_assignment}${cookie_secs}`;
    document.cookie = cookie_s;
}
*/

async function create_config_form(parentElementId = "form-holder"){
    var parentElement = document.getElementById(parentElementId);
    var schema_validator = createAjvValidator({ schema: await schema_promise.json() });
    var editor_properties = {
        content: {
            json: window.configuration // supplied by http_server.py
        },
        validator: schema_validator,
        onChange: (updatedContent) => {
            if (updatedContent && updatedContent.json !== undefined) {
                window.configuration = updatedContent.json;
                // saveUserConfigToCookie(configuration);
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

create_config_form();