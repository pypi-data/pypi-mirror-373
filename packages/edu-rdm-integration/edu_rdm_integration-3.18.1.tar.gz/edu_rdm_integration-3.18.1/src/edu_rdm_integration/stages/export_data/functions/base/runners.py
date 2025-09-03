from edu_function_tools.runners import (
    EduRunner,
)

from edu_rdm_integration.stages.export_data.functions.base.helpers import (
    BaseExportDataRunnerHelper,
)
from edu_rdm_integration.stages.export_data.functions.base.results import (
    BaseExportDataRunnerResult,
)
from edu_rdm_integration.stages.export_data.functions.base.validators import (
    BaseExportDataRunnerValidator,
)


class BaseExportDataRunner(EduRunner):
    """Базовый класс ранеров функций выгрузки данных для интеграции с "Региональная витрина данных"."""

    def _prepare_helper_class(self) -> type[BaseExportDataRunnerHelper]:
        """Возвращает класс помощника ранера функции."""
        return BaseExportDataRunnerHelper

    def _prepare_validator_class(self) -> type[BaseExportDataRunnerValidator]:
        """Возвращает класс валидатора ранера функции."""
        return BaseExportDataRunnerValidator

    def _prepare_result_class(self) -> type[BaseExportDataRunnerResult]:
        """Возвращает класс результата ранера функции."""
        return BaseExportDataRunnerResult

    def _prepare_model_ids_chunks(self, *args, model_ids_map=None, **kwargs):
        """Формирование чанков идентификаторов записей моделей для дальнейшей работы в рамках функций."""
        # model_ids_chunks = make_chunks(
        #     iterable=model_ids,
        #     size=settings.RDM_EXPORT_CHUNK_SIZE,
        # )

        return ()

    def _get_runnable_objects(self, *args, **kwargs):
        """Возвращает генератор запускаемых объектов."""
        model_ids_chunks = self._prepare_model_ids_chunks(*args, **kwargs)

        for chunk_index, model_ids_chunk in enumerate(model_ids_chunks, start=1):
            for runnable_class in self._prepare_runnable_classes():
                runnable = runnable_class(
                    model_ids=list(model_ids_chunk),
                    chunk_index=chunk_index,
                    *args,
                    **kwargs,
                )

                if isinstance(runnable, tuple):
                    yield from runnable
                else:
                    yield runnable
