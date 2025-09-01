import hashlib


def hash_text(text):
    md5_hash = hashlib.md5()
    md5_hash.update(text.encode('utf-8'))
    return md5_hash.hexdigest()


def str_to_bool(value):
    return value.lower() in ['true', '1', 'yes']
