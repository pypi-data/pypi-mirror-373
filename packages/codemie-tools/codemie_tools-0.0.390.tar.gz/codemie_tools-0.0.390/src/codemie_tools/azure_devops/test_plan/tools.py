import json
import os
from typing import Type, Optional

from azure.devops.connection import Connection
from azure.devops.v7_0.test_plan.models import (
    TestPlanCreateParams,
    TestSuiteCreateParams,
    SuiteTestCaseCreateUpdateParameters
)
from azure.devops.v7_0.test_plan.test_plan_client import TestPlanClient
from msrest.authentication import BasicAuthentication
from pydantic import BaseModel, Field

from codemie_tools.azure_devops.test_plan.tools_vars import (
    CREATE_TEST_PLAN_TOOL,
    DELETE_TEST_PLAN_TOOL,
    GET_TEST_PLAN_TOOL,
    CREATE_TEST_SUITE_TOOL,
    DELETE_TEST_SUITE_TOOL,
    GET_TEST_SUITE_TOOL,
    ADD_TEST_CASE_TOOL,
    GET_TEST_CASE_TOOL,
    GET_TEST_CASES_TOOL
)
from codemie_tools.base.codemie_tool import CodeMieTool, logger

PROJECT_NAME_IS_REQUIRED = "Project name or ID is required but not provided"

ID_OR_PROJECT_NAME = "Project ID or project name"

# Ensure Azure DevOps cache directory is set
if not os.environ.get('AZURE_DEVOPS_CACHE_DIR', None):
    os.environ['AZURE_DEVOPS_CACHE_DIR'] = ""

CLIENT_IS_NOT_INITIALIZED = """Azure DevOps client initialisation failed: 
Please check your Azure DevOps credentials are provided in 'Integrations'"""


class CreateTestPlanInput(BaseModel):
    test_plan_create_params: str = Field(description="JSON of the test plan create parameters")
    project: Optional[str] = Field(description=ID_OR_PROJECT_NAME, default=None)


class DeleteTestPlanInput(BaseModel):
    plan_id: int = Field(description="ID of the test plan to be deleted")
    project: Optional[str] = Field(description=ID_OR_PROJECT_NAME, default=None)


class GetTestPlanInput(BaseModel):
    plan_id: Optional[int] = Field(description="ID of the test plan to get", default=None)
    project: Optional[str] = Field(description=ID_OR_PROJECT_NAME, default=None)


class CreateTestSuiteInput(BaseModel):
    test_suite_create_params: str = Field(description="JSON of the test suite create parameters")
    plan_id: int = Field(description="ID of the test plan that contains the suites")
    project: Optional[str] = Field(description=ID_OR_PROJECT_NAME, default=None)


class DeleteTestSuiteInput(BaseModel):
    plan_id: int = Field(description="ID of the test plan that contains the suite")
    suite_id: int = Field(description="ID of the test suite to delete")
    project: Optional[str] = Field(description=ID_OR_PROJECT_NAME, default=None)


class GetTestSuiteInput(BaseModel):
    plan_id: int = Field(description="ID of the test plan that contains the suites")
    suite_id: Optional[int] = Field(description="ID of the suite to get", default=None)
    project: Optional[str] = Field(description=ID_OR_PROJECT_NAME, default=None)


class AddTestCaseInput(BaseModel):
    suite_test_case_create_update_parameters: str = Field(
        description='JSON array of the suite test case create update parameters. Example: "[{"work_item":{"id":"23"}}]"'
    )
    plan_id: int = Field(description="ID of the test plan to which test cases are to be added")
    suite_id: int = Field(description="ID of the test suite to which test cases are to be added")
    project: Optional[str] = Field(description=ID_OR_PROJECT_NAME, default=None)


class GetTestCaseInput(BaseModel):
    plan_id: int = Field(description="ID of the test plan for which test cases are requested")
    suite_id: int = Field(description="ID of the test suite for which test cases are requested")
    test_case_id: str = Field(description="Test Case Id to be fetched")
    project: Optional[str] = Field(description=ID_OR_PROJECT_NAME, default=None)


class GetTestCasesInput(BaseModel):
    plan_id: int = Field(description="ID of the test plan for which test cases are requested")
    suite_id: int = Field(description="ID of the test suite for which test cases are requested")
    project: Optional[str] = Field(description=ID_OR_PROJECT_NAME, default=None)


class BaseAzureDevOpsTestPlanTool(CodeMieTool):
    """Base class for Azure DevOps Test Plan tools."""
    organization_url: Optional[str] = None
    token: Optional[str] = None
    project: Optional[str] = None  # Default project for all tools
    limit: Optional[int] = 5
    _client: Optional[TestPlanClient] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_client()

    def _setup_client(self):
        """Set up Azure DevOps client."""
        if not self.organization_url or not self.token:
            logger.error("Missing required configuration for Azure DevOps: organization_url or token")
            return
        
        try:
            # Set up connection to Azure DevOps using Personal Access Token (PAT)
            credentials = BasicAuthentication('', self.token)
            connection = Connection(base_url=self.organization_url, creds=credentials)
            # Retrieve the test plan client
            self._client = connection.clients.get_test_plan_client()
        except Exception as e:
            logger.error(f"Failed to connect to Azure DevOps: {e}")
            return


