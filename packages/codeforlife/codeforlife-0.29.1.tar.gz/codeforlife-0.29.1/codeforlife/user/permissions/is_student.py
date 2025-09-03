# pylint: disable=duplicate-code
"""
© Ocado Group
Created on 12/12/2023 at 13:55:40(+00:00).
"""

from ...permissions import IsAuthenticated
from ..models import StudentUser, User


class IsStudent(IsAuthenticated):
    """Request's user must be a student."""

    def has_permission(self, request, view):
        user = request.user
        return (
            super().has_permission(request, view)
            and isinstance(user, User)
            and StudentUser.objects.filter(id=user.id).exists()
        )
