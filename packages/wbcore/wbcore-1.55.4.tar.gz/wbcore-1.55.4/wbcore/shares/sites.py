from dataclasses import dataclass, field

from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from wbcore.metadata.configs.display.instance_display import Section
from wbcore.serializers import Serializer
from wbcore.serializers.fields import CharField


@dataclass
class ShareSite:
    serializers: list[Serializer] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)

    @cached_property
    def serializer_class(self) -> Serializer:
        return type(
            "ShareSerializer",
            tuple(self.serializers),
            dict(widget_endpoint=CharField(label=_("Widget URL"), read_only=True)),
        )

    @cached_property
    def sorted_sections(self) -> list[Section]:
        return list(map(lambda x: x["section"], sorted(self.sections, key=lambda x: x["weight"])))


share_site = ShareSite()
