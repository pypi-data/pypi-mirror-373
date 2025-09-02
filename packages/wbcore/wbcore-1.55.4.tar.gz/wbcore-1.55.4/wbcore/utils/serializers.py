from django.utils.translation import gettext_lazy as _

import wbcore.serializers as wb_serializers
from wbcore.utils.date import current_quarter_date_end, current_quarter_date_start


class StartEndDateSerializer(wb_serializers.Serializer):
    start = wb_serializers.DateField(label=_("Start"), default=current_quarter_date_start)
    end = wb_serializers.DateField(label=_("End"), default=current_quarter_date_end)
