from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Manager
from django.db.models import Model as djangoModel
from django.db.models import TimeField as django_TimeField
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _


class FieldError(ValueError):
    pass


class ForeignKeyFieldError(FieldError):
    def __init__(self, msg, model, value):
        self.model = model
        self.value = value
        self.msg = msg
        super(ForeignKeyFieldError, self).__init__(self.msg)


class FieldValueMissing(FieldError):
    def __init__(self, field_name):
        super(FieldValueMissing, self).__init__("No value found for field %s" % field_name)


class ListGeoException(Exception):
    """
    Raised when no there are a field than it not is defined in the class
    """
    def __init__(self, message):
        Exception.__init__(self, message)


MISSING_ERROR_MESSAGE = (
    'ValidationError raised by `{class_name}`, but error key `{key}` does '
    'not exist in the `error_messages` dictionary.'
)


class Field:
    default_error_messages = {
        'required': _('This field is required.'),
    }
    position = 0
    field_name = "Field"

    def __init__(self, *args, null=False, **kwargs):
        self.in_csv = kwargs.pop('in_csv', True)

        if 'row_num' in kwargs:
            self.position = kwargs.pop('row_num')
        else:
            self.position = Field.position
            Field.position += 1
        if 'match' in kwargs:
            self.match = kwargs.pop('match')

        if 'default' in kwargs:
            # with this value we can overwrite all values in csv
            # for this field. It is usefull when we can a default value
            # but we don't put one default value in the model
            self.has_default = self.to_python(kwargs.pop('default'))

        # If null value is allowed, this field could be empty in the row
        self.null = null

        # Collect default error message from self and parent classes
        error_messages = kwargs.get('error_messages')
        messages = {}
        for cls in reversed(self.__class__.__mro__):
            messages.update(getattr(cls, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

    def fail(self, key, **kwargs):
        """
        A helper method that simply raises a validation error.
        """
        try:
            msg = self.error_messages[key]
        except KeyError:
            class_name = self.__class__.__name__
            msg = MISSING_ERROR_MESSAGE.format(class_name=class_name, key=key)
            raise AssertionError(msg)
        message_string = msg.format(**kwargs)
        raise ValidationError(message_string, code=key)


class IntegerField(Field):
    default_error_messages = {
        'invalid': _('A valid integer is required.'),
    }
    field_name = "Integer"

    def to_python(self, value):
        if hasattr(self, "null") and not value:
            return None
        try:
            data = int(value)
        except (TypeError, ValueError):
            self.fail('invalid')
        return data


class TimeField(Field):
    field_name = "Time"

    def to_python(self, value):
        if self.null and not value:
            return None
        field = django_TimeField()
        return field.to_python(value)


class BooleanField(Field):
    field_name = "Boolean"

    def default_is_true_method(self, value):
        if hasattr(self, "null") and not value:
            return None
        return value.lower() == "true"

    def __init__(self, *args, **kwargs):
        if 'is_true' in kwargs:
            self.is_true_method = kwargs.pop('is_true')
        else:
            self.is_true_method = self.default_is_true_method
        super(BooleanField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        return self.is_true_method(value)


class CharField(Field):
    field_name = "String"

    def to_python(self, value):
        if value:
            return value.strip()
        else:
            return value


class FloatField(Field):
    default_error_messages = {
        'invalid': _('A valid number is required.'),
    }
    field_name = "Float"

    def to_python(self, value):
        # handle empty values depending of this field is nullable
        if not value:
            if self.null:
                return None
            self.fail('required')
        try:
            return float(value)
        except (TypeError, ValueError):
            self.fail('invalid')


class DateField(Field):
    DEFAULT_DATE_FORMAT = '%Y-%m-%d'
    field_name = "Date"

    def __init__(self, *args, **kwargs):
        self.strptime = kwargs.pop('strptime', self.DEFAULT_DATE_FORMAT)

    def to_python(self, value):
        if value:
            try:
                return datetime.strptime(value, self.strptime)
            except ValueError as e:
                raise ValidationError(e)
        return None


class ForeignKey(Field):
    field_name = "ForeignKey"

    def __init__(self, *args, **kwargs):
        self.pk = kwargs.pop('pk', 'pk')
        if len(args) < 1:
            raise ValueError("You should provide a Model as the first argument.")
        self.model = args[0]
        try:
            if not issubclass(self.model, djangoModel):
                raise TypeError("The first argument should be a django model class.")
        except TypeError:
            raise TypeError("The first argument should be a django model class.")
        super(ForeignKey, self).__init__(**kwargs)

    def to_python(self, value):
        try:
            return self.model.objects.get(**{self.pk: value})
        except ObjectDoesNotExist:
            msg = "No match found for %(model)s with value %(value)s"
            params = {'model': self.model.__name__, 'value': value}
            raise ValidationError(msg, params=params)


class SlugRelatedField(Field):
    # We use this field for match one object in one ForeignKey
    # but we need an other field that is not a tipical id
    # Practicaly is the same of ForeignKey but from other identificatior
    # not the id or pk
    field_name = "Slug_Related_Field"
    queryset = None

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.args = args
        self.kwargs = kwargs
        self.queryset = kwargs.pop('queryset', self.queryset)

        if 'match' in kwargs:
            self.match = kwargs['match']
        if 'slug_field' in kwargs:
            self.slug_field = kwargs['slug_field']

        assert self.queryset is not None, (
            'Relational field must provide a `queryset` argument, '
            'override `get_queryset`, or set read_only=`True`.'
        )
        self.model = self.queryset.model

    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, (QuerySet, Manager)):
            # Ensure queryset is re-evaluated whenever used.
            # Note that actually a `Manager` class may also be used as the
            # queryset argument. This occurs on ModelSerializer fields,
            # as it allows us to generate a more expressive 'repr' output
            # for the field.
            # Eg: 'MyRelationship(queryset=ExampleModel.objects.all())'
            queryset = queryset.all()
        return queryset

    def get(self, value):
        # wee split in this function for help to RelatedFromUniquesField
        return self.get_queryset().get(**{self.slug_field: value.strip()})

    def to_python(self, value):
        # handle empty values depending of this field is nullable
        if not value:
            if self.null:
                return None

            # handle if null is defined on model field
            model_field = self.csv_model._meta.get_field(self.source)
            if model_field.null:
                # FIXME this is hacky, any other idea to address that?
                # monkey patch to avoid csvimporter.validate() raise ValidationError
                # this field cannot be blank while runnin `object.clean_fields()`
                model_field.blank = True
                return None

            self.fail('required')

        try:
            return self.get(value)
        except ObjectDoesNotExist:
            msg = "No match found for %(model)s with value %(value)s"
            params = {'model': self.model.__name__, 'value': value}
            raise ValidationError(msg, params=params)

        except (TypeError, ValueError) as e:
            raise ValidationError(e, code='invalid')


class CachedSlugRelatedField(Field):
    """
    SlugRelatedField which caches queryset on memory to boost importer speed.

    It performs a single "big" database query instead of N "small" queries
    where N is the number of rows to be imported.
    """
    def __init__(self, *args, null=False, **kwargs):
        queryset = kwargs.pop('queryset')
        slug_field = kwargs.pop('slug_field')

        self.queryset = queryset
        self.slug_field = slug_field
        self.model = queryset.model

        super().__init__(*args, null=null, **kwargs)

    def to_python(self, value):
        if not hasattr(self, 'cached_queryset'):
            # NOTE: cast to str dict key because CSV value by default its a string
            self.cached_queryset = {
                str(getattr(obj, self.slug_field)): obj for obj in self.queryset
            }

        value = value.strip()
        try:
            return self.cached_queryset[value]
        except KeyError:
            msg = "No match found for '%(model)s' with value '%(value)s' on field '%(slug)s'"
            params = {'model': self.model.__name__, 'value': value, 'slug': self.slug_field}
            raise ValidationError(msg, params=params, code='invalid')


class RelatedFromUniquesField(SlugRelatedField):
    # overwrite SlugRelatedField for du a query more complex
    # from fields of unique together

    field_name = "Related_Uniques_together_field"

    def get(self, dvalue):
        d = {k: dvalue[self.slug_field[k]].strip() for k in self.slug_field}
        return self.get_queryset().get(**d)


class CsvRelated(Field):
    field_name = "Csv_Related"

    def __init__(self, *args, **kwargs):
        self.csvModel = args[0]

    def to_python(self, value):
        return value


class DefaultField(Field):
    """
    We use this field for override all values in csv or add one
    that not exist in the csv

    """

    field_name = "DefaultField"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = args[0]

    def to_python(self):
        return self.value


class ManyToManyField(Field):
    """
    We use this field for save one Information int csv in a
    additional table that to be a realtion many to many

    """

    field_name = "ManyToManyField"

    def __init__(self, *args, **kwargs):
        self.csvModel = args[0]
        self.method = self.csvModel.__name__.lower()
        if 'dict_params' in kwargs:
            self.dict_params = kwargs['dict_params']
        if 'match' in kwargs:
            self.match = kwargs['match']

    def task(self, object_father):
        if hasattr(object_father, self.method):
            method = getattr(object_father, self.method)
            getattr(method, 'add')(self.parameters)

    def to_python(self, colname, line_number, value):
        self.colname = colname
        self.line_number = line_number
        self.dict_params[self.match] = value

        p1 = self.csvModel.objects.get(**self.dict_params)
        self.parameters = p1
        return self


class CsvFieldLink(Field):
    """
    We use this field for save the same Information in to fields
    in the model but there are only one in the csv is offer.
    As args you get a dictionary composed for k the value in the
    model and v the column name from you want copy
    normaly this key not exist in the csv file.
    And is necessary that the name of the CsvFieldLink is the same
    than the key of this dictionary

    """

    field_name = "Csv_Field_Link"

    def __init__(self, *args, **kwargs):
        self.link = args[0]

    def to_python(self, value):
        return value


class ComposedKeyField(ForeignKey):
    def to_python(self, value):
        try:
            return self.model.objects.get(**value)
        except ObjectDoesNotExist:
            raise ForeignKeyFieldError("No match found for %s" % self.model.__name__, self.model.__name__, value)


class MultiSlugRelatedField(SlugRelatedField):
    """
    overwrite SlugRelatedField for do a query more complex
    from observation of pecbms.
    The target is get one value from more than one field of them.
    Is tipicaly when the foreingkey depend of more than one field.
    """

    field_name = "MultiSlugRelatedField"

    def __init__(self, *args, **kwargs):
        super(MultiSlugRelatedField, self).__init__(*args, **kwargs)
        # matchs is similar to match but is a dictionary
        # becouse is multiple
        self.matchs = kwargs.pop('matchs', None)

    def get(self, dvalue):
        return self.get_queryset().get(**dvalue)

    def to_python(self, line):
        try:
            dvalues = {self.matchs[k]: line[k].strip() for k in self.matchs.keys()}
            return self.get(dvalues)
        except ObjectDoesNotExist:
            raise ForeignKeyFieldError("No match found for %s" % self.model.__name__, self.model.__name__, line)
        except (TypeError, ValueError, KeyError):
            raise FieldError('invalid')
