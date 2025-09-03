from django.db.models.options import (
    DEFAULT_NAMES,
    Options,
    normalize_together,
)
from django.utils.text import (
    camel_case_to_spaces,
    format_lazy,
)


MODEL_ENUM_DEFAULT_NAMES = (
    *DEFAULT_NAMES,
    'extensible',
)


class ModelEnumOptions(Options):
    """Опции модели-перечисления.

    Добавляется опция extensible для определения возможности расширения модели-перечисления из плагинов
    """

    def __init__(self, meta, app_label=None):
        super().__init__(meta=meta, app_label=app_label)

        # Указывает на возможность расширения модели-перечисления из плагинов. Напрямую влияет на механизм удаления
        # элементов перечисления из БД. Если модель-перечисление расширяемая, то удаление значения из БД не
        # производится в автоматическом режиме после прогона миграций. При такой реализации, удаление значений из БД
        # выполняется разработчиком при помощи data-миграций или отдельных скриптов/запросов.
        self.extensible = True

    # TODO BOBUH-19054
    def contribute_to_class(self, cls, name):
        """Переопределенный метод для указания кастомного набора опций."""
        from django.db import (
            connection,
        )
        from django.db.backends.utils import (
            truncate_name,
        )

        cls._meta = self
        self.model = cls
        # First, construct the default values for these options.
        self.object_name = cls.__name__
        self.model_name = self.object_name.lower()
        self.verbose_name = camel_case_to_spaces(self.object_name)

        # Store the original user-defined values for each option,
        # for use when serializing the model definition
        self.original_attrs = {}

        # Next, apply any overridden values from 'class Meta'.
        if self.meta:
            meta_attrs = self.meta.__dict__.copy()
            for name in self.meta.__dict__:
                # Ignore any private attributes that Django doesn't care about.
                # NOTE: We can't modify a dictionary's contents while looping
                # over it, so we loop over the *original* dictionary instead.
                if name.startswith('_'):
                    del meta_attrs[name]

            # Расширена и замена константа DEFAULT_NAMES на MODEL_ENUM_DEFAULT_NAMES с кастомными параметрами в Meta
            for attr_name in MODEL_ENUM_DEFAULT_NAMES:
                if attr_name in meta_attrs:
                    setattr(self, attr_name, meta_attrs.pop(attr_name))
                    self.original_attrs[attr_name] = getattr(self, attr_name)
                elif hasattr(self.meta, attr_name):
                    setattr(self, attr_name, getattr(self.meta, attr_name))
                    self.original_attrs[attr_name] = getattr(self, attr_name)

            self.unique_together = normalize_together(self.unique_together)
            self.index_together = normalize_together(self.index_together)

            # verbose_name_plural is a special case because it uses a 's'
            # by default.
            if self.verbose_name_plural is None:
                self.verbose_name_plural = format_lazy('{}s', self.verbose_name)

            # order_with_respect_and ordering are mutually exclusive.
            self._ordering_clash = bool(self.ordering and self.order_with_respect_to)

            # Any leftover attributes must be invalid.
            if meta_attrs != {}:
                raise TypeError("'class Meta' got invalid attribute(s): %s" % ','.join(meta_attrs))
        else:
            self.verbose_name_plural = format_lazy('{}s', self.verbose_name)
        del self.meta

        # If the db_table wasn't provided, use the app_label + model_name.
        if not self.db_table:
            self.db_table = f'{self.app_label}_{self.model_name}'
            self.db_table = truncate_name(self.db_table, connection.ops.max_name_length())
