import re
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread

import requests
from logbook import Logger

from hansken.util import ChunkedIO


log = Logger(__name__)


UPLOAD_PATH = '/image-upload'
PATH_PATTERN = re.compile(
    r'^/(?:image-upload/)?(?P<image_id>[a-f0-9\-]+)(?P<extension>\.nfi(:?\.idx)?)(:?\?.*)?$', re.IGNORECASE
)
PATH_TEMPLATE = '/image-upload/{image_id}{extension}'


def read_chunked(fobj):
    # read hexadecimal number of bytes in the next chunk
    chunk_size = int(fobj.readline(), 16)
    while chunk_size:
        yield fobj.read(chunk_size)
        # consume \r\n at the end of chunk
        fobj.readline()
        # read hexadecimal number of bytes in the next chunk
        chunk_size = int(fobj.readline(), 16)


class WebHDFSRequestHandler(SimpleHTTPRequestHandler):
    """
    HTTP request handler that mimics WebHDFS's handling of PUT requests.
    """

    def log_message(self, format, *args):  # noqa: A002 (copying super)
        # avoid super writing to stderr
        log.debug('{} - {}', self.address_string(), format % args)

    def do_redirect(self):
        path = PATH_PATTERN.match(self.path)
        if path:
            location = PATH_TEMPLATE.format(**path.groupdict())
            log.debug('sending temporary redirect from {} to {}', self.path, location)
            self.send_response(307)
            self.send_header('Location', location)
            self.end_headers()
            return None
        else:
            log.debug('sending bad request (cannot match path {} for redirect)', self.path)
            self.send_response(400)
            self.end_headers()
            return None

    def _slice_chunk(self, response, image_id, chunk, offset, extension, at_attempt):
        # NB: method uses plain raise; should only be called from an except block!
        if response.status_code == 416:
            # TODO: return a 416 response for applicable upload issues rather than a 500 (HANSKEN-17174)
            resource_size = response.headers['Content-Range']
            resource_size = re.match(r'^bytes .+/(?P<size>\d+)$', resource_size, re.IGNORECASE)
            if not resource_size:
                log.warn('no usable resource size available in 416 response: {}', response.headers['Content-Range'])
                raise
            # reported size does not match offset, skip the difference
            skip = int(resource_size.group('size')) - offset
        elif response.status_code == 500:
            response_text = response.text.strip()
            # using the plain text error message to determine how much of the bytes were processed previously
            # despite the error response
            offsets = re.match(r'^expected offset (\d+) but was (\d+)$', response_text, re.IGNORECASE)
            if offsets:
                expected, sent = offsets.groups()
                # skip the difference, send the trailing end of the buffer we tried to append
                skip = int(expected) - int(sent)
            else:
                log.warn('failed to recognize offsets for partial retry from error message "{}"', response_text)
                # raise original error with original traceback (causing a 500, see note below)
                raise
        else:
            # cannot deal with this error in a satisfiable way, continue original error
            raise

        if skip < 0:
            # not something we can solve by skipping bytes, continue original error
            raise

        # offset + skip should equal expected, return (recursive) result (not resetting the attempt
        # counter) or bubble an error
        log.warn(
            'retrying partial chunk at offset {}, skipping {} bytes that seem to be present at offset {}',
            offset + skip,
            skip,
            offset,
        )
        return self.process_chunk(image_id, chunk[skip:], offset + skip, extension, at_attempt=at_attempt)

    def process_chunk(self, image_id, chunk, offset, extension, at_attempt=None):
        def should_retry():
            return self.server.max_retries is None or attempt <= self.server.max_retries + 1

        def should_slice(response):
            return (
                # trigger 1: response 416 (range not satisfiable)
                response.status_code == 416
                or (
                    # trigger 2: response 500 (internal error) with a specific error message body
                    response.status_code == 500 and response.text.strip().lower().startswith('expected offset')
                )
            )

        attempt = at_attempt or 1
        while attempt == 1 or should_retry():
            try:
                return self.server.upload_callback(image_id=image_id, extension=extension, data=chunk, offset=offset)
            except requests.ConnectionError as e:
                attempt += 1
                if should_retry():
                    log.warn(
                        'uploading a chunk at offset {} failed due to {}, retrying in {}s',
                        offset,
                        str(e),
                        self.server.retry_wait,
                        e,
                    )
                    time.sleep(self.server.retry_wait)
            except requests.HTTPError as e:
                attempt += 1
                response_text = e.response.text.strip()
                if should_slice(e.response):
                    return self._slice_chunk(e.response, image_id, chunk, offset, extension, at_attempt=attempt)
                if e.response.status_code == 500 and should_retry():
                    log.warn(
                        'uploading a chunk at offset {} failed due to {}: {}: {}, retrying in {}s',
                        offset,
                        e.response.status_code,
                        e.response.reason,
                        response_text,
                        self.server.retry_wait,
                        e,
                    )
                    time.sleep(self.server.retry_wait)
                else:
                    # chunk upload is not being retried, log exception
                    log.exception(
                        'uploading a chunk at offset {} failed: {}: {}: {}',
                        offset,
                        # log detailed error information, including error response body
                        e.response.status_code,
                        e.response.reason,
                        response_text,
                        e,
                    )
                    # raise original error with original traceback (causing a 500, see note below)
                    raise

        # loop exits only at exhausted number of attempts, give up
        # NB: this error will show up on the 'client side', i.e. the hansken-image-tool process as a 500 response
        raise ValueError(f'maximum attempts ({attempt}) reached for chunk at offset {offset} for image {image_id}')

    def do_upload(self):
        path = PATH_PATTERN.match(self.path)
        if path:
            image_id = path.group('image_id')
            extension = path.group('extension')
            data = self.rfile
            if self.headers.get('Transfer-Encoding') == 'chunked':
                log.debug('getting chunked data, wrapping rfile with chunk generator')
                data = read_chunked(self.rfile) if self.server.streaming else ChunkedIO(read_chunked(self.rfile))

            if self.server.streaming:
                log.info('image will be uploaded as a stream')
                try:
                    log.debug('forwarding image data as-is to remote')
                    self.server.upload_callback(image_id=image_id, extension=extension, data=data)
                except (requests.ConnectionError, requests.HTTPError) as e:
                    if hasattr(e, 'response'):
                        log.exception(
                            'uploading image data failed, no retry available: {}: {}: {}',
                            e.response.status_code,
                            e.response.reason,
                            e.response.text.strip(),
                            e,
                        )
                    else:
                        log.exception('uploading image data failed, no retry available: {}', str(e), e)

                    # close i/o resources (force broken pipe on the client side)
                    data.close()
                    self.rfile.close()
                    # remote service can't process our request, indicate gateway error to client
                    log.debug('sending bad gateway response for image {}', image_id)
                    self.send_response(502)
                    self.end_headers()
                    return None
            else:
                log.info('image will be uploaded in chunks')
                buffer = memoryview(bytearray(self.server.bufsize))
                num_read = data.readinto(buffer)
                offset = 0

                while num_read:
                    try:
                        log.debug('uploading {} bytes of {} image data at offset {}', num_read, extension, offset)
                        self.process_chunk(image_id, buffer[:num_read], offset, extension)
                        offset += num_read
                        num_read = data.readinto(buffer)
                    except ValueError:
                        # close i/o resources (force broken pipe on the client side)
                        data.close()
                        self.rfile.close()
                        raise

            log.debug('sending created response for image {}', image_id)
            self.send_response(201)
            self.end_headers()
            return None
        else:
            log.debug('sending bad request (cannot match path {} for upload)', self.path)
            self.send_response(400)
            self.end_headers()
            return None

    def do_PUT(self):  # noqa: N802
        log.debug('got PUT request for {}', self.path)

        try:
            if self.path.startswith(UPLOAD_PATH):
                return self.do_upload()
            else:
                return self.do_redirect()
        except Exception as e:
            log.exception('handling PUT request for {} failed', self.path, e)
            self.send_response(500)
            self.end_headers()
            return None


class WebHDFSServer(HTTPServer):
    """
    HTTP server that mimics WebHDFS on a local address.
    """

    def __init__(self, upload_callback, streaming, bufsize=8 << 20, max_retries=8, retry_wait=10.0):
        # bind to port 0, let OS find a free port
        super().__init__(('localhost', 0), WebHDFSRequestHandler)

        self.upload_callback = upload_callback
        self.bufsize = bufsize
        self.max_retries = max_retries
        self.retry_wait = retry_wait
        self.streaming = streaming
        self._thread = None

    def __enter__(self):
        if not self._thread:
            self._thread = Thread(name=f'webhdfs-server-{self.server_port}', target=self.serve_forever)
            log.info('starting WebHDFS server on port {} in the background', self.server_port)
            self._thread.start()

            return super().__enter__()
        else:
            raise ValueError('server already started or in error state')

    def __exit__(self, exc_type, exc_val, exc_tb):
        log.info('shutting down WebHDFS server on port {}', self.server_port)
        self.shutdown()
        # wait for server thread to exit
        self._thread.join()
        self._thread = None

        return super().__exit__(exc_type, exc_val, exc_tb)
