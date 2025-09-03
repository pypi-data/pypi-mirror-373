from io import BytesIO

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
except ImportError:
    pass


def get_load_function(key_type: str):
    if key_type == 'pem':
        return serialization.load_pem_private_key
    elif key_type == 'der':
        return serialization.load_der_private_key
    else:
        raise ValueError(f'Unsupported key type: {key_type}')

def load_private_key(
    private_key_string: str,
    private_key_type: str = 'pem',
    passphrase: str = None,
):
    load_func = get_load_function(private_key_type)
    key_bytes = private_key_string.encode('utf-8')

    if passphrase is not None:
        passphrase = passphrase.encode('utf-8') if isinstance(passphrase, str) else passphrase

    # Use BytesIO to wrap the bytes as a file-like object
    key_file_like = BytesIO(key_bytes)
    p_key = load_func(
        key_file_like.read(),
        password=passphrase,
        backend=default_backend()
    )
    pkb = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    return pkb
