def exclude_keywords_from_mapping(mapping, keywords_to_exclude=None):
    if keywords_to_exclude:
        for keyword in keywords_to_exclude:
            mapping = {k: v for k, v in mapping.items() if keyword not in v}
    return mapping