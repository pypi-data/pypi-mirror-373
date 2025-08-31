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
from geek_cafe_saas_models.asset.asset_file import AssetFile

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

def create_file(db: DynamoDB, tenant_id: str, user_id: str, asset_id: str, file_name: str) -> AssetFile:
    file = AssetFile()
    file.tenant_id = tenant_id
    file.user_id = user_id
    file.xref_pk = asset_id
    file.file_name = file_name
    file.size_bytes = 1000
    file.content_type = "plain/text"
    file.storage_type = "cloud"
    file.metadata = {
        "provider": "AWS",
        "type": "S3",
        "bucket": "bucket-abc",
        "object-key": f"/dir/path/{file_name}"
    }
    response = db.save(table_name=TABLE_NAME, item=file)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    return file

def test_asset_file_attachment(db: DynamoDB):
    
    # Create an asset
    asset1 = create_asset(db, "Test Laptop", "T1", "U1")
    
    max_range = 100
    for i in range(0, max_range):
        # same tenant but multiple different users upload files
        create_file(db, asset1.tenant_id, f"user{i}", asset1.get_pk_id(), f"test_file{i}.txt")
    
    
    # Query all users (within a given tenant) assigned to this asset (by asset ID)
    query = AssetFile()  
    query.tenant_id = "T1"
    query.xref_pk = asset1.get_pk_id()
    
    key = query.get_key("gsi2")
    result = db.query(table_name=TABLE_NAME, key=key)
    assert len(result["Items"]) == max_range
    
 


    

