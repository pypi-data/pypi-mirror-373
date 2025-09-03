from m3_db_utils.helpers import (
    ModelEnumDBValueUpdater,
)


def update_model_enum_values(*args, **kwargs):
    """Функция синхронизации состояний значений моделей-перечислений."""
    model_db_value_updater = ModelEnumDBValueUpdater()
    model_db_value_updater.run()
