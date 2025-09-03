from gc_jira_api.Requestor import RequestExecutor

POSSIBLE_DISABLE_WORDS = [
    "zz(archived)",
    "zz(archivado)",
    "zz/archivado)",
]


class JiraProject:
    def __init__(self, jira_username, jira_password, jira_server) -> None:
        self.requestor = RequestExecutor(
            jira_username,
            jira_password,
            jira_server,
        )

    def get_all_projects(self, filter_by_active=True):
        def _is_project_active(project):
            project_name_lowercase = project["name"].lower().replace(" ", "")
            for disabled_word in POSSIBLE_DISABLE_WORDS:
                if disabled_word in project_name_lowercase:
                    return False
            return True

        all_projects = self.requestor.fetch_data("project/")
        if filter_by_active:
            all_projects = list(filter(_is_project_active, all_projects))

        return all_projects

    def get_project_info(self, project_key: str):
        project_info = self.requestor.fetch_data(f"project/{project_key}/")

        project_roles = self.requestor.fetch_data(
            f"project/{project_key}/role"
        )

        project_role_members = []
        if project_roles:
            for _, role_url in project_roles.items():
                role_members = self.requestor.fetch_data(
                    role_url,
                    is_absolute_url=True,
                )
                project_role_members.append(role_members)

        return {
            "roles": project_role_members,
            "info": project_info if project_info != [] else None,
        }

    def get_project_info_by_name(self, project_name: str):
        def _get_project_data(project_info):
            project_key = project_info.get("key", None)

            project_roles = self.requestor.fetch_data(
                f"project/{project_key}/role"
            )

            project_role_members = []
            if project_roles:
                for role_name, role_url in project_roles.items():
                    if role_name == "atlassian-addons-project-access":
                        continue
                    role_members = self.requestor.fetch_data(
                        role_url,
                        is_absolute_url=True,
                    )
                    project_role_members.append(role_members)

            return {
                "content": {
                    "roles": project_role_members,
                    "info": project_info if project_info != [] else None,
                },
                "error": None,
            }

        project_info = self.requestor.fetch_data(
            f"project/search?query={project_name}&expand=lead"
        )

        if project_info and len(project_info) == 1:
            project_info = project_info[0]

            return _get_project_data(project_info=project_info)
        elif project_info and len(project_info) > 1:
            selected_project = None
            for project in project_info:
                if project["name"] == project_name:
                    selected_project = project
                    break

            if selected_project:
                return _get_project_data(project_info=selected_project)

            return {"error": "Many projects found."}

    def get_project_members(self, project_key: str):
        project_roles = self.requestor.fetch_data(
            f"project/{project_key}/role"
        )

        project_role_members = []
        if project_roles:
            for _, role_url in project_roles.items():
                role_members = self.requestor.fetch_data(
                    role_url,
                    is_absolute_url=True,
                )
                project_role_members.append(role_members)

        return project_role_members

    def get_project_data(self, project_key: str):
        return self.requestor.fetch_data(f"project/{project_key}")

    def get_groups_for_email(self, email: str):
        user = self.requestor.fetch_data(
            "user/search",
            url_params={"query": f"{email}"},
        )

        if user:
            user_data = self.requestor.fetch_data(
                "user",
                url_params={
                    "accountId": user[0]["accountId"],
                    "expand": "groups,applicationRoles",
                },
            )

            return user_data

    def update_project(self, project_key: str, body: dict):
        return self.requestor.fetch_data(
            url=f"project/{project_key}",
            method="PUT",
            url_params=body,
        )

    def get_all_permissions_schemes(self):
        return self.requestor.fetch_data("permissionscheme")

    def get_user_info(self, username: str):
        user_info = self.requestor.fetch_data(f"user/search?query={username}")

        return user_info

    def get_user_info_by_id(self, user_id: str):
        user_info = self.requestor.fetch_data(
            f"user/search?accountId={user_id}"
        )

        return user_info

    def create_project(self, data: dict):
        created_info = self.requestor.fetch_data(
            "project",
            method="POST",
            url_params=data,
        )

        return created_info

    def get_all_project_categories(self):
        return self.requestor.fetch_data("projectCategory")

    def get_all_project_roles(self, project_code: str):
        return self.requestor.fetch_data(f"project/{project_code}/role")

    def set_users_in_project(self, project_key, role_id, request_body):
        return self.requestor.fetch_data(
            f"project/{project_key}/role/{role_id}",
            method="PUT",
            url_params=request_body,
        )

    def get_user_groups(self, user_id: str):
        return self.requestor.fetch_data(f"user/groups?accountId={user_id}")

    def bulk_issue_create(self, issues):
        def _create_issue_batches():
            batch_size = 50
            batches = []
            if issues:
                for i in range(0, len(issues), batch_size):
                    batch = issues[i : i + batch_size]  # noqa: E203
                    batches.append(batch)
            return batches

        results = []
        for issue_batch in _create_issue_batches():
            result = self.requestor.fetch_data(
                "issue/bulk",
                method="POST",
                url_params={"issueUpdates": issue_batch},
            )

            results.append(result)

        return results

    def get_custom_field_contexts(self, custom_field: str):
        return self.requestor.fetch_data(f"field/{custom_field}/contexts")

    def get_custom_field_options(self, custom_field: str, context_id: int):
        return self.requestor.fetch_data(
            f"field/{custom_field}/context/{context_id}/option"
        )

    def create_custom_field_options(
        self, custom_field: str, context_id: int, data: dict
    ):
        return self.requestor.fetch_data(
            f"field/{custom_field}/context/{context_id}/option",
            method="POST",
            url_params=data,
        )

    def get_issue_by_id(self, issue_id: str):
        return self.requestor.fetch_data(f"issue/{issue_id}")

    def get_all_project_issues(self, project_key: str):
        all_issues = []
        next_page_token = None
        max_results = 5000

        while True:
            if next_page_token:
                endpoint = f"search/jql?jql=project={project_key}&nextPageToken={next_page_token}&maxResults={max_results}"  # noqa: E501
            else:
                endpoint = f"search/jql?jql=project={project_key}&maxResults={max_results}"  # noqa: E501

            response = self.requestor.fetch_data(endpoint)

            issues = response.get("issues", [])
            all_issues.extend(issues)

            if response.get("isLast", True):
                break

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return {"issues": all_issues}

    def get_issue_worklogs(
        self,
        issue_id: str,
        starter_after=None,
        starter_before=None,
    ):
        all_worklogs = []
        start_at = 0
        max_results = 100

        while True:
            response = self.requestor.fetch_data(
                f"issue/{issue_id}/worklog?startedAfter={starter_after}&startedBefore={starter_before}&maxResults={max_results}&startAt={start_at}",  # noqa: E501
            )

            worklogs = response.get("worklogs", [])
            all_worklogs.extend(worklogs)

            if start_at + max_results >= response.get("total", 0):
                break

            start_at += max_results

        return {"worklogs": all_worklogs}
