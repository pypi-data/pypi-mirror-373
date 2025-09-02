from datetime import datetime

from markdown import Markdown


def parse_release_note(release_note):
    md = Markdown(extensions=["meta"], tab_length=2)
    content = md.convert(release_note)
    meta = md.Meta
    version = meta["version"][0]
    module = meta["module"][0]
    summary = meta["summary"][0]
    release_date = datetime.strptime(meta["date"][0], "%Y-%m-%d")
    return content, meta, version, module, summary, release_date
