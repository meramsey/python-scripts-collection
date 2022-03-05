def natural_key(string_):
    import re
    """See https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


matching_tags = ['v2.8.10', 'v2.8.9', 'v2.8.8', 'v2.8.7', 'v2.8.6', 'v2.8.5', 'v2.8.4', 'v2.8.3', 'v2.8.2', 'v2.8.1',
                 'v2.8.0', 'v2.8.11']
sorted_tags = sorted(matching_tags, key=natural_key, reverse=True)
print(f'Matching tags: {matching_tags}')
print(f'Sorted Matching tags: {sorted_tags}')
last_tag = sorted_tags[0]
print(last_tag)
