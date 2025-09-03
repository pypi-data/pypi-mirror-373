import colander

from caerp.forms import files
import json


def geojson_validator(node, value):
    if value is None or value.get("delete"):
        return
    file_obj = value.get("fp")
    file_obj.seek(0)
    try:
        data = file_obj.read().decode("utf-8")
        data = json.loads(data)
        file_obj.seek(0)
    except Exception as e:
        raise colander.Invalid(node, f"Fichier geojson incorrect : {e}")

    if not isinstance(data.get("type"), str) or data["type"] != "FeatureCollection":
        raise colander.Invalid(node, "invalid geojson type")
    if not isinstance(data["features"], list):
        raise colander.Invalid(node, "incorrect features type")
    for idx, feature in enumerate(data["features"]):
        if feature["type"] != "Feature":
            raise colander.Invalid(node, f"feature {idx}: type incorrect")
        if not isinstance(feature["geometry"], dict):
            raise colander.Invalid(node, f"feature {idx} geometry incorrect")
        if not isinstance(feature["properties"], dict):
            raise colander.Invalid(node, f"feature {idx} properties incorrect")
        if not feature["properties"].get("name"):
            raise colander.Invalid(node, f"feature {idx} property 'name' non trouvée")
        if not feature["properties"].get("description"):
            raise colander.Invalid(
                node, f"feature {idx} property 'description' non trouvée"
            )
    file_obj.seek(0)


class CAEPlacesSchema(colander.MappingSchema):
    """
    CAE locations schema
    """

    cae_places = files.FileNode(
        title="Choix du fichier geojson",
        description="Remplacer la liste",
        show_delete_control=True,
        missing=colander.drop,
        validator=geojson_validator,
    )
