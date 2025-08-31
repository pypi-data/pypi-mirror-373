class PyS3FUSEError(Exception):
    pass


class S3ConnectionError(PyS3FUSEError):
    pass


class PysClientError(PyS3FUSEError):
    pass
