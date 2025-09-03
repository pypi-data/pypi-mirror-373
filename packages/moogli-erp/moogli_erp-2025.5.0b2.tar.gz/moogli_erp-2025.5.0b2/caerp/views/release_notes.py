"""
Release notes view
"""
import json
from caerp.utils.sys_environment import resource_filename


def release_notes(request):
    # Récupération des notes de version depuis le fichier JSON
    release_notes_filepath = resource_filename("static/release_notes.json")
    with open(release_notes_filepath) as release_notes_file:
        data = json.load(release_notes_file)
    release_notes = data["release_notes"]
    # Est-ce qu'on veut la version "Entrepreneurs" ?
    version_es = "version_es" in request.params
    # Traitement des données pour envoi au template
    i = 1
    for version in release_notes:
        version["version_code"] = version["version"].replace(".", "")
        version["is_last_version"] = i == 1
        version["notes"] = []
        version_notes = version.pop("changelog")
        for note in version_notes:
            if version_es:
                # On ne garde que les infos dédiées aux entrepreneurs
                if "target" in note and note["target"] in ["all", "entrepreneur"]:
                    version["notes"].append(note)
            else:
                # On affiche les infos classiques
                """
                Sans les notes destinées uniquement aux entrepreneurs, partant du
                principe qu'elles ne sont qu'une reformulation d'une note existante
                """
                if "target" in note and note["target"] == "entrepreneur":
                    continue
                version["notes"].append(note)
        i = i + 1
    return dict(
        title="Notes de version",
        release_notes=release_notes,
        version_es=version_es,
    )


def includeme(config):
    config.add_route("release_notes", "/release_notes")
    config.add_view(
        release_notes,
        route_name="release_notes",
        renderer="release_notes.mako",
    )
