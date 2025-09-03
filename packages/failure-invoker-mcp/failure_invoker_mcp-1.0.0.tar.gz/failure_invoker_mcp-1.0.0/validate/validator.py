import re
from typing import Any, Dict, List, Optional


class ExperimentValidator:
    """Class to validate experiment templates and experiments."""

    def __init__(self):
        self.required_template_fields = ["description", "roleArn", "actions", "targets"]

        self.valid_action_ids = [
            "aws:arc:start-zonal-autoshift",
            "aws:cloudwatch:assert-alarm-state",
            "aws:dsql:cluster-connection-failure",
            "aws:dynamodb:global-table-pause-replication",
            "aws:ebs:pause-volume-io",
            "aws:ec2:api-insufficient-instance-capacity-error",
            "aws:ec2:asg-insufficient-instance-capacity-error",
            "aws:ec2:reboot-instances",
            "aws:ec2:send-spot-instance-interruptions",
            "aws:ec2:stop-instances",
            "aws:ec2:terminate-instances",
            "aws:ecs:drain-container-instances",
            "aws:ecs:stop-task",
            "aws:ecs:task-cpu-stress",
            "aws:ecs:task-io-stress",
            "aws:ecs:task-kill-process",
            "aws:ecs:task-network-blackhole-port",
            "aws:ecs:task-network-latency",
            "aws:ecs:task-network-packet-loss",
            "aws:eks:inject-kubernetes-custom-resource",
            "aws:eks:pod-cpu-stress",
            "aws:eks:pod-delete",
            "aws:eks:pod-io-stress",
            "aws:eks:pod-memory-stress",
            "aws:eks:pod-network-blackhole-port",
            "aws:eks:pod-network-latency",
            "aws:eks:pod-network-packet-loss",
            "aws:eks:terminate-nodegroup-instances",
            "aws:elasticache:replicationgroup-interrupt-az-power",
            "aws:fis:inject-api-internal-error",
            "aws:fis:inject-api-throttle-error",
            "aws:fis:inject-api-unavailable-error",
            "aws:fis:wait",
            "aws:lambda:invocation-add-delay",
            "aws:lambda:invocation-error",
            "aws:lambda:invocation-http-integration-response",
            "aws:memorydb:multi-region-cluster-pause-replication",
            "aws:network:disrupt-connectivity",
            "aws:network:route-table-disrupt-cross-region-connectivity",
            "aws:network:transit-gateway-disrupt-cross-region-connectivity",
            "aws:rds:failover-db-cluster",
            "aws:rds:reboot-db-instances",
            "aws:s3:bucket-pause-replication",
            "aws:ssm:send-command",
            "aws:ssm:start-automation-execution",
        ]

        self.valid_resource_types = [
            "aws:arc:zonal-shift-managed-resource",
            "aws:dsql:cluster",
            "aws:dynamodb:global-table",
            "aws:ec2:autoscaling-group",
            "aws:ec2:ebs-volume",
            "aws:ec2:instance",
            "aws:ec2:spot-instance",
            "aws:ec2:subnet",
            "aws:ec2:transit-gateway",
            "aws:ecs:cluster",
            "aws:ecs:task",
            "aws:eks:cluster",
            "aws:eks:nodegroup",
            "aws:eks:pod",
            "aws:elasticache:replicationgroup",
            "aws:iam:role",
            "aws:lambda:function",
            "aws:memorydb:multi-region-cluster",
            "aws:rds:cluster",
            "aws:rds:db",
            "aws:s3:bucket",
        ]

        self.valid_selection_modes = ["ALL", "COUNT", "PERCENT"]
        self.valid_stop_condition_sources = ["aws:cloudwatch:alarm", "none"]

    async def validate_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Validate experiment template configuration"""
        errors = []
        warnings = []

        try:
            # Basic field validation
            basic_validation = self._validate_basic_template_fields(template)
            errors.extend(basic_validation["errors"])
            warnings.extend(basic_validation["warnings"])

            # Role ARN validation
            role_validation = self._validate_role_arn(template.get("roleArn"))
            errors.extend(role_validation["errors"])
            warnings.extend(role_validation["warnings"])

            # Actions validation
            actions_validation = self._validate_actions(template.get("actions", {}))
            errors.extend(actions_validation["errors"])
            warnings.extend(actions_validation["warnings"])

            # Targets validation
            targets_validation = self._validate_targets(template.get("targets", {}))
            errors.extend(targets_validation["errors"])
            warnings.extend(targets_validation["warnings"])

            # Stop conditions validation
            if "stopConditions" in template:
                stop_validation = self._validate_stop_conditions(
                    template["stopConditions"]
                )
                errors.extend(stop_validation["errors"])
                warnings.extend(stop_validation["warnings"])

            return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation failed: {str(e)}"],
                "warnings": [],
            }

    def _validate_basic_template_fields(
        self, template: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Validate basic template fields"""
        errors = []
        warnings = []

        # Check required fields
        for field in self.required_template_fields:
            if field not in template:
                errors.append(f"Missing required field: {field}")

        # Description validation
        description = template.get("description", "")
        if not description.strip():
            errors.append("Description cannot be empty")
        elif len(description) > 512:
            errors.append("Description exceeds maximum length of 512 characters")

        return {"errors": errors, "warnings": warnings}

    def _validate_role_arn(self, role_arn: Optional[str]) -> Dict[str, List[str]]:
        """Validate IAM role ARN"""
        errors = []
        warnings = []

        if not role_arn:
            errors.append("Role ARN is required")
            return {"errors": errors, "warnings": warnings}

        # Basic ARN format validation
        arn_pattern = r"^arn:aws:iam::\d{12}:role/.+"
        if not re.match(arn_pattern, role_arn):
            errors.append("Invalid IAM role ARN format")

        return {"errors": errors, "warnings": warnings}

    def _validate_actions(self, actions: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate experiment actions"""
        errors = []
        warnings = []

        if not actions:
            errors.append("At least one action must be specified")
            return {"errors": errors, "warnings": warnings}

        for action_name, action_config in actions.items():
            # Action ID validation
            action_id = action_config.get("actionId")
            if not action_id:
                errors.append(f"Action '{action_name}' missing actionId")
            elif action_id not in self.valid_action_ids:
                errors.append(
                    f"Invalid actionId '{action_id}' in action '{action_name}'"
                )

            # Parameters validation
            parameters = action_config.get("parameters", {})
            if action_id and self._requires_parameters(action_id) and not parameters:
                warnings.append(f"Action '{action_name}' may require parameters")

            # Targets validation for action
            targets = action_config.get("targets")
            if targets and not isinstance(targets, dict):
                errors.append(f"Action '{action_name}' targets must be a dictionary")

        return {"errors": errors, "warnings": warnings}

    def _validate_targets(self, targets: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate experiment targets"""
        errors = []
        warnings = []

        if not targets:
            errors.append("At least one target must be specified")
            return {"errors": errors, "warnings": warnings}

        for target_name, target_config in targets.items():
            # Resource type validation
            resource_type = target_config.get("resourceType")
            if not resource_type:
                errors.append(f"Target '{target_name}' missing resourceType")
            elif resource_type not in self.valid_resource_types:
                errors.append(
                    f"Invalid resourceType '{resource_type}' in target '{target_name}'"
                )

            # Selection mode validation
            selection_mode = target_config.get("selectionMode", "ALL")
            if selection_mode not in self.valid_selection_modes:
                errors.append(
                    f"Invalid selectionMode '{selection_mode}' in target '{target_name}'"
                )

            # Resource count/percentage validation
            if selection_mode == "COUNT":
                resource_arns = target_config.get("resourceArns", [])
                if not resource_arns:
                    warnings.append(
                        f"Target '{target_name}' with COUNT mode should specify resourceArns"
                    )
            elif selection_mode == "PERCENT":
                resource_arns = target_config.get("resourceArns", [])
                if not resource_arns:
                    warnings.append(
                        f"Target '{target_name}' with PERCENT mode should specify resourceArns"
                    )

            # Filters validation
            filters = target_config.get("filters", {})
            if filters and not isinstance(filters, dict):
                errors.append(f"Target '{target_name}' filters must be a dictionary")

        return {"errors": errors, "warnings": warnings}

    def _validate_stop_conditions(
        self, stop_conditions: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Validate stop conditions"""
        errors = []
        warnings = []

        if not isinstance(stop_conditions, list):
            errors.append("Stop conditions must be a list")
            return {"errors": errors, "warnings": warnings}

        for i, condition in enumerate(stop_conditions):
            source = condition.get("source")
            if not source:
                errors.append(f"Stop condition {i + 1} missing source")
            elif source not in self.valid_stop_condition_sources:
                errors.append(
                    f"Invalid stop condition source '{source}' in condition {i + 1}"
                )

            if source == "aws:cloudwatch:alarm":
                value = condition.get("value")
                if not value:
                    errors.append(
                        f"Stop condition {i + 1} with CloudWatch alarm source missing value"
                    )
                elif not value.startswith("arn:aws:cloudwatch:"):
                    errors.append(
                        f"Stop condition {i + 1} value must be a valid CloudWatch alarm ARN"
                    )

        return {"errors": errors, "warnings": warnings}

    def _requires_parameters(self, action_id: str) -> bool:
        """Check if action typically requires parameters"""
        parameter_required_actions = [
            "aws:ssm:send-command",
            "aws:ssm:start-automation-execution",
            "aws:fis:wait",
            "aws:lambda:invocation-add-delay",
        ]
        return action_id in parameter_required_actions

    def validate_experiment(self, experiment: Dict[str, Any]) -> Dict[str, Any]:
        """Validate experiment configuration"""
        errors = []
        warnings = []

        # Experiment template ID validation
        experiment_template_id = experiment.get("experimentTemplateId")
        if not experiment_template_id:
            errors.append("Experiment template ID is required")

        # Tags validation
        tags = experiment.get("tags", {})
        if tags and not isinstance(tags, dict):
            errors.append("Tags must be a dictionary")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
