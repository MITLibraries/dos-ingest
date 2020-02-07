import pytest
import requests_mock
import xml.etree.ElementTree as ET

import models


@pytest.fixture
def item():
    item = ET.fromstring('<records><record><metadata><atom:entry xmlns:atom="http://www.w3.org/2005/Atom"><atom:link rel="alternate" href="http://hdl.handle.net/1234"/><atom:title>Test Title</atom:title><atom:link rel="http://www.openarchives.org/ore/terms/aggregates" href="http://dome.mit.edu/bitstream/handle/1721.3/74331/MC0356_114633.pdf?sequence=1" title="MC0356_114633.pdf" type="application/pdf" length="706590"/><atom:link rel="http://www.openarchives.org/ore/terms/aggregates" href="http://dome.mit.edu/bitstream/handle/1721.3/74331/license.txt?sequence=2" title="license.txt" type="text/plain" length="1748"/></atom:entry></metadata></record></records>')

    return item


def test_authenticate():
    """"test authenticate function."""
    with requests_mock.Mocker() as m:
        token = '123abc'.encode('utf-8')
        target_url = 'mock://dos.mock'
        username = 'test'
        password = 'test'
        m.post(f'{target_url}users/signin', content=token)
        header = models.authenticate(target_url, username, password)
        assert 'Bearer 123abc' == header['Authorization']


def test_get_bitstreams(item):
    """"test get_bitstreams function."""
    file_type = 'application/pdf'
    links = models.get_bitstreams(item, file_type, models.NS)
    for link in links:
        assert link == ('http://dome.mit.edu/bitstream/handle/1721.3/74331'
                        + '/MC0356_114633.pdf?sequence=1')


def test_extract_handle(item):
    """"test extract_handle function."""
    handle = models.extract_handle(item, models.NS)
    assert handle == 'http://hdl.handle.net/1234'


def test_post_parameters():
    """"test post_parameters function."""
    with requests_mock.Mocker() as m:
        header = {'Authorization': '123abc'}
        target_url = 'mock://mock.mock/'
        full_url = 'mock://mock.mock/object'
        full_url2 = 'mock://mock.mock/object?oid=1'
        metadata_system = 'archivesspace'
        source_system = 'dome'
        handle = 'hdl.net'
        title = 'Test title'
        bitstream_array = []
        json_object = '1'
        json_object2 = {'files': [{'path': 'dos://123'}]}
        m.post(full_url, json=json_object)
        m.get(full_url2, json=json_object2)
        links = models.post_parameters(header, target_url, metadata_system,
                                       source_system, handle, title,
                                       bitstream_array)
        for link in links:
            assert link == 'dos://123'
