"""
Geek Cafe, LLC
MIT License. See Project Root for license information.
"""

import pytest
from typing import List
from datetime import datetime, UTC

import moto

from boto3_assist.dynamodb.dynamodb import DynamoDB
from boto3_assist.environment_services.environment_loader import EnvironmentLoader
from tests.common.db_test_helpers import DbTestHelper

from geek_cafe_saas_models.asset import Asset
from geek_cafe_saas_models.asset.asset_tree_node import AssetTreeNode
from geek_cafe_saas_models.core.tree.node import NodeKind

TABLE_NAME = "mock_test_table"

@pytest.fixture(scope="module")
def env_setup():
    EnvironmentLoader().load_environment_file(file_name=".env.mock", raise_error_if_not_found=True)

@pytest.fixture
def db(env_setup):
    with moto.mock_aws():
        db = DynamoDB()
        DbTestHelper().helper_create_mock_table(table_name=TABLE_NAME,client= db.client)
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

def append_tree_node(
    db: DynamoDB,
    *,
    root_pk: str,
    node_name: str,
    node_type: NodeKind,
    tenant_id: str,
    user_id: str,
    parent_pk: str | None,
    path: list[str],
    asset: Asset | None = None,
) -> AssetTreeNode:
    node = AssetTreeNode()
    node.type = node_type
    node.name = node_name
    node.tenant_id = tenant_id
    node.user_id = user_id
    node.parent_pk = parent_pk
    node.root_pk = root_pk
    node.path = path
    if asset:
        node.leaf_item_pk = asset.get_pk_id()
    db.save(table_name=TABLE_NAME, item=node)
    return node

def create_container_node(
    db: DynamoDB,
    *,
    root_pk: str,
    parent_path: list[str],
    node_name: str,
    tenant_id: str,
    user_id: str
) -> AssetTreeNode:
    return append_tree_node(
        db=db,
        root_pk=root_pk,
        node_type=NodeKind.CONTAINER,
        node_name=node_name,
        tenant_id=tenant_id,
        user_id=user_id,
        parent_pk=root_pk,
        path=parent_path + [node_name],
    )

def test_asset_tree_structure(db: DynamoDB):
    tenant_id = "T1"
    user_id = "U1"
    root_pk = f"{tenant_id}-assets"

    # Root container
    root_node = append_tree_node(
        db=db,
        root_pk=root_pk,
        node_type=NodeKind.CONTAINER,
        node_name="assets",
        tenant_id=tenant_id,
        user_id=user_id,
        parent_pk=None,
        path=["assets"],
    )

    # Computer assets
    computer_assets = [
        create_asset(db, "Mac Book Pro", tenant_id, user_id),
        create_asset(db, "Mac Book Air", tenant_id, user_id),
        create_asset(db, "Mac Mini", tenant_id, user_id),
    ]

    # Computers container
    computers_node = create_container_node(
        db=db,
        root_pk=root_pk,
        parent_path=root_node.path,
        node_name="computers",
        tenant_id=tenant_id,
        user_id=user_id,
    )

    # Add computer assets to tree
    for asset in computer_assets:
        append_tree_node(
            db=db,
            root_pk=root_pk,
            node_type=NodeKind.LEAF,
            node_name=asset.name,
            tenant_id=tenant_id,
            user_id=user_id,
            parent_pk=computers_node.get_pk_id(),
            asset=asset,
            path=computers_node.path + [asset.name],
        )

    # Additional nodes
    pi_node = create_container_node(
        db=db,
        root_pk=root_pk,
        parent_path=computers_node.path,
        node_name="raspberry pi",
        tenant_id=tenant_id,
        user_id=user_id,
    )

    phone_node = create_container_node(
        db=db,
        root_pk=root_pk,
        parent_path=root_node.path,
        node_name="phones",
        tenant_id=tenant_id,
        user_id=user_id,
    )

    # Add phones + others
    iphone = create_asset(db, "iPhone 13", tenant_id, user_id)
    append_tree_node(
        db=db,
        root_pk=root_pk,
        node_type=NodeKind.LEAF,
        node_name=iphone.name,
        tenant_id=tenant_id,
        user_id=user_id,
        parent_pk=phone_node.get_pk_id(),
        asset=iphone,
        path=phone_node.path + [iphone.name],
    )

    pi = create_asset(db, "raspberry pi zero", tenant_id, user_id)
    append_tree_node(
        db=db,
        root_pk=root_pk,
        node_type=NodeKind.LEAF,
        node_name=pi.name,
        tenant_id=tenant_id,
        user_id=user_id,
        parent_pk=pi_node.get_pk_id(),
        asset=pi,
        path=pi_node.path + [pi.name],
    )

    bike = create_asset(db, "21 speed", tenant_id, user_id)
    append_tree_node(
        db=db,
        root_pk=root_pk,
        node_type=NodeKind.LEAF,
        node_name=bike.name,
        tenant_id=tenant_id,
        user_id=user_id,
        parent_pk=root_node.get_pk_id(),
        asset=bike,
        path=root_node.path + [bike.name],
    )

    # Secondary tenant root
    second_tenant = "T2"
    second_user = "U2"
    second_root_pk = f"{second_tenant}-assets"
    append_tree_node(
        db=db,
        root_pk=second_root_pk,
        node_type=NodeKind.CONTAINER,
        node_name="assets",
        tenant_id=second_tenant,
        user_id=second_user,
        parent_pk=None,
        path=["assets"],
    )

    # Query for first tenant's full tree
    query_model = AssetTreeNode()
    query_model.root_pk = root_pk
    query_model.tenant_id = tenant_id
    query_model.user_id = user_id
    key = query_model.get_key("gsi1")
    response = db.query(table_name=TABLE_NAME, key=key, ascending=True)

    items = response["Items"]
    assert len(items) == 10  # 1 root + 2 containers + 6 leaves + 1 pi + 1 bike
