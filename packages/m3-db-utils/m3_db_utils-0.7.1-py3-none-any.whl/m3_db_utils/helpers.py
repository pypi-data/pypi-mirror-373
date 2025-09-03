from typing import (
    Type,
)

import django
from django.apps import (
    apps,
)
from django.db.models import (
    Model,
)

from m3_db_utils.consts import (
    ATTRIBUTE_NOT_FOUND,
    KEY_FIELD_NAME,
)
from m3_db_utils.models import (
    ModelEnum,
    ModelEnumValue,
)


def is_abstract_model(model: Type[Model]) -> bool:
    """Проверяет, является ли модель абстрактной.

    Args:
        model: Класс наследник Model
    Returns:
        bool: Является ли модель абстрактной
    """
    return hasattr(model, '_meta') and hasattr(model._meta, 'abstract') and model._meta.abstract


def is_proxy_model(model: Type[Model]) -> bool:
    """Проверяет, является ли модель прокси.

    Args:
        model: Класс наследник Model
    Returns:
        bool: Является ли модель прокси
    """
    return hasattr(model, '_meta') and hasattr(model._meta, 'proxy') and model._meta.proxy


class ModelEnumDBValueUpdater:
    """Актуализатор значений моделей-перечислений.

    Перечисление поддерживает добавление, обновление и удаление значений перечислений.

    Производится поиск всех моделей-перечислений. Для каждой модели выбираются все значения из БД и собираются все
    значения из класса модели-перечисления.

    Далее производится сравнение значений, если value уже есть в БД, то необходимо проверить, требуется ли обновление.
    Если требуется, то значения обновляются и помещаются в список объектов на обновление.

    Если value есть в БД, но нет в перечислении, то он был удален.

    Если value нет в БД, но есть в значениях перечисления, то было добавлено новое значение перечисления.
    """

    def __init__(self):
        # Модель-перечисление в обработке
        self._temp_model = None
        # Наименование моделей-перечислений в обработке
        self._temp_model_field_names = None

        self._temp_db_enums = None
        self._temp_db_keys = None
        self._temp_model_enums = None
        self._temp_model_keys = None

    def _process_creating_values(self):
        """Обработка создаваемых значений."""
        for_creating = []

        keys = self._temp_model_keys.difference(self._temp_db_keys)

        for key in keys:
            model_enum_value = self._temp_model_enums[key]

            parameters = {
                field_name: getattr(model_enum_value, field_name)
                for field_name in self._temp_model_field_names
                if getattr(model_enum_value, field_name, ATTRIBUTE_NOT_FOUND) != ATTRIBUTE_NOT_FOUND
            }

            for_creating.append(self._temp_model(**parameters))

        self._temp_model.objects.bulk_create(for_creating)

    def _process_deleting_values(self):
        """Обработка удаляемых значений."""
        if not self._temp_model._meta.extensible:
            keys = self._temp_db_keys.difference(self._temp_model_keys)

            self._temp_model.objects.filter(key__in=keys).delete()

    def _process_updating_values(self):
        """Обработка обновляемых значений."""
        for_updating = []

        keys = self._temp_model_keys.intersection(self._temp_db_keys)

        for key in keys:
            db_enum_value = self._temp_db_enums[key]
            model_enum_value = self._temp_model_enums[key]

            has_changes = any(
                [
                    getattr(db_enum_value, field_name) != getattr(model_enum_value, field_name, ATTRIBUTE_NOT_FOUND)
                    for field_name in self._temp_model_field_names
                ]
            )

            if has_changes:
                for field_name in self._temp_model_field_names:
                    value = getattr(model_enum_value, field_name, ATTRIBUTE_NOT_FOUND)

                    if value != ATTRIBUTE_NOT_FOUND:
                        setattr(db_enum_value, field_name, value)

                for_updating.append(db_enum_value)

        if django.VERSION >= (2, 2):
            self._temp_model.objects.bulk_update(
                objs=for_updating,
                fields=[field_name for field_name in self._temp_model_field_names if field_name != KEY_FIELD_NAME],
            )
        else:
            for obj in for_updating:
                obj.save()

    def _process_model(
        self,
        model,
    ):
        """Подготовка значений модели-перечисления и дальнейшая их обработка.

        Args:
            model: класс модели-перечисления
        """
        self._temp_db_enums = {instance.key: instance for instance in model.objects.all()}

        self._temp_model_enums = {}

        model_dict = {}
        for class_ in model.__mro__:
            model_dict.update(vars(class_))

        for key in filter(lambda k: k.isupper(), model_dict.keys()):
            enum_value = getattr(model, key)

            if isinstance(enum_value, ModelEnumValue):
                self._temp_model_enums[enum_value.key] = enum_value

        self._temp_model = model
        self._temp_model_field_names = [field.name for field in model._meta.fields]

        self._temp_db_keys = set(self._temp_db_enums.keys())
        self._temp_model_keys = set(self._temp_model_enums.keys())

        self._process_creating_values()
        self._process_deleting_values()
        self._process_updating_values()

    def run(self):
        """Запуск актуализации записей моделей-пересечений."""
        models = filter(
            lambda m: issubclass(m, ModelEnum) and not is_abstract_model(m) and not is_proxy_model(m),
            apps.get_models(),
        )

        for model in models:
            self._process_model(model)
