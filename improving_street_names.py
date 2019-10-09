import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "sample.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Circle", "Way", "Terrace", "Crescent", "Harbour", "Trail"]

mapping = { "St": "Street",
            "St.": "Street",
            "STREET": "Street",
            "street": "Street",
            "Rd.": "Road",
            "Rd": "Road",
            "road": "Road",
            "rd": "rd",
            "Blvd": "Boulevard",
            "Boulevade": "Boulevard",
            "Crt": "Court",
            "Ct": "Court",
            "Dr.": "Drive",
            "Dr": "Drive",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "avenue": "Avenue",
            "Pkwy": "Parkway",
            "PKWY": "Parkway",
            "Ln": "Lane",
            "LN": "Lane",
            "Pl.": "Place",
            "Pl": "Place",
            "Sq": "Square",
            "Sq.": "Square",
            "Cresent": "Crescent",
            "Trl": "Trail",
            "89)": "89",
            "Hrbr": "Harbour",
            "Cir": "Circle"}


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street") or (elem.attrib['k'] == "destination:street")


def audit_street(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_street_name(name, mapping):
    m = street_type_re.search(name)
    if m:
        street_ending = m.group()
        if street_ending not in expected:
            if street_ending in mapping.keys():
                return re.sub(street_type_re, mapping[street_ending], name)
            else:
                return name
        else:
            return name
#
#
# PROVINCE NAMES
#
#
# The following three functions audit and provide the functions to identify and fix the inconsistencies of the province names.
def is_province_name(elem):
    return (elem.attrib['k'] == "addr:province")

def audit_province(filename):
    osm_file = open(filename, "r")
    province_list = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == "addr:province" and tag.attrib['v'] != "ON":
                    province_list.add(tag.attrib['v'])
    osm_file.close()
    return province_list

def update_province_name(name):
    if name == 'Ontario':
        return 'ON'
    else:
        return name
#
#
# POSTAL CODES
#
#
# The following functions audit, identify, and fix the inconsistencies of the postal codes.
def is_postal_code(elem):
    return (elem.attrib['k'] == 'addr:postcode')

# Canadian format of postal code. The postal code can either have a space inbetween the first three and last three character or have no space.
post_code_re = re.compile(r'[A-z]\d[A-z]\s?\d[A-z]\d')

def audit_post_code_type(post_code):
    m = post_code_re.match(post_code)
    # Check if postal code is in a non-Canadian format.
    if m is None:
        return post_code
               
def audit_post_code(osmfile):
    osm_file = open(osmfile, "r")
    post_code_list = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postal_code(tag):
                    if audit_post_code_type(tag.attrib['v']) is not None:
                        post_code_list.add(tag.attrib['v'])
    osm_file.close()
    return post_code_list

def update_post_code(post_code):
    # Remove all spaces (" ") from the postal code to remove potential spaces before or after postal code (e.g. " M5J0A8 " -> "M5J0A8")
    post_code = post_code.replace(" ", "")
    # Make sure all characters are upper case.
    post_code = post_code.upper()
    # Return postal code with space inbetween first three character and last three characters.
    return post_code[:3] + " " + post_code[3:]


    
    
    



