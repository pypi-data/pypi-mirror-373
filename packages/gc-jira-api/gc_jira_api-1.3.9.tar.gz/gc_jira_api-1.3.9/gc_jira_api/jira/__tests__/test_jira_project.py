import unittest
from unittest.mock import patch

from gc_jira_api.jira import JiraProject
from gc_jira_api.Requestor import RequestExecutor

JIRA_SERVER = "JIRA_SERVER_TEST"
JIRA_USERNAME = "JIRA_USERNAME_TEST"
JIRA_PASSWORD = "JIRA_PASSWORD_TEST"


class TestJiraProject(unittest.TestCase):
    @patch.object(RequestExecutor, "fetch_data")
    def test_get_all_projects(self, mock_fetch_data):
        mock_fetch_data.return_value = [
            {"name": "Project 1"},
            {"name": "zz(archived) Project 2"},
            {"name": "Active Project"},
        ]

        jira_project = JiraProject(JIRA_USERNAME, JIRA_PASSWORD, JIRA_SERVER)

        all_projects = jira_project.get_all_projects(filter_by_active=True)
        self.assertEqual(len(all_projects), 2)
        self.assertEqual(all_projects[0]["name"], "Project 1")
        self.assertEqual(all_projects[1]["name"], "Active Project")

        all_projects = jira_project.get_all_projects(filter_by_active=False)
        self.assertEqual(len(all_projects), 3)

    @patch.object(RequestExecutor, "fetch_data")
    def test_get_project_info(self, mock_fetch_data):
        mock_fetch_data.side_effect = [
            {"name": "Project Info"},  # First call return
            {"role1": "role_url1", "role2": "role_url2"},  # Second call return
            {"members": ["User1", "User2"]},  # Third call return
            {"members": ["User3", "User4"]},  # Fourth call return
        ]

        jira_project = JiraProject(JIRA_USERNAME, JIRA_PASSWORD, JIRA_SERVER)

        project_info = jira_project.get_project_info("PROJECT_KEY")
        self.assertIn("info", project_info)
        self.assertIn("roles", project_info)
        self.assertEqual(project_info["info"]["name"], "Project Info")
        self.assertEqual(len(project_info["roles"]), 2)

    @patch.object(RequestExecutor, "fetch_data")
    def test_get_project_info_by_name(self, mock_fetch_data):
        mock_fetch_data.side_effect = [
            [
                {"key": "PROJECT_KEY", "name": "Project Name"}
            ],  # First call return
            {"role1": "role_url1", "role2": "role_url2"},  # Second call return
            {"members": ["User1", "User2"]},  # Third call return
            {"members": ["User3", "User4"]},  # Fourth call return
        ]

        jira_project = JiraProject(JIRA_USERNAME, JIRA_PASSWORD, JIRA_SERVER)

        project_info = jira_project.get_project_info_by_name("Project Name")
        self.assertIn("content", project_info)
        self.assertIn("roles", project_info["content"])
        self.assertEqual(len(project_info["content"]["roles"]), 2)

    @patch.object(RequestExecutor, "fetch_data")
    def test_get_project_members(self, mock_fetch_data):
        mock_fetch_data.side_effect = [
            {"role1": "role_url1", "role2": "role_url2"},  # First call return
            {"members": ["User1", "User2"]},  # Second call return
            {"members": ["User3", "User4"]},  # Third call return
        ]

        jira_project = JiraProject(JIRA_USERNAME, JIRA_PASSWORD, JIRA_SERVER)

        project_members = jira_project.get_project_members("PROJECT_KEY")
        self.assertEqual(len(project_members), 2)
        self.assertEqual(project_members[0]["members"], ["User1", "User2"])
        self.assertEqual(project_members[1]["members"], ["User3", "User4"])

    @patch.object(RequestExecutor, "fetch_data")
    def test_get_project_data(self, mock_fetch_data):
        mock_fetch_data.return_value = {
            "key": "PROJECT_KEY",
            "name": "Project Name",
        }

        jira_project = JiraProject(JIRA_USERNAME, JIRA_PASSWORD, JIRA_SERVER)

        project_data = jira_project.get_project_data("PROJECT_KEY")
        self.assertEqual(project_data["name"], "Project Name")

    @patch.object(RequestExecutor, "fetch_data")
    def test_get_groups_for_email(self, mock_fetch_data):
        mock_fetch_data.side_effect = [
            [{"accountId": "user123"}],  # First call return
            {"groups": ["group1", "group2"], "applicationRoles": ["role1"]},
        ]

        jira_project = JiraProject(JIRA_USERNAME, JIRA_PASSWORD, JIRA_SERVER)

        user_data = jira_project.get_groups_for_email("user@example.com")
        self.assertIn("groups", user_data)
        self.assertIn("applicationRoles", user_data)
        self.assertEqual(user_data["groups"], ["group1", "group2"])

    @patch.object(RequestExecutor, "fetch_data")
    def test_update_project(self, mock_fetch_data):
        mock_fetch_data.return_value = {
            "key": "PROJECT_KEY",
            "name": "Updated Project",
        }

        jira_project = JiraProject(JIRA_USERNAME, JIRA_PASSWORD, JIRA_SERVER)

        updated_project = jira_project.update_project(
            "PROJECT_KEY", {"name": "Updated Project"}
        )
        self.assertEqual(updated_project["name"], "Updated Project")

    @patch.object(RequestExecutor, "fetch_data")
    def test_get_all_permissions_schemes(self, mock_fetch_data):
        mock_fetch_data.return_value = [
            {"id": "1", "name": "Scheme1"},
            {"id": "2", "name": "Scheme2"},
        ]

        jira_project = JiraProject(JIRA_USERNAME, JIRA_PASSWORD, JIRA_SERVER)

        permissions_schemes = jira_project.get_all_permissions_schemes()
        self.assertEqual(len(permissions_schemes), 2)
        self.assertEqual(permissions_schemes[0]["name"], "Scheme1")

    @patch.object(RequestExecutor, "fetch_data")
    def test_get_user_info(self, mock_fetch_data):
        mock_fetch_data.return_value = [
            {"accountId": "user123", "displayName": "User One"}
        ]

        jira_project = JiraProject(JIRA_USERNAME, JIRA_PASSWORD, JIRA_SERVER)

        user_info = jira_project.get_user_info("User One")
        self.assertEqual(user_info[0]["displayName"], "User One")

    @patch.object(RequestExecutor, "fetch_data")
    def test_get_user_info_by_id(self, mock_fetch_data):
        mock_fetch_data.return_value = [
            {"accountId": "user123", "displayName": "User One"}
        ]

        jira_project = JiraProject(JIRA_USERNAME, JIRA_PASSWORD, JIRA_SERVER)

        user_info = jira_project.get_user_info_by_id("user123")
        self.assertEqual(user_info[0]["displayName"], "User One")

    @patch.object(RequestExecutor, "fetch_data")
    def test_create_project(self, mock_fetch_data):
        mock_fetch_data.return_value = {
            "key": "NEW_PROJECT",
            "name": "New Project",
        }

        jira_project = JiraProject(JIRA_USERNAME, JIRA_PASSWORD, JIRA_SERVER)

        created_project = jira_project.create_project({"name": "New Project"})
        self.assertEqual(created_project["name"], "New Project")

    @patch.object(RequestExecutor, "fetch_data")
    def test_get_all_project_categories(self, mock_fetch_data):
        mock_fetch_data.return_value = [
            {"id": "1", "name": "Category1"},
            {"id": "2", "name": "Category2"},
        ]

        jira_project = JiraProject(JIRA_USERNAME, JIRA_PASSWORD, JIRA_SERVER)

        categories = jira_project.get_all_project_categories()
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0]["name"], "Category1")

    @patch.object(RequestExecutor, "fetch_data")
    def test_get_all_project_roles(self, mock_fetch_data):
        mock_fetch_data.return_value = {
            "role1": "role_url1",
            "role2": "role_url2",
        }

        jira_project = JiraProject(JIRA_USERNAME, JIRA_PASSWORD, JIRA_SERVER)

        roles = jira_project.get_all_project_roles("PROJECT_CODE")
        self.assertEqual(len(roles), 2)
        self.assertIn("role1", roles)

    @patch.object(RequestExecutor, "fetch_data")
    def test_set_users_in_project(self, mock_fetch_data):
        mock_fetch_data.return_value = {
            "roleId": "123",
            "projectKey": "PROJECT_KEY",
        }

        jira_project = JiraProject(JIRA_USERNAME, JIRA_PASSWORD, JIRA_SERVER)

        response = jira_project.set_users_in_project(
            "PROJECT_KEY", "123", {"users": ["user1", "user2"]}
        )
        self.assertEqual(response["roleId"], "123")

    @patch.object(RequestExecutor, "fetch_data")
    def test_get_user_groups(self, mock_fetch_data):
        mock_fetch_data.return_value = [
            {"groupName": "Group1"},
            {"groupName": "Group2"},
        ]

        jira_project = JiraProject(JIRA_USERNAME, JIRA_PASSWORD, JIRA_SERVER)

        user_groups = jira_project.get_user_groups("user123")
        self.assertEqual(len(user_groups), 2)
        self.assertEqual(user_groups[0]["groupName"], "Group1")
