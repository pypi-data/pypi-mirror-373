from abc import (
    ABCMeta,
)

from edu_function_tools.presenters import (
    EduResultPresenter,
)


class BaseCollectingExportedDataResultPresenter(EduResultPresenter, metaclass=ABCMeta):
    """Презентер результата работы функций сбора данных для интеграции с "Региональная витрина данных"."""
