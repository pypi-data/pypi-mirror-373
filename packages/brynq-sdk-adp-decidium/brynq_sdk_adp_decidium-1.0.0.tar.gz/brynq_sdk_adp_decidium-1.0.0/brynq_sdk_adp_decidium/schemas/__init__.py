"""Schema definitions for ADP package"""


# Import schemas
from .workers import (
    WorkerGet,
    WorkerHireRequest,
    WorkerRehireRequest,
    WorkerTerminateEventData,
    WorkerUpdateRequest,
)
from .work_assignment import (
    WorkerWorkAssignmentModifyRequest,
    WorkAssignmentTerminateRequest,
)
from .payroll import (
    PayDataInputAddRequest,
    PayDataInputReplaceRequest,
)
from .pay_distributions import PayDistributionChangeRequest
from .dependents import DependentGet, DependentAddRequest, DependentChangeRequest, DependentRemoveRequest
from .document import (
    IdentityDocumentAddRequest,
    ImmigrationDocumentAddRequest,
    DOCUMENT_TYPES,
)

__all__ = [
    'WorkerGet',
    'WorkerHireRequest',
    'WorkerRehireRequest',
    'WorkerTerminateEventData',
    'WorkerUpdateRequest',
    'WorkerWorkAssignmentModifyRequest',
    'WorkAssignmentTerminateRequest',
    'PayDataInputAddRequest',
    'PayDataInputReplaceRequest',
    'PayDistributionChangeRequest',
    'DependentGet',
    'DependentAddRequest',
    'DependentChangeRequest',
    'DependentRemoveRequest',
    'IdentityDocumentAddRequest',
    'ImmigrationDocumentAddRequest',
    'DOCUMENT_TYPES',
]
