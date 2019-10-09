import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
# Import functions and variables from the improving_street_names file.
from improving_street_names import *

import schema

OSM_PATH = "toronto_canada.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    # Tags are handled the same for node and way.
    for tag in element.iter('tag'):
        tag_attribs = {}
        tag_attribs['id'] = element.attrib['id']
        if ':' in tag.get('k'):
            location_of_colon = tag.get('k').index(':')
            tag_attribs['type'] = tag.get('k')[:location_of_colon]
            tag_attribs['key'] = tag.get('k')[location_of_colon+1:]
        else:
            tag_attribs['key'] = tag.get('k')
            tag_attribs['type'] = 'regular'
        # Correct street name, province name, and postal code key values.
        if is_street_name(tag):
            tag_attribs['value'] = update_street_name(tag.get('v'), mapping)
        elif is_province_name(tag):
            tag_attribs['value'] = update_province_name(tag.get('v'))
        elif is_postal_code(tag):
            tag_attribs['value'] = update_post_code(tag.get('v'))
        else:
            tag_attribs['value'] = tag.get('v')         
        if PROBLEMCHARS.findall(tag.get('k')) != []:
            del tag_attribs['key']
        tags.append(tag_attribs)
    # Populate node attributes.
    if element.tag == 'node':
        for field in NODE_FIELDS:
            node_attribs[field] = element.get(field)
        return {'node': node_attribs, 'node_tags': tags}
    # Populate way attributes
    elif element.tag == 'way':
        for field in WAY_FIELDS:
            way_attribs[field] = element.get(field)
        count = 0
        # Populate way nodes
        for way_node in element.iter('nd'):
            way_node_attribs = {}
            way_node_attribs['id'] = element.attrib['id']
            way_node_attribs['node_id'] = way_node.get('ref')
            way_node_attribs['position'] = count
            count += 1
            way_nodes.append(way_node_attribs)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

process_map(OSM_PATH, validate=False)