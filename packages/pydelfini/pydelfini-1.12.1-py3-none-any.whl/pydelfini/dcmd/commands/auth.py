from pydelfini.delfini_core.api.auth import auth_get_session
from pydelfini.delfini_core.api.user import user_update_user
from pydelfini.delfini_core.models import AuthGetSessionResponse200
from pydelfini.delfini_core.models import UpdateUser
from pydelfini.delfini_core.models import UpdateUserMetadata

from .base_commands import BaseCommands


class AuthCommands(BaseCommands):
    """Authentication and authorization operations"""

    def whoami(self) -> None:
        """Information about your current session"""
        session = auth_get_session.sync(client=self.core)
        if not isinstance(session, AuthGetSessionResponse200):
            raise Exception("could not read session")

        self._output(session.to_dict())

    @BaseCommands._with_arg("key")
    @BaseCommands._with_arg("value")
    def set_metadata(self) -> None:
        session = auth_get_session.sync(client=self.core)
        if not isinstance(session, AuthGetSessionResponse200):
            raise Exception("could not read session")

        user_name = session.user.identity.user_name
        metadata: dict[str, str] = {}

        # TODO: fetch existing metadata so that this is not destructive
        # response = user_get_user.sync(user_name)
        # ...
        metadata[self.args.key] = self.args.value

        user_update_user.sync(
            user_name,
            body=UpdateUser(metadata=UpdateUserMetadata.from_dict(metadata)),
            client=self.core,
        )
