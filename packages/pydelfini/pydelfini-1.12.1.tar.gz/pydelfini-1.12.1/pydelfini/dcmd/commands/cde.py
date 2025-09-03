from pydelfini.delfini_core.api.cde import cdes_delete_cdeset
from pydelfini.delfini_core.api.cde import cdes_list_cdesets
from pydelfini.delfini_core.api.cde import cdes_new_cdeset
from pydelfini.delfini_core.api.data_dictionaries import (
    collections_dictionaries_copy_to_cdeset,
)
from pydelfini.delfini_core.models import CdesNewCdesetBody
from pydelfini.delfini_core.models import CollectionsDictionariesCopyToCdesetBody

from .base_commands import BaseCommands


class CdeCommands(BaseCommands):
    """Manipulating CDE sets"""

    @BaseCommands._with_arg("cdeset_name", help="name of new CDE set")
    @BaseCommands._with_arg("description", help="short description for the new CDE set")
    def new(self) -> None:
        """Create a new CDE set.

        Admin access is required.

        """
        cdes_new_cdeset.sync(
            body=CdesNewCdesetBody(
                name=self.args.cdeset_name, description=self.args.description
            ),
            client=self.core,
        )

    def list(self) -> None:
        """List available CDE sets."""
        cdeset_list = cdes_list_cdesets.sync(client=self.core)

        self._output(cdeset_list.to_dict())

    @BaseCommands._with_arg("cdeset_name", help="name of CDE set to delete")
    def delete(self) -> None:
        """Delete a CDE set.

        Admin access is required.

        """
        cdes_delete_cdeset.sync(cdeset_name=self.args.cdeset_name, client=self.core)

    @BaseCommands._with_arg("cdeset_name", help="name of CDE set to update")
    @BaseCommands._with_arg("collection_id", help="collection UUID")
    @BaseCommands._with_arg("version_id", help="collection version, typically 'LIVE'")
    @BaseCommands._with_arg("item_id", help="item UUID")
    @BaseCommands._with_arg(
        "--description", help="optional update to CDE set description"
    )
    def copy_from_pdd(self) -> None:
        """Copy data elements into a CDE set from a PDD.

        Admin access is required, as well as access to the specified PDD.

        """
        if self.args.description:
            description = self.args.description
        else:
            description = ""
            for cdeset in cdes_list_cdesets.sync(client=self.core).cdesets:
                if cdeset.name == self.args.cdeset_name:
                    description = cdeset.description

            if not description:
                raise ValueError(
                    f"did not find existing CDE set: {self.args.cdeset_name}"
                )

        collections_dictionaries_copy_to_cdeset.sync(
            collection_id=self.args.collection_id,
            version_id=self.args.version_id,
            item_id=self.args.item_id,
            body=CollectionsDictionariesCopyToCdesetBody(
                name=self.args.cdeset_name,
                description=description,
            ),
            client=self.core,
        )
