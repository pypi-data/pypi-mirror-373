def get_default_url_conversion(url_conversion, **kwargs):
    defaults = {'files_fields': [], 'coerce': None, 'is_list': True}
    defaults.update(kwargs)
    if url_conversion:
        defaults.update(url_conversion)
    return defaults


def get_batched_list(object_list, batch_size):
    return [object_list[index : index + batch_size] for index in range(0, len(object_list), batch_size)]
