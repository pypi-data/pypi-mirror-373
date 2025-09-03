def m3_db_utils_after_migrate_receiver(sender, **kwargs):
    """Выполняет обновление значений моделей-перечислений после выполнения миграций."""
    from m3_db_utils.api import (
        update_model_enum_values,
    )

    update_model_enum_values()
