# mypy: disable-error-code="import-not-found, unused-ignore"
# %!pip install pydelfini
import pandas as pd
import pydelfini

client = pydelfini.login("delfini.local")


collection = client.get_collection_by_name("MHSVI")
# collection = pydelfini.explore()

dataframe = collection.get_table("my-folder/my-data")

folder_list = collection.folder("my-folder")
dataframe = folder_list.get_table("my-data")

for item in folder_list:
    # do something
    pass

for item in collection.walk():
    # recurse over all items in the collection
    pass

new_dataframe = pd.DataFrame({"A": [1, 2, 3]})
collection.write_table("output-data", new_dataframe, format="csv")


# more ideas
collection.new_folder("new")  # type: ignore

with collection.open("my-binary", "w") as fp:
    fp.write("a,b,c\n10,1,15\n20,2,25\n")

collection.set_parser(  # type: ignore
    "my-binary", name="csv", options={}, columns={"a": {"name": "a", "type": "Integer"}}
)
