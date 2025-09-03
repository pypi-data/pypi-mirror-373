import collections.abc
import copy
from itertools import (
    chain,
)
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from django.apps import (
    apps,
)
from django.core.exceptions import (
    FieldError,
    MultipleObjectsReturned,
    ObjectDoesNotExist,
)
from django.db.models import (
    NOT_PROVIDED,
    CharField,
    Model,
    PositiveIntegerField,
)
from django.db.models.base import (
    ModelBase,
    _has_contribute_to_class,
    subclass_exception,
)
from django.db.models.deletion import (
    CASCADE,
)
from django.db.models.fields.related import (
    OneToOneField,
    resolve_relation,
)
from django.db.models.utils import (
    make_model_tuple,
)
from django.utils.functional import (
    cached_property,
)

from m3_db_utils.consts import (
    DEFAULT_ORDER_NUMBER,
    KEY_FIELD_NAME,
    ORDER_NUMBER_FIELD_NAME,
)
from m3_db_utils.exceptions import (
    RequiredFieldEmptyModelEnumValueError,
)
from m3_db_utils.mixins import (
    CharValueMixin,
    IntegerValueMixin,
    PositiveIntegerValueMixin,
    TitleFieldMixin,
)
from m3_db_utils.options import (
    ModelEnumOptions,
)
from m3_db_utils.strings import (
    EXTEND_NON_EXTENSIBLE_MODEL_ENUMERATION_ERROR,
)


class FictiveForeignKeyField(PositiveIntegerField):
    """Фиктивный внешний ключ, представляющий собой поле с положительным целым значением.

    Используется в случаях, когда требуется обозначить поле как внешний ключ, но внешним ключом оно не являлось.
    """

    def __init__(self, *args, to: str = None, **kwargs):
        if to is None:
            raise ValueError('Не указан параметр to')
        else:
            super().__init__(*args, **kwargs)

            self.to = to

    def deconstruct(self):
        """Return enough information to recreate the field as a 4-tuple.

         * The name of the field on the model, if contribute_to_class() has
           been run.
         * The import path of the field, including the class:e.g.
           django.db.models.IntegerField This should be the most portable
           version, so less specific may be better.
         * A list of positional arguments.
         * A dict of keyword arguments.

        Note that the positional or keyword arguments must contain values of
        the following types (including inner values of collection types):

         * None, bool, str, int, float, complex, set, frozenset, list, tuple,
           dict
         * UUID
         * datetime.datetime (naive), datetime.date
         * top-level classes, top-level functions - will be referenced by their
           full import path
         * Storage instances - these have their own deconstruct() method

        This is because the values here must be serialized into a text format
        (possibly new Python code, possibly JSON) and these are the only types
        with encoding handlers defined.

        There's no need to return the exact way the field was instantiated this
        time, just ensure that the resulting field is the same - prefer keyword
        arguments over positional ones, and omit parameters with their default
        values.
        """
        # Short-form way of fetching all the default parameters
        keywords = {}
        possibles = {
            'to': None,
            'verbose_name': None,
            'primary_key': False,
            'max_length': None,
            'unique': False,
            'blank': False,
            'null': False,
            'db_index': False,
            'default': NOT_PROVIDED,
            'editable': True,
            'serialize': True,
            'unique_for_date': None,
            'unique_for_month': None,
            'unique_for_year': None,
            'choices': None,
            'help_text': '',
            'db_column': None,
            'db_tablespace': None,
            'auto_created': False,
            'validators': [],
            'error_messages': None,
        }
        attr_overrides = {
            'unique': '_unique',
            'error_messages': '_error_messages',
            'validators': '_validators',
            'verbose_name': '_verbose_name',
            'db_tablespace': '_db_tablespace',
        }
        equals_comparison = {'choices', 'validators'}
        for name, default in possibles.items():
            value = getattr(self, attr_overrides.get(name, name))
            # Unroll anything iterable for choices into a concrete list
            if name == 'choices' and isinstance(value, collections.abc.Iterable):
                value = list(value)
            # Do correct kind of comparison
            if name in equals_comparison:
                if value != default:
                    keywords[name] = value
            else:
                if value is not default:
                    keywords[name] = value
        # Work out path - we shorten it for known Django core fields
        path = '%s.%s' % (self.__class__.__module__, self.__class__.__qualname__)
        if path.startswith('django.db.models.fields.related'):
            path = path.replace('django.db.models.fields.related', 'django.db.models')
        elif path.startswith('django.db.models.fields.files'):
            path = path.replace('django.db.models.fields.files', 'django.db.models')
        elif path.startswith('django.db.models.fields.json'):
            path = path.replace('django.db.models.fields.json', 'django.db.models')
        elif path.startswith('django.db.models.fields.proxy'):
            path = path.replace('django.db.models.fields.proxy', 'django.db.models')
        elif path.startswith('django.db.models.fields'):
            path = path.replace('django.db.models.fields', 'django.db.models')
        # Return basic info - other fields should override this.
        return (self.name, path, [], keywords)


