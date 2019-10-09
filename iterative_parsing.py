import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
    tags_with_counts = {}
    for event, element in ET.iterparse(filename):
        if element.tag in tags_with_counts:
            tags_with_counts[element.tag] += 1
        else:
            tags_with_counts[element.tag] = 1
    return tags_with_counts
