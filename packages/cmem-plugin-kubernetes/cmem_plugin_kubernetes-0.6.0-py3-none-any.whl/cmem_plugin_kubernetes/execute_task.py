"""Pod exec workflow task"""

import shlex
from collections import OrderedDict
from collections.abc import Sequence
from pathlib import Path
from tempfile import NamedTemporaryFile

from cmem_plugin_base.dataintegration.context import ExecutionContext, ExecutionReport
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginAction, PluginParameter
from cmem_plugin_base.dataintegration.entity import (
    Entities,
    EntitySchema,
)
from cmem_plugin_base.dataintegration.parameter.choice import ChoiceParameterType
from cmem_plugin_base.dataintegration.parameter.code import YamlCode
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import FixedNumberOfInputs, FixedSchemaPort
from cmem_plugin_base.dataintegration.typed_entities.file import FileEntitySchema, LocalFile
from kubernetes.client import CoreV1Api, V1NamespaceList
from kubernetes.config import load_incluster_config, new_client_from_config
from kubernetes.stream import stream

DEFAULT_CONFIG = YamlCode("")
CONFIG_TYPES = OrderedDict(
    {
        "incluster": "incluster: Use the service account kubernetes gives to pods to connect.",
        "explicit": "explicit: Use a YAML configuration file to connect (see advanced parameters).",
    }
)


@Plugin(
    label="Execute a command in a kubernetes pod",
    plugin_id="cmem_plugin_kubernetes-Execute",
    description="Connect to a cluster, execute a command and gather the output.",
    documentation="""
This plugin enables execution of commands inside Kubernetes pods and captures their output.

## Features

- Supports multiple connection types:
  - **In-cluster**: Uses the service account kubernetes gives to pods
    (for plugins running inside k8s)
  - **Explicit config**: Uses a YAML kubeconfig file for external connections
- Executes shell commands in specified pods within namespaces
- Captures both stdout and stderr output
- Returns command output as a file entity for further processing
- Includes namespace listing functionality to verify cluster access and connectivity

## Output

Command output is captured and returned as a text file entity that can be consumed by
downstream workflow tasks.

## Use Cases

- Running external pipelines
- Running diagnostic commands in production pods
- Executing maintenance scripts from within or outside the cluster
- Gathering system information and logs
- Performing health checks and troubleshooting
    """,
    icon=Icon(package=__package__, file_name="kubernetes.svg"),
    actions=[
        PluginAction(
            name="list_namespaces_action",
            label="List Namespaces",
            description="Check access to the cluster and list namespaces.",
        ),
    ],
    parameters=[
        PluginParameter(
            param_type=ChoiceParameterType(CONFIG_TYPES),
            name="config_type",
            label="Config Type",
            description="The type of configuration you wish to use.",
            default_value="explicit",
        ),
        PluginParameter(
            name="namespace",
            label="Namespace",
            description="Namespaces provide a mechanism for isolating groups of resources.",
        ),
        PluginParameter(
            name="pod",
            label="Pod",
            description="Pods are an abstraction that represent groups of one or more application "
            "containers (such as Docker), and some shared resources for those containers.",
        ),
        PluginParameter(
            name="command",
            label="Command",
            description="The command to execute.",
        ),
        PluginParameter(
            name="kube_config",
            label="Kube Config",
            description="YAML source code of the kube config.",
            advanced=True,
        ),
    ],
)
class PodExec(WorkflowPlugin):
    """Execute a command in a kubernetes pod"""

    config_type: str
    namespace: str
    pod: str
    command: str
    kube_config: str
    output_schema: EntitySchema
    _client: CoreV1Api | None = None

    def __init__(
        self,
        config_type: str,
        namespace: str,
        pod: str,
        command: str,
        kube_config: YamlCode = DEFAULT_CONFIG,
    ) -> None:
        self.config_type = config_type
        self.kube_config = kube_config.code
        self.namespace = namespace
        self.pod = pod
        self.command = command
        self.output_schema: FileEntitySchema = FileEntitySchema()
        self.input_ports = FixedNumberOfInputs([])
        self.output_port = FixedSchemaPort(schema=self.output_schema)

    def create_client(self) -> CoreV1Api:
        """Create a kubernetes client"""
        if self.config_type == "incluster":
            load_incluster_config()
            return CoreV1Api()
        if self.config_type == "explicit":
            with NamedTemporaryFile() as tmp_file:
                Path(tmp_file.name).write_text(self.kube_config)
                api_client = new_client_from_config(config_file=tmp_file.name)
                return CoreV1Api(api_client=api_client)
        raise ValueError(f"Invalid config type - choose from: {CONFIG_TYPES.keys()}")

    @property
    def client(self) -> CoreV1Api:
        """Lazy loaded Kubernetes client"""
        if not self._client:
            self._client = self.create_client()
        return self._client

    def list_namespaces_action(self) -> str:
        """Check access action"""
        namespaces: V1NamespaceList = self.client.list_namespace()
        output = "Client was able to list the following namespaces:\n\n"
        for namespace in namespaces.items:
            output += f"- {namespace.metadata.name}\n"
        return output

    def execute(
        self,
        inputs: Sequence[Entities],  # noqa: ARG002
        context: ExecutionContext,
    ) -> Entities:
        """Run the workflow operator."""
        command = shlex.split(self.command)
        self.log.info(f"Execute command {command!s} on pod {self.pod}@{self.namespace}")
        exec_response = stream(
            self.client.connect_get_namespaced_pod_exec,
            name=self.pod,
            namespace=self.namespace,
            command=command,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
        )
        context.report.update(
            ExecutionReport(
                entity_count=1,
                operation="done",
                operation_desc="command executed",
            )
        )
        with NamedTemporaryFile(mode="w+t", delete=False) as tmp_file:
            tmp_file.write(exec_response)
        file = LocalFile(path=tmp_file.name, mime="text/plain")
        entity = self.output_schema.to_entity(value=file)
        return Entities(
            schema=self.output_schema,
            entities=iter([entity]),
        )
