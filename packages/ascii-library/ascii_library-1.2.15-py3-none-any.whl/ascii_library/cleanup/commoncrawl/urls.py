import logging
import re
from urllib.parse import urljoin, urlparse

import cchardet
import idna
import tldextract
from bs4 import BeautifulSoup

from ascii_library.cleanup.commoncrawl.text_extraction import TextExtractor

logging.basicConfig(
    level=logging.WARN, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# from surt import surt

# url_parse_host_pattern = re.compile(
#    r"^https?://([a-z0-9_.-]{2,253})(?:[/?#]|\Z)", re.IGNORECASE | re.ASCII
# )
# match IP addresses
# - including IPs with leading `www.' (stripped)
ip_pattern = re.compile(r"^(?:www\.)?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\Z")


# valid host names, relaxed allowing underscore, allowing also IDNAs
# https://en.wikipedia.org/wiki/Hostname#Restrictions_on_valid_hostnames
host_part_pattern = re.compile(
    r"^[a-z0-9]([a-z0-9_-]{0,61}[a-z0-9])?\Z", re.IGNORECASE | re.ASCII
)

# pattern to split a data URL (<scheme>://<netloc>/<path> or <scheme>:/<path>)
data_url_pattern = re.compile("^(s3|s3a|https?|file|hdfs):(?://([^/]*))?/(.*)")


def get_surt_host(url):  # noqa: C901
    extracted = tldextract.extract(url, include_psl_private_domains=True)
    registered_domain = extracted.registered_domain

    if registered_domain == "":
        registered_domain = f"{extracted.subdomain}.{extracted.domain}"
        if registered_domain == "":
            try:
                # Fallback to urlparse if tldextract fails
                host = urlparse(url).hostname
            except Exception as e:
                logger.debug(f"Failed to parse URL {url}: {e}")
                return None
            if not host:
                return None
        else:
            host = registered_domain
    else:
        host = registered_domain

    host = host.strip().lower()
    if len(host) < 1 or len(host) > 253:
        return None
    if ip_pattern.match(host):
        return None
    parts = host.split(".")
    if parts[-1] == "":
        # trailing dot is allowed, strip it
        parts = parts[0:-1]
    if len(parts) <= 1:
        # do not accept single-word hosts, must be at least `domain.tld'
        return None
    if len(parts) > 2 and parts[0] == "www":
        # strip leading 'www' to reduce number of "duplicate" hosts,
        # but leave at least 2 trailing parts (www.com is a valid domain)
        parts = parts[1:]
    for i, part in enumerate(parts):
        if len(part) > 63:
            return None
        if not host_part_pattern.match(part):
            try:
                idn = idna.encode(part).decode("ascii")
            except (
                idna.IDNAError,
                idna.core.InvalidCodepoint,
                UnicodeError,
                IndexError,
                Exception,
            ):
                logger.debug("Invalid host name: {}".format(url))
                return None

            # TODO: idna verifies the resulting string for length restrictions or invalid chars,
            #       maybe no further verification is required:
            if host_part_pattern.match(idn):
                parts[i] = idn
            else:
                logger.debug("Invalid host name: {}".format(url))
                return None
    parts.reverse()
    return ".".join(parts)


# get_surt_host('https://google.com')


def get_surt_host_tld(url):
    # Use tldextract to get the registered domain
    extracted = tldextract.extract(url, include_psl_private_domains=True)
    registered_domain = extracted.registered_domain

    # Form the src_url_surt_host using the registered domain
    surt_host = f"https://{registered_domain}"
    return surt_host


def compute_surt_host(src_url, url):
    u = urljoin(src_url, url)
    # res = get_surt_host(u)
    res = get_surt_host(
        f"https://{tldextract.extract(u, include_psl_private_domains=True).registered_domain}"
    )
    return res


def auto_parse(content):
    content_start = content.strip()[
        :20
    ]  # Checking the first 20 characters, adjust as needed
    if content_start.startswith("<?xml"):
        return "lxml-xml"
    elif "<!DOCTYPE" in content_start or "<html" in content_start.lower():
        return "lxml"
    else:
        # Default or other logic
        # E.g., if you are unsure, you might default to HTML
        return "lxml"


def determine_content_type(record, content, content_type):  # noqa: C901
    # Check HTTP headers for Content-Type
    if content_type:
        if "text/html" in content_type:
            return "lxml"
        elif "text/xml" in content_type:
            return "lxml-xml"
        # ... add more types as needed

    url = record.headers.get("WARC-Target-URI")
    if url.endswith(".html"):
        return "lxml"
    elif url.endswith(".xml"):
        return "lxml-xml"
    # ... check for other extensions as needed

    return auto_parse(
        content
    )  # Default if no type could be determined guess based on actual content


def extract_charset_from_headers(headers):
    """Extract charset from the Content-Type header."""
    content_type = headers.get("Content-Type")
    if content_type:
        match = re.search(r"charset=([\w-]+)", content_type)
        if match:
            return match.group(1)
    return None


def detect_encoding(content_bytes):
    """Detect the encoding of content using chardet."""
    return cchardet.detect(content_bytes)["encoding"]


def should_parse_content_type(content_type):
    # Split on ";" and take the first part to get the MIME type only
    mime_type = content_type.split(";")[0].strip()
    # Check if the MIME type is one of the specified types
    return mime_type in ["text/html", "application/xml", "text/xml"]


def seems_like_binary(content):
    # Ensure content is treated as bytes
    if isinstance(content, str):
        content_bytes = content.encode()  # Convert to bytes
    else:
        content_bytes = content  # Assume it's already bytes

    return b"\x00" in content_bytes[:1024]  # Check the first 1KB for null byte


def extract_links_and_text_from_html(record, html_content, src_url):  # noqa: C901
    """Extracts all links and their attributes from an HTML content using BeautifulSoup."""
    http_headers = record.http_headers
    if http_headers:
        content_type = http_headers.get("Content-Type")
    else:
        content_type = None

    link_data = []

    if not seems_like_binary(html_content) and should_parse_content_type(content_type):
        ct = determine_content_type(record, html_content, content_type)
        soup = BeautifulSoup(html_content, ct)

        # Tags and their respective attributes that might contain links
        standard_tags = {
            "a": "href",
            "link": "href",
            "img": "src",
            "script": "src",
            "object": "data",
            "iframe": "src",
            "source": "src",
            "track": "src",
            "area": "href",
            "base": "href",
            "blockquote": "cite",
            "q": "cite",
        }

        meta_tags = {
            "og:url",
            "og:image",
            "og:image:secure_url",
            "og:video",
            "og:video:url",
            "og:video:secure_url",
            "twitter:url",
            "twitter:image:src",
            "twitter:image",
            "thumbnail",
            "application-url",
            "msapplication-starturl",
            "msapplication-TileImage",
            "vb_meta_bburl",
        }

        def is_hidden(element):
            style = element.attrs.get("style", "")
            if "display: none" in style or "visibility: hidden" in style:
                return True
            if "position: absolute" in style and any(
                coord in style
                for coord in ["left: -", "top: -", "right: -", "bottom: -"]
            ):
                return True
            if element.has_attr("hidden"):  # Check for the "hidden" attribute
                return True
            return False

        for tag, attr in standard_tags.items():
            for t in soup.find_all(tag, **{attr: True}):
                if is_hidden(t):
                    continue  # Skip hidden elements
                link_url = t[attr]
                link_attributes = {
                    "url": str(link_url),
                    "surt_host": str(compute_surt_host(src_url, link_url)),
                    "attributes": {
                        str(k): str(v) for k, v in t.attrs.items() if k != attr
                    },
                }
                link_data.append(link_attributes)

        # Handle the meta tags
        for meta_tag in meta_tags:
            for t in soup.find_all(
                "meta", attrs={"property": meta_tag, "content": True}
            ):
                link_data.append(
                    {
                        "url": str(t["content"]),
                        "surt_host": str(compute_surt_host(src_url, t["content"])),
                        "attributes": {"property": str(meta_tag)},
                    }
                )
            for t in soup.find_all("meta", attrs={"name": meta_tag, "content": True}):
                link_data.append(
                    {
                        "url": str(t["content"]),
                        "surt_host": str(compute_surt_host(src_url, t["content"])),
                        "attributes": {"name": str(meta_tag)},
                    }
                )

        # Now extract the text using the TextExtractor, using the same soup
        text_extractor = TextExtractor()
        text_extractor.handle_node(soup)
        text_extractor.get_extracted_text()
        extracted_text = text_extractor.extracted_text  # None if no text extracted

    return link_data, extracted_text


def extract_links_from_headers(headers, src_url):
    """Extracts links from HTTP headers and formats them to match the output schema of extract_links_from_html."""
    links_with_attributes = []

    # 1. Extract from Location header (commonly used for redirects)
    location = headers.get("Location")
    if location:
        links_with_attributes.append(
            {
                "url": location,
                "surt_host": compute_surt_host(src_url, location),
                "attributes": {"rel": "location"},
            }
        )

    # 2. Extract from Link header
    link_header = headers.get("Link")
    if link_header:
        # Link headers can contain multiple links separated by commas.
        # This regex captures URLs wrapped in < > and their associated attributes.
        link_pattern = re.compile(r'<([^>]+)>\s*;\s*rel="([^"]+)"')
        for match in link_pattern.findall(link_header):
            url, rel = match
            links_with_attributes.append(
                {
                    "url": url,
                    "surt_host": compute_surt_host(src_url, url),
                    "attributes": {"rel": rel},
                }
            )

    # 3. Content-Location header
    content_location = headers.get("Content-Location")
    if content_location:
        links_with_attributes.append(
            {
                "url": content_location,
                "surt_host": compute_surt_host(src_url, content_location),
                "attributes": {"rel": "content-location"},
            }
        )

    return links_with_attributes
