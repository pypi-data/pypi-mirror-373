from fastgenerateapi.settings.all_settings import settings


def get_one_cache_decorator(func):
    if settings.app_settings.CACHE_GET_ONE_WHETHER_OPEN:
        return func
    else:
        return no_decorator


def get_all_cache_decorator(func):
    if settings.app_settings.CACHE_GET_ALL_WHETHER_OPEN:
        return func
    else:
        return no_decorator


def tree_cache_decorator(func):
    if settings.app_settings.CACHE_TREE_WHETHER_OPEN:
        return func
    else:
        return no_decorator


def no_decorator(func):
    return func

