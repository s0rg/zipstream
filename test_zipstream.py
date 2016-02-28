import os
import io
import zlib
import zipfile

import zipstream


def gen_data(size=1024):
    return b'ABCDEF' * size


def get_zipstream_result(name, data):
    zips = zipstream.ZipStream(zlib.Z_DEFAULT_COMPRESSION)

    # write as two chunks, because i can!
    l = len(data)
    zips.write(name, data[:l//2])
    zips.write(name, data[l//2:])

    # normally, you dont need this `info` result
    info = zips.store(name)

    zips_res = zips.read()

    return info, zips_res


def get_zipfile_result(name, data):
    zipb = io.BytesIO()
    zipf = zipfile.ZipFile(zipb, mode='w', compression=zipfile.ZIP_DEFLATED)
    zipf.writestr(name, data)
    zipf.close()

    info = zipf.filelist[0]

    zipf_res = zipb.getvalue()
    zipb.close()

    return info, zipf_res


def run_test(name, fn, data):
    print('=== {}'.format(name))

    info, res = fn(name + '.test', data)

    hdr = info.FileHeader()

    print('\tHeaders[{}]: {}'.format(len(hdr), hdr))
    print('\tResult: {} bytes'.format(len(res)))

    with open(name + '_test.zip', 'wb') as fd:
        fd.write(res)

    return info, res


def test_me():
    src_data = gen_data()

    print('Data size: {}'.format(len(src_data)))

    zis_header, zis_result = run_test('zipstrm', get_zipstream_result, src_data)
    zip_header, zip_result = run_test('zipfile', get_zipfile_result, src_data)

    # tests
    assert(zis_header.CRC==zip_header.CRC)
    assert(zis_header.file_size==zip_header.file_size)
    assert(zis_header.compress_size==zip_header.compress_size)

    zis_header_bytes = zis_header.FileHeader()
    zip_header_bytes = zip_header.FileHeader()

    assert(len(zis_header_bytes)==len(zip_header_bytes))

    assert(len(zis_result)==len(zip_result))

test_me()

