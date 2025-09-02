from django.conf import settings
from django.db import DEFAULT_DB_ALIAS, router
from django.contrib.contenttypes.management import create_contenttypes
from django.apps import apps as global_apps


def _get_all_permissions(opts):
    if action := getattr(settings, "IMPORT_EXPORT_IMPORT_PERMISSION_CODE", None):
        yield "%s_%s" % (action, opts.model_name), "Import %s %s" % (action, opts.verbose_name_raw),
    if action := getattr(settings, "IMPORT_EXPORT_EXPORT_PERMISSION_CODE", None):
        yield "%s_%s" % (action, opts.model_name), "Export %s %s" % (action, opts.verbose_name_raw),

    yield "select_%s" % (opts.model_name,), "Can select %s" % (opts.verbose_name_raw,)


def create_wbcore_permissions(
    app_config,
    verbosity=2,
    interactive=True,
    using=DEFAULT_DB_ALIAS,
    apps=global_apps,
    **kwargs,
):
    if not app_config.models_module:
        return

    # Ensure that contenttypes are created for this app. Needed if
    # 'django.contrib.auth' is in INSTALLED_APPS before
    # 'django.contrib.contenttypes'.
    create_contenttypes(
        app_config,
        verbosity=verbosity,
        interactive=interactive,
        using=using,
        apps=apps,
        **kwargs,
    )

    app_label = app_config.label
    try:
        app_config = apps.get_app_config(app_label)
        ContentType = apps.get_model("contenttypes", "ContentType")
        Permission = apps.get_model("auth", "Permission")
    except LookupError:
        return

    if not router.allow_migrate_model(using, Permission):
        return

    # This will hold the permissions we're looking for as
    # (content_type, (codename, name))
    searched_perms = []
    # The codenames and ctypes that should exist.
    ctypes = set()
    for klass in app_config.get_models():
        # Force looking up the content types in the current database
        # before creating foreign keys to them.
        ctype = ContentType.objects.db_manager(using).get_for_model(klass, for_concrete_model=False)

        ctypes.add(ctype)
        for perm in _get_all_permissions(klass._meta):
            searched_perms.append((ctype, perm))

    # Find all the Permissions that have a content_type for a model we're
    # looking for.  We don't need to check for codenames since we already have
    # a list of the ones we're going to create.
    all_perms = set(
        Permission.objects.using(using)
        .filter(
            content_type__in=ctypes,
        )
        .values_list("content_type", "codename")
    )

    perms = []
    for ct, (codename, name) in searched_perms:
        if (ct.pk, codename) not in all_perms:
            permission = Permission()
            permission._state.db = using
            permission.codename = codename
            permission.name = name
            permission.content_type = ct
            perms.append(permission)

    Permission.objects.using(using).bulk_create(perms)
    if verbosity >= 2:
        for perm in perms:
            print("Adding permission '%s'" % perm)
