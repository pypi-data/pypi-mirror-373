from wbcore.contrib.guardian.models.mixins import PermissionObjectModelMixin


class PermissionTestModel(PermissionObjectModelMixin):
    class Meta(PermissionObjectModelMixin.Meta):
        managed = False
