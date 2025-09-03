import django


if django.VERSION < (3, 2):
    default_app_config = 'm3_db_utils.apps.M3DBUtilsConfig'
