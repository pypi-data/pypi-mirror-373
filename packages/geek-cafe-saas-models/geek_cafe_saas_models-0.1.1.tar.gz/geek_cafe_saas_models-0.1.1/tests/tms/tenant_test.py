"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

import unittest
import moto


from boto3_assist.dynamodb.dynamodb import DynamoDB
from boto3_assist.environment_services.environment_loader import EnvironmentLoader
from tests.common.db_test_helpers import DbTestHelper
from geek_cafe_saas_models.tenant import Tenant

@moto.mock_aws
class TenantTests(unittest.TestCase):
    "Tenant Tests"

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)

        ev: EnvironmentLoader = EnvironmentLoader()
        # NOTE: you need to make sure the the env file below exists or you will get an error
        ev.load_environment_file(file_name=".env.mock", raise_error_if_not_found=True)
        self.__table_name = "mock_test_table"

        self.db: DynamoDB = DynamoDB()

    def setUp(self):
        # load our test environment file to make sure we override any default AWS Environment Vars setup
        # we don't want to accidentally connect to live environments
        # https://docs.getmoto.org/en/latest/docs/getting_started.html

        self.db: DynamoDB = self.db or DynamoDB()
        DbTestHelper().helper_create_mock_table(self.__table_name, self.db.client)
        print("Setup Complete")

    def test_tenant_model(self):
        """
        Test Tenant Model and Saving
        """
        # add some values an any order we want
        tenant:Tenant = Tenant()

        tenant.name = "geekcafe.com"
        tenant.contact_first_name = "Eric"
        tenant.contact_last_name = "Wilson"
        tenant.contact_email = "XXXXXXXXXXXXXXXXX"
        tenant.contact_phone = "XXXXXXXXXXXXXXXXX"
        
        response = self.db.save(table_name=self.__table_name, item=tenant)

        status_code = response["ResponseMetadata"]["HTTPStatusCode"]

        self.assertEqual(status_code, 200)
        
    def test_multiple_tenants(self):
        """
        Test Tenant Model and Saving
        """
        # add some values an any order we want
        tenant1:Tenant = Tenant()

        tenant1.name = "geekcafe.com"
        tenant1.contact_first_name = "Eric"
        tenant1.contact_last_name = "Wilson"
        tenant1.contact_email = "XXXXXXXXXXXXXXXXX"
        tenant1.contact_phone = "XXXXXXXXXXXXXXXXX"

        tenant2:Tenant = Tenant()

        tenant2.name = "geekcafe.com"
        tenant2.contact_first_name = "Eric"
        tenant2.contact_last_name = "Wilson"
        tenant2.contact_email = "XXXXXXXXXXXXXXXXX"
        tenant2.contact_phone = "XXXXXXXXXXXXXXXXX"

        response1 = self.db.save(table_name=self.__table_name, item=tenant1)
        response2 = self.db.save(table_name=self.__table_name, item=tenant2)

        status_code1 = response1["ResponseMetadata"]["HTTPStatusCode"]
        status_code2 = response2["ResponseMetadata"]["HTTPStatusCode"]

        self.assertEqual(status_code1, 200)
        self.assertEqual(status_code2, 200)

        tenantSearch:Tenant = Tenant()

        # this model allows tenants with the same name, which will create two separate tenants
        tenantSearch.name = "geekcafe.com"

        # key = tenantSearch.get_key("gsi1")
        key = tenantSearch.get_key("gsi1")
        
        response = self.db.query(table_name=self.__table_name, key=key)

        items =response["Items"]
        self.assertEqual(len(items), 2)

    