class ModelEnumValue:
    """Значение модели-перечисления.

    Универсальная сущность, которая используется в качестве значений параметров класса модели-перечисления наследника
    m3_db_utils.models.ModelEnum. Должны быть заполнены поля, обозначенные в моделе, как обязательные. Иначе не будет
    возможности записать значения в базу данных. Часть полей значения модели-перечисления может не иметь необходимости
    записи в БД. Для этого в моделе не нужно создавать одноименных полей.

    Ключ записи заполняется при инициализации класса модели именем параметра класса модели-перечисления. Это позволяет
    избежать дублирования имен и использования в коде и базе одинакового идентификатора, что упростит задачу при
    рефакторинге, т.к. ссылка на модель-перечисление - это внешний ключ и изменение значений будет означать создание
    миграции с прохождением всех моделей, ссылающихся на модель-перечисление и замену старого значения на новое.
    """

    def __init__(self, key=None, order_number=None, **kwargs):
        """Инициализация значения модели-перечисления.

        Args:
            key: ключ, выступает значением первичного ключа. Заполняется при инициализации класса модели-перечисления
                именем переменной класса модели-перечисления
            order_number: порядковый номер значения модели-перечисления используемый в сортировке значений
                модели-перечисления
            kwargs: в именованных параметрах передаются параметры значения перечисления. В моделе должны быть поля, с
                соответствующими названиями и типами. Если будут переданы значения, выходящие за рамки полей модели,
                они будут сохранены в значении модели-перечисления, но в базу данных не будут записаны. При сохранении
                значений в базу данных будут браться значения полей.
        """
        self._required_fields = [KEY_FIELD_NAME, ORDER_NUMBER_FIELD_NAME]
        self._fields = [*kwargs.keys(), *self._required_fields]

        self._key = key

        kwargs[ORDER_NUMBER_FIELD_NAME] = order_number

        for field_name, field_value in kwargs.items():
            setattr(self, field_name, field_value)

    def __repr__(self):
        return f'<{self.__class__.__name__} @key="{self.key}" @order_number={self.order_number}>'

    def __str__(self):
        return self.__repr__()

    @property
    def key(self) -> str:
        """Возвращает ключ."""
        return self._key

    @key.setter
    def key(self, v):
        """Устанавливает ключ."""
        self._key = v

    @property
    def fields(self) -> List[str]:
        """Возвращает список полей значения модели-перечисления."""
        return self._fields

    def set_field_value(self, field_name: str, field_value: Any, force: bool = False):
        """Установка значения поля.

        Args:
            field_name: имя поля
            field_value: значение поля
            force: установить значение, даже если оно уже было установлено ранее
        """
        if hasattr(self, field_name) and (getattr(self, field_name) is None or force):
            setattr(self, field_name, field_value)

    def set_required_field(self, field_name):
        """Установка обязательности поля в значении модели-перечисления."""
        if getattr(self, field_name, None) is None:
            raise RequiredFieldEmptyModelEnumValueError

        self._required_fields.append(field_name)

    @cached_property
    def required_fields(self):
        """Возвращает список обязательных для заполнения полей значения модели-перечисления."""
        return self._required_fields

    @cached_property
    def required_fields_without_key(self):
        """Возвращает список обязательных для заполнения полей значения модели-перечисления без поля key."""
        required_fields = copy.deepcopy(self.required_fields)
        required_fields.remove(KEY_FIELD_NAME)

        return required_fields


