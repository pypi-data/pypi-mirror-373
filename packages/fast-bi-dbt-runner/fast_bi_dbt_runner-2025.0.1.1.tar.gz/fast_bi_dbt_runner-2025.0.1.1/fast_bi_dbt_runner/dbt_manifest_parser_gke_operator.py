import json
import datetime
import textwrap
from datetime import datetime
import re
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s
from airflow.exceptions import AirflowException
from airflow.utils.task_group import TaskGroup
from airflow.providers.google.cloud.operators.kubernetes_engine import GKEStartPodOperator
from itertools import chain

class CustomGKEStartPodOperator(GKEStartPodOperator):
    def execute(self, context):
        """
        Executes a GKEStartPodOperator task with customized exception handling.

        This custom operator extends the GKEStartPodOperator from the Airflow library.
        It overrides the execute method to catch AirflowException raised by the parent class.
        The error message is then shortened and a new AirflowException is raised with the
        shortened message. This approach allows for more concise error reporting while
        preserving the detailed error information.

        :param context: The context dictionary provided by Airflow.
        """
        try:
            super().execute(context)
        except AirflowException as e:
            # Shorten the error message for clearer reporting
            msg = str(e)
            short_msg = textwrap.shorten(msg, width=160)
            raise AirflowException(short_msg) from None

