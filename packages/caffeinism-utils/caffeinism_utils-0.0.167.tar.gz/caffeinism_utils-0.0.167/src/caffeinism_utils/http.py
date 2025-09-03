from httpx._multipart import MultipartStream, get_multipart_boundary_from_content_type

from .prefetch import aprefetch_iterator


def build_async_multipart_stream(data, files, content_type):
    multipart = MultipartStream(
        data=data or {},
        files=files,
        boundary=get_multipart_boundary_from_content_type(content_type or None),
    )
    return multipart.get_headers(), aprefetch_iterator(multipart)
