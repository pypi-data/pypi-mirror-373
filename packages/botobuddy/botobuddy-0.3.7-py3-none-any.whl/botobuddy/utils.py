def dslice(d, *keys):
    '''
    Slice a dictionary into a new dictionary, using the keys to define the slice.

    Each key can be a string, or a dictionary with the following keys:
    - k: the key to slice
    - c: the cast or conversion function
    - d: the default value
    - n: the name of the key in the result dictionary
    '''

    result = {}

    for k_def in keys:
        if isinstance(k_def, dict):
            key = k_def['k']
            cast = k_def.get('c', None)
            default = k_def.get('d', None)
            name = k_def.get('n', key)
        else:
            key = k_def
            cast = None
            default = None
            name = key

        if key in d:
            value = d[key]

            if cast:
                value = cast(value)
        else:
            value = default

        if value is not None:
            result[name] = value

    return result
