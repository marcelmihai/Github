import json
import requests
from splunk_instrumentation.constants import QUICKDRAW_URL, DEFAULT_QUICKDRAW


def get_quick_draw(qd_url=None):
    """A factory to get the quickdraw result.
    if not supplied with qd_url, it will grab QUICKDRAW_URL from constants
    """
    if get_quick_draw.quick_draw_results:
        return get_quick_draw.quick_draw_results
    url = qd_url or QUICKDRAW_URL
    try:
        response = requests.get(url)
        response = json.loads(response.text)
        get_quick_draw.quick_draw_results = response
    except:
        return DEFAULT_QUICKDRAW
    return response

get_quick_draw.quick_draw_results = None
