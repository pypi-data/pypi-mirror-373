def safe_get(data: dict, attribute: str, default: any = None, splitter:str = '.'):
    if attribute is None:
        return default

    for key in attribute.split(splitter):
        try:
            data = data[key]

            if data is None and default is not None:
                return default
        except KeyError:
            return default
        except TypeError:
            return default

    return data