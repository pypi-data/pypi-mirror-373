from urllib.parse import ParseResult


def set_url_port(url: ParseResult, port: int) -> ParseResult:
    if url.username:
        netloc = f"{url.username}@{url.hostname}:{port}"
    else:
        netloc = f"{url.hostname}:{port}"

    return ParseResult(
        scheme=url.scheme,
        netloc=netloc,
        path=url.path,
        params=url.params,
        query=url.query,
        fragment=url.fragment,
    )
