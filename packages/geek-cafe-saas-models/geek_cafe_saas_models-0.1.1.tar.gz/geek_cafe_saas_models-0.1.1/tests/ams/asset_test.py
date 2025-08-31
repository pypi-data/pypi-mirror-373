"""
Geek Cafe, LLC
MIT License. See Project Root for the license information.
"""

import pytest
from datetime import datetime, UTC
from dateutil.relativedelta import relativedelta
from typing import List, Generator

import moto
from mypy_boto3_dynamodb import DynamoDBClient

from boto3_assist.dynamodb.dynamodb import DynamoDB
from boto3_assist.environment_services.environment_loader import EnvironmentLoader
from boto3_assist.utilities.datetime_utility import DatetimeUtility
from tests.common.db_test_helpers import DbTestHelper

from geek_cafe_saas_models.asset import Asset
from geek_cafe_saas_models.asset.asset_activity import AssetActivity
from geek_cafe_saas_models.asset.asset_tag import AssetTag
from geek_cafe_saas_models.asset.asset_tree_node import AssetTreeNode
from geek_cafe_saas_models.core.tree.node import NodeKind

TABLE_NAME = "mock_test_table"


@pytest.fixture(scope="module")
def env_setup():
    EnvironmentLoader().load_environment_file(file_name=".env.mock", raise_error_if_not_found=True)


@pytest.fixture
def db(env_setup) ->  Generator[DynamoDB, None, None]:
    with moto.mock_aws():
        db = DynamoDB()
        DbTestHelper().helper_create_mock_table(TABLE_NAME, db.client)
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


def test_asset_model_save_and_load(db: DynamoDB):
    asset = create_asset(db, "Mac Book Pro", "T1", "U1")

    response = db.get(table_name=TABLE_NAME, model=asset)
    stored_asset = Asset().map(response["Item"])

    assert stored_asset.name == asset.name
    assert stored_asset.id == asset.id
    assert stored_asset.tenant_id == asset.tenant_id
    assert stored_asset.user_id == asset.user_id
    assert float(stored_asset.metadata["purchase_price"]) == 5000
    assert stored_asset.metadata["purchase_price_unit"] == "usd"





def test_asset_activity_query(db: DynamoDB):
    asset1 = create_asset(db, "Mac Book Pro", "T3", "U3")
    for i in range(5):
        entry = AssetActivity()
        entry.tenant_id = asset1.tenant_id
        entry.xref_pk = asset1.get_pk_id()
        entry.name = "some service"
        entry.category = "service"
        entry.description = "took it in for another service"
        entry.cost = 100
                
        entry.date_utc = DatetimeUtility.add_days(datetime.now(UTC), -i)
        db.save(table_name=TABLE_NAME, item=entry)

    asset2 = create_asset(db, "Mac Book Pro", "T4", "U4")
    for i in range(15):
        entry = AssetActivity()
        entry.tenant_id = asset2.tenant_id #t4
        entry.xref_pk = asset2.get_pk_id()
        entry.name = "some service"
        entry.category = "service"
        entry.description = "took it in for another service"
        entry.cost = 100
        entry.date_utc = DatetimeUtility.add_days(datetime.now(UTC), -i)
        db.save(table_name=TABLE_NAME, item=entry)

    model = AssetActivity()
    
    model.xref_pk = asset1.get_pk_id()
    key = model.get_key("gsi1")
    response = db.query(table_name=TABLE_NAME, key=key)

    assert len(response["Items"]) == 5


    model = AssetActivity()
    model.tenant_id = asset2.tenant_id
    model.xref_pk = asset2.get_pk_id()
    key = model.get_key("gsi1")
    response = db.query(table_name=TABLE_NAME, key=key)

    assert len(response["Items"]) == 15


def test_asset_keywords_and_gsi(db: DynamoDB):
    asset = create_asset(db, "Mac Book Pro", "T4", "U4")
    keywords = ["mac", "laptop", "apple", "macbook", "pro"]
    for word in keywords:
        keyword_model = AssetTag()
        keyword_model.asset_id = asset.id
        keyword_model.name = word
        keyword_model.tenant_id = asset.tenant_id
        keyword_model.user_id = asset.user_id
        db.save(table_name=TABLE_NAME, item=keyword_model)

    model = AssetTag()
    model.asset_id = asset.id
    model.tenant_id = asset.tenant_id
    key = model.get_key("gsi1")
    response = db.query(table_name=TABLE_NAME, key=key)

    db_keywords = sorted(item["name"] for item in response["Items"])
    assert db_keywords == sorted(keywords)

    model.user_id = "INVALID"
    key = model.get_key("gsi2")
    response = db.query(table_name=TABLE_NAME, key=key)
    assert len(response["Items"]) == 0
