class MultipartEncoder(object):

    def __init__(self, stream, size, filename='file', fieldname='file', filetype=None, boundary=None):
        self.size = int(size)
        self.stream = stream
        self.filename = filename
        self.fieldname = fieldname
        self.filetype = filetype or 'application/octet-stream'
        self.boundary = boundary or '0'*8
        self.offset = 0

    @property
    def content_type(self):
        return f'multipart/form-data; boundary={self.boundary}'

    @property
    def header(self):
        return (
            f'--{self.boundary}\r\n'
            f'Content-Disposition: form-data; name="{self.fieldname}"; filename="{self.filename}"\r\n'
            f'Content-Type: {self.filetype}\r\n\r\n'
        ).encode()

    @property
    def footer(self):
        return f'\r\n--{self.boundary}--\r\n'.encode()

    def __len__(self):
        return self.size + len(self.header) + len(self.footer)

    def read(self, size=-1):
        if not self.offset:
            chunk = self.header + self.stream.read(size - len(self.header))
        else:
            chunk = self.stream.read(size)
            if chunk == b'':
                if self.offset < len(self):
                    chunk = self.footer
                else:
                    return b''
        self.offset += len(chunk)
        return chunk
