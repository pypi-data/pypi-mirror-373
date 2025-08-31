from typing import TYPE_CHECKING
from boto3_assist.dynamodb.dynamodb_index import DynamoDBIndex, DynamoDBKey

if TYPE_CHECKING:
    from ..file import File


class Indexes:
    pass

    def __init__(self, model: "File"):
        from ..file import File

        self.model: File = model
        self._setup_indexes()

    def _setup_indexes(self):
        for setup in (self._setup_pk, self._setup_gsi1, self._setup_gsi2):
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

        # GSI: get all tenant files, optionally lock down to a user and a file name
        gsi: DynamoDBIndex = DynamoDBIndex()

        gsi.name = "gsi1"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(
            ("tenant", self.model.tenant_id)
        )
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(
            ("user", self.model.user_id),
            ("archived", self.model.is_archived),
            (self.model.model_name, self.model.file_name),
            ("ts", self.model.updated_utc_ts()),
            
        )
        self.model.indexes.add_secondary(gsi)

    def _setup_gsi2(self):

        # GSI: get all tenant files, optionally lock down to a user and a file name
        gsi: DynamoDBIndex = DynamoDBIndex()

        gsi.name = "gsi2"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(
            ("tenant", self.model.tenant_id)
        )
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(
            ("user", self.model.user_id),
            ("category", self.model.category or "NA"),
            (self.model.model_name, self.model.file_name),
            ("ts", self.model.updated_utc_ts()),
            
        )
        self.model.indexes.add_secondary(gsi)
