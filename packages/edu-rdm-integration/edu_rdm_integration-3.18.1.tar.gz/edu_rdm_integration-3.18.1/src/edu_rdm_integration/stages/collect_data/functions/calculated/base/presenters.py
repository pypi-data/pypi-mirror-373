from abc import (
    ABCMeta,
)

from edu_function_tools.presenters import (
    EduResultPresenter,
)


class BaseCollectingCalculatedExportedDataResultPresenter(EduResultPresenter, metaclass=ABCMeta):
    """Презентер результата работы функций сбора расчетных данных для интеграции с "Региональная витрина данных"."""
