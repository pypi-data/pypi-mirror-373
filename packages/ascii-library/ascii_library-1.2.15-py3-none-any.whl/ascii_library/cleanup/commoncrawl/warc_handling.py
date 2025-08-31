import logging
import os
from io import BytesIO
from tempfile import SpooledTemporaryFile, TemporaryFile

import botocore
import requests
from fastwarc.stream_io import FastWARCError
from fastwarc.warc import ArchiveIterator as FastWarcArchiveIterator
from fastwarc.warc import WarcRecord, WarcRecordType

from ascii_library.cleanup.commoncrawl.urls import data_url_pattern

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_payload_stream(record: WarcRecord):
    return record.reader


def get_warc_header(record: WarcRecord, header: str, default: str = None):
    return record.headers.get(header, default)


def get_http_headers(record: WarcRecord):
    return record.http_headers.astuples()  # type: ignore


def is_response_record(record: WarcRecord):
    """Return true if WARC record is a WARC response record"""
    return record.record_type == WarcRecordType.response


def is_wet_text_record(record: WarcRecord):
    """Return true if WARC record is a WET text/plain record"""
    return (
        record.record_type == WarcRecordType.conversion
        and record.headers.get("Content-Type") == "text/plain"
    )


def is_wat_json_record(record: WarcRecord):
    """Return true if WARC record is a WAT record"""
    return (
        record.record_type == WarcRecordType.metadata
        and record.headers.get("Content-Type") == "application/json"
    )


def is_html(record: WarcRecord):  # noqa: C901
    """Return true if (detected) MIME type of a record is HTML"""
    html_types = ["text/html", "application/xhtml+xml"]
    if ("WARC-Identified-Payload-Type" in record.headers) and (
        record.headers["WARC-Identified-Payload-Type"] in html_types
    ):
        return True
    for name, value in record.http_headers.astuples():  # type: ignore
        if name.lower() == "content-type":
            content_type = value.lower()
            for html_type in html_types:
                if html_type in content_type:
                    return True
    return False


def fetch_warc(  # noqa: C901
    uri, warc_input_failed, base_uri=None, offset=-1, length=-1, s3client=None
):
    """Fetch WARC/WAT/WET files (or a record if offset and length are given)"""
    # s3client = boto3.client('s3', use_ssl=False)

    (scheme, netloc, path) = (None, None, None)
    uri_match = data_url_pattern.match(uri)
    if not uri_match and base_uri:
        # relative input URI (path) and base URI defined
        uri = base_uri + uri
        uri_match = data_url_pattern.match(uri)

    if uri_match:
        (scheme, netloc, path) = uri_match.groups()
    else:
        # keep local file paths as is
        path = uri

    stream = None

    if scheme in ["s3", "s3a"]:
        bucketname = netloc
        if not bucketname:
            logger.error("Invalid S3 URI: " + uri)
            return
        if not path:
            logger.error("Empty S3 path: " + uri)
            return
        elif path[0] == "/":
            # must strip leading / in S3 path
            path = path[1:]
        if offset > -1 and length > 0:
            rangereq = "bytes={}-{}".format(offset, (offset + length - 1))
            # Note: avoid logging too many small fetches
            logger.debug("Fetching {} ({})".format(uri, rangereq))
            try:
                response = s3client.get_object(
                    Bucket=bucketname, Key=path, Range=rangereq
                )
                stream = BytesIO(response["Body"].read())
            except botocore.client.ClientError as e:  # type: ignore
                logger.error(
                    "Failed to download: s3://{}/{} (offset: {}, length: {}) - {}".format(
                        bucketname, path, offset, length, e
                    )
                )
                warc_input_failed.add(1)
                return
        else:
            logger.info("Reading from S3 {}".format(uri))
            # download entire file using a temporary file for buffering
            warctemp = TemporaryFile(mode="w+b")  # , dir=args.local_temp_dir)
            # print('***************')
            # print(warctemp.name)
            try:
                s3client.download_fileobj(bucketname, path, warctemp)
                warctemp.seek(0)
                stream = warctemp
                # stream = input_data
                # stream = FastWarcArchiveIterator(open(input_data, 'rb'))
            except botocore.client.ClientError as e:  # type: ignore
                logger.error("Failed to download {}: {}".format(uri, e))
                warc_input_failed.add(1)
                warctemp.close()

    elif scheme == "http" or scheme == "https":
        headers = None
        if offset > -1 and length > 0:
            headers = {"Range": "bytes={}-{}".format(offset, (offset + length - 1))}
            # Note: avoid logging many small fetches
            logger.debug("Fetching {} ({})".format(uri, headers))
        else:
            logger.info("Fetching {}".format(uri))
            pass
        response = requests.get(uri, headers=headers)

        if response.ok:
            # includes "HTTP 206 Partial Content" for range requests
            warctemp = SpooledTemporaryFile(
                max_size=2097152,
                mode="w+b",
                # dir=args.local_temp_dir
            )
            warctemp.write(response.content)
            warctemp.seek(0)
            stream = warctemp
        else:
            logger.error("Failed to download {}: {}".format(uri, response.status_code))
            pass

    elif scheme == "hdfs":
        try:
            import pydoop.hdfs as hdfs  # type: ignore

            logger.error("Reading from HDFS {}".format(uri))
            stream = hdfs.open(uri)
        except RuntimeError as e:
            logger.error("Failed to open {}: {}".format(uri, e))
            warc_input_failed.add(1)

    else:
        logger.info("Reading local file {}".format(uri))
        if scheme == "file":
            # must be an absolute path
            uri = os.path.join("/", path)
        else:
            base_dir = os.path.abspath(os.path.dirname(__file__))
            uri = os.path.join(base_dir, uri)
        try:
            stream = open(uri, "rb")
        except IOError as e:
            logger.error("Failed to open {}: {}".format(uri, e))
            warc_input_failed.add(1)

    return stream


def iterate_records(warc_uri, archive_iterator, process_record, records_processed):
    """Iterate over all WARC records and process them"""
    for record in archive_iterator:
        for res in process_record(record):
            yield res
        records_processed.add(1)


def process_warc(uri, stream, warc_input_failed, process_record, records_processed):
    """Parse a WARC (or WAT/WET file) via FastWARC"""
    # process only WARC response and metadata (including WAT) records
    # WarcRecordType.metadata |
    fastwarc_record_filter = WarcRecordType.response

    warc_parse_http_header = True
    try:
        rec_iter = FastWarcArchiveIterator(
            stream,
            record_types=fastwarc_record_filter,
            parse_http=warc_parse_http_header,
        )
        for res in iterate_records(
            uri,
            rec_iter,
            process_record=process_record,
            records_processed=records_processed,
        ):
            yield res
    except FastWARCError as e:
        warc_input_failed.add(1)
        logger.error("Invalid WARC: {} - {}".format(uri, e))
