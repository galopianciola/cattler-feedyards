from rest_framework import status
from rest_framework.exceptions import ValidationError


class ConflictValidationError(ValidationError):
    status_code = status.HTTP_409_CONFLICT
