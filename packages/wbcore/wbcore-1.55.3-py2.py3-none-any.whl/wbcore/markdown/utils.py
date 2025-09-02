import re

from dynamic_preferences.registries import global_preferences_registry
from weasyprint import default_url_fetcher

from wbcore.markdown.models import Asset


def custom_url_fetcher(url):
    try:
        if s := re.search(
            r".*wbcore/markdown/asset/([0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})",
            url,
        ):
            asset = Asset.objects.get(id=s.group(1))
            url = asset.file.url
        return default_url_fetcher(url)
    except Exception:
        global_preferences = global_preferences_registry.manager()
        default_placeholder_url = global_preferences.get("wbcore__default_empty_image_placeholder", no_cache=True)
        return default_url_fetcher(default_placeholder_url)


def remove_styled_table(html_content):
    tags = ["table", "col", "td"]
    for tag in tags:
        reg_str = "<" + tag + "(.*?)" + ">"
        reg_style = '(style=".*?;")'
        _attributs = re.findall(reg_str, html_content)
        dict_attrs = {}
        for attribut in _attributs:
            dict_attrs[attribut] = re.sub(reg_style, "", attribut)

        for _key, _value in dict_attrs.items():
            html_content = re.sub(_key, _value, html_content)

    return html_content
