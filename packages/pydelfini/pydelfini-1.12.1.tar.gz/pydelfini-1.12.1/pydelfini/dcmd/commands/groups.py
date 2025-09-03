from pydelfini.delfini_core.api.group import group_create_group
from pydelfini.delfini_core.api.group import group_delete_group
from pydelfini.delfini_core.api.group import group_get_group_members
from pydelfini.delfini_core.api.group import group_get_groups
from pydelfini.delfini_core.api.group import group_set_group_member
from pydelfini.delfini_core.api.group import group_update_group
from pydelfini.delfini_core.models import GroupCreateGroupBody
from pydelfini.delfini_core.models import GroupMember
from pydelfini.delfini_core.models import GroupRole
from pydelfini.delfini_core.models import GroupUpdateGroupBody
from pydelfini.delfini_core.models import VisibilityLevel

from .base_commands import BaseCommands


class GroupsCommands(BaseCommands):
    """Operations on groups"""

    @BaseCommands._with_arg("name")
    @BaseCommands._with_arg("--public", action="store_true")
    def new(self) -> None:
        """Create a new group."""
        rv = group_create_group.sync(
            body=GroupCreateGroupBody(
                name=self.args.name,
                visibility_level=(
                    VisibilityLevel.PUBLIC
                    if self.args.public
                    else VisibilityLevel.UNLISTED
                ),
            ),
            client=self.core,
        )

        self._output(rv.to_dict())

    def list(self) -> None:
        """List all visible groups."""
        rv = group_get_groups.sync(client=self.core)

        self._output(rv.to_dict())

    @BaseCommands._with_arg("--name")
    @BaseCommands._with_arg("--make-public", action="store_true")
    @BaseCommands._with_arg("--make-unlisted", action="store_true")
    @BaseCommands._with_arg("group_id")
    def update(self) -> None:
        """Update a group."""
        update = GroupUpdateGroupBody()
        if self.args.name:
            update.name = self.args.name
        if self.args.make_public:
            update.visibility_level = VisibilityLevel.PUBLIC
        if self.args.make_unlisted:
            update.visibility_level = VisibilityLevel.UNLISTED
        group_update_group.sync(
            group_id=self.args.group_id, body=update, client=self.core
        )

    @BaseCommands._with_arg("group_id")
    def list_members(self) -> None:
        """List members of a group."""
        rv = group_get_group_members.sync(
            group_id=self.args.group_id, with_users=False, client=self.core
        )
        self._output(rv.to_dict())

    @BaseCommands._with_arg("group_id")
    @BaseCommands._with_arg("user_id")
    @BaseCommands._with_arg(
        "--role", choices=["ADMIN", "MEMBER", "VIEWER"], default="MEMBER"
    )
    def join(self) -> None:
        """Join a user to a group."""
        role = GroupRole(self.args.role)
        group_set_group_member.sync(
            group_id=self.args.group_id,
            body=GroupMember(role=role, user_id=self.args.user_id),
            client=self.core,
        )

    @BaseCommands._with_arg("group_id")
    def delete(self) -> None:
        """Remove a group."""
        rv = group_delete_group.sync(group_id=self.args.group_id, client=self.core)
        assert rv
