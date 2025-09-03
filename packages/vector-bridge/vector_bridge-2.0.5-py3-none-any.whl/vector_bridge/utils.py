from concurrent.futures import Future
from datetime import datetime
from threading import Thread


def call_with_future(fn, future, args, kwargs):
    try:
        result = fn(*args, **kwargs)
        future.set_result(result)
    except Exception as exc:
        future.set_exception(exc)


def threaded(fn):
    def wrapper(*args, **kwargs):
        future = Future()
        Thread(target=call_with_future, args=(fn, future, args, kwargs)).start()
        return future

    return wrapper


def custom_json_serializer_datetime(obj):
    """
    Custom JSON serializer for datetime objects.
    Converts datetime objects to ISO 8601 strings.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO 8601 format
    raise TypeError(f"Type {type(obj)} not serializable")
