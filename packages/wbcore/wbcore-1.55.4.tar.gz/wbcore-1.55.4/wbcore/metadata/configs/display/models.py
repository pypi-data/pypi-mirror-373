from django.contrib.auth import get_user_model
from django.db import models


class Preset(models.Model):
    title = models.CharField(max_length=64)
    user = models.ForeignKey(
        to=get_user_model(), related_name="presets", on_delete=models.CASCADE, null=True, blank=True
    )
    display_identifier = models.CharField(max_length=512)
    display = models.JSONField(null=True, blank=True)


class AppliedPreset(models.Model):
    user = models.ForeignKey(to=get_user_model(), related_name="applied_presets", on_delete=models.CASCADE)
    display_identifier_path = models.CharField(max_length=1024)
    preset = models.ForeignKey(
        to=Preset, related_name="applied_presets", on_delete=models.SET_NULL, null=True, blank=True
    )
    display = models.JSONField(null=True, blank=True)
