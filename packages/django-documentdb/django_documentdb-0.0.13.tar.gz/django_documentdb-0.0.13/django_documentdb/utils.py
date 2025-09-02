import copy
import time
from functools import cached_property

import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.backends.utils import logger


def check_django_compatability():
    """
    Verify that this version of django-documentdb is compatible with the
    installed version of Django. For example, any django-documentdb 5.0.x is
    compatible with Django 5.0.y.
    """
    from . import __version__

    if django.VERSION[:2] < (5, 0):
        A = django.VERSION[0]
        B = django.VERSION[1]
        raise ImproperlyConfigured(
            f"You must use the latest version of django-documentdb {A}.{B}.x "
            f"with Django {A}.{B}.y (found django-documentdb {__version__})."
        )


def set_wrapped_methods(cls):
    """Initialize the wrapped methods on cls."""
    if hasattr(cls, "logging_wrapper"):
        for attr in cls.wrapped_methods:
            setattr(cls, attr, cls.logging_wrapper(attr))
        del cls.logging_wrapper
    return cls


@set_wrapped_methods
class OperationDebugWrapper:
    # The PyMongo database and collection methods that this backend uses.
    wrapped_methods = {
        "find",
        "aggregate",
        "distinct",
        "create_collection",
        "create_indexes",
        "drop",
        "index_information",
        "insert_many",
        "delete_many",
        "drop_index",
        "rename",
        "update_many",
    }

    def __init__(self, db, collection=None):
        self.collection = collection
        self.db = db
        use_collection = collection is not None
        self.collection_name = f"{collection.name}." if use_collection else ""
        self.wrapped = self.collection if use_collection else self.db.database

    def __getattr__(self, attr):
        return getattr(self.wrapped, attr)

    def profile_call(self, func, args=(), kwargs=None):
        start = time.monotonic()
        retval = func(*args, **kwargs or {})
        duration = time.monotonic() - start
        return duration, retval

    def log(self, op, duration, args, kwargs=None):
        # If kwargs are used by any operations in the future, they must be
        # added to this logging.
        msg = "(%.3f) %s"
        args = ", ".join(repr(arg) for arg in args)
        kwargs = ", ".join(f"{k}={v!r}" for k, v in (kwargs or {}).items())
        operation = f"db.{self.collection_name}{op}({args} {kwargs})"
        if len(settings.DATABASES) > 1:
            msg += f"; alias={self.db.alias}"
        self.db.queries_log.append(
            {
                "sql": operation,
                "time": "%.3f" % duration,
            }
        )
        logger.debug(
            msg,
            duration,
            operation,
            extra={
                "duration": duration,
                "sql": operation,
                "alias": self.db.alias,
            },
        )

    def logging_wrapper(method):
        def wrapper(self, *args, **kwargs):
            func = getattr(self.wrapped, method)
            # Collection.insert_many() mutates args (the documents) by adding
            #  _id. deepcopy() to avoid logging that version.
            original_args = copy.deepcopy(args)
            try:
                duration, retval = self.profile_call(func, args, kwargs)
            except Exception as e:
                self.log(method, 0, original_args, kwargs)
                raise e
            self.log(method, duration, original_args, kwargs)
            return retval

        return wrapper


@set_wrapped_methods
class OperationCollector(OperationDebugWrapper):
    def __init__(self, collected_sql=None, *, collection=None, db=None):
        super().__init__(db, collection)
        self.collected_sql = collected_sql

    def log(self, op, args, kwargs=None):
        args = ", ".join(repr(arg) for arg in args)
        kwargs = ", ".join(f"{k}={v!r}" for k, v in (kwargs or {}).items())
        operation = f"db.{self.collection_name}{op}({args} {kwargs})"
        self.collected_sql.append(operation)

    def logging_wrapper(method):
        def wrapper(self, *args, **kwargs):
            self.log(method, args, kwargs)

        return wrapper


class DocumentDBIncompatibleWarning(Warning):
    pass


class NotOptimalOperationWarning(Warning):
    pass


class IndexNotUsedWarning(DocumentDBIncompatibleWarning, NotOptimalOperationWarning):
    pass


class Distinct:
    def __init__(
        self,
        fields: dict[str, str | dict],
    ):
        self.fields = fields

    def aggregation(self):
        return [
            {"$group": {"_id": self.fields}},
            {"$project": {key: f"$_id.{key}" for key in self.fields}},
        ]

    @cached_property
    def is_simple_distinct(self):
        return len(self.fields) == 1

    @property
    def field(self) -> str:
        return list(self.fields.keys())[0]  # noqa: RUF015
