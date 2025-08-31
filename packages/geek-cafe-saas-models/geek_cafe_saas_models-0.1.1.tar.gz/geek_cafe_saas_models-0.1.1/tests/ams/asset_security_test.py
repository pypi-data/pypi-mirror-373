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
from geek_cafe_saas_models.asset.asset_security import AssetSecurity

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

def test_asset_security_assignment_and_query(db: DynamoDB):
    tenant_id = "T1"
    asset_owner = "U1"
    asset_assignee = "U2"

    # Create an asset
    asset1 = create_asset(db, "Test Laptop", tenant_id, asset_owner)
    asset2 = create_asset(db, "Test Laptop 1", tenant_id, asset_owner)

    # Assign user to asset1
    security = AssetSecurity()
    security.xref_pk = asset1.get_pk_id()    
    security.xref_type = asset1.model_name
    security.tenant_id = asset1.tenant_id
    security.user_id = asset_assignee
    security.owner_id = asset_owner
    security.access_levels = "read, write"
    response = db.save(table_name=TABLE_NAME, item=security)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    security = AssetSecurity()
    security.xref_pk = asset2.get_pk_id()    
    security.xref_type = asset2.model_name
    security.tenant_id = asset2.tenant_id
    security.user_id = asset_assignee
    security.owner_id = asset_owner
    security.access_levels = "write"


    response = db.save(table_name=TABLE_NAME, item=security)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    security = AssetSecurity()
    security.xref_pk = asset1.get_pk_id()    
    security.xref_type = asset1.model_name
    security.tenant_id = asset1.tenant_id
    security.owner_id = asset_owner
    security.user_id = "UX"
    security.access_levels = "read"
    
    response = db.save(table_name=TABLE_NAME, item=security)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


    security = AssetSecurity()
    security.xref_pk = "*"
    security.xref_type = asset1.model_name
    security.tenant_id = asset1.tenant_id
    security.owner_id = asset_owner
    security.user_id = "U-admin"
    security.access_levels = "*"
    
    response = db.save(table_name=TABLE_NAME, item=security)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    # Query all users assigned to this asset (by asset ID)
    query_by_asset = AssetSecurity()  
    query_by_asset.tenant_id = "T1"  
    query_by_asset.owner_id = asset_owner
    key = query_by_asset.get_key("gsi1")
    result = db.query(table_name=TABLE_NAME, key=key)
    assert len(result["Items"]) == 4
    
 

    # Query all assets assigned to this user (by user ID)
    query_model = AssetSecurity()  
    query_model.tenant_id = "T1"
    query_model.user_id = asset_assignee    
    key = query_model.get_key("gsi2")
    result_model = db.query(table_name=TABLE_NAME, key=key)

    assert len(result_model["Items"]) == 2


    query_model = AssetSecurity()  
    query_model.tenant_id = "T1"
    query_model.user_id =  "U-admin"    
    key = query_model.get_key("gsi2")
    result_model = db.query(table_name=TABLE_NAME, key=key)

    assert len(result_model["Items"]) == 1
   
