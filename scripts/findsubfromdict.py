def find_sub_dict(data, key, value):
    # https://stackoverflow.com/a/50957001
    if isinstance(data, dict) and key in data and data[key] == value:
        return data
    elif not isinstance(data, dict):
        return None
    else:
        for v in data.values():
            result = find_sub_dict(v, key, value)
            if result is not None:
                return result
