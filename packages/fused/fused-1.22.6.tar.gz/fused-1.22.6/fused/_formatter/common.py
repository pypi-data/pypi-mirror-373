import sys
from functools import lru_cache
from html import escape
from typing import Optional
from uuid import uuid4

if sys.version_info >= (3, 9):
    from importlib.resources import files
else:
    from importlib_resources import files

STATIC_FILES = (
    ("fused._static.html", "icons-svg-inline.html"),
    ("fused._static.css", "style.css"),
)


# Note: remove this lru_cache if changing the CSS
@lru_cache(None)
def load_static_files():
    """Lazily load the resource files into memory the first time they are needed"""
    return [
        files(package).joinpath(resource).read_text(encoding="utf-8")
        for package, resource in STATIC_FILES
    ]


def icon(icon_name):
    # icon_name should be defined in xarray/static/html/icon-svg-inline.html
    return "<svg class='icon xr-{0}'><use xlink:href='#{0}'></use></svg>".format(
        icon_name
    )


def copyable_text(text: Optional[str], *, show_text: bool = True) -> str:
    """Returns an HTML fragment for a copyable text block"""
    if text is None:
        return ""
    id = f"copyable-{uuid4()}"
    js_fragment = f"var el = document.getElementById('{id}'); navigator.clipboard.writeText(el.innerText); var el2 = document.getElementById('{id}-copied'); el2.classList.add('fused-copy-fade-inout'); setTimeout(function(){{el2.classList.remove('fused-copy-fade-inout');}}, 1600);"
    copy_icon = icon("icon-copy")
    copy = f'<a onclick="javascript:{js_fragment}" class="fused-copy-button" title="Copy to clipboard">{copy_icon}</a>'
    code_style = 'style="display: none;"' if not show_text else ""
    copy_indicator = f'<span id="{id}-copied" class="fused-copy-hidden">Copied</span>'
    code_fragment = f'<code id="{id}" {code_style}>{escape(text)}</code>'
    return f"{code_fragment} {copy} {copy_indicator}"
