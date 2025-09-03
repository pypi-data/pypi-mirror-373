from abc import (
    ABCMeta,
)

from edu_function_tools.presenters import (
    EduResultPresenter,
)


class BaseExportDataResultPresenter(EduResultPresenter, metaclass=ABCMeta):
    """Презентер результата работы функций выгрузки данных для интеграции с "Региональная витрина данных"."""
