import re
from contextlib import suppress

from django.core.management.base import BaseCommand
from markdown import Markdown

from wbcore.release_notes.models import ReleaseNote


def parse_changelog(change_log_path: str, changelog_section_regex: str):
    with open(change_log_path) as file:
        section = ""
        previous_matched_version = None
        previous_matched_date = None

        for line in file:
            match = re.search(changelog_section_regex, line)
            if match:
                if previous_matched_version and previous_matched_date:
                    yield previous_matched_version, previous_matched_date, section
                section = ""
                previous_matched_version = match.group(1)
                previous_matched_date = match.group(2)
            section += line + "\n"
        if previous_matched_version and previous_matched_date:
            yield previous_matched_version, previous_matched_date, section


class Command(BaseCommand):
    help = "Handles the creation/deletion/changing of release notes through markdown files"

    def add_arguments(self, parser):
        parser.add_argument("module_changelog_path_tuples", nargs="*", type=str, default=["stainly:CHANGELOG.md"])
        parser.add_argument(
            "changelog_section_regex", nargs="?", type=str, default=r"^##\sv?(\d+\.\d+\.\d+).*(\d{4}-\d{2}-\d{2}).*$"
        )

    def handle(self, *args, **options):
        for module_changelog_path_tuple in options["module_changelog_path_tuples"]:
            module, changelog_path = module_changelog_path_tuple.split(":")
            stale_release_notes = ReleaseNote.objects.filter(module=module)
            with suppress(FileNotFoundError):
                for version, release_date, section in parse_changelog(
                    changelog_path, options["changelog_section_regex"]
                ):
                    md = Markdown(extensions=["meta"], tab_length=2)
                    content = md.convert(section)
                    release_note_obj, created = ReleaseNote.objects.update_or_create(
                        version=version,
                        module=module,
                        defaults={"release_date": release_date, "summary": f"v{version}", "notes": content},
                    )
                    stale_release_notes = stale_release_notes.exclude(id=release_note_obj.id)
                stale_release_notes.delete()
