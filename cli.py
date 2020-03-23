import datetime
import glob
import logging

import click
import structlog
import xml.etree.ElementTree as ET

import models

logger = structlog.get_logger()


@click.group()
@click.option('-m', '--metadata_system', prompt='Enter metadata system',
              help='The metadata system of record.')
@click.option('-s', '--source_system', prompt='Enter source system',
              help='The source system of the object.')
@click.option('-f', '--file_type', prompt='Enter file type',
              help='The MIME file type to export.')
@click.option('-t', '--target_url', envvar='TARGET_URL')
@click.option('-u', '--username', prompt='Enter username',
              envvar='TEST_USERNAME', help='The username for authentication.')
@click.option('-p', '--password', prompt='Enter password',
              envvar='TEST_PASS', hide_input=True,
              help='The password for authentication.')
@click.pass_context
def main(ctx, metadata_system, source_system, file_type, target_url, username,
         password):
    dt = datetime.datetime.utcnow().isoformat(timespec='seconds')
    log_suffix = f'{dt}.log'
    structlog.configure(processors=[
                        structlog.stdlib.filter_by_level,
                        structlog.stdlib.add_log_level,
                        structlog.stdlib.PositionalArgumentsFormatter(),
                        structlog.processors.TimeStamper(fmt="iso"),
                        structlog.processors.JSONRenderer()
                        ],
                        context_class=dict,
                        logger_factory=structlog.stdlib.LoggerFactory())
    logging.basicConfig(format="%(message)s",
                        handlers=[logging.FileHandler(f'logs/log-{log_suffix}',
                                  'w')],
                        level=logging.INFO)
    logger.info('Application start')
    header = models.authenticate(target_url, username, password)
    logger.info('Authenticated')
    ctx.obj = {}
    ctx.obj['metadata_system'] = metadata_system
    ctx.obj['source_system'] = source_system
    ctx.obj['file_type'] = file_type
    ctx.obj['target_url'] = target_url
    ctx.obj['header'] = header


@main.command()
@click.argument('file_name')
@click.pass_context
def oai(ctx, file_name):
    """"Exports the bitstream links of a file type from a collection"""
    metadata_system = ctx.obj['metadata_system']
    source_system = ctx.obj['source_system']
    file_type = ctx.obj['file_type']
    target_url = ctx.obj['target_url']
    header = ctx.obj['header']
    items = ET.parse(file_name)
    ingest_data = {}
    for item in items.iterfind('oai:record', models.NS):
        handle = models.extract_handle(item, models.NS)
        if handle == '':
            continue
        title = item.findtext('.//atom:title', namespaces=models.NS)
        bitstreams = models.get_bitstreams(item, file_type, models.NS)
        for bitstream in bitstreams:
            files = {}
            files['file'] = bitstream
            resp = models.post_parameters(header, target_url, metadata_system,
                                          source_system, handle, title, files)
            for link in resp['files']:
                logger.info(link)
                ingest_data[link] = handle
    models.create_ingest_report(ingest_data, file_name)


@main.command()
@click.argument('file_path')
@click.pass_context
def file(ctx, file_path):
    metadata_system = ctx.obj['metadata_system']
    source_system = ctx.obj['source_system']
    file_type = ctx.obj['file_type']
    target_url = ctx.obj['target_url']
    files = glob.glob(f'{file_path}/**/*.{file_type}', recursive=True)
    for file in files:
        title = ''
        handle = ''
        bitstream_array = [file]
        id = models.post_parameters(target_url, metadata_system, source_system,
                                    handle, title, bitstream_array)
        logger.info(id)


if __name__ == '__main__':
    main()
