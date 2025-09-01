"""
FIS MCP Server - Python Implementation
Converted from Node.js MCP server for AWS Fault Injection Simulator
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import boto3
import mcp.server.stdio
import mcp.types as types
import requests
from mcp.server.fastmcp import FastMCP

from validate.validator import ExperimentValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("fis-mcp-server")
validator = ExperimentValidator()


# Initialize AWS client
def _get_aws_client():
    """Get AWS FIS client with proper configuration"""
    region = os.environ.get("AWS_REGION", "us-west-2")
    return boto3.client("fis", region_name=region)


def _get_account_id():
    """Get current AWS account ID"""
    sts_client = boto3.client("sts")
    return sts_client.get_caller_identity()["Account"]


client = _get_aws_client()


def _load_config() -> Dict[str, Any]:
    """Load configuration from aws_config.json if it exists"""
    config_path = os.path.join(os.path.dirname(__file__), "aws_config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load config file: {str(e)}")
    return {}


# @mcp.tool()
# async def create_experiment_template(
#     description: str,
#     role_arn: str,
#     action_id: str,
#     target_resource_type: str,
#     stop_conditions: List[Dict[str, Any]],
#     action_parameters: Optional[Dict[str, Any]] = None,
#     action_targets: Optional[Dict[str, str]] = None,
#     target_resource_arns: Optional[List[str]] = None,
#     target_selection_mode: str = "ALL",
#     target_filters: Optional[Dict[str, Any]] = None,
#     tags: Optional[Dict[str, str]] = None,
# ) -> types.CallToolResult:
#     """Create a new AWS FIS experiment template"""
#     try:
#         # Compose actions structure
#         action_config = {"actionId": action_id}
#         if action_parameters:
#             action_config["parameters"] = action_parameters
#         if action_targets:
#             action_config["targets"] = action_targets

#         actions = {"action_name": action_config}

#         # Compose targets structure
#         target_config = {
#             "resourceType": target_resource_type,
#             "selectionMode": target_selection_mode,
#         }
#         if target_resource_arns:
#             target_config["resourceArns"] = target_resource_arns
#         if target_filters:
#             target_config["filters"] = target_filters

#         targets = {"target1": target_config}

#         # Compose template configuration
#         template_config = {
#             "description": description,
#             "roleArn": role_arn,
#             "actions": actions,
#             "targets": targets,
#             "stopConditions": stop_conditions,
#         }

#         if tags:
#             template_config["tags"] = tags

#         # Validate template configuration
#         validation_result = await validator.validate_template(template_config)

#         if not validation_result["valid"]:
#             error_msg = "Template validation failed:\n"
#             for error in validation_result["errors"]:
#                 error_msg += f"- {error}\n"
#             if validation_result["warnings"]:
#                 error_msg += "\nWarnings:\n"
#                 for warning in validation_result["warnings"]:
#                     error_msg += f"- {warning}\n"
#             raise Exception(error_msg)

#         # Log warnings if any
#         if validation_result["warnings"]:
#             logger.warning("Template validation warnings:")
#             for warning in validation_result["warnings"]:
#                 logger.warning(f"- {warning}")

#         # Validate and clean actions to remove unsupported parameters
#         cleaned_actions = _clean_actions(actions)

#         input_params = {
#             "description": description,
#             "roleArn": role_arn,
#             "actions": cleaned_actions,
#             "targets": targets,
#             "stopConditions": stop_conditions,
#         }

#         # Add optional parameters
#         if tags:
#             input_params["tags"] = tags

#         response = client.create_experiment_template(**input_params)

#         result_text = f"Successfully created experiment template:\n{json.dumps(response['experimentTemplate'], indent=2, default=str)}"

#         return types.CallToolResult(
#             content=[types.TextContent(type="text", text=result_text)]
#         )

#     except Exception as error:
#         raise Exception(f"Failed to create experiment template: {str(error)}")


def _clean_actions(actions: Dict[str, Any]) -> Dict[str, Any]:
    """Clean actions to remove unsupported parameters based on action type"""
    cleaned_actions = {}

    # Actions that don't support duration parameter
    no_duration_actions = [
        "aws:ec2:reboot-instances",
        "aws:ec2:stop-instances",
        "aws:ec2:terminate-instances",
        "aws:rds:failover-db-cluster",
        "aws:rds:reboot-db-instances",
    ]

    for action_name, action_config in actions.items():
        cleaned_config = action_config.copy()

        # Remove duration parameter for actions that don't support it
        if action_config.get("actionId") in no_duration_actions:
            if (
                "parameters" in cleaned_config
                and "duration" in cleaned_config["parameters"]
            ):
                logger.warning(
                    f"Removing unsupported 'duration' parameter from action {action_config.get('actionId')}"
                )
                del cleaned_config["parameters"]["duration"]
                # If parameters is now empty, remove it entirely
                if not cleaned_config["parameters"]:
                    del cleaned_config["parameters"]

        cleaned_actions[action_name] = cleaned_config

    return cleaned_actions


# @mcp.tool()
# async def list_experiment_templates(
#     params: Dict[str, Any] = None,
# ) -> types.CallToolResult:
#     """List all AWS FIS experiment templates"""
#     try:
#         if params is None:
#             params = {}

#         input_params = {}
#         if "maxResults" in params:
#             input_params["maxResults"] = params["maxResults"]
#         if "nextToken" in params:
#             input_params["nextToken"] = params["nextToken"]

#         response = client.list_experiment_templates(**input_params)
#         templates = response.get("experimentTemplates", [])

#         template_list = []
#         for template in templates:
#             template_list.append(
#                 {
#                     "id": template.get("id"),
#                     "description": template.get("description"),
#                     "creationTime": template.get("creationTime"),
#                     "lastUpdateTime": template.get("lastUpdateTime"),
#                     "tags": template.get("tags", {}),
#                 }
#             )

#         result_text = f"Found {len(templates)} experiment templates:\n{json.dumps(template_list, indent=2, default=str)}"

#         return types.CallToolResult(
#             content=[types.TextContent(type="text", text=result_text)]
#         )

#     except Exception as error:
#         raise Exception(f"Failed to list experiment templates: {str(error)}")


# @mcp.tool()
# async def get_experiment_template(template_id: str) -> types.CallToolResult:
#     """Get detailed information about a specific experiment template"""
#     try:
#         response = client.get_experiment_template(id=template_id)

#         result_text = f"Experiment template details:\n{json.dumps(response['experimentTemplate'], indent=2, default=str)}"

#         return types.CallToolResult(
#             content=[types.TextContent(type="text", text=result_text)]
#         )

#     except Exception as error:
#         raise Exception(f"Failed to get experiment template: {str(error)}")


# @mcp.tool()
# async def list_experiments(params: Dict[str, Any] = None) -> types.CallToolResult:
#     """List all AWS FIS experiments"""
#     try:
#         if params is None:
#             params = {}

#         input_params = {}
#         if "maxResults" in params:
#             input_params["maxResults"] = params["maxResults"]
#         if "nextToken" in params:
#             input_params["nextToken"] = params["nextToken"]

#         response = client.list_experiments(**input_params)
#         experiments = response.get("experiments", [])

#         experiment_list = []
#         for experiment in experiments:
#             experiment_list.append(
#                 {
#                     "id": experiment.get("id"),
#                     "experimentTemplateId": experiment.get("experimentTemplateId"),
#                     "state": experiment.get("state", {}),
#                     "creationTime": experiment.get("creationTime"),
#                     "tags": experiment.get("tags", {}),
#                 }
#             )

#         result_text = f"Found {len(experiments)} experiments:\n{json.dumps(experiment_list, indent=2, default=str)}"

#         return types.CallToolResult(
#             content=[types.TextContent(type="text", text=result_text)]
#         )

#     except Exception as error:
#         raise Exception(f"Failed to list experiments: {str(error)}")


# @mcp.tool()
# async def get_experiment(experiment_id: str) -> types.CallToolResult:
#     """Get detailed information about a specific experiment"""
#     try:
#         response = client.get_experiment(id=experiment_id)

#         result_text = f"Experiment details:\n{json.dumps(response['experiment'], indent=2, default=str)}"

#         return types.CallToolResult(
#             content=[types.TextContent(type="text", text=result_text)]
#         )

#     except Exception as error:
#         raise Exception(f"Failed to get experiment: {str(error)}")


# @mcp.tool()
# async def start_experiment(
#     template_id: str, tags: Dict[str, str] = None
# ) -> types.CallToolResult:
#     """Start a chaos engineering experiment from a template"""
#     try:
#         input_params = {"experimentTemplateId": template_id}

#         # Add optional tags
#         if tags:
#             input_params["tags"] = tags

#         response = client.start_experiment(**input_params)

#         result_text = f"Successfully started experiment:\n{json.dumps(response['experiment'], indent=2, default=str)}"

#         return types.CallToolResult(
#             content=[types.TextContent(type="text", text=result_text)]
#         )

#     except Exception as error:
#         raise Exception(f"Failed to start experiment: {str(error)}")


# @mcp.tool()
# async def stop_experiment(experiment_id: str) -> types.CallToolResult:
#     """Stop a running chaos engineering experiment"""
#     try:
#         response = client.stop_experiment(id=experiment_id)

#         result_text = f"Successfully stopped experiment:\n{json.dumps(response['experiment'], indent=2, default=str)}"

#         return types.CallToolResult(
#             content=[types.TextContent(type="text", text=result_text)]
#         )

#     except Exception as error:
#         raise Exception(f"Failed to stop experiment: {str(error)}")


@mcp.tool()
async def db_failure(
    db_identifier: str,
    failure_type: str = "reboot",
    region: Optional[str] = None,
) -> types.CallToolResult:
    """Execute database failure experiment with minimal configuration"""
    try:
        if not region:
            region = os.environ.get("AWS_REGION", "us-west-2")

        account_id = _get_account_id()
        role_arn = f"arn:aws:iam::{account_id}:role/FISExperimentRole"

        # Determine if it's RDS instance or Aurora cluster
        rds_client = boto3.client("rds", region_name=region)
        is_cluster = False

        try:
            rds_client.describe_db_clusters(DBClusterIdentifier=db_identifier)
            is_cluster = True
        except rds_client.exceptions.DBClusterNotFoundFault:
            try:
                rds_client.describe_db_instances(DBInstanceIdentifier=db_identifier)
                is_cluster = False
            except rds_client.exceptions.DBInstanceNotFoundFault:
                raise Exception(f"Database {db_identifier} not found")

        # Set appropriate values based on resource type
        if is_cluster:
            resource_type = "aws:rds:cluster"
            resource_arn = f"arn:aws:rds:{region}:{account_id}:cluster:{db_identifier}"
            if failure_type == "reboot":
                action_id = "aws:rds:failover-db-cluster"  # Clusters don't support reboot, use failover
            elif failure_type == "failover":
                action_id = "aws:rds:failover-db-cluster"
            elif failure_type == "stop":
                action_id = "aws:rds:stop-db-cluster"
            else:
                action_id = "aws:rds:failover-db-cluster"
        else:
            resource_type = "aws:rds:db"
            resource_arn = f"arn:aws:rds:{region}:{account_id}:db:{db_identifier}"
            if failure_type == "reboot":
                action_id = "aws:rds:reboot-db-instances"
            elif failure_type == "failover":
                action_id = "aws:rds:reboot-db-instances"  # Instances don't support failover, use reboot
            elif failure_type == "stop":
                action_id = "aws:rds:stop-db-instances"
            else:
                action_id = "aws:rds:reboot-db-instances"

        # Create template
        template_config = {
            "description": f"DB {failure_type} experiment for {db_identifier}",
            "roleArn": role_arn,
            "actions": {
                "db_action": {
                    "actionId": action_id,
                    "targets": {
                        "DBInstances" if not is_cluster else "DBClusters": "db_target"
                    },
                }
            },
            "targets": {
                "db_target": {
                    "resourceType": resource_type,
                    "resourceArns": [resource_arn],
                    "selectionMode": "ALL",
                }
            },
            "stopConditions": [{"source": "none"}],
        }

        # Create and start experiment
        template_response = client.create_experiment_template(**template_config)
        template_id = template_response["experimentTemplate"]["id"]

        experiment_response = client.start_experiment(experimentTemplateId=template_id)

        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"DB failure experiment started: {experiment_response['experiment']['id']} ({'cluster' if is_cluster else 'instance'})",
                )
            ]
        )

    except Exception as error:
        raise Exception(f"DB failure experiment failed: {str(error)}")


def _convert_duration(duration_str: str) -> str:
    """Convert duration string to ISO 8601 format (PT format)"""
    import re

    # Already in PT format
    if duration_str.startswith("PT"):
        return duration_str

    # Parse common formats like "60s", "10m", "2h"
    match = re.match(r"(\d+)([smh])", duration_str.lower())
    if not match:
        raise ValueError(
            f"Invalid duration format: {duration_str}. Use formats like '60s', '10m', '2h'"
        )

    value, unit = match.groups()
    unit_map = {"s": "S", "m": "M", "h": "H"}

    return f"PT{value}{unit_map[unit]}"


@mcp.tool()
async def az_failure(
    availability_zone: str,
    duration: str = "10m",
    region: Optional[str] = None,
) -> types.CallToolResult:
    """Execute availability zone failure experiment with minimal configuration"""
    try:
        if not region:
            region = os.environ.get("AWS_REGION", "us-west-2")

        account_id = _get_account_id()
        role_arn = f"arn:aws:iam::{account_id}:role/FISExperimentRole"

        # Convert duration to PT format
        pt_duration = _convert_duration(duration)

        # Get all subnets in the specified AZ
        ec2_client = boto3.client("ec2", region_name=region)
        response = ec2_client.describe_subnets(
            Filters=[{"Name": "availability-zone", "Values": [availability_zone]}]
        )

        subnet_arns = []
        for subnet in response["Subnets"]:
            subnet_id = subnet["SubnetId"]
            subnet_arn = f"arn:aws:ec2:{region}:{account_id}:subnet/{subnet_id}"
            subnet_arns.append(subnet_arn)

        if not subnet_arns:
            raise Exception(
                f"No subnets found in availability zone {availability_zone}"
            )

        # Get all EC2 instances in the specified AZ
        instances_response = ec2_client.describe_instances(
            Filters=[
                {"Name": "availability-zone", "Values": [availability_zone]},
                {"Name": "instance-state-name", "Values": ["running", "stopped"]},
            ]
        )

        instance_arns = []
        for reservation in instances_response["Reservations"]:
            for instance in reservation["Instances"]:
                instance_id = instance["InstanceId"]
                instance_arn = (
                    f"arn:aws:ec2:{region}:{account_id}:instance/{instance_id}"
                )
                instance_arns.append(instance_arn)

        # Get all ASGs in the specified AZ
        asg_client = boto3.client("autoscaling", region_name=region)
        asg_response = asg_client.describe_auto_scaling_groups()

        asg_arns = []
        for asg in asg_response["AutoScalingGroups"]:
            # Check if ASG has instances in the target AZ
            for az in asg["AvailabilityZones"]:
                if az == availability_zone:
                    asg_arn = asg["AutoScalingGroupARN"]
                    asg_arns.append(asg_arn)
                    break

        # Get all RDS instances in the specified AZ
        rds_client = boto3.client("rds", region_name=region)
        db_instances_response = rds_client.describe_db_instances()
        db_clusters_response = rds_client.describe_db_clusters()

        db_instance_arns = []
        db_cluster_arns = []

        for db in db_instances_response["DBInstances"]:
            if db["AvailabilityZone"] == availability_zone:
                db_arn = db["DBInstanceArn"]
                db_instance_arns.append(db_arn)

        for cluster in db_clusters_response["DBClusters"]:
            for az in cluster.get("AvailabilityZones", []):
                if az == availability_zone:
                    cluster_arn = cluster["DBClusterArn"]
                    db_cluster_arns.append(cluster_arn)
                    break

        # Create template for AZ failure
        template_config = {
            "description": f"AZ failure experiment for {availability_zone}",
            "roleArn": role_arn,
            "targets": {
                "Subnet": {
                    "resourceType": "aws:ec2:subnet",
                    "resourceArns": subnet_arns,
                    "selectionMode": "ALL",
                },
                "EC2-Instances": {
                    "resourceType": "aws:ec2:instance",
                    "resourceArns": instance_arns,
                    "selectionMode": "ALL",
                },
                "ASG": {
                    "resourceType": "aws:ec2:autoscaling-group",
                    "resourceArns": asg_arns,
                    "selectionMode": "ALL",
                },
                "DB-Instances": {
                    "resourceType": "aws:rds:db",
                    "resourceArns": db_instance_arns,
                    "selectionMode": "ALL",
                },
                "DB-Clusters": {
                    "resourceType": "aws:rds:cluster",
                    "resourceArns": db_cluster_arns,
                    "selectionMode": "ALL",
                },
            },
            "actions": {
                "Stop-Instances": {
                    "actionId": "aws:ec2:stop-instances",
                    "parameters": {"startInstancesAfterDuration": pt_duration},
                    "targets": {"Instances": "EC2-Instances"},
                },
                "Pause-ASG": {
                    "actionId": "aws:ec2:asg-insufficient-instance-capacity-error",
                    "parameters": {
                        "availabilityZoneIdentifiers": availability_zone,
                        "duration": pt_duration,
                        "percentage": "100",
                    },
                    "targets": {"AutoScalingGroups": "ASG"},
                },
                "Stop-DB-Instances": {
                    "actionId": "aws:rds:reboot-db-instances",
                    "targets": {"DBInstances": "DB-Instances"},
                },
                "Failover-DB-Clusters": {
                    "actionId": "aws:rds:failover-db-cluster",
                    "targets": {"Clusters": "DB-Clusters"},
                },
                "Pause-network-connectivity": {
                    "actionId": "aws:network:disrupt-connectivity",
                    "parameters": {"duration": pt_duration, "scope": "all"},
                    "targets": {"Subnets": "Subnet"},
                },
            },
            "stopConditions": [{"source": "none"}],
            "experimentOptions": {"emptyTargetResolutionMode": "skip"},
        }

        # Create and start experiment
        template_response = client.create_experiment_template(**template_config)
        template_id = template_response["experimentTemplate"]["id"]

        experiment_response = client.start_experiment(experimentTemplateId=template_id)

        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"AZ failure experiment started: {experiment_response['experiment']['id']}",
                )
            ]
        )

    except Exception as error:
        raise Exception(f"AZ failure experiment failed: {str(error)}")


@mcp.tool()
async def msk_failure(
    cluster_name: str,
    failure_percent: int = 50,
    region: Optional[str] = None,
) -> types.CallToolResult:
    """Execute MSK cluster failure experiment using SSM automation"""
    try:
        if not region:
            region = os.environ.get("AWS_REGION", "us-west-2")

        account_id = _get_account_id()
        role_arn = f"arn:aws:iam::{account_id}:role/FISExperimentRole"

        # Get cluster ARN and broker IDs
        kafka_client = boto3.client("kafka", region_name=region)
        clusters = kafka_client.list_clusters()["ClusterInfoList"]
        cluster_arn = None
        for cluster in clusters:
            if cluster["ClusterName"] == cluster_name:
                cluster_arn = cluster["ClusterArn"]
                break

        if not cluster_arn:
            raise Exception(f"MSK cluster {cluster_name} not found")

        # Get actual broker node info
        nodes_response = kafka_client.list_nodes(ClusterArn=cluster_arn)
        broker_ids = [
            str(node["BrokerNodeInfo"]["BrokerId"])
            for node in nodes_response["NodeInfoList"]
        ]

        # Select percentage of brokers based on failure_percent
        import random

        num_brokers_to_affect = max(1, int(len(broker_ids) * failure_percent / 100))
        selected_broker_ids = random.sample(broker_ids, num_brokers_to_affect)

        # Create SSM document
        ssm_client = boto3.client("ssm", region_name=region)
        doc_name = f"MSK-RestartBroker-{cluster_name}"

        ssm_document = {
            "schemaVersion": "0.3",
            "description": f"Restart MSK brokers for {cluster_name}",
            "assumeRole": role_arn,
            "parameters": {
                "ClusterArn": {"type": "String"},
                "BrokerIds": {"type": "StringList"},
            },
            "mainSteps": [
                {
                    "name": "RestartBroker",
                    "action": "aws:executeAwsApi",
                    "inputs": {
                        "Service": "kafka",
                        "Api": "RebootBroker",
                        "ClusterArn": "{{ ClusterArn }}",
                        "BrokerIds": "{{ BrokerIds }}",
                    },
                }
            ],
        }

        try:
            ssm_client.create_document(
                Content=json.dumps(ssm_document),
                Name=doc_name,
                DocumentType="Automation",
            )
        except ssm_client.exceptions.DocumentAlreadyExistsException:
            pass

        # Create FIS template
        template_config = {
            "description": f"MSK broker restart for {cluster_name}",
            "roleArn": role_arn,
            "actions": {
                "msk_action": {
                    "actionId": "aws:ssm:start-automation-execution",
                    "parameters": {
                        "documentArn": f"arn:aws:ssm:{region}:{account_id}:document/{doc_name}",
                        "parameters": json.dumps(
                            {
                                "ClusterArn": cluster_arn,
                                "BrokerIds": selected_broker_ids,
                            }
                        ),
                    },
                }
            },
            "stopConditions": [{"source": "none"}],
        }

        # Create and start experiment
        template_response = client.create_experiment_template(**template_config)
        template_id = template_response["experimentTemplate"]["id"]

        experiment_response = client.start_experiment(experimentTemplateId=template_id)

        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"MSK failure experiment started: {experiment_response['experiment']['id']} (affecting brokers: {selected_broker_ids})",
                )
            ]
        )

    except Exception as error:
        raise Exception(f"MSK failure experiment failed: {str(error)}")


# @mcp.tool()
# async def get_aws_resources() -> types.CallToolResult:
#     """Get AWS resources available for FIS experiments"""
#     try:
#         response = requests.get(
#             os.environ.get("RESOURCE_SCANNER_URL", ""),
#             timeout=30,
#         )
#         response.raise_for_status()

#         data = response.json()

#         result_text = f"AWS Resources available for FIS experiments:\n{json.dumps(data, indent=2)}"

#         return types.CallToolResult(
#             content=[types.TextContent(type="text", text=result_text)]
#         )

#     except Exception as error:
#         raise Exception(f"Failed to get AWS resources: {str(error)}")


def handle_list_tools() -> List[types.Tool]:
    """List available tools"""
    logger.info("Handling list_tools request")

    tools = [
        # types.Tool(
        #     name="create_experiment_template",
        #     description="Create a new AWS FIS experiment template",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "description": {
        #                 "type": "string",
        #                 "description": "Description of the experiment template",
        #             },
        #             "role_arn": {
        #                 "type": "string",
        #                 "description": "IAM role ARN for the experiment",
        #             },
        #             "action_id": {
        #                 "type": "string",
        #                 "description": "FIS action ID (e.g., 'aws:ec2:stop-instances')",
        #             },
        #             "target_resource_type": {
        #                 "type": "string",
        #                 "description": "Target resource type (e.g., 'aws:ec2:instance')",
        #             },
        #             "stop_conditions": {
        #                 "type": "array",
        #                 "description": "Stop conditions for the experiment",
        #             },
        #             "action_parameters": {
        #                 "type": "object",
        #                 "description": "Optional parameters for the action",
        #             },
        #             "action_targets": {
        #                 "type": "object",
        #                 "description": "Optional target mapping for the action",
        #             },
        #             "target_resource_arns": {
        #                 "type": "array",
        #                 "items": {"type": "string"},
        #                 "description": "Optional list of specific resource ARNs to target",
        #             },
        #             "target_selection_mode": {
        #                 "type": "string",
        #                 "enum": ["ALL", "COUNT", "PERCENT"],
        #                 "description": "Target selection mode (default: ALL)",
        #             },
        #             "target_filters": {
        #                 "type": "object",
        #                 "description": "Optional filters for target selection",
        #             },
        #             "tags": {
        #                 "type": "object",
        #                 "description": "Optional tags for the experiment template",
        #             },
        #         },
        #         "required": [
        #             "description",
        #             "role_arn",
        #             "action_id",
        #             "target_resource_type",
        #             "stop_conditions",
        #         ],
        #     },
        # ),
        # types.Tool(
        #     name="list_experiment_templates",
        #     description="List all AWS FIS experiment templates",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "maxResults": {
        #                 "type": "number",
        #                 "description": "Maximum number of results to return",
        #             },
        #             "nextToken": {
        #                 "type": "string",
        #                 "description": "Token for pagination",
        #             },
        #         },
        #     },
        # ),
        # types.Tool(
        #     name="get_experiment_template",
        #     description="Get detailed information about a specific experiment template",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "id": {
        #                 "type": "string",
        #                 "description": "Experiment template ID",
        #             }
        #         },
        #         "required": ["id"],
        #     },
        # ),
        # types.Tool(
        #     name="list_experiments",
        #     description="List all AWS FIS experiments",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "maxResults": {
        #                 "type": "number",
        #                 "description": "Maximum number of results to return",
        #             },
        #             "nextToken": {
        #                 "type": "string",
        #                 "description": "Token for pagination",
        #             },
        #         },
        #     },
        # ),
        # types.Tool(
        #     name="start_experiment",
        #     description="Start a chaos engineering experiment from a template",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "template_id": {
        #                 "type": "string",
        #                 "description": "Experiment template ID to start",
        #             },
        #             "tags": {
        #                 "type": "object",
        #                 "description": "Optional tags for the experiment",
        #             },
        #         },
        #         "required": ["template_id"],
        #     },
        # ),
        # types.Tool(
        #     name="stop_experiment",
        #     description="Stop a running chaos engineering experiment",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "experiment_id": {
        #                 "type": "string",
        #                 "description": "Experiment ID to stop",
        #             }
        #         },
        #         "required": ["experiment_id"],
        #     },
        # ),
        # types.Tool(
        #     name="get_experiment",
        #     description="Get detailed information about a specific experiment",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "id": {"type": "string", "description": "Experiment ID"}
        #         },
        #         "required": ["id"],
        #     },
        # ),
        # types.Tool(
        #     name="get_aws_resources",
        #     description="Get AWS resources available for FIS experiments including EC2, ECS, RDS, and Lambda",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "resource_types": {
        #                 "type": "array",
        #                 "items": {"type": "string"},
        #                 "description": "Specific resource types to query (ec2, ecs, rds, lambda). If not specified, all types are queried.",
        #             },
        #             "include_fis_targets": {
        #                 "type": "boolean",
        #                 "description": "Whether to include FIS-compatible target definitions",
        #                 "default": True,
        #             },
        #         },
        #     },
        # ),
        types.Tool(
            name="db_failure",
            description="Execute database failure experiment with minimal configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "db_identifier": {
                        "type": "string",
                        "description": "Database identifier (RDS instance name or Aurora cluster name)",
                    },
                    "failure_type": {
                        "type": "string",
                        "enum": ["reboot", "failover", "stop"],
                        "description": "Type of failure to simulate (default: reboot)",
                    },
                    "region": {
                        "type": "string",
                        "description": "AWS region (uses AWS_REGION env var if not specified)",
                    },
                },
                "required": ["db_identifier"],
            },
        ),
        types.Tool(
            name="az_failure",
            description="Execute availability zone failure experiment with minimal configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "availability_zone": {
                        "type": "string",
                        "description": "Availability zone to target (e.g., us-west-2a)",
                    },
                    "duration": {
                        "type": "string",
                        "description": "Duration of the failure (e.g., '60s', '10m', '2h', default: '10m')",
                    },
                    "region": {
                        "type": "string",
                        "description": "AWS region (uses AWS_REGION env var if not specified)",
                    },
                },
                "required": ["availability_zone"],
            },
        ),
        types.Tool(
            name="msk_failure",
            description="Execute MSK cluster failure experiment with minimal configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_name": {
                        "type": "string",
                        "description": "MSK cluster name to target",
                    },
                    "failure_percent": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "description": "Percentage of brokers to affect (default: 50)",
                    },
                    "region": {
                        "type": "string",
                        "description": "AWS region (uses AWS_REGION env var if not specified)",
                    },
                },
                "required": ["cluster_name"],
            },
        ),
    ]

    # 각 도구가 올바른 형식인지 확인
    for i, tool in enumerate(tools):
        logger.info(f"Tool {i}: {type(tool)} - {getattr(tool, 'name', 'NO_NAME')}")
        if not hasattr(tool, "name"):
            logger.error(f"Tool missing name attribute: {tool}")
            raise ValueError(f"Invalid tool definition: {tool}")

    logger.info(f"Returning {len(tools)} tools")
    return tools


# Tool handler removed - using individual @mcp.tool() decorators instead


def run_server():
    """Run the MCP server"""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
    run_server()
