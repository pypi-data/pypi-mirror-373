class SignedObjectType:
    """
    A collection of objects types for sign
    """

    XML = 'xml'
    SIMPLE_FILE = 'base64'
    RAW = 'base64_raw'
    BIG_FILE = 'base64_hash'

    ITEMS = (
        XML,
        SIMPLE_FILE,
        RAW,
        BIG_FILE
    )

    CHOICES = (
        (XML, 'xml'),
        (SIMPLE_FILE, 'base64'),
        (RAW, 'base64_raw'),
        (BIG_FILE, 'base64_hash'),
    )
