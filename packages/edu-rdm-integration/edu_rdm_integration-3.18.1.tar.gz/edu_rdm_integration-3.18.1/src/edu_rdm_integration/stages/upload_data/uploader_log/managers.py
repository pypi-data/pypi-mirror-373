from django.db.models import (
    Case,
    CharField,
    F,
    Manager,
    PositiveSmallIntegerField,
    Q,
    Value,
    When,
)
from django.db.models.functions import (
    Cast,
)

from edu_rdm_integration.stages.upload_data.uploader_log.enums import (
    RequestResultStatus,
)


class UploaderClientLogManager(Manager):
    """Менеджер модели журнала Загрузчика данных в витрину."""

    def get_queryset(self):
        """Возвращает кварисет."""
        query = super().get_queryset()

        result_status = Case(
            When(
                Q(Q(error__isnull=True) | Q(error__exact='')) & Q(Q(response__isnull=False) & ~Q(response__exact='')),
                then=Value(RequestResultStatus.SUCCESS),
            ),
            default=Value(RequestResultStatus.ERROR),
            output_field=PositiveSmallIntegerField(),
        )

        query = query.annotate(
            request_datetime=F('date_time'),
            attachment_file=Case(
                When(request__icontains='POST', then=F('uploader_client_log__attachment__attachment')),
                When(
                    request__icontains='GET',
                    then=F('upload_status_request_log__upload__attachment__attachment'),
                ),
                default=Value(''),
                output_field=CharField(),
            ),
            status_code=Case(
                When(request__icontains='POST', then=Value('', output_field=CharField())),
                When(
                    request__icontains='GET',
                    then=Cast('upload_status_request_log__request_status__value', output_field=CharField()),
                ),
                default=Value(''),
            ),
            status_description=Case(
                When(
                    request__icontains='POST',
                    then=Value('', output_field=CharField()),
                ),
                When(
                    request__icontains='GET',
                    then=F('upload_status_request_log__request_status__title'),
                ),
                default=Value(''),
                output_field=CharField(),
            ),
            is_emulation=Case(
                When(
                    request__icontains='POST',
                    then=F('uploader_client_log__is_emulation'),
                ),
                When(
                    request__icontains='GET',
                    then=F('upload_status_request_log__upload__is_emulation'),
                ),
                default=Value(False),
            ),
            request_id=Case(
                When(request__icontains='POST', then=F('uploader_client_log__request_id')),
                When(request__icontains='GET', then=F('upload_status_request_log__upload__request_id')),
                default=Value(''),
            ),
            result_status=result_status,
        )

        return query
