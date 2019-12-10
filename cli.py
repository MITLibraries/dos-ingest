import click
import requests
import xml.etree.ElementTree as ET

import models


@click.group()
@click.argument('file_name')
@click.pass_context
def main(ctx, file_name):
    with open(file_name, 'rb') as f:
        items = ET.parse(f)
        ctx.obj = {}
        ctx.obj['items'] = items.iter()


@main.command()
@click.option('-m', '--metadata_source', prompt='Enter metadata system',
              help='The metadata system of record.')
@click.option('-f', '--file_type', prompt='Enter file type',
              help='The MIME file type to export.')
@click.option('-u', '--target_url', prompt='Enter target URL',
              help='The target URL for ingest.')
@click.pass_context
def export(ctx, metadata_source, file_type, target_url):
    """"Exports the bitstream links of a file type from a collection"""
    items = ctx.obj['items']
    record_tag = '{http://www.openarchives.org/OAI/2.0/}record'
    for item in [e for e in items if e.tag == record_tag]:
        handle = models.extract_handle(item)
        title = models.extract_title(item)
        bitstreams = models.get_bitstreams(item, file_type)
        bitstream_array = []
        for bitstream in bitstreams:
            bitstream_array.append(bitstream)
        params = {}
        params['metadata_source'] = metadata_source
        params['handle'] = handle
        params['title'] = title
        params['bitstreams'] = bitstream_array
        params = [params]
        # Will add to header as authentication method becomes clearer
        header = {}
        id = requests.post(target_url, headers=header,
                           params=params).json()


if __name__ == '__main__':
    main()
