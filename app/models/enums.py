from enum import Enum


class UserRole(str, Enum):
    CLIENT = "client"
    FREELANCER = "freelancer"


class ProjectStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BidStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ContractStatus(str, Enum):
    ACTIVE = "active"
    FINISHED = "finished"
    CANCELLED = "cancelled"
