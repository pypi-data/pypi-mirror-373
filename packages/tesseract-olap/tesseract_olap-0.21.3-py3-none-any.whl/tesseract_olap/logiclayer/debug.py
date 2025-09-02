import pprint

import orjson
from fastapi.responses import PlainTextResponse, Response

from tesseract_olap.common import AnyDict
from tesseract_olap.query import DataQuery, DataRequest

LF = "\n"
pp = pprint.PrettyPrinter(sort_dicts=True)


def debug_response(
    accept: str,
    *,
    request: DataRequest,
    query: DataQuery,
    debug: AnyDict,
) -> Response:
    priority = [item.split(";")[0] for item in accept.split(",")]
    restype = sorted(
        ["text/plain", "application/json", "text/html"],
        key=lambda x: priority.index(x) if x in priority else 99,
    )

    if restype[0] == "text/plain":
        content = text_debug_response(request, query, debug)
        return PlainTextResponse(content, media_type="text/plain")

    if restype[0] == "text/html":
        content = html_debug_response(request, query, debug)
        return PlainTextResponse(content, media_type="text/html")

    content = {
        "request": pp.pformat(request),
        "query": pp.pformat(query),
        **debug,
    }
    return PlainTextResponse(orjson.dumps(content), media_type="application/json")


def html_debug_response(request: DataRequest, query: DataQuery, debug: AnyDict) -> str:
    sections = {
        "DataRequest": f"<pre>{pp.pformat(request)}</pre>",
        "DataQuery": f"<pre>{pp.pformat(query)}</pre>",
        **{
            f"Fetch {name.capitalize()}": "\n".join(
                f"<h3>{title}</h3><pre>{content}</pre>" for title, content in debug.items()
            )
            for name, debug in debug.items()
        },
    }
    return f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8" /><style>pre{{white-space:normal}}</style></head>
<body>
{LF.join(f"<h2>{title}</h2>{content}" for title, content in sections.items())}
</body>
</html>
"""


def text_debug_response(request: DataRequest, query: DataQuery, debug: AnyDict) -> str:
    sections = {
        "DataRequest": f"```{pp.pformat(request)}```",
        "DataQuery": f"```{pp.pformat(query)}```",
        **{
            f"Fetch {name.capitalize()}": "\n\n".join(
                f"## {title}\n```{content}```" for title, content in debug.items()
            )
            for name, debug in debug.items()
        },
    }
    return "\n\n".join(f"# {title}\n{content}" for title, content in sections.items())
