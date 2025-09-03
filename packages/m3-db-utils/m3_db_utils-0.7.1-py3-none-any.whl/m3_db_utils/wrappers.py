import logging
import threading
import traceback
from time import (
    time,
)
from typing import (
    Any,
    List,
    Optional,
    Tuple,
)

from django.db.backends import (
    utils as backutils,
)

from m3_db_utils.consts import (
    LOG_QUERY,
    UNNAMED,
)
from m3_db_utils.excludes import (
    is_path_must_be_excluded,
)
from m3_db_utils.settings import (
    SQL_LOG_ONLY_REGISTERED,
    SQL_LOG_WITH_PARAMETERS,
    SQL_LOG_WITH_STACK_TRACE,
)


logger = logging.getLogger('sql_logger')


class DBUtilsCursorDebugWrapper(backutils.CursorWrapper):
    """Расширение класса обертки над курсором.

    Создано для дополнения выводимого лога трейсбэком до строки, которая инициировала запрос.
    """

    @staticmethod
    def get_log_option_for_func():
        """Получение запроса для логирования."""
        thread_locals = threading.local()

        return getattr(thread_locals, LOG_QUERY, None)

    def _get_stack_trace(self):
        """Получение трейса для выявления места вызова SQL-запроса."""
        lines = []
        stack = traceback.extract_stack()

        for path, linenum, func, line in stack:
            # уберем некоторые неинформативные строки
            # список исключаемых путей можно найти в
            # web_bb.debug_tools.ecxludes.EXCLUDED_PATHS
            if is_path_must_be_excluded(path):
                continue

            lines.append(f'File "{path}", line {linenum}, in {func}')
            lines.append(f'  {line}')

        return '\n'.join(lines)

    def _log_query(
        self,
        sql: str,
        duration: float,
        params: Tuple[Any],
        stack_trace: Optional[str],
        query_name: str,
    ):
        """Осуществляет логирование запроса."""
        query_name = query_name if query_name else UNNAMED
        sql = sql % tuple(params) if SQL_LOG_WITH_PARAMETERS and params else sql

        db_alias = self.db.alias if hasattr(self.db, 'alias') else 'default'

        logger.info(
            msg=f'({duration}.3f) {sql}; args={params}',
            extra={
                'duration': duration,
                'sql': sql,
                'params': params,
                'stack_trace': stack_trace,
                'query_name': query_name,
                'database': db_alias,
            },
        )

    def _log_queries(
        self,
        sql: str,
        duration: float,
        param_list: List[Tuple[Any]],
        stack_trace: Optional[str],
        query_name: str,
    ):
        """Осуществляет логирование запроса."""
        query_name = query_name if query_name else UNNAMED
        sql_queries = []

        for params in param_list:
            sql = sql % tuple(params) if SQL_LOG_WITH_PARAMETERS and params else sql

            sql_queries.append(sql)

        db_alias = self.db.alias if hasattr(self.db, 'alias') else 'default'

        logger.info(
            msg=f'({duration}.3f) {sql}; args={param_list}',
            extra={
                'duration': duration,
                'sql': '\n'.join(sql_queries),
                'param_list': param_list,
                'stack_trace': stack_trace,
                'query_name': query_name,
                'database': db_alias,
            },
        )

    def execute(self, sql, params=None):
        """Выполнение запроса."""
        start = time()
        query_name = self.get_log_option_for_func()

        try:
            return super().execute(sql, params)
        finally:
            if SQL_LOG_ONLY_REGISTERED and query_name or not SQL_LOG_ONLY_REGISTERED:
                stop = time()
                duration = stop - start
                stack_trace = self._get_stack_trace() if SQL_LOG_WITH_STACK_TRACE else None

                self._log_query(
                    sql=sql,
                    duration=duration,
                    params=params,
                    stack_trace=stack_trace,
                    query_name=query_name,
                )

    def executemany(self, sql, param_list):
        """Выполнение нескольких запросов."""
        start = time()
        query_name = self.get_log_option_for_func()

        try:
            return super().executemany(sql, param_list)
        finally:
            if SQL_LOG_ONLY_REGISTERED and query_name or not SQL_LOG_ONLY_REGISTERED:
                stop = time()
                duration = stop - start
                stack_trace = self._get_stack_trace() if SQL_LOG_WITH_STACK_TRACE else None

                self._log_queries(
                    sql=sql,
                    duration=duration,
                    param_list=param_list,
                    stack_trace=stack_trace,
                    query_name=query_name,
                )
