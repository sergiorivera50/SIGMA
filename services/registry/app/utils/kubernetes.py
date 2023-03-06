from flask import current_app
import os
import yaml


def parse_manifest(filename, manifests_dir="manifests", **values):
    path = os.path.join(current_app.root_path, manifests_dir, filename)
    tmpl = open(path, "rt").read()
    text = tmpl.format(**values)
    return yaml.safe_load(text)
