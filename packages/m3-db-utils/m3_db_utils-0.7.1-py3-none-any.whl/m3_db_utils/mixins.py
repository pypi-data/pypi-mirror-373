from abc import (
    abstractmethod,
)
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
)

from django.db.models import (
    CharField,
    IntegerField,
    PositiveIntegerField,
    TextField,
)
from django.db.models.base import (
    Model,
)

from m3_django_compat import (
    classproperty,
)

from m3_db_utils.consts import (
    DEFAULT_ORDER_NUMBER,
)


if TYPE_CHECKING:
    from m3_db_utils.models import (
        ModelEnumValue,
        TitledModelEnum,
    )


class TitleFieldMixin(Model):
    """Добавляет поле текстовое поле title обязательное для заполнения."""

    title = TextField(verbose_name='расшифровка значения')

    class Meta:
        abstract = True


class BaseValueMixin:
    """Базовый миксин для миксинов добавления поля value со значением модели-перечисления."""

    @classmethod
    def get_values_to_enum_data(cls) -> Dict[Any, 'ModelEnumValue']:
        """Возвращает словарь значений перечисления, где в качестве ключа выступает значение поля value."""
        return {
            model_enum_value.value: model_enum_value
            for model_enum_value in cls.get_enum_data().values()
            if hasattr(model_enum_value, 'value')
        }


class IntegerValueMixin(BaseValueMixin, Model):
    """Добавляет целочисленное поле value обязательное для заполнения."""

    value = IntegerField(verbose_name='значение')

    class Meta:
        abstract = True


class PositiveIntegerValueMixin(BaseValueMixin, Model):
    """Добавляет положительное целочисленное поле value обязательное для заполнения."""

    value = PositiveIntegerField(verbose_name='значение')

    class Meta:
        abstract = True


class CharValueMixin(BaseValueMixin, Model):
    """Добавляет символьное поле value обязательное для заполнения."""

    value = CharField(verbose_name='значение ', max_length=256)

    class Meta:
        abstract = True


class BaseEnumRegisterMixin:
    """Базовый миксин, для регистрации класса в модель-перечисление."""

    enum: 'TitledModelEnum'
    """Модель-перечисление в которую регистрируется класс."""
    order_number: int = DEFAULT_ORDER_NUMBER
    """Порядковый номер следования значения модели-перечисления."""

    @classmethod
    def get_register_params(cls) -> Dict[str, Any]:
        """Возвращает словарь параметров для регистрации класса в модель-перечисление."""
        return {'order_number': cls.order_number, 'title': cls.title, 'key': cls.key}

    @classproperty
    @abstractmethod
    def key(cls) -> str:
        """Ключ класса, регистрируемого в модели-перечисления."""

    @classproperty
    @abstractmethod
    def title(cls) -> str:
        """Расшифровка класса, регистрируемого в модели-перечисления."""

    @classmethod
    def register(cls) -> None:
        """Метод, регистрирующий класс в модель-перечисление."""
        params = cls.get_register_params()
        cls.enum.extend(**params)
