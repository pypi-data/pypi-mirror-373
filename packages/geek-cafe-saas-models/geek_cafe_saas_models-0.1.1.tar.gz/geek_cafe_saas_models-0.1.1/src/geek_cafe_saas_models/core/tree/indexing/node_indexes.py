"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from typing import TYPE_CHECKING

from boto3_assist.dynamodb.dynamodb_index import DynamoDBIndex, DynamoDBKey

if TYPE_CHECKING:
    from ..node import Node


class Indexes:
    pass

    def __init__(self, model: "Node"):
        from ..node import Node

        self.model: Node = model
        self._setup_indexes()

    def _setup_indexes(self):
        for setup in (self._setup_pk, self._setup_gsi1):
            setup()

    def _setup_pk(self):
        primary: DynamoDBIndex = DynamoDBIndex()
        primary.name = "primary"
        primary.partition_key.attribute_name = "pk"
        primary.partition_key.value = lambda: DynamoDBKey.build_key(
            (self.model.model_name, self.model.id)
        )

        primary.sort_key.attribute_name = "sk"
        primary.sort_key.value = lambda: DynamoDBKey.build_key(
            (self.model.model_name, self.model.id)
        )
        self.model.indexes.add_primary(primary)

    def _setup_gsi1(self):

        # GSI: returns a tree of nodes, in order by depth and name
        gsi: DynamoDBIndex = DynamoDBIndex()

        gsi.name = "gsi1"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(
            ("tenant", self.model.tenant_id),
            (self.model.model_name, self.model.root_pk),
        )
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        # sort order
        gsi.sort_key.value = lambda: self.__build_key()

        self.model.indexes.add_secondary(gsi)

    def __build_key(self):
        key = {}
        if self.model._name:
            # using the path seems to be the best way to get a a tree 
            # however leafs may not appear below the container.  the UI will
            # need to render if correctly.
            key = DynamoDBKey.build_key(
                ("path", self.safe_path(self.model.path)),
            )
        else:
            # this is for cases when we build the key with the model.
            # we may not include a name (but the name is required).
            # this will query everything and sort by the path
            key = DynamoDBKey.build_key(("path", None))

        return key

    def safe_path(self, path: list[str]) -> str:
        full_path = "/".join(path).lower()
        
        if len(full_path) > 1024:
            raise ValueError("Path is too long")
        return full_path
