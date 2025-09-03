from pydelfini.delfini_core.api.user import user_delete_user
from pydelfini.delfini_core.api.user import user_get_users
from pydelfini.delfini_core.api.user import user_update_user_admin
from pydelfini.delfini_core.models import UserAdminUpdate
from pydelfini.delfini_core.models import UserGetUsersResponse200
from pydelfini.delfini_core.paginator import Paginator

from .base_commands import BaseCommands


class UsersCommands(BaseCommands):
    """Operations on users"""

    def list(self) -> None:
        """List users."""
        pager = Paginator[UserGetUsersResponse200](user_get_users, self.core)

        data = []
        for page in pager.paginate():
            data.extend([u.to_dict() for u in page.users])

        self._output(data, preferred_type="table")

    @BaseCommands._with_arg("username")
    def delete(self) -> None:
        """Delete a user."""
        user_delete_user.sync(self.args.username, client=self.core)

    @BaseCommands._with_arg("username")
    def disable(self) -> None:
        """Disable a user."""
        resp = user_update_user_admin.sync(
            self.args.username,
            body=UserAdminUpdate(is_disabled=True),
            client=self.core,
        )
        self._output(resp.to_dict())

    @BaseCommands._with_arg("username")
    def enable(self) -> None:
        """Enable a user."""
        resp = user_update_user_admin.sync(
            self.args.username,
            body=UserAdminUpdate(is_disabled=False),
            client=self.core,
        )
        self._output(resp.to_dict())
