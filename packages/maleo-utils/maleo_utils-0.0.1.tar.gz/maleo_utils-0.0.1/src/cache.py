def build_key(*ext: str, namespace: str):
    return ":".join([namespace, *ext])
