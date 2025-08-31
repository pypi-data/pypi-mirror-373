"""
Geek Cafe, LLC
MIT License. See Project Root for the license information.
"""

import pytest
from datetime import datetime
import moto

from boto3_assist.dynamodb.dynamodb import DynamoDB
from boto3_assist.environment_services.environment_loader import EnvironmentLoader
from tests.common.db_test_helpers import DbTestHelper

from geek_cafe_saas_models.asset import Asset
from geek_cafe_saas_models.asset.asset_assignment import AssetAssignment

TABLE_NAME = "mock_test_table"

@pytest.fixture(scope="module")
def env_setup():
    EnvironmentLoader().load_environment_file(file_name=".env.mock", raise_error_if_not_found=True)

@pytest.fixture
def db(env_setup):
    with moto.mock_aws():
        db = DynamoDB()
        DbTestHelper().helper_create_mock_table(table_name=TABLE_NAME, client=db.client)
        yield db

def create_asset(db: DynamoDB, name: str, tenant_id: str, user_id: str) -> Asset:
    asset = Asset()
    asset.name = name
    asset.tenant_id = tenant_id
    asset.user_id = user_id
    asset.metadata = {
        "purchase_price": 5000,
        "purchase_price_unit": "usd",
        "purchase_date_utc": datetime(2022, 1, 1, 12, 0, 0).isoformat(),
    }
    response = db.save(table_name=TABLE_NAME, item=asset)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    return asset

def test_asset_rights_assignment_and_query(db: DynamoDB):
    tenant_id = "T1"
    asset_owner = "U1"
    user_two = "U2"
    user_three = "U3"
    # Create an asset
    asset1 = create_asset(db, "Test Laptop", tenant_id, asset_owner)
    asset2 = create_asset(db, "Test Laptop", tenant_id, asset_owner)

    # Assign user2 to asset1
    relation = AssetAssignment()
    relation.xref_pk = asset1.get_pk_id()    
    relation.user_id = user_two
    relation.type = "assigned_to"
    relation.tenant_id = asset1.tenant_id
    relation.start_utc = datetime.now()

    response = db.save(table_name=TABLE_NAME, item=relation)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    # Assign user2 to asset2
    relation = AssetAssignment()
    relation.xref_pk = asset2.get_pk_id()    
    relation.user_id = user_two
    relation.type = "assigned_to"
    relation.tenant_id = asset2.tenant_id
    relation.start_utc = datetime.now()

    response = db.save(table_name=TABLE_NAME, item=relation)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    
    # Assign user3 to asset 1
    relation = AssetAssignment()
    relation.xref_pk = asset1.get_pk_id()
    relation.tenant_id = "T1"
    relation.user_id = user_three
    relation.type = "assigned_to"
    relation.tenant_id = asset1.tenant_id
    relation.start_utc = datetime.now()
    key = relation.get_key("gsi1")
    response = db.save(table_name=TABLE_NAME, item=relation)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    # Query all assets assigned to user2 (by user ID)
    query_model = AssetAssignment()  
    query_model.tenant_id = "T1"
    query_model.user_id = user_two
    query_model.type = "assigned_to"
    key = query_model.get_key("gsi1")
    result_model = db.query(table_name=TABLE_NAME, key=key)

    assert len(result_model["Items"]) == 2
    

    # Query all users (within a given tenant) assigned to this asset (by asset ID)
    query_by_asset = AssetAssignment()  
    query_by_asset.tenant_id = "T1"
    query_by_asset.xref_pk = asset1.get_pk_id()
    query_by_asset.type = "assigned_to"
    key = query_by_asset.get_key("gsi2")
    result = db.query(table_name=TABLE_NAME, key=key)
    assert len(result["Items"]) == 2
    
 

    