class DbtManifestParser:
    """
    A class analyses dbt project and parses manifest.json and creates the respective task groups
    :param manifest_path: Path to the directory containing the manifest files
    :param pod_name: name of Kubercluster pod
    :param dbt_tag: define different parts of a project. Have to be set as
    a list of one or a few values
    :param env_var: airflow variables
    :param image: docker image where define dbt command
    :param namespace: default
    :param PROJECT_ID: identificator of google project project_id.
    Getting from Airflow environment variables {{ var.value.PROJECT_ID }}
    :param CLUSTER_ZONE: Getting from Airflow environment variables {{ var.value.CLUSTER_ZONE }}
    :param CLUSTER_NAME: Getting from Airflow environment variables {{ var.value.CLUSTER_NAME_DBT }}
    """
    def __init__(
            self,
            dbt_tag,
            env_vars,
            airflow_vars,
            manifest_path=None,
            pod_name=None,
            image=None,
            namespace=None,
            project_id=None,
            cluster_zone=None,
            cluster_name=None,
    ) -> None:
        self.env_vars = env_vars
        self.airflow_vars = airflow_vars
        self.pod_name = pod_name
        self.dbt_tag = dbt_tag
        self.image = image
        self.namespace = namespace
        self.project_id = project_id
        self.cluster_zone = cluster_zone
        self.cluster_name = cluster_name
        self.manifest_path = manifest_path
        self.manifest_data = self.load_dbt_manifest()
        self.dbt_tasks = {}
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

    def delete_source_test(self, nodes_list):
        tests_without_source = {}
        for k, v in list(nodes_list.items()):
            if v["resource_type"] == 'test':
                if v.get("group_type"):
                    for i in v.get("group_type"):
                        if i == "source":
                            del nodes_list[k]
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
        print("PATH: " + str(self.manifest_path))
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
            k = self.manifest_data[node].get('package_name')
            v = self.manifest_data[node].get('resource_type')  # {dvo_shared: [seed, model, test]}
            if v not in package_list.get(k, []) and k != "re_data":
                package_list[k] = package_list.get(k, []) + [v]
        return package_list

    def filter_models(self, models_list):
        filtered_dict = {}
        for i in self.manifest_data.keys():
            if self.manifest_data[i]['name'] in models_list:
                filtered_dict[i] = self.manifest_data[i]
            if self.manifest_data[i]['depends_on'] and self.manifest_data[i]['resource_type'] == 'test':
                for depends_on_model in self.manifest_data[i]['depends_on']:
                    if depends_on_model.split(".")[-1] in models_list:
                        filtered_dict[i] = self.manifest_data[i]
        return filtered_dict

    def add_additional_env_variables(self, task_params, dbt_command, node_name):
        # create env_vars_with_model list as a copy of env_vars
        # to avoid redefinition of env_vars list
        env_vars_with_model = self.env_vars.copy()
        airflow_var = self.airflow_vars.copy()

        if task_params.get('full_refresh', None):
            if dbt_command != "test":
                dbt_command = task_params['full_refresh']

        env_vars_with_model.append(k8s.V1EnvVar(name="DBT_COMMAND", value=f"{dbt_command}"))
        # add to env_vars_with_model new variable MODEL that equal
        # to current DBT project model node_name
        if node_name:
            env_vars_with_model.append(k8s.V1EnvVar(name="MODEL", value=f"{node_name}"))
        if dbt_command == "seed":
            env_vars_with_model.append(k8s.V1EnvVar(name="SEED", value="true"))
        else:
            env_vars_with_model.append(k8s.V1EnvVar(name="SEED", value="false"))

        if task_params:
            env_vars_with_model_keys = [i.name for i in env_vars_with_model]
            kuber_dag_new_params = [k8s.V1EnvVar(name=k, value=str(v)) for k, v in task_params.items() if
                                    k not in env_vars_with_model_keys]
            env_vars_with_model.extend(kuber_dag_new_params)
            airflow_var = {**task_params, **airflow_var}

        if dbt_command == "snapshot":
            env_vars_with_model.append(k8s.V1EnvVar(name="SNAPSHOT", value="true"))
            if not airflow_var.get('DBT_SNAPSHOT_INTERVAL') or airflow_var['DBT_SNAPSHOT_INTERVAL'] == 'daily':
                env_vars_with_model.append(k8s.V1EnvVar(name="SNAPSHOT_RUN_PERIOD", value="true"))
            else:
                env_vars_with_model.append(k8s.V1EnvVar(name="SNAPSHOT_RUN_PERIOD", value="false"))

            if airflow_var.get('DBT_DAG_RUN_DATE'):
                date_input = datetime.datetime.strptime(airflow_var['DBT_DAG_RUN_DATE'], "%Y-%m-%d")
                if airflow_var.get('DBT_SNAPSHOT_VALID_FROM'):
                    date_input_from = datetime.datetime.strptime(airflow_var['DBT_SNAPSHOT_VALID_FROM'], "%Y-%m-%d")
                    if airflow_var.get('DBT_SNAPSHOT_VALID_TO'):
                        date_input_to = datetime.datetime.strptime(airflow_var['DBT_SNAPSHOT_VALID_TO'], "%Y-%m-%d")

                        if airflow_var['DBT_SNAPSHOT_INTERVAL'] == 'monthly' \
                                and date_input_from.day <= date_input.day <= date_input_to.day:
                            env_vars_with_model.append(k8s.V1EnvVar(name="SNAPSHOT_RUN_PERIOD", value="true"))
                        elif airflow_var['DBT_SNAPSHOT_INTERVAL'] == 'weekly' \
                                and date_input_from.weekday() <= date_input.weekday() <= date_input_to.weekday():
                            env_vars_with_model.append(k8s.V1EnvVar(name="SNAPSHOT_RUN_PERIOD", value="true"))
        else:
            env_vars_with_model.append(k8s.V1EnvVar(name="SNAPSHOT", value="false"))
        return env_vars_with_model

    def create_dbt_task(self, dbt_command, running_rule, task_params={}, node_name=None, node_alias=None, parent_group=None):
        """
        Takes the manifest JSON content and returns a GKEStartPodOperator task
        to run a dbt command.
        Args:
            node_name: The name of the node from manifest.json. By default is equal to None
            running_rule: trigger rules
            dbt_command: dbt command: run, test
            task_params:
        Returns: A GKEStartPodOperator task that runs the respective dbt command
        """
        env_vars_with_model = self.add_additional_env_variables(task_params, dbt_command, node_name)

        if node_name is None:
            node_name = dbt_command + "_all_models"
            node_alias = dbt_command + "_all_models"
            if dbt_command == "source freshness":
                node_name ="freshness_all_sources"
                node_alias = "freshness_all_sources"

        """
        Create GKEStartPodOperator operators
            Args:
              task_id: The ID specified for the task.
              name: Name of task you want to run, used to generate Pod ID
              namespace: The namespace to run within Kubernetes
              image: Docker image specified
              trigger_rule: the conditions that Airflow applies to tasks
              to determine whether they are ready to execute.
              ALL_DONE - all upstream tasks are done with their execution
        """
        affinity = {
            'podAntiAffinity': {
                'preferredDuringSchedulingIgnoredDuringExecution': [
                    {
                        'weight': 100,
                        'podAffinityTerm': {
                            'labelSelector': {
                                'matchExpressions': [
                                    {
                                        'key': 'component',
                                        'operator': 'In',
                                        'values': ['scheduler', 'triggerer', 'worker']
                                    }
                                ]
                            },
                            'topologyKey': 'kubernetes.io/hostname'
                        }
                    }
                ]
            }
        }

        dbt_task = CustomGKEStartPodOperator(
            task_id=node_alias,
            name=self.pod_name + "_" + node_alias,
            project_id=self.project_id,
            location=self.cluster_zone,
            cluster_name=self.cluster_name,
            namespace=self.namespace,
            image=self.image,
            use_internal_ip=True,
            # Debug - uncomment for debug the container.
            # cmds=["bash", "-cx"],
            # arguments=[f" tail -f /dev/null "],
            # trigger_rule=TriggerRule.ALL_DONE,
            # Optional, run with specific K8S SA Account
            # service_account_name="airflow",
            trigger_rule=running_rule,
            secrets=[],
            labels={"app": "dbt"},
            startup_timeout_seconds=240,
            env_vars=env_vars_with_model,
            get_logs=True,
            image_pull_policy="IfNotPresent",
            image_pull_secrets="fast-bi-common-secret",
            annotations={},
            do_xcom_push=False,
            is_delete_operator_pod=True,
            container_resources=k8s.V1ResourceRequirements(
                requests={"memory": "128Mi", "cpu": "100m"},
            ),
            affinity=affinity,
            task_group=parent_group
        )
        return dbt_task

    def create_task_groups(self, parent_group, fqn, node, task_name, task_alias, dbt_command, running_rule,
                           task_params):
        """
        Recursively creates task groups from FQN and adds the task to the final group.
        """
        if not fqn:
            # Base case: If FQN is empty, add a task
            if node not in self.dbt_tasks:
                self.dbt_tasks[node] = self.create_dbt_task(dbt_command=dbt_command,
                                                                          running_rule=running_rule,
                                                                          task_params=task_params,
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
                                    task_params)

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
        """
        task_params = {k: v for k, v in task_params.items() if v}  # Filter out empty values
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
                            dbt_command = "source freshness"
                        # Create the dynamic task groups under root_group
                        self.create_task_groups(root_group, fqn, node_id, task_name, task_alias, dbt_command, running_rule,
                                                task_params)
            self.set_dependencies(resource_type)
            return root_group