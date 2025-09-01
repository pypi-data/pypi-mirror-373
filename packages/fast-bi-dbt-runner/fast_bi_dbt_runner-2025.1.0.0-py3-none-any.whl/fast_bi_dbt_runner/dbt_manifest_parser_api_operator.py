import json
import datetime
import re
import logging
import requests
import uuid
from datetime import datetime
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s
from airflow.hooks.base import BaseHook
from airflow.utils.task_group import TaskGroup
from airflow.operators.python_operator import PythonOperator
from itertools import chain
from time import sleep
from airflow.exceptions import AirflowFailException



class DbtManifestParser:
    """
    A class analyses dbt project and parses manifest.json and creates the respective task groups
    :param manifest_path: Path to the directory containing the manifest files
    :param dbt_tag: define different parts of a project. Have to be set as
    a list of one or a few values
    :param image: docker image where define dbt command
    :param namespace: default
    """

    def __init__(
        self,
        dbt_tag,
        env_vars,
        airflow_vars,
        manifest_path=None,
        image=None,
        namespace=None,
        connection_id=None
    ) -> None:
        self.env_vars = env_vars
        self.airflow_vars = airflow_vars
        self.dbt_tag = dbt_tag
        self.image = image
        self.namespace = namespace
        self.manifest_path = manifest_path
        self.manifest_data = self.load_dbt_manifest()
        self.dbt_tasks = {}
        self.connection_id = connection_id
        self.dbt_log_format_file = "debug" if self.airflow_vars.get("MODEL_DEBUG_LOG") \
                                and self.airflow_vars.get("MODEL_DEBUG_LOG").lower() == "true" \
                                else "info"
        self.fqn_unique_list = []
        self.existing_task_groups = {}

    def get_valid_start_date(self, start_date_raw):
        """
            Tries to parse the START_DATE from Airflow Variables.
            Supports:
            - days_ago() function
            - ISO format (YYYY-MM-DDTHH:MM:SS)
        """
        # Check if start_date_raw follows days_ago(N) pattern
        if re.fullmatch(r"days_ago\(\d+\)", start_date_raw):
            days_value = int(start_date_raw[9:-1])  # Extract the number from days_ago(N)
            return days_ago(days_value)

        # Check if start_date_raw follows the correct ISO format
        try:
            return datetime.fromisoformat(start_date_raw)  # Parse as ISO datetime
        except ValueError:
            raise ValueError(
                f"Invalid start_date format: {start_date_raw}. Must be ISO format (YYYY-MM-DDTHH:MM:SS) or 'days_ago(N)'.")

    def is_resource_type_in_manifest(self, resource_type):
        if any(resource_type in sub_dict.values() for sub_dict in self.manifest_data.values()):
            return 1

    def check_node_cycle_for_tests(self, nodes_list):
        tmp_list = []
        new_depends_on_list = []
        for k, v in nodes_list.items():
            if v["resource_type"] == 'test':

                has_model = any(node.startswith("model") for node in v["depends_on"])
                has_source = any(node.startswith("source") for node in v["depends_on"])
                if has_model and has_source:
                    v['depends_on'] = [node for node in v['depends_on'] if not node.startswith("source")]

                for node in v["depends_on"]:
                    for parent_node_k, parent_node_v in nodes_list.items():
                        if parent_node_k == node:
                            for item in parent_node_v["depends_on"]:
                                if item not in tmp_list:
                                    tmp_list.append(item)

                for node in v["depends_on"]:
                    if node not in tmp_list:
                        new_depends_on_list.append(node)
                v["depends_on"] = new_depends_on_list
                new_depends_on_list = []
                tmp_list = []
        return nodes_list

    def change_to_test_in_models_depends_on(self, nodes_list):
        models_tests_dict = {}
        for k, v in nodes_list.items():
            if v["resource_type"] == 'test':
                for depends_on_model in v['depends_on']:
                    models_tests_dict.setdefault(depends_on_model, []).append(k)

        for k, v in nodes_list.items():
            temp_models_list = []
            if v["resource_type"] != 'test':
                for i in v['depends_on']:
                    if i.split(".")[1] != "re_data":
                        if i not in temp_models_list:
                            if i in models_tests_dict:
                                temp_models_list.extend(models_tests_dict[i])
                            else:
                                temp_models_list.append(i)
                    if temp_models_list:
                        v['depends_on'] = list(set(temp_models_list))
        return nodes_list

    def get_file_tests(self, nodes_list):
        for k, v in nodes_list.items():
            if v["resource_type"] == 'test':
                for i in v.get('depends_on'):
                    if v.get('file_key_name'):
                        if v.get('file_key_name') not in i.split("."):
                            v['depends_on'].remove(i)
                            v['group_type'].remove(i.split(".")[0])
        return nodes_list

    def change_macros_dependencies_to_source_dependencies(self, current_node, source_dict):
        depends_list = []
        depends_list_full_path = []
        if current_node['config'].get('depends_on'):
            depends_list = depends_list + current_node['config'].get('depends_on')

        if current_node["depends_on"].get("macros"):
            for i in current_node["depends_on"].get("macros"):
                if i and i.split('.')[-1] == "generate_columns_from_airbyte_yml":
                    source_table_name = current_node["name"].replace("stg", "raw")
                    depends_list.append(source_table_name)
        depends_list = list(set(depends_list))
        for key in depends_list:
            for k, v in source_dict.items():
                if key in v['name']:
                    depends_list_full_path.append(k)
        if current_node["depends_on"].get("nodes"):
            depends_list_full_path = list(set(depends_list_full_path + current_node["depends_on"].get("nodes")))
        return depends_list_full_path

    def load_dbt_manifest(self):
        """
        Helper function to load the dbt manifest file.
        Returns: A JSON object containing the dbt manifest content.
        """
        with open(self.manifest_path, encoding="utf-8") as file:
            file_content = json.load(file)

            node_dependency = {
                k: v
                for k, v in file_content["nodes"].items()
                if k.split(".")[0] in ["model", "seed", "snapshot", "test", "source"]}

            get_sources = {
                k: v
                for k, v in file_content["sources"].items()
                if k.split(".")[0] in ["source"] and (v.get("freshness")
                                                      and ((v.get("freshness").get("warn_after")
                                                            and v.get("freshness").get("warn_after").get("count"))
                                                           or (v.get("freshness").get("error_after")
                                                               and v.get("freshness").get("error_after").get("count"))))
            }

            get_source_new_dict = {
                k: {
                    "name": v["name"],
                    "alias": v["name"],
                    "package_name": v["package_name"],
                    "resource_type": v["resource_type"],
                    "schema": v["schema"],
                    "fqn": v["fqn"],
                    "group_type": ["source"],
                    "depends_on": [],
                    "tags": v["tags"],
                    "file_key_name": ""
                }
                for k, v in get_sources.items()}

            node_dependency_unique = {
                k: {
                    "name": v["name"],
                    "alias": v["alias"],
                    "package_name": v["package_name"],
                    "resource_type": v["resource_type"],
                    "schema": v["schema"],
                    "fqn": v["fqn"],
                    "group_type": [v["resource_type"]] if v["resource_type"] != "test" else list(
                        set([i.split('.')[0] for i in v["depends_on"].get("nodes", [])])),
                    "depends_on": self.change_macros_dependencies_to_source_dependencies(v, get_source_new_dict),
                    "tags": v["tags"],
                    "file_key_name": v.get("file_key_name", "").split(".")[-1]
                }
                for k, v in node_dependency.items()
                if 'depends_on' in v and (v.get("config").get("materialized") != "ephemeral")}

            node_dependency_unique = self.check_node_cycle_for_tests(node_dependency_unique)
            node_dependency_unique = {**node_dependency_unique, **get_source_new_dict}

            if self.dbt_tag:
                for node in node_dependency_unique:
                    if node_dependency_unique[node].get('depends_on') and \
                            node_dependency_unique[node].get('resource_type') == 'test':
                        for dependent_node in node_dependency_unique[node].get('depends_on'):
                            if dependent_node.split(".")[0] == 'model':
                                node_dependency_unique[node]['tags'].extend(
                                    node_dependency_unique[dependent_node].get('tags'))

                node_dependency_unique = self.filter_tasks_by_tag(node_dependency_unique, self.dbt_tag)
                # node_dependency_unique = self.delete_source_test(node_dependency_unique)
            node_dependency_unique = self.get_file_tests(node_dependency_unique)
            node_dependency_unique = self.change_to_test_in_models_depends_on(node_dependency_unique)
        return node_dependency_unique

    def get_package_list(self):
        package_list = {}
        for node in self.manifest_data.keys():
            k = self.manifest_data[node].get("package_name")
            v = self.manifest_data[node].get(
                "resource_type"
            )  # {dvo_shared: [seed, model, test]}
            if v not in package_list.get(k, []) and k != "re_data":
                package_list[k] = package_list.get(k, []) + [v]
        return package_list

    def filter_models(self, models_list):
        filtered_dict = {}
        for i in self.manifest_data.keys():
            if self.manifest_data[i]["name"] in models_list:
                filtered_dict[i] = self.manifest_data[i]
            if self.manifest_data[i]["depends_on"] and self.manifest_data[i]["resource_type"] == "test":
                for depends_on_model in self.manifest_data[i]["depends_on"]:
                    if depends_on_model.split(".")[-1] in models_list:
                        filtered_dict[i] = self.manifest_data[i]
        return filtered_dict

    def post_api(self, task_id, project_dir, command, host, login, password):
        data = {"command": command, "task_id": task_id, "project_dir": project_dir}
        for i in range(1, 3600):
            post_task_response = requests.post(host, json=data, auth=(login, password))
            if post_task_response.status_code == 200:
                post_task_response.close()
                return post_task_response.json()
        raise Exception("POST API server call failed")

    def get_api(self, task_id, host, login, password):
        print("Start get api")
        for attempt in range(1, 3600):
            get_response = requests.get(host + "/" + task_id, auth=(login, password))
            if get_response.status_code == 200:
                state = get_response.json().get("state")
                if state == "SUCCESS":
                    print("Finish get api")
                    return get_response.json()["log_content"]
                elif state == "FAILURE":
                    print(get_response.json()["log_content"])
                    raise AirflowFailException("FAILED TASK")
            get_response.close()
        print("Finish get api")
        return None

    def post_to_api_server(
        self, task_id, project_dir, command, **kwargs
    ):
        gcd_conn = BaseHook.get_connection(self.connection_id)
        host = gcd_conn.host
        login = gcd_conn.login
        password = gcd_conn.password

        unique_task_id = task_id + str(uuid.uuid4())
        print(f"task_id: {unique_task_id}")
        print(f"FULL DBT COMMAND: {command}")
        if not self.post_api(
            unique_task_id, project_dir, command, host, login, password
        ):
            raise Exception("POST API server call failed")
        else:
            response = self.get_api(unique_task_id, host, login, password)
            if not response:
                raise Exception("GET API server call failed")
            else:
                return response

    def create_api_task(
            self,
            project_dir,
            dbt_command,
            running_rule,
            task_params={},
            full_command_list=None,
            node_name=None,
            node_alias=None,
            parent_group=None
    ):
        """
        Takes the manifest JSON content and returns a KubernetesPodOperator task
        to run a dbt command.
        Args:
            node_name: The name of the node from manifest.json. By default, is equal to None
            dbt_command: dbt command: run, test
            running_rule: argument which defines the rule by which the generated task get triggered
        Returns: A KubernetesPodOperator task that runs the respective dbt command
        :param node_alias:
        :param full_command_list:
        :param project_dir:
        :param dbt_command:
        :param running_rule:
        :param node_name:
        :param task_params:
        """

        if node_name is None:
            if "re_data" not in dbt_command:
                if not isinstance(dbt_command, list):
                    node_name = dbt_command + "_all_models"
                    node_alias = dbt_command + "_all_models"
                if "freshness" in dbt_command:
                    node_name = dbt_command + "_all_sources"
                    node_alias = dbt_command + "_all_sources"

            else:
                node_alias = "re_data_all_models"

        if full_command_list is None:
            if dbt_command == "re_data":
                full_command_list = [
                    "--log-level-file",
                    self.dbt_log_format_file,
                    "run",
                    "--select",
                    "package:re_data"]
            elif dbt_command == "freshness":
                full_command_list = ["--log-level-file",
                                     self.dbt_log_format_file,
                                     "source",
                                     dbt_command,
                                     "--exclude",
                                     "package:re_data"]
            else:
                full_command_list = ["--log-level-file",
                                     self.dbt_log_format_file,
                                     dbt_command,
                                     "--exclude",
                                     "package:re_data"]

        if dbt_command != "test" and dbt_command != "freshness" and task_params.get('full_refresh') is True:
            full_command_list.append("-f")

        if task_params.get("DBT_VAR"):
            full_command_list.extend(["--vars", task_params.get("DBT_VAR")])

        if self.airflow_vars.get("TARGET"):
            full_command_list.extend(["--target", self.airflow_vars.get("TARGET")])

        print(f"FULL DBT COMMAND: {str(full_command_list)}")
        print(f"node_name: {node_name}")
        print(f"node_alias: {node_alias}")

        dbt_task = PythonOperator(
            task_id=node_alias,
            python_callable=self.post_to_api_server,
            op_kwargs={
                "task_id": node_alias,
                "project_dir": project_dir,
                "command": full_command_list
            },
            trigger_rule=running_rule,
            task_group=parent_group
        )
        return dbt_task

    def create_task_groups(self, parent_group, fqn, node, task_name, task_alias, dbt_command, running_rule,
                                            task_params, full_command_with_model_name, project_dir):
        """
        Recursively creates task groups from FQN and adds the task to the final group.
        """
        if not fqn:
            # Base case: If FQN is empty, add a task
            if node not in self.dbt_tasks:
                self.dbt_tasks[node] = self.create_api_task(project_dir=project_dir,
                                                            dbt_command=dbt_command,
                                                            running_rule=running_rule,
                                                            task_params=task_params,
                                                            full_command_list=full_command_with_model_name,
                                                            node_name=task_name,
                                                            node_alias=task_alias,
                                                            parent_group=parent_group)
            return

        # Get the current level and create a subgroup
        current_level = fqn[0]
        if current_level != "re_data":
            subgroup = getattr(parent_group, current_level, None)

            # If the subgroup does not exist, create it
            if not subgroup:
                subgroup = TaskGroup(group_id=current_level, parent_group=parent_group)
                setattr(parent_group, current_level, subgroup)

            # Recurse into the next level
            self.create_task_groups(subgroup, fqn[1:], node, task_name, task_alias, dbt_command, running_rule,
                                    task_params, full_command_with_model_name, project_dir)

    def set_dependencies(self, resource_type):
        """
         Sets the dependencies between tasks based on the `depends_on` attribute in the manifest data.
        """
        for node in self.manifest_data.keys():
            if resource_type in self.manifest_data[node]['group_type']:
                for upstream_node in self.manifest_data[node].get("depends_on", []):
                    if self.dbt_tasks.get(upstream_node, []):
                        self.dbt_tasks[upstream_node] >> self.dbt_tasks[node]

    def create_dbt_task_groups(
            self,
            group_name,
            resource_type,
            project_dir,
            dbt_command,
            running_rule,
            task_params={}):
        """
        Parse out a JSON file and populates the task groups with dbt tasks
        Args:
            group_name: name of Task Groups uses for DAGs graph view in the Airflow UI.
            resource_type: type of manifest nodes group: model, seed, snapshot
            package_name: project name, tag that define by which certain records
            from the manifest nodes will be selected
            dbt_command: dbt command run or test
            running_rule: trigger rule
            task_params: parameters that was added in the task
        Returns: task group
        :param task_params:
        :param running_rule:
        :param group_name:
        :param resource_type:
        :param dbt_command:
        :param project_dir:
        """

        task_params = {k: v for k, v in task_params.items() if v}  # get only not empty value in task_params
        if "full_refresh_model_name" in task_params:
            self.manifest_data = self.filter_models(task_params["full_refresh_model_name"])

        if self.is_resource_type_in_manifest(resource_type):
            # Initialize the root TaskGroup from `group_name` (should be a TaskGroup instance, not a string)
            with TaskGroup(group_id=group_name, parent_group=None) as root_group:
                for node_id, node_data in self.manifest_data.items():
                    if group_name[:-1] in node_data["group_type"]:
                        # Extract FQN and task name
                        fqn = node_data["fqn"][:-1]  # Remove model name from the FQN
                        task_name = node_data["name"]
                        task_alias = node_data["alias"]
                        if node_data['resource_type'] == "test":
                            dbt_command = "test"
                        if node_data['resource_type'] == "source":
                            task_name = f"source:{node_data['schema']}.{task_name}"
                            dbt_command = "freshness"
                        if task_name:
                            if node_data['resource_type'] == "source":
                                full_command_with_model_name = ["--log-level-file",
                                                                self.dbt_log_format_file,
                                                                "source",
                                                                dbt_command,
                                                                "--select",
                                                                task_name]
                            else:
                                full_command_with_model_name = ["--log-level-file",
                                                                self.dbt_log_format_file,
                                                                dbt_command,
                                                                "--exclude",
                                                                "package:re_data",
                                                                "--select",
                                                                task_name]

                        else:
                            if node_data['resource_type'] == "source":
                                full_command_with_model_name = ["--log-level-file",
                                                                self.dbt_log_format_file,
                                                                "source",
                                                                dbt_command,
                                                                "--exclude",
                                                                "package:re_data"]
                            else:
                                full_command_with_model_name = ["--log-level-file",
                                                                self.dbt_log_format_file,
                                                                dbt_command,
                                                                "--exclude",
                                                                "package:re_data"]
                        # Create the dynamic task groups under root_group
                        self.create_task_groups(root_group, fqn, node_id, task_name, task_alias, dbt_command, running_rule,
                                                task_params, full_command_with_model_name, project_dir)
            self.set_dependencies(resource_type)
            return root_group