class ModelEnumMetaclass(ModelBase):
    """Метакласс для моделей-перечислений с переопределенным набором параметров в Meta.

    Поведение достигается путем замены стандартного Options на кастомный.
    """

    # TODO BOBUH-19054
    def __new__(cls, name, bases, attrs, **kwargs):
        """Создание класса модели-перечисления."""
        super_new = super(ModelBase, cls).__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        # Create the class.
        module = attrs.pop('__module__')
        new_attrs = {'__module__': module}
        classcell = attrs.pop('__classcell__', None)
        if classcell is not None:
            new_attrs['__classcell__'] = classcell
        attr_meta = attrs.pop('Meta', None)

        cls._patch_model_enum_values(attrs=attrs)

        # Pass all attrs without a (Django-specific) contribute_to_class()
        # method to type.__new__() so that they're properly initialized
        # (i.e. __set_name__()).
        contributable_attrs = {}
        for obj_name, obj in list(attrs.items()):
            if _has_contribute_to_class(obj):
                contributable_attrs[obj_name] = obj
            else:
                new_attrs[obj_name] = obj
        new_class = super_new(cls, name, bases, new_attrs, **kwargs)

        abstract = getattr(attr_meta, 'abstract', False)
        meta = attr_meta or getattr(new_class, 'Meta', None)
        base_meta = getattr(new_class, '_meta', None)

        app_label = None

        # Look for an application configuration to attach the model to.
        app_config = apps.get_containing_app_config(module)

        if getattr(meta, 'app_label', None) is None:
            if app_config is None:
                if not abstract:
                    raise RuntimeError(
                        f"Model class {module}.{name} doesn't declare an explicit app_label and isn't in an "
                        f'application in INSTALLED_APPS.'
                    )

            else:
                app_label = app_config.label

        # Options был заменен на ModelEnumOptions для добавления дополнительных параметров в Meta
        new_class.add_to_class('_meta', ModelEnumOptions(meta, app_label))

        if not abstract:
            new_class.add_to_class(
                'DoesNotExist',
                subclass_exception(
                    'DoesNotExist',
                    tuple(x.DoesNotExist for x in parents if hasattr(x, '_meta') and not x._meta.abstract)
                    or (ObjectDoesNotExist,),
                    module,
                    attached_to=new_class,
                ),
            )
            new_class.add_to_class(
                'MultipleObjectsReturned',
                subclass_exception(
                    'MultipleObjectsReturned',
                    tuple(x.MultipleObjectsReturned for x in parents if hasattr(x, '_meta') and not x._meta.abstract)
                    or (MultipleObjectsReturned,),
                    module,
                    attached_to=new_class,
                ),
            )
            if base_meta and not base_meta.abstract:
                # Non-abstract child classes inherit some attributes from their
                # non-abstract parent (unless an ABC comes before it in the
                # method resolution order).
                if not hasattr(meta, 'ordering'):
                    new_class._meta.ordering = base_meta.ordering
                if not hasattr(meta, 'get_latest_by'):
                    new_class._meta.get_latest_by = base_meta.get_latest_by

        is_proxy = new_class._meta.proxy

        # If the model is a proxy, ensure that the base class
        # hasn't been swapped out.
        if is_proxy and base_meta and base_meta.swapped:
            raise TypeError("%s cannot proxy the swapped model '%s'." % (name, base_meta.swapped))

        # Add remaining attributes (those with a contribute_to_class() method)
        # to the class.
        for obj_name, obj in contributable_attrs.items():
            new_class.add_to_class(obj_name, obj)

        # All the fields of any type declared on this model
        new_fields = chain(
            new_class._meta.local_fields, new_class._meta.local_many_to_many, new_class._meta.private_fields
        )
        field_names = {f.name for f in new_fields}

        # Basic setup for proxy models.
        if is_proxy:
            base = None
            for parent in [kls for kls in parents if hasattr(kls, '_meta')]:
                if parent._meta.abstract:
                    if parent._meta.fields:
                        raise TypeError(
                            f"Abstract base class containing model fields not permitted for proxy model {name}'."
                        )
                    else:
                        continue
                if base is None:
                    base = parent
                elif parent._meta.concrete_model is not base._meta.concrete_model:
                    raise TypeError("Proxy model '%s' has more than one non-abstract model base class." % name)
            if base is None:
                raise TypeError("Proxy model '%s' has no non-abstract model base class." % name)
            new_class._meta.setup_proxy(base)
            new_class._meta.concrete_model = base._meta.concrete_model
        else:
            new_class._meta.concrete_model = new_class

        # Collect the parent links for multi-table inheritance.
        parent_links = {}
        for base in reversed([new_class] + parents):
            # Conceptually equivalent to `if base is Model`.
            if not hasattr(base, '_meta'):
                continue
            # Skip concrete parent classes.
            if base != new_class and not base._meta.abstract:
                continue
            # Locate OneToOneField instances.
            for field in base._meta.local_fields:
                if isinstance(field, OneToOneField):
                    related = resolve_relation(new_class, field.remote_field.model)
                    parent_links[make_model_tuple(related)] = field

        # Track fields inherited from base models.
        inherited_attributes = set()
        # Do the appropriate setup for any model parents.
        for base in new_class.mro():
            if base not in parents or not hasattr(base, '_meta'):
                # Things without _meta aren't functional models, so they're
                # uninteresting parents.
                inherited_attributes.update(base.__dict__)
                continue

            parent_fields = base._meta.local_fields + base._meta.local_many_to_many
            if not base._meta.abstract:
                # Check for clashes between locally declared fields and those
                # on the base classes.
                for field in parent_fields:
                    if field.name in field_names:
                        raise FieldError(
                            f'Local field {field.name!r} in class {name!r} clashes with field of the same name from '
                            f'base class {base.__name__!r}.'
                        )
                    else:
                        inherited_attributes.add(field.name)

                # Concrete classes...
                base = base._meta.concrete_model
                base_key = make_model_tuple(base)
                if base_key in parent_links:
                    field = parent_links[base_key]
                elif not is_proxy:
                    attr_name = '%s_ptr' % base._meta.model_name
                    field = OneToOneField(
                        base,
                        on_delete=CASCADE,
                        name=attr_name,
                        auto_created=True,
                        parent_link=True,
                    )

                    if attr_name in field_names:
                        raise FieldError(
                            f"Auto-generated field '{attr_name}' in class {name!r} for parent_link to base class "
                            f'{base.__name__!r} clashes with declared field of the same name.'
                        )

                    # Only add the ptr field if it's not already present;
                    # e.g. migrations will already have it specified
                    if not hasattr(new_class, attr_name):
                        new_class.add_to_class(attr_name, field)
                else:
                    field = None
                new_class._meta.parents[base] = field
            else:
                base_parents = base._meta.parents.copy()

                # Add fields from abstract base class if it wasn't overridden.
                for field in parent_fields:
                    if (
                        field.name not in field_names
                        and field.name not in new_class.__dict__
                        and field.name not in inherited_attributes
                    ):
                        new_field = copy.deepcopy(field)
                        new_class.add_to_class(field.name, new_field)
                        # Replace parent links defined on this base by the new
                        # field. It will be appropriately resolved if required.
                        if field.one_to_one:
                            for parent, parent_link in base_parents.items():
                                if field == parent_link:
                                    base_parents[parent] = new_field

                # Pass any non-abstract parent classes onto child.
                new_class._meta.parents.update(base_parents)

            # Inherit private fields (like GenericForeignKey) from the parent
            # class
            for field in base._meta.private_fields:
                if field.name in field_names:
                    if not base._meta.abstract:
                        raise FieldError(
                            f'Local field {field.name!r} in class {name!r} clashes with field of the same name from '
                            f'base class {base.__name__!r}.'
                        )
                else:
                    field = copy.deepcopy(field)
                    if not base._meta.abstract:
                        field.mti_inherited = True
                    new_class.add_to_class(field.name, field)

        # Copy indexes so that index names are unique when models extend an
        # abstract model.
        new_class._meta.indexes = [copy.deepcopy(idx) for idx in new_class._meta.indexes]

        if abstract:
            # Abstract base models can't be instantiated and don't appear in
            # the list of models for an app. We do the final setup for them a
            # little differently from normal models.
            attr_meta.abstract = False
            new_class.Meta = attr_meta
            return new_class

        new_class._prepare()
        new_class._meta.apps.register_model(new_class._meta.app_label, new_class)

        cls._patch_new_class_after_init(new_class, attrs)

        return new_class

    def __setattr__(cls, name, value):
        if isinstance(value, ModelEnumValue) and not cls._meta.extensible:
            raise RuntimeError(EXTEND_NON_EXTENSIBLE_MODEL_ENUMERATION_ERROR)

        super(ModelBase, cls).__setattr__(name, value)

    @classmethod
    def _patch_model_enum_values(cls, attrs: Dict[str, Any]):
        """Патчинг параметров моделей-перечислений с добавлением ключей."""
        for key, value in attrs.items():
            if isinstance(value, ModelEnumValue):
                value.key = key

    @staticmethod
    def _set_default_model_enum_values(new_class, attrs: Dict[str, Any]):
        """Установка дефолтных значений из полей модели в поля значения модели-перечисления.

        Работает, если значения еще не были заполнены.
        """
        fields_with_default_values = [
            field
            for field in new_class._meta.fields
            if getattr(field, 'default', None) is not None and getattr(field, 'default', None) != NOT_PROVIDED
        ]

        model_attrs = {}
        for class_ in new_class.__mro__:
            model_attrs.update(vars(class_))

        model_enum_values = [value for value in model_attrs.values() if isinstance(value, ModelEnumValue)]

        for model_enum_value in model_enum_values:
            for model_field in fields_with_default_values:
                model_enum_value.set_field_value(
                    field_name=model_field.name,
                    field_value=model_field.default,
                )

    @staticmethod
    def _set_model_enum_value_required_fields(new_class, attrs: Dict[str, Any]):
        """Добавление обязательных для заполнения полей в значении модели-перечисления."""
        required_fields = []

        for field in new_class._meta.fields:
            is_blank = getattr(field, 'blank', None)
            has_default = getattr(field, 'default', None)

            if is_blank is not None and (not is_blank and (has_default is None or has_default == NOT_PROVIDED)):
                required_fields.append(field.name)

        model_attrs = {}
        for class_ in new_class.__mro__:
            model_attrs.update(vars(class_))

        for key, value in model_attrs.items():
            if isinstance(value, ModelEnumValue):
                for field_name in required_fields:
                    try:
                        value.set_required_field(field_name=field_name)
                    except RequiredFieldEmptyModelEnumValueError:
                        raise RequiredFieldEmptyModelEnumValueError(
                            f'У модели-перечисления поле "{field_name}" является обязательным. В значении свойства '
                            f'класса "{new_class.__name__}" модели-перечисления "{key}" необходимо установить значение '
                            f'для поля "{field_name}"!'
                        )

    @classmethod
    def _patch_new_class_after_init(cls, new_class, attrs: Dict[str, Any]):
        """Патчинг сформированного класса модели после его инициализации."""
        cls._set_default_model_enum_values(new_class=new_class, attrs=attrs)
        cls._set_model_enum_value_required_fields(new_class=new_class, attrs=attrs)


