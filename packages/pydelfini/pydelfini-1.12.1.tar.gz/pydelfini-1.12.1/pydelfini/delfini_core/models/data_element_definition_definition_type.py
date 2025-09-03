from enum import Enum


class DataElementDefinitionDefinitionType(str, Enum):
    ALSOKNOWNAS = "alsoKnownAs"
    ALTERNATEQUESTIONTEXT = "alternateQuestionText"
    ASSOCIATEDWITH = "associatedWith"
    COLUMNNAME = "columnName"
    LONGDESCRIPTION = "longDescription"
    OTHER = "other"
    PREFERREDQUESTIONTEXT = "preferredQuestionText"
    SHORTDESCRIPTION = "shortDescription"
    SOURCE = "source"

    def __str__(self) -> str:
        return str(self.value)
