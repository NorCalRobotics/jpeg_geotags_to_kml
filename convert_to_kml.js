async function convertToKML() {
    var titleTextBox = document.getElementById("project-name"), title;

    if(titleTextBox && titleTextBox.value.trim() !== "") {
        title = titleTextBox.value.trim();
    }
    else {
        title = "UntitledProject";
    }

    await window.convert_photos_to_kml(title, document.getElementById("photo-picker").files);
}