class ModelEnum(Model, metaclass=ModelEnumMetaclass):
    """Модель-перечисление.

    Предназначен для создания перечислений, которые будут храниться в базе данных. На значения перечислений можно
    ссылаться через внешний ключ. Данный подход является более удобным с точки зрения работы на уровне SQL -
    организации сортировки, фильтрации и пр. На стороне Python, работа производится как с обычным перечислением.

    При ссылке на перечисление через внешний ключ, лучше указывать on_delete=PROTECTED, т.к. при удалении значений
    перечисления явно будут возникать ошибки на уровне БД, что позволит сохранить целостность данных.

    В перечислении значения указываются в свойствах класса именуемых заглавными буквами с разделителем нижнее
    подчеркивание. Значением перечисления является именованный кортеж ModelEnumValue.

    Добавление записей в перечисление производится путем указания нового свойства и присваиванием ему значения
    m3_db_utils.models.ModelEnumValue.

    Модель-перечисление поддерживает сортировку значений для вывода пользователю в заданном порядке. Для указания
    порядка следования значений используется поле order_number. Поле будет добавлено в таблицу модели перечисления,
    т.к. логика вывода значений модели-перечисления может быть реализована и на уровне SQL. По умолчанию проставляется
    значение 1000, чтобы все значения модели-перечисления, без явно проставленного порядкового номера находились в
    конце.

    Перечисление поддерживает добавление, обновление и удаление значений перечислений.
    Актуализатор :class:`m3_db_utils.helpers.ModelEnumDBValueUpdater` по добавлению, обновлению и удалению значений
    перечисления. Запускается на сигнал post_migrate. В актуализаторе производится поиск всех моделей перечислений. Для
    каждой модели выбираются все значения из БД и собираются все значения из класса модели-перечисления.

    Далее производится сравнение значений:

    - Если key уже есть в БД, то необходимо проверить, требуется ли обновление. Если требуется, то значения обновляются
        и помещаются в список объектов на обновление;
    - Если key есть в БД, но нет в перечислении, то он был удален;
    - Если key нет в БД, но есть в значениях перечисления, то было добавлено новое значение перечисления.

    В Meta опциях появился параметр extensible. Он отвечает за возможность расширения (патчинга) класса
    модели-перечисления из плагинов. Если True, то можно, False - запрещается. Данный параметр напрямую влияет на
    отключение плагина. Если модель-перечисление расширяемая, то при отключении плагина, значения элементов перечисления
    не будут удаляться из БД при актуализации значений. Т.к. ссылка на перечисление представлена в виде внешнего ключа,
    то при попытке удаления значения из модели-перечисления, в случае использования, будет получена ошибка о
    невозможности удаления значения. В этом случае необходимо реализовать миграцию данных, которая будет заменять
    старое значение, на новое или удалять зависимые записи.
    """

    is_strict_order_number = False
    """Флаг, указывающий на то, что порядковые номера значений перечисления должны быть уникальны."""

    key = CharField(verbose_name='ключ', null=False, primary_key=True, db_index=True, max_length=512)

    order_number = PositiveIntegerField(verbose_name='Порядковый номер', default=DEFAULT_ORDER_NUMBER)

    class Meta:
        abstract = True

    @classmethod
    def _calculate_order_number(cls, order_number: Optional[int], *args, **kwargs) -> int:
        """Вычисление порядкового номера элемента модели-перечисления.

        Является вспомогательным методом для расширения модели-перечисления.
        """
        order_number_enum_data = cls._get_order_number_enum_data()

        if order_number is None:
            order_numbers = order_number_enum_data.keys()
            calculated_order_number = max(order_numbers) + 1 if order_number_enum_data else 1
        else:
            if order_number in order_number_enum_data and cls.is_strict_order_number:
                raise ValueError(
                    f'Order number "{order_number}" is already in use in the "{cls.__name__}". '
                    f'Please choose a different one.'
                )

            calculated_order_number = order_number

        return calculated_order_number

    @classmethod
    def _get_enum_data(cls) -> Dict[str, ModelEnumValue]:
        enum_data = {}

        model_dict = {}
        for class_ in cls.__mro__:
            model_dict.update(vars(class_))

        for key in filter(lambda k: k.isupper(), model_dict.keys()):
            enum_value = getattr(cls, key)

            if isinstance(enum_value, ModelEnumValue):
                enum_data[key] = enum_value

        return enum_data

    @classmethod
    def _get_order_number_enum_data(cls) -> Dict[int, ModelEnumValue]:
        """Возвращает данные перечисления в виде словаря с порядковым номером в качестве ключа."""
        enum_data = cls._get_enum_data()

        order_number_enum_data = {model_value.order_number: model_value for model_value in enum_data.values()}

        return order_number_enum_data

    @classmethod
    def get_enum_data(cls, is_reversed: bool = False) -> Dict[str, ModelEnumValue]:
        """Возвращает данные перечисления в виде словаря.

        Args:
            is_reversed: флаг, указывающий на то, что необходимо вернуть значения модели перечисления отсортированных
                в обратном порядке order_number

        Returns:
            {
                key: ModelEnumValue,
                ...
            }
        """
        enum_data = cls._get_enum_data()

        sorted_enum_data = dict(sorted(enum_data.items(), key=lambda edi: edi[1].order_number, reverse=is_reversed))

        return sorted_enum_data

    @classmethod
    def get_model_enum_values(cls, is_reversed: bool = False) -> List[ModelEnumValue]:
        """Получение значений модели перечисления.

        Args:
            is_reversed: флаг, указывающий на то, что необходимо вернуть значения модели перечисления отсортированных
                в обратном порядке order_number
        """
        return list(cls.get_enum_data(is_reversed=is_reversed).values())

    @classmethod
    def get_model_enum_keys(cls, is_reversed: bool = False) -> List[str]:
        """Получение ключей модели перечисления.

        Args:
            is_reversed: флаг, указывающий на то, что необходимо вернуть ключи значений модели перечисления
            отсортированных в обратном порядке order_number
        """
        return list(cls.get_enum_data(is_reversed=is_reversed).keys())

    @classmethod
    def get_model_enum_value(cls, key: str) -> ModelEnumValue:
        """Возвращает значение элемента перечисления.

        Args:
            key: ключ элемента перечисления, указывается заглавными буквами с разделителем нижнее подчеркивание

        Returns:
            ModelEnumValue - значение элемента перечисления
        """
        enum_data = cls.get_enum_data()

        return enum_data[key]

    @classmethod
    def extend(cls, key, order_number: Optional[int] = None, **kwargs):
        """Метод расширения модели-перечисления, например из плагина.

        Необходимо, чтобы сама модель-перечисление была расширяемой. Для этого необходимо, чтобы был установлен
        extensible = True в Meta.

        Args:
            key: ключ элемента перечисления, указывается заглавными буквами с разделителем нижнее подчеркивание
            order_number: порядковый номер значения модели перечисления используемый при сортировке
            kwargs: дополнительные именованные параметры
        """
        order_number = cls._calculate_order_number(order_number=order_number)

        setattr(cls, key, ModelEnumValue(key=key, order_number=order_number, **kwargs))

    @classmethod
    def extends(cls, items: List[Dict[str, Any]]):
        """Метод расширения модели-перечисления множеством значений.

        Расширение производится, например, из плагина. Необходимо, чтобы сама модель-перечисление была расширяемой.
        Для этого необходимо, чтобы был установлен extensible = True в Meta.

        Args:
            items: список словарей со значениями для формирования значений модели-перечисления. Обязательным полем
                является key, order_number заполняется в случае необходимости соблюдения порядка значений
                модели-перечисления.
        """
        for item in items:
            cls.extend(**item)

    @property
    def model_enum_value(self) -> ModelEnumValue:
        """Получение значения модели-перечисления у экземпляра модели."""
        return getattr(self, self.key)


class IntegerModelEnum(ModelEnum, IntegerValueMixin):
    """Модель-перечисление с обязательным для заполнения целочисленным полем value."""

    class Meta:
        abstract = True


class PositiveIntegerModelEnum(ModelEnum, PositiveIntegerValueMixin):
    """Модель-перечисление с обязательным для заполнения целочисленным положительным полем value."""

    class Meta:
        abstract = True


class CharModelEnum(ModelEnum, CharValueMixin):
    """Модель-перечисление c обязательным для заполнения символьным полем value."""

    class Meta:
        abstract = True


class TitledModelEnum(ModelEnum, TitleFieldMixin):
    """Модель-перечисление c обязательным для заполнения текстовым полем title."""

    class Meta:
        abstract = True


class TitledIntegerModelEnum(IntegerModelEnum, TitleFieldMixin):
    """Модель-перечисление с обязательными для заполнения целочисленным полем value и текстовым полем title."""

    class Meta:
        abstract = True


class TitledPositiveIntegerModelEnum(PositiveIntegerModelEnum, TitleFieldMixin):
    """Модель-перечисление с обязательными целочисленным положительным полем value и текстовым полем title."""

    class Meta:
        abstract = True


class TitledCharModelEnum(CharModelEnum, TitleFieldMixin):
    """Модель-перечисление c символьным полем value и текстовым полем title."""

    class Meta:
        abstract = True


class FictiveForeignKeyMixin:
    """Добавляет метод получения фиктивных внешних ключей."""

    @cached_property
    def fictive_foreign_key_field_names(self) -> List[str]:
        """Возвращает список имен полей с фиктивными внешними ключами."""
        field_names = []

        for field in self._meta.concrete_fields:
            if isinstance(field, FictiveForeignKeyField):
                field_names.append(field.attname)

        return field_names
