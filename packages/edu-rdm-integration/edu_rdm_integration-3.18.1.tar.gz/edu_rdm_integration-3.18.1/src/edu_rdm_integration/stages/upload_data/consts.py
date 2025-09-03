from edu_rdm_integration.stages.upload_data.models import (
    RDMRequestStatus,
)


FAILED_STATUSES = {
    RDMRequestStatus.FAILED_PROCESSING,
    RDMRequestStatus.REQUEST_ID_NOT_FOUND,
    RDMRequestStatus.FLC_ERROR,
}
