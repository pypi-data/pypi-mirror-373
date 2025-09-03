from enum import Enum


class CollectionsItemsCompleteMultipartUploadBodyAction(str, Enum):
    CANCEL = "cancel"
    COMPLETE = "complete"

    def __str__(self) -> str:
        return str(self.value)
