import re


def filter_s(content):
    """特殊符号转义"""
    if content is None:
        return None
    else:
        content = re.sub(r'\'|\"|\n|\\', "", content)

    return content
