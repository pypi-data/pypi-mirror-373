from django.db.models import Case, Value, When
from dynamic_preferences.users.registries import user_preferences_registry
from dynamic_preferences.users.viewsets import UserPreferencesViewSet as BaseUserPreferencesViewSet


class UserPreferencesViewSet(BaseUserPreferencesViewSet):
    def get_queryset(self):
        obsolete_expressions = []
        weight_expressions = []
        # we mount a when statement dynamically from the static user preference registry
        # if the condition is matched, we assume the preference is not obsolete.
        for section_name, preferences in user_preferences_registry.items():
            for pref in preferences.values():
                obsolete_expressions.append(When(section=section_name, name=pref.name, then=Value(False)))
                weight_expressions.append(
                    When(section=section_name, name=pref.name, then=Value(getattr(pref, "weight", 0)))
                )
        return (
            super()
            .get_queryset()
            .annotate(
                is_obsolete=Case(*obsolete_expressions, default=Value(True)),
                weight=Case(*weight_expressions, default=Value(0)),
            )
            .exclude(is_obsolete=True)
            .order_by("weight", "name")
        )
