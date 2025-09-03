from django.conf import (
    settings,
)

from edu_function_tools.runners import (
    EduRunner,
)
from educommon.utils.seqtools import (
    make_chunks,
)


class BaseCollectingDataRunner(EduRunner):
    """Базовый класс ранеров функций сбора данных для интеграции с "Региональная витрина данных".

    Поддерживается режим принудительного запуска функций без постановки в очередь на исполнение.
    """

    def _get_runnable_objects(self, logs, *args, **kwargs):
        """Возвращает генератор запускаемых объектов."""
        if not self.forced_run:
            yield from super()._get_runnable_objects(raw_logs=logs, *args, **kwargs)
            return

        raw_logs_chunks = make_chunks(
            iterable=logs,
            size=settings.RDM_COLLECT_CHUNK_SIZE,
        )

        for chunk_index, raw_logs_chunk in enumerate(raw_logs_chunks, start=1):
            raw_logs = list(raw_logs_chunk)
            for runnable_class in self._prepare_runnable_classes():
                runnable = runnable_class(
                    raw_logs=raw_logs,
                    chunk_index=chunk_index,
                    *args,
                    **kwargs,
                )

                if isinstance(runnable, tuple):
                    yield from runnable
                else:
                    yield runnable
