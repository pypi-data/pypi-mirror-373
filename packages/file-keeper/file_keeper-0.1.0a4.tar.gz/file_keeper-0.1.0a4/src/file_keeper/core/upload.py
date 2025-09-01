"""Upload implementation."""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from io import BufferedReader, BytesIO
from typing import Any, TypeAlias, cast

import magic

from . import registry, types, utils

SAMPLE_SIZE = 1024 * 2

UploadFactory: TypeAlias = Callable[[Any], "Upload | BytesIO | BufferedReader | bytes | bytearray | None"]

upload_factories = registry.Registry[UploadFactory, type]()


@dataclasses.dataclass
class Upload:
    """Standard upload details.

    Args:
        stream: iterable of bytes or file-like object
        filename: name of the file
        size: size of the file in bytes
        content_type: MIMEtype of the file

    Examples:
        >>> Upload(
        >>>     BytesIO(b"hello world"),
        >>>     "file.txt",
        >>>     11,
        >>>     "text/plain",
        >>> )
    """

    stream: types.PStream
    """Content as iterable of bytes"""
    filename: str
    """Name of the file"""
    size: int
    """Size of the file"""
    content_type: str
    """MIME Type of the file"""

    @property
    def seekable_stream(self) -> types.PSeekableStream | None:
        """Return stream that can be rewinded after reading.

        If internal stream does not support file-like `seek`, nothing is
        returned from this property.

        Use this property if you want to read the file ahead, to get CSV column
        names, list of files inside ZIP, EXIF metadata. If you get `None` from
        it, stream does not support seeking and you won't be able to rewind
        cursor to the beginning of the file after reading something.

        Example:
            ```py
            upload = make_upload(...)
            if fd := upload.seekable_stream():
                # read fragment of the file
                chunk = fd.read(1024)
                # move cursor to the end of the stream
                fd.seek(0, 2)
                # position of the cursor is the same as number of bytes in stream
                size = fd.tell()
                # move cursor back, because you don't want to accidentally loose
                # any bites from the beginning of stream when uploader reads from it
                fd.seek(0)
            ```

        Returns:
            file-like stream or nothing

        """
        if hasattr(self.stream, "tell") and hasattr(self.stream, "seek"):
            return cast(types.PSeekableStream, self.stream)

        return None

    def hashing_reader(self, **kwargs: Any) -> utils.HashingReader:
        """Get reader for the upload that computes hash while reading content."""
        return utils.HashingReader(self.stream, **kwargs)


@utils.ensure_setup
def make_upload(value: Any) -> Upload:
    """Convert value into [Upload][file_keeper.Upload] object.

    Use this function for simple and reliable initialization of
    [Upload][file_keeper.Upload] object. Avoid creating
    [Upload][file_keeper.Upload] manually, unless you are 100% sure you can
    provide correct MIMEtype, size and stream.

    Example:
        Bytes, binary streams, file objects, and a number of other types can be
        converted into [Upload][file_keeper.Upload] object.

        ```pycon
        >>> upload = make_upload(b"hello world")
        ```

        Upload object contains generic information about the file.

        ```pycon
        >>> print(upload.size)
        11
        >>> print(upload.content_type)
        text/plain
        ```

        Unsupported types will raise TypeError.

        ```pycon
        >>> make_upload("unicode string")
        Traceback (most recent call last):
          ...
        TypeError: <class 'str'> cannot be converted into Upload
        ```

    Args:
        value: content of the file

    Raises:
        TypeError: if value cannot be converted into Upload object

    Returns:
        upload object with specified content

    """
    if isinstance(value, Upload):
        return value

    initial_type: type = type(value)  # pyright: ignore[reportUnknownVariableType]

    fallback_factory = None

    for t in upload_factories:
        if initial_type is t:
            transformed_value = upload_factories[t](value)
            if transformed_value is not None:
                value = transformed_value
                break

        if not fallback_factory and issubclass(initial_type, t):
            fallback_factory = upload_factories[t]

    else:
        if fallback_factory:
            value = fallback_factory(value)

    # ideal situation: factory produced the Upload object
    if isinstance(value, Upload):
        return value

    if isinstance(value, bytes | bytearray):
        value = BytesIO(value)

    # convenient situation: factory produced binary buffer and we know how to
    # transform it into an Upload. Factories will choose this option to avoid
    # repeating mimetype detection logic
    if isinstance(value, BytesIO | BufferedReader):
        mime = magic.from_buffer(value.read(SAMPLE_SIZE), True)
        _ = value.seek(0, 2)
        size = value.tell()
        _ = value.seek(0)

        return Upload(value, getattr(value, "name", ""), size, mime)


    source_type = type(value)  # pyright: ignore[reportUnknownVariableType]
    msg = f"{source_type} cannot be converted into Upload"
    raise TypeError(msg)
