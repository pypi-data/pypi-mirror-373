import enum

class TableConfigEnum(str, enum.Enum):
    COMPANY = "genesis-companies"
    INSTALLMENTS = "exodo-installments"
    CUSTOMER = "genesis-customers"
    RENEGOTIATION_CAMPAIGNS = "exodo-renegotiation-campaigns"
    ROLES = "genesis-user-roles"
    USERS = "genesis-users"
    RENEGOTIATION_BLOCKED_CUSTOMERS = "exodo-renegotiation-blocked-customers"
    AUDIT = "genesis-audit-log"
    TAG_ASSOCIATIONS = "genesis-tag-associations"
    AGREEMENT =  "exodo-agreements"
    BILLING = "exodo-billings"


class AuthErrorCodeEnum(str, enum.Enum):
    USER_NOT_AUTHENTICATED = "USER_NOT_AUTHENTICATED"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    ROLE_NOT_FOUND = "ROLE_NOT_FOUND"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    INVALID_PERMISSION_FORMAT = "INVALID_PERMISSION_FORMAT"
    DATABASE_ERROR = "DATABASE_ERROR"


class PaymentMethodEnum(str, enum.Enum):
    boleto = 'BOLETO'
    pix = 'PIX'
    bolepix = 'BOLEPIX'
    credit_card = 'CREDIT_CARD'

    @classmethod
    def is_valid(self, value: str) -> bool:
        return value in [p.value for p in PaymentMethodEnum]

class StatusEnum(str, enum.Enum):
    processing = 'processing'
    ready_for_approval = 'ready_for_approval'
    in_creation = 'in_creation'
    active = 'active'
    cancelled = 'cancelled'
    paused = 'paused'
    finished = 'finished'

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in [s.value for s in StatusEnum]


    def status_level(self) -> int:
        status_levels = {
            StatusEnum.processing: 1,
            StatusEnum.ready_for_approval: 2,
            StatusEnum.in_creation: 3,
            StatusEnum.paused: 4,
            StatusEnum.active: 5,
            StatusEnum.cancelled: 6,
            StatusEnum.finished: 7
        }
        return status_levels.get(self, 0)


class PaymentStatusEnum(str, enum.Enum):
    pending = 'pending'
    overdue = 'overdue'
    protest = 'protest'
    derogatory = 'derogatory'

    @classmethod
    def is_valid(self, value: str) -> bool:
        return value in [p.value for p in PaymentStatusEnum]


class TemplateEmailEnum(str, enum.Enum):
    READY_TO_APPROVAL = "ready_to_approval_template.html"


class DerogatoryStatusEnum(str, enum.Enum):
    DEROGATORY_REQUESTED = "pending_derogatory"
    DEROGATORY_IN_PROGRESS = "processing_derogatory"
    DEROGATED = "derogatory"
    DEROGATORY_CANCELLED = "derogatory_cancelled"
    DEROGATORY_RECEIVED = "paid_after_derogatory"
    DEROGATORY_DISAPPROVED = ""

class ProtestStatusEnum(str, enum.Enum):
    PROTEST_REQUESTED = "pending_protest"
    PROTEST_ONGOING = "processing_protest"
    PROTEST_IRREGULAR = "protest_irregular"
    PROTEST_IRREGULAR_RECEIVED = "protest_irregular_received"
    PROTEST_CANCELLED = "protest_cancelled"
    WAITING_CANCELLATION = "waiting_cancellation"
    PROTEST_WAITING_CANCELLATION_CANCELLED = "protest_waiting_cancellation_cancelled"
    PROTEST_WAITING_CANCELLATION_PAID = "protest_waiting_cancellation_paid"
    PROTEST_RECEIVED = "paid_after_protested"
    PROTESTED = "protested"
    PROTEST_SUSPENDED = "protest_suspended"


class RenegotiationTypeEnum(str, enum.Enum):
    RENEGOTIATION = 'RENEGOTIATION'
    AGREEMENT = 'AGREEMENT'