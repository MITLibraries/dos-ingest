import csv
import requests

NS = {'oai': 'http://www.openarchives.org/OAI/2.0/',
      'atom': 'http://www.w3.org/2005/Atom'}


def authenticate(target_url, username, password):
    "Authenticates user to the DOS API."
    username = 'admin'
    password = 'admin'
    data = {'username': username, 'password': password}
    session = requests.post(f'{target_url}users/signin', params=data).content
    session = session.decode('utf-8')
    header = {'Authorization': f'Bearer {session}'}
    return header


def get_bitstreams(item, file_type, namespace):
    """"Retrieves the bitstreams of the specified item."""
    for element in item.iterfind('.//atom:link', namespace):
        if element.attrib.get('type') == file_type:
            yield element.attrib['href']


def extract_handle(item, namespace):
    """"Retrieves the bitstreams of the specified item."""
    handle = ''
    handle = item.find('.//atom:link[@rel="alternate"]',
                       namespaces=namespace)
    if handle is not None:
        handle = handle.attrib['href']
    return handle


def post_parameters(header, target_url, metadata_system, source_system, handle,
                    title, bitstream_array):
    """"Posts parameters to API endpoint."""
    params = {}
    params['metadata_system'] = metadata_system
    params['source_system'] = source_system
    params['handle'] = handle
    params['title'] = title
    params['target_links'] = bitstream_array
    id = requests.post(f'{target_url}object', headers=header,
                       params=params).json()
    dig_obj = requests.get(f'{target_url}object?oid={id}', headers=header,
                           params=params).json()
    links = dig_obj.get('files')
    for link in links:
        yield link['path']


def create_ingest_report(ingest_data, file_name):
    """Creates ingest report of handles and DOS links."""
    with open(f'{file_name}-dos-ingest.csv', 'w') as writecsv:
        writer = csv.writer(writecsv)
        writer.writerow(['handle'] + ['dos_link'])
        for link, handle in ingest_data.items():
            writer.writerow([handle] + [link])
