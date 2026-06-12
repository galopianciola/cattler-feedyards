from api.exceptions import ConflictValidationError


class ConflictOnValidationErrorMixin:
    def is_valid(self, *, raise_exception=False):
        valid = super().is_valid(raise_exception=False)
        if (
            not valid and raise_exception
        ):  # CreateAPIView llama a is_valid con raise_exception=True
            raise ConflictValidationError(detail=self.errors)
        return valid
