import re

job_id_re = re.compile(r"job_id=(\w*)")
bin_size_re = re.compile(r"^\d+(ms|us|ns|[YMWDhms]){1}")
image_re = re.compile(
    r"^(?P<repo>[\w.\-_]+((?::\d+|)(?=/[a-z0-9._-]+/[a-z0-9._-]+))|)(?:/|)"
    r"(?P<image>[a-z0-9.\-_]+(?:/[a-z0-9.\-_]+|))(:(?P<tag>[\w.\-_]{1,127})|)$"
)


def _parse_container(name: str) -> dict:
    match = image_re.match(name)

    return {
        "repo": match.group("repo"),
        "image": match.group("image"),
        "tag": match.group("tag"),
    }
