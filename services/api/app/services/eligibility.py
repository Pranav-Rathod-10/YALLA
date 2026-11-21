"""Who may request which trip. Shared by the request service and trip responses
(`can_request`) so clients can explain a disabled button instead of guessing."""

from app.core.config import get_settings
from app.core.errors import ForbiddenError
from app.models import Trip, User
from app.models.enums import Gender


class FemalesOnlyError(ForbiddenError):
    code, title = "females_only", "Females only trip"


def females_only_block(user: User, trip: Trip) -> FemalesOnlyError | None:
    """ADR 0007: only women may request or instant-join a Females only trip. Optionally
    require a verified gender (`YALLA_FEMALES_ONLY_REQUIRE_VERIFIED`)."""
    if not trip.females_only:
        return None
    if user.gender != Gender.female:
        return FemalesOnlyError("Only women can join this trip. Set your gender in your profile.")
    if get_settings().females_only_require_verified and not user.gender_verified:
        return FemalesOnlyError("Only verified women can join this trip.")
    return None


def can_request(user: User, trip: Trip) -> bool:
    return trip.host_id != user.id and females_only_block(user, trip) is None
