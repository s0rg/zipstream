# zipstream
Lazy stream-oriented zip file packer


```python

import zipstream

s = zipstream.ZipStream()

s.write('hello.txt', 'hello'.encode('ascii'))
s.write('hello.txt', ' world'.encode('ascii'))
s.store('hello.txt')  # flush packed data to underlying zip stream

res = s.read()

with open('hello.zip', 'wb') as fd:
    fd.write(res)

```

# License
-------

zipstream is released under the terms of the [MIT license](http://en.wikipedia.org/wiki/MIT_License>)

