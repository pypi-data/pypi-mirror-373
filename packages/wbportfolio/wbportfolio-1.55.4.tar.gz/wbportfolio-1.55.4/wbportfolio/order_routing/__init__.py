from django.db.models import TextChoices

class ExecutionStatus(TextChoices):
    PENDING = "PENDING", "Pending"
    IN_DRAFT = "IN_DRAFT", "In Draft"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
    REJECTED = "REJECTED", "Rejected"
    FAILED = "FAILED", "Failed"
    UNKNOWN = "UNKNOWN", "Unknown"

class RoutingException(Exception):
    def __init__(self, errors):
        # messages: a list of strings
        super().__init__()  # You can pass a summary to the base Exception
        self.errors = errors

    def __str__(self):
        return str(self.errors)
