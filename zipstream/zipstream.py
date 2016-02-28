import io
import time
import zipfile

from .zlibstream import ZlibStream


class ZipInfoFacade(zipfile.ZipInfo):
    '''
    Makes selected fileds in zipfile.ZipInfo read-only
    '''
    __readonly__ = (
        'CRC',
        'compress_size',
        'file_size',
    )

    def __init__(self, wrapped_info):
        self.__dict__['_wrapped'] = wrapped_info

    def __getattr__(self, attr):
        return getattr(self._wrapped, attr)

    def __setattr__(self, attr, value):
        if attr not in self.__readonly__:
            setattr(self._wrapped, attr, value)


class ZipStream(object):

    def __init__(self, compression=6):
        self.compression = compression
        self._files = {}
        self._buf = io.BufferedRandom(io.BytesIO())
        self._zip = zipfile.ZipFile(self._buf, mode='w')
        self._res = None  # for cached result

    def write(self, name, data):
        n = name.lower()
        self._files.setdefault(n, ZlibStream(self.compression)).write(data)

    def store(self, name):
        name = name.lower()

        zinfo = zipfile.ZipInfo(filename=name, date_time=time.localtime(time.time())[:6])

        zinfo.external_attr = 0o600 << 16  # from ZipFile.writestr
        zinfo.compress_type = zipfile.ZIP_DEFLATED

        zstream = self._files[name]
        self._files[name] = None  # prevent name collision (instead just of .pop())

        zinfo.CRC = zstream.crc32
        zinfo.file_size = zstream.src_len

        data = zstream.read()
        zstream.close()
        zstream = None  # make it ready for gc

        zinfo.compress_size = len(data)

        ro_info = ZipInfoFacade(zinfo)

        '''
        Monkey-patch _get_compressor, this is bad, i know.
        But this is only way to make ZipFile work with already
        compressed stream.
        '''
        fn = zipfile._get_compressor
        zipfile._get_compressor = lambda c: None

        self._zip.writestr(ro_info, data)

        '''
        Restore saved handler
        '''
        zipfile._get_compressor = fn

        # for debug purpose only
        return ro_info

    def read(self):
        if self._res is None:
            self._zip.close()
            b = self._buf
            b.seek(0, io.SEEK_SET)
            self._res = b.read()
            b.close()
        return self._res