class CreateTestPlanTool(BaseAzureDevOpsTestPlanTool):
    """Tool to create a test plan in Azure DevOps."""
    name: str = CREATE_TEST_PLAN_TOOL.name
    description: str = CREATE_TEST_PLAN_TOOL.description
    args_schema: Type[BaseModel] = CreateTestPlanInput

    def execute(self, test_plan_create_params: str, project: Optional[str] = None):
        """Create a test plan in Azure DevOps."""
        if not self._client:
            return CLIENT_IS_NOT_INITIALIZED
        
        # Use provided project or default from class if not provided
        project_to_use = project or self.project
        if not project_to_use:
            return PROJECT_NAME_IS_REQUIRED
            
        try:
            params = json.loads(test_plan_create_params)
            test_plan_create_params_obj = TestPlanCreateParams(**params)
            test_plan = self._client.create_test_plan(test_plan_create_params_obj, project_to_use)
            return f"Test plan {test_plan.id} created successfully."
        except Exception as e:
            logger.error(f"Error creating test plan: {e}")
            return f"Error creating test plan: {e}"


class DeleteTestPlanTool(BaseAzureDevOpsTestPlanTool):
    """Tool to delete a test plan in Azure DevOps."""
    name: str = DELETE_TEST_PLAN_TOOL.name
    description: str = DELETE_TEST_PLAN_TOOL.description
    args_schema: Type[BaseModel] = DeleteTestPlanInput

    def execute(self, plan_id: int, project: Optional[str] = None):
        """Delete a test plan in Azure DevOps."""
        if not self._client:
            return CLIENT_IS_NOT_INITIALIZED
        
        # Use provided project or default from class if not provided
        project_to_use = project or self.project
        if not project_to_use:
            return PROJECT_NAME_IS_REQUIRED
            
        try:
            self._client.delete_test_plan(project_to_use, plan_id)
            return f"Test plan {plan_id} deleted successfully."
        except Exception as e:
            logger.error(f"Error deleting test plan: {e}")
            return f"Error deleting test plan: {e}"


class GetTestPlanTool(BaseAzureDevOpsTestPlanTool):
    """Tool to get a test plan or list test plans in Azure DevOps."""
    name: str = GET_TEST_PLAN_TOOL.name
    description: str = GET_TEST_PLAN_TOOL.description
    args_schema: Type[BaseModel] = GetTestPlanInput

    def execute(self, plan_id: Optional[int] = None, project: Optional[str] = None):
        """Get a test plan or list of test plans in Azure DevOps."""
        if not self._client:
            return CLIENT_IS_NOT_INITIALIZED
        
        # Use provided project or default from class if not provided
        project_to_use = project or self.project
        if not project_to_use:
            return PROJECT_NAME_IS_REQUIRED
            
        try:
            if plan_id:
                test_plan = self._client.get_test_plan_by_id(project_to_use, plan_id)
                return test_plan.as_dict()
            else:
                test_plans = self._client.get_test_plans(project_to_use)
                return [plan.as_dict() for plan in test_plans[:self.limit]]
        except Exception as e:
            logger.error(f"Error getting test plan(s): {e}")
            return f"Error getting test plan(s): {e}"


class CreateTestSuiteTool(BaseAzureDevOpsTestPlanTool):
    """Tool to create a test suite in Azure DevOps."""
    name: str = CREATE_TEST_SUITE_TOOL.name
    description: str = CREATE_TEST_SUITE_TOOL.description
    args_schema: Type[BaseModel] = CreateTestSuiteInput

    def execute(self, test_suite_create_params: str, plan_id: int, project: Optional[str] = None):
        """Create a test suite in Azure DevOps."""
        if not self._client:
            return CLIENT_IS_NOT_INITIALIZED
        
        # Use provided project or default from class if not provided
        project_to_use = project or self.project
        if not project_to_use:
            return PROJECT_NAME_IS_REQUIRED
            
        try:
            params = json.loads(test_suite_create_params)
            test_suite_create_params_obj = TestSuiteCreateParams(**params)
            test_suite = self._client.create_test_suite(test_suite_create_params_obj, project_to_use, plan_id)
            return f"Test suite {test_suite.id} created successfully."
        except Exception as e:
            logger.error(f"Error creating test suite: {e}")
            return f"Error creating test suite: {e}"


class DeleteTestSuiteTool(BaseAzureDevOpsTestPlanTool):
    """Tool to delete a test suite in Azure DevOps."""
    name: str = DELETE_TEST_SUITE_TOOL.name
    description: str = DELETE_TEST_SUITE_TOOL.description
    args_schema: Type[BaseModel] = DeleteTestSuiteInput

    def execute(self, plan_id: int, suite_id: int, project: Optional[str] = None):
        """Delete a test suite in Azure DevOps."""
        if not self._client:
            return CLIENT_IS_NOT_INITIALIZED
        
        # Use provided project or default from class if not provided
        project_to_use = project or self.project
        if not project_to_use:
            return PROJECT_NAME_IS_REQUIRED
            
        try:
            self._client.delete_test_suite(project_to_use, plan_id, suite_id)
            return f"Test suite {suite_id} deleted successfully."
        except Exception as e:
            logger.error(f"Error deleting test suite: {e}")
            return f"Error deleting test suite: {e}"


