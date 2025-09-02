def normalize_value(value):
    try:
        return (
            value.replace("\n", "")
            .replace("    ", "")
            .replace("  ", "")
            .replace("\r", "")
            .replace("'", "")
            .replace('"', "")
        )
    except AttributeError:
        return value
