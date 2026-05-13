import os
import sys
import json
import tkinter as tk


repo_dir = sys.path[0]
submodule_path = os.path.join(repo_dir, "tkinter-json-editor")
if submodule_path not in sys.path:
    sys.path.append(submodule_path)
from JsonEditor import JsonEditor


def json_schema_gui(schema_filename, json_filename):
    if not os.path.exists(schema_filename):
        return

    with open(schema_filename, "r") as schema_file:
        schema = json.load(schema_file)

    # Pass in your schema-compliant data
    root = tk.Tk()
    editor = JsonEditor(root, schema=schema)
    editor.set_title(schema["title"])

    # Load the user's current settings
    if os.path.exists(json_filename):
        editor.load_json_from_file(json_filename)
    root.mainloop()


def www_server_gui():
    # Load your local schema
    www_schema_filename = os.path.join(repo_dir, "www_server.schema.json")
    www_json_filename = os.path.join(repo_dir, "www_server.json")

    json_schema_gui(www_schema_filename, www_json_filename)


def photo_collection_gui():
    # Load your local schema
    schema_filename = os.path.join(repo_dir, "photo_collection_settings.schema.json")
    json_filename = os.path.join(repo_dir, "photo_collection_settings.json")

    json_schema_gui(schema_filename, json_filename)


if __name__ == "__main__":
    print(photo_collection_gui())