class GetTestSuiteTool(BaseAzureDevOpsTestPlanTool):
    """Tool to get a test suite or list test suites in Azure DevOps."""
    name: str = GET_TEST_SUITE_TOOL.name
    description: str = GET_TEST_SUITE_TOOL.description
    args_schema: Type[BaseModel] = GetTestSuiteInput

    def execute(self, plan_id: int, suite_id: Optional[int] = None, project: Optional[str] = None):
        """Get a test suite or list of test suites in Azure DevOps."""
        if not self._client:
            return CLIENT_IS_NOT_INITIALIZED
        
        # Use provided project or default from class if not provided
        project_to_use = project or self.project
        if not project_to_use:
            return PROJECT_NAME_IS_REQUIRED
            
        try:
            if suite_id:
                test_suite = self._client.get_test_suite_by_id(project_to_use, plan_id, suite_id)
                return test_suite.as_dict()
            else:
                test_suites = self._client.get_test_suites_for_plan(project_to_use, plan_id)
                return [suite.as_dict() for suite in test_suites[:self.limit]]
        except Exception as e:
            logger.error(f"Error getting test suite(s): {e}")
            return f"Error getting test suite(s): {e}"


class AddTestCaseTool(BaseAzureDevOpsTestPlanTool):
    """Tool to add a test case to a suite in Azure DevOps."""
    name: str = ADD_TEST_CASE_TOOL.name
    description: str = ADD_TEST_CASE_TOOL.description
    args_schema: Type[BaseModel] = AddTestCaseInput

    def execute(self, suite_test_case_create_update_parameters: str, plan_id: int, suite_id: int, project: Optional[str] = None):
        """Add a test case to a suite in Azure DevOps."""
        if not self._client:
            return CLIENT_IS_NOT_INITIALIZED
        
        # Use provided project or default from class if not provided
        project_to_use = project or self.project
        if not project_to_use:
            return PROJECT_NAME_IS_REQUIRED
            
        try:
            params = json.loads(suite_test_case_create_update_parameters)
            suite_test_case_params_list = []
            
            # Handle both array and single object scenarios
            if isinstance(params, list):
                for param in params:
                    suite_test_case_params_list.append(SuiteTestCaseCreateUpdateParameters(**param))
            else:
                suite_test_case_params_list.append(SuiteTestCaseCreateUpdateParameters(**params))
            
            test_cases = self._client.add_test_cases_to_suite(suite_test_case_params_list, project_to_use, plan_id, suite_id)
            return [test_case.as_dict() for test_case in test_cases]
        except Exception as e:
            logger.error(f"Error adding test case: {e}")
            return f"Error adding test case: {e}"


class GetTestCaseTool(BaseAzureDevOpsTestPlanTool):
    """Tool to get a test case from a suite in Azure DevOps."""
    name: str = GET_TEST_CASE_TOOL.name
    description: str = GET_TEST_CASE_TOOL.description
    args_schema: Type[BaseModel] = GetTestCaseInput

    def execute(self, plan_id: int, suite_id: int, test_case_id: str, project: Optional[str] = None):
        """Get a test case from a suite in Azure DevOps."""
        if not self._client:
            return CLIENT_IS_NOT_INITIALIZED
        
        # Use provided project or default from class if not provided
        project_to_use = project or self.project
        if not project_to_use:
            return PROJECT_NAME_IS_REQUIRED
            
        try:
            test_cases = self._client.get_test_case(project_to_use, plan_id, suite_id, test_case_id)
            if test_cases:  # Check if the list is not empty
                test_case = test_cases[0]
                return test_case.as_dict()
            else:
                return f"No test cases found with criteria: project {project_to_use}, plan {plan_id}, suite {suite_id}, test case id {test_case_id}"
        except Exception as e:
            logger.error(f"Error getting test case: {e}")
            return f"Error getting test case: {e}"


class GetTestCasesTool(BaseAzureDevOpsTestPlanTool):
    """Tool to get test cases from a suite in Azure DevOps."""
    name: str = GET_TEST_CASES_TOOL.name
    description: str = GET_TEST_CASES_TOOL.description
    args_schema: Type[BaseModel] = GetTestCasesInput

    def execute(self, plan_id: int, suite_id: int, project: Optional[str] = None):
        """Get test cases from a suite in Azure DevOps."""
        if not self._client:
            return CLIENT_IS_NOT_INITIALIZED
        
        # Use provided project or default from class if not provided
        project_to_use = project or self.project
        if not project_to_use:
            return PROJECT_NAME_IS_REQUIRED
            
        try:
            test_cases = self._client.get_test_case_list(project_to_use, plan_id, suite_id)
            return [test_case.as_dict() for test_case in test_cases[:self.limit]]
        except Exception as e:
            logger.error(f"Error getting test cases: {e}")
            return f"Error getting test cases: {e}"
