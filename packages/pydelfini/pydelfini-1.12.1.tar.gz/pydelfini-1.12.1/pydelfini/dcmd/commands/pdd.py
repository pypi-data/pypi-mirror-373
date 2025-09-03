import os.path

from pydelfini import item_io
from pydelfini.delfini_core.api.data_dictionaries import (
    collections_dictionaries_get_ordered_dictionary,
)
from pydelfini.delfini_core.api.data_dictionaries import (
    collections_dictionaries_new_bundle,
)
from pydelfini.delfini_core.api.data_dictionaries import (
    collections_dictionaries_set_order,
)
from pydelfini.delfini_core.models import BundleDefinition
from pydelfini.delfini_core.models import DataElementBundle
from pydelfini.delfini_core.models import OrderedDictionary
from pydelfini.delfini_core.models import PreferredOrder
from pydelfini.delfini_core.paginator import Paginator

from .base_commands import BaseCommands


class PddCommands(BaseCommands):
    """Operations on PDDs (data dictionaries)"""

    @BaseCommands._with_arg("collection_id")
    @BaseCommands._with_arg("filename")
    @BaseCommands._with_arg("--item-name")
    @BaseCommands._with_arg("--folder-id", default="ROOT")
    def upload(self) -> None:
        """Upload a PDD from a local file."""

        item_name = self.args.item_name or os.path.basename(self.args.filename)
        writer = item_io.DelfiniItemCreatorText(
            self.args.collection_id,
            "LIVE",
            item_name,
            self.core,
            folder_id=self.args.folder_id,
            type="dictionary",
        )
        with writer as ofp:
            with open(self.args.filename) as ifp:
                ofp.write(ifp.read())
        print("id:", writer.item_id)

    @BaseCommands._with_arg("collection_name")
    @BaseCommands._with_arg("item_name")
    @BaseCommands._with_arg("--version-id", default="LIVE")
    def list(self) -> None:
        """List ordered elements in a PDD."""

        collection = self.client.get_collection_by_name(self.args.collection_name)
        item = collection[self.args.item_name]

        pager = Paginator[OrderedDictionary](
            collections_dictionaries_get_ordered_dictionary, self.core
        )

        for page in pager.paginate(collection.id, collection.version_id, item.id):
            for entry in page.entries:
                if isinstance(entry, DataElementBundle):
                    print(entry.name)
                    for element in entry.elements:
                        print(f"   [{element.id}] {element.name}")
                else:
                    print(f"[{entry.id}] {entry.name}")

    @BaseCommands._with_arg("collection_name")
    @BaseCommands._with_arg("item_name")
    @BaseCommands._with_arg("bundle_name")
    @BaseCommands._with_arg("element_id", nargs="+")
    def bundle(self) -> None:
        """Create a new element bundle."""

        collection = self.client.get_collection_by_name(self.args.collection_name)
        item = collection[self.args.item_name]

        print("New bundle name:", self.args.bundle_name)
        print("Element IDs:", self.args.element_id)

        new_bundle = BundleDefinition(
            name=self.args.bundle_name,
            elements=self.args.element_id,
        )
        bundle = collections_dictionaries_new_bundle.sync(
            collection.id,
            collection.version_id,
            item.id,
            body=new_bundle,
            client=self.core,
        )
        print()
        print("New bundle ID:", bundle.id)

    @BaseCommands._with_arg("collection_name")
    @BaseCommands._with_arg("item_name")
    @BaseCommands._with_arg("ids", nargs="+")
    def set_order(self) -> None:
        """Set the preferred order of the PDD."""

        collection = self.client.get_collection_by_name(self.args.collection_name)
        item = collection[self.args.item_name]

        collections_dictionaries_set_order.sync(
            collection.id,
            collection.version_id,
            item.id,
            body=PreferredOrder(order=self.args.ids),
            client=self.core,
        )
