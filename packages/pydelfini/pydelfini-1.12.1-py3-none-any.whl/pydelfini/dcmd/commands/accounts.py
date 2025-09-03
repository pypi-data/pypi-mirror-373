from pydelfini.delfini_core import Paginator
from pydelfini.delfini_core.api.account import account_create_account
from pydelfini.delfini_core.api.account import account_delete_account
from pydelfini.delfini_core.api.account import account_list_accounts
from pydelfini.delfini_core.api.account import account_update_account_pages
from pydelfini.delfini_core.api.items import collections_items_list_items
from pydelfini.delfini_core.models import AccountCreateAccountBody
from pydelfini.delfini_core.models import AccountCreateAccountBodyMetadata
from pydelfini.delfini_core.models import CollectionsItemsListItemsResponse200
from pydelfini.delfini_core.models import ItemType
from pydelfini.delfini_core.models import UpdateAccountPages

from .base_commands import BaseCommands


class AccountsCommands(BaseCommands):
    """Operations on accounts"""

    @BaseCommands._with_arg("name")
    @BaseCommands._with_arg("--description", default="")
    def new(self) -> None:
        """Create a new account."""
        rv = account_create_account.sync(
            body=AccountCreateAccountBody(
                name=self.args.name,
                metadata=AccountCreateAccountBodyMetadata.from_dict(
                    {"x-description": self.args.description}
                ),
            ),
            client=self.core,
        )

        self._output(rv.to_dict())

    def list(self) -> None:
        """List all accounts."""
        rv = account_list_accounts.sync(client=self.core)

        self._output(rv.to_dict())

    @BaseCommands._with_arg("account_id")
    def delete(self) -> None:
        """Remove an account."""
        rv = account_delete_account.sync(
            account_id=self.args.account_id, client=self.core
        )
        assert rv

    @BaseCommands._with_arg("account_id")
    @BaseCommands._with_arg("collection_id")
    @BaseCommands._with_arg("--version-id", default="LIVE")
    def update_space(self) -> None:
        """Copy pages from the designated collection into the account space."""
        # first, we need a list of item IDs
        pager = Paginator[CollectionsItemsListItemsResponse200](
            collections_items_list_items, self.core
        )
        item_ids: list[str] = []
        for page in pager.paginate(
            collection_id=self.args.collection_id,
            version_id=self.args.version_id,
            type=[ItemType.FILE],
        ):
            item_ids.extend(i.id for i in page.items)

        account_update_account_pages.sync(
            account_id=self.args.account_id,
            body=UpdateAccountPages(
                collection_id=self.args.collection_id,
                version_id=self.args.version_id,
                item_ids=item_ids,
            ),
            client=self.core,
        )
