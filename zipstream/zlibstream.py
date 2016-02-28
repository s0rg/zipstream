import io
import zlib


class ZlibStream(object):

    def __init__(self, level=6, wbits=-15):
        self._zlib = zlib.compressobj(level, wbits=wbits)
        self._buf = io.BytesIO()
        self._len_orig = 0
        self._crc32 = 0
        self._closed = False

    @property
    def src_len(self):
        return self._len_orig

    @property
    def crc32(self):
        return self._crc32

    def write(self, b):
        self._len_orig += len(b)
        self._crc32 = zlib.crc32(b, self._crc32) & 0xffffffff
        self._buf.write(self._zlib.compress(b))

    def read(self):
        self._buf.write(self._zlib.flush())
        return self._buf.getvalue()

    @property
    def closed(self):
        return self._closed

    def close(self):
        if self._closed:
            return
        self._buf.close()
        self._closed = True

    def __del__(self):
        self.close()

