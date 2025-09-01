import pandas as pd
import requests
import cssutils
from cachetools.func import ttl_cache
from IPython.display import display as __display__


def display(v):
    if isinstance(v, pd.DataFrame):
        __display__(v.style.pipe(_make_pretty))
    elif isinstance(v, pd.io.formats.style.Styler):
        __display__(v.pipe(_make_pretty))
    else:
        __display__(v)


def _make_pretty(styler):
    css_styles = _load_css()
    styler.format(precision=3, thousands=",")
    styler.set_table_styles(css_styles)

    return styler


def _read_resource_file(url: str) -> str:
    r = requests.request(
        method="GET",
        url=url,
    )
    r.raise_for_status()

    return r.text


@ttl_cache(maxsize=1, ttl=60)
def _load_css() -> list:
    url = "https://storage.googleapis.com/pyqqq-resource/colab.css"
    text = _read_resource_file(url)
    target_url = text.split('"')[1]

    styles = []
    sheet = cssutils.parseUrl(target_url)
    for rule in sheet:
        selector = rule.selectorText
        props = rule.style.cssText
        styles.append({
            'selector': selector,
            'props': props.replace('\n', ' '),
        })

    return styles
