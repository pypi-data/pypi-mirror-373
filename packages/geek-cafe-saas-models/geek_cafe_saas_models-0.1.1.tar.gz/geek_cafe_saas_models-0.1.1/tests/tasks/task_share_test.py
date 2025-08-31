import pytest
from boto3_assist.dynamodb.dynamodb import DynamoDB
from geek_cafe_saas_models.task import Task
from geek_cafe_saas_models.task.task_share import TaskShare
from tests.common.db_test_helpers import DbTestHelper
from boto3_assist.environment_services.environment_loader import EnvironmentLoader
import moto

TABLE_NAME = "mock_test_table"


class TaskShareTestHelper:
    def __init__(self, db: DynamoDB):
        self.db = db
        self.tasks: dict[str, Task] = {}
        

    def create_task(self, name: str, tenant_id: str, owner_id: str) -> Task:
        t = Task()
        t.subject = name
        t.tenant_id = tenant_id
        t.user_id = owner_id
        t.metadata = {}
        resp = self.db.save(table_name=TABLE_NAME, item=t)
        assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200
        self.tasks[name] = t
        return t

    def share(self, task: Task, shared_with: str, access_levels: list[str]):
        s = TaskShare()
        s.xref_pk = task.get_pk_id()
        s.xref_type = task.model_name
        s.tenant_id = task.tenant_id
        s.owner_id = task.owner_id
        s.user_id = shared_with
        s.access_levels = access_levels
        resp = self.db.save(table_name=TABLE_NAME, item=s)
        assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200
        
        return s


@pytest.fixture(scope="module")
def env_setup():
    EnvironmentLoader().load_environment_file(file_name=".env.mock", raise_error_if_not_found=True)


@pytest.fixture
def db(env_setup):
    with moto.mock_aws():
        db = DynamoDB()
        DbTestHelper().helper_create_mock_table(table_name=TABLE_NAME, client=db.client)
        yield db


@pytest.fixture
def ts_helper(db) -> TaskShareTestHelper:
    helper = TaskShareTestHelper(db)
    # --- create 3 tasks:
    t1 = helper.create_task("Task 1", tenant_id="T1", owner_id="U1")
    t2 = helper.create_task("Task 2", tenant_id="T1", owner_id="U1")
    # task 3 won't be shared with anyone else
    t3 = helper.create_task("Task 3", tenant_id="T1", owner_id="U2")

    # --- share t1 with three users
    helper.share(t1, "U2", ["read", "write"])
    helper.share(t1, "U3", ["read"])
    helper.share(t1, "U4", ["*"])
    # --- share t2 with one user
    helper.share(t2, "U2", ["write"])

    return helper


class TestTaskShareQueries:
    def test_query_all_shares_for_task1(self, ts_helper: TaskShareTestHelper):
        """
        Test a query for all users for task1
        """
        db = ts_helper.db
        task1 = ts_helper.tasks["Task 1"]
        # build the GSI1 key for task1
        q = TaskShare()
        q.xref_pk = task1.get_pk_id()
        q.owner_id = task1.owner_id
        key = q.get_key("gsi1")

        result = db.query(table_name=TABLE_NAME, key=key)
        # we shared with U2, U3 and U4
        assert len(result["Items"]) == 3

        # sanity-check the partition/sort values
        assert key.partition_key.value == "owner#U1"
        assert key.sort_key.value == f"xref#{task1.get_pk_id()}"

    def test_query_all_tasks_for_U2(self, ts_helper: TaskShareTestHelper):
        """
        Get all tasks for a specific user
        """
        db = ts_helper.db
        # GSI2 query: all tasks shared to U2
        q = TaskShare()
        q.tenant_id = "T1"
        q.user_id = "U2"
        key = q.get_key("gsi2")

        result = db.query(table_name=TABLE_NAME, key=key)
        # U2 has shares for Task1 and Task2
        assert len(result["Items"]) == 2
        assert key.partition_key.value == "user#U2"
        # since sort_key is prefixed with xref#task#, we check it contains our prefix
        assert key.sort_key.value.startswith("xref#task#")

    def test_query_all_tasks_for_user_U4(self, ts_helper: TaskShareTestHelper):
        """
        Get all tasks for a specific user
        """
        db = ts_helper.db
        q = TaskShare()
        q.tenant_id = "T1"
        q.user_id = "U4"
        key = q.get_key("gsi2")

        result = db.query(table_name=TABLE_NAME, key=key)
        # U4 only got Task1
        assert len(result["Items"]) == 1

    def test_query_find_all_tasks_shared_to_others(self, ts_helper: TaskShareTestHelper):
        """
        Use Case: I want to see all the shares that i have created for all of my tasks.
        This gives me a wide visibility (see all shares) All Tasks -> All Shares
        This does mean that you will see duplicate tasks.
        """
        
        model: TaskShare = TaskShare()
        model.owner_id = "U1"

        result = ts_helper.db.query(table_name=TABLE_NAME, key=model.get_key("gsi1"))
        # 4 tasks have been 
        assert len(result["Items"]) == 4

    def test_query_find_task_shared_to_others(self, ts_helper: TaskShareTestHelper):
        """
        Use Case: I want to see all the shares that i have created for a specific task.
        This gives narrow visibility 1 Task -> Everyone I've shared it with.
        """
        
        model: TaskShare = TaskShare()
        model.owner_id = "U1"
        model.xref_pk = ts_helper.tasks["Task 1"].get_pk_id()

        result = ts_helper.db.query(table_name=TABLE_NAME, key=model.get_key("gsi1"))
        # 3 tasks have been shared
        assert len(result["Items"]) == 3


    def test_custom_rule_only_writers(self, ts_helper: TaskShareTestHelper):
        """
        Example of “testing criteria/rules”:
        let's say we want only those TaskShare items
        where access_levels includes 'write' — how would you test that?
        """
        
        model: TaskShare = TaskShare()
        model.owner_id = "U1"
        # get all of my shared items
        result = ts_helper.db.query(table_name=TABLE_NAME, key=model.get_key("gsi1"))
        
        writers = [s for s in result["Items"] if "write" in s["access_levels"] or "*" in s["access_levels"]] 
        assert len(writers) == 3  # Task1→U2, Task2→U2, Task2→U4 (this assumes you want * to be included)
