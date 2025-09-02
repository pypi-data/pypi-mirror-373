from typing import Union

from lxml import objectify

from prosuite.utils.file import load_file_as_string


def objectify_xml(path_file) -> objectify.ObjectifiedElement:
    """
    Try to objectify the xml file and return the objectified element. Return None if it fails.
    """
    try:
        return objectify.parse(path_file).getroot()
    except:
        raise Exception(f"Error parsing {path_file}")


def try_get_lxml_attrib(node: objectify.ObjectifiedElement, attribute_name: str) -> Union[str, None]:
    """
    If the attribute exists on the objectified node then return it, else return None
    """
    if attribute_name in node.attrib.keys():
        return node.attrib[attribute_name]
    else:
        return None


def to_spatial_reference_xml(sr_id: str):
    if sr_id.lower() == "lv95":
        return load_file_as_string("LV95.txt")
    elif sr_id.lower() == "lv03":
        return load_file_as_string("LV_03.txt")
    else:
        raise Exception
