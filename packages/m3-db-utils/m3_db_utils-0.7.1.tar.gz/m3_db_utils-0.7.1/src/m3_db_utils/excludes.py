# исключаемые пути для трейсбека, чтобы не выводить лишнее
EXCLUDED_PATHS = (
    'site-packages',
    'debug_tools',
)


def is_path_must_be_excluded(path: str):
    """Определяем, нужно ли исключать путь из вывода трейсбека.

    Args:
         path: str. Строка пути из трейсбека.

    Returns:
        True, если данный путь входит в исключаемые;
        False, если данный путь не должен быть исключен.
    """
    result = False
    for _exclude_path in EXCLUDED_PATHS:
        if _exclude_path in path:
            result = True
            break

    return result
