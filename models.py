def get_bitstreams(item, file_type):
    """"Retrieves the bitstreams of the specified item"""
    elements = item.iter()
    link_tag = '{http://www.w3.org/2005/Atom}link'
    for element in [e for e in elements if e.tag == link_tag
                    and 'type' in e.attrib.keys()
                    and e.attrib['type'] == file_type]:
        link = element.attrib['href']
        yield link


def extract_handle(item):
    """"Retrieves the bitstreams of the specified item"""
    elements = item.iter()
    link_tag = '{http://www.w3.org/2005/Atom}link'
    for element in [e for e in elements if e.tag == link_tag
                    and e.attrib['rel'] == 'alternate']:
        handle = element.attrib['href']
        return handle


def extract_title(item):
    """"Retrieves the bitstreams of the specified item"""
    elements = item.iter()
    link_tag = '{http://www.w3.org/2005/Atom}title'
    for element in [e for e in elements if e.tag == link_tag]:
        title = element.text
        return title
