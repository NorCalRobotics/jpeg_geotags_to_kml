var json_promise = fetch('cloud.json');
var schema_promise = fetch('cloud.schema.json');
var configuration = await json_promise.json();
var config_schema = await schema_promise.json();

function create_config_form(parentElementId = "form-holder"){
    var parentElement = document.getElementById(parentElementId);

    const editor = new window.JSONEditor(parentElement, {
            schema: config_schema,
            theme: 'html',
            disable_collapse: true,
            disable_properties: true
        });
        
    editor.setValue(configuration);

    // Expose editor globally so your main pipeline button can read from it later
    window.currentFormEditor = editor;
}

create_config_form();