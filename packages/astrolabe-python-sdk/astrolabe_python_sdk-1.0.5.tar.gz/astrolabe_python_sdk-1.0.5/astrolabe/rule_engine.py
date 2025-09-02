"""
Astrolabe Rule Engine - Flag evaluation logic with conditions
"""

from typing import Any, Dict, List, Optional
from enum import Enum
import logging


class AttributeNotDefinedException(Exception):
    """Exception raised when a required attribute is not found in context"""

    pass


class Operator(Enum):
    """Supported condition operators"""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    IN = "in"
    NOT_IN = "not_in"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"


class LogicalOperator(Enum):
    """Logical operators for combining conditions"""

    AND = "AND"
    OR = "OR"


class RuleEngine:
    """
    Rule engine for evaluating flag conditions
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def evaluate_flag(
        self,
        flag_config: Dict[str, Any],
        environment: str,
        attributes: Dict[str, Any],
        default: Any,
    ) -> Any:
        """
        Evaluate a flag based on its configuration, environment, and user attributes.

        Args:
            flag_config: Complete flag configuration
            environment: Current environment (development, staging, production)
            attributes: User/context attributes for rule evaluation
            default: Default value to return if flag is disabled or no rules match

        Returns:
            Evaluated flag value
        """
        flag_key = flag_config.get("key", "unknown")
        self.logger.debug(
            f"Evaluating flag '{flag_key}' for environment '{environment}'"
        )

        # Find environment configuration
        env_config = self._find_environment_config(flag_config, environment)
        if not env_config:
            self.logger.debug(
                f"No environment config found for '{environment}', using default: {default}"
            )
            return default

        # Check if flag is enabled for this environment
        if not env_config.get("enabled", False):
            self.logger.debug(
                f"Flag '{flag_key}' is disabled for environment '{environment}', using default: {default}"
            )
            return default

        self.logger.debug(
            f"Flag '{flag_key}' is enabled for environment '{environment}', evaluating rules"
        )

        # Evaluate rules first
        rule_result = self._evaluate_rules(
            env_config.get("rules", []), attributes, flag_key
        )
        if rule_result is not None:
            self.logger.info(
                f"Flag '{flag_key}' matched rule condition, returning: {rule_result}"
            )
            return rule_result

        # Fall back to environment default value
        env_default = env_config.get("defaultValue", default)
        self.logger.debug(f"Flag '{flag_key}' using environment default: {env_default}")
        return env_default

    def _find_environment_config(
        self, flag_config: Dict[str, Any], environment: str
    ) -> Optional[Dict[str, Any]]:
        """Find the configuration for the specified environment"""
        environments = flag_config.get("environments", [])
        for env_config in environments:
            if env_config.get("environment") == environment:
                return env_config
        return None

    def _evaluate_rules(
        self, rules: List[Dict[str, Any]], attributes: Dict[str, Any], flag_key: str
    ) -> Any:
        """
        Evaluate all rules in order until one matches.

        Args:
            rules: List of rule configurations
            attributes: User/context attributes
            flag_key: Flag key for logging

        Returns:
            Return value of first matching rule, or None if no rules match
        """
        for rule in rules:
            if not rule.get("enabled", True):
                self.logger.debug(
                    f"Rule '{rule.get('name', 'unnamed')}' is disabled, skipping"
                )
                continue

            if self._evaluate_rule_conditions(rule, attributes, flag_key):
                return_value = rule.get("returnValue")
                self.logger.debug(
                    f"Rule '{rule.get('name', 'unnamed')}' matched, returning: {return_value}"
                )
                return return_value

        return None

    def _evaluate_rule_conditions(
        self, rule: Dict[str, Any], attributes: Dict[str, Any], flag_key: str
    ) -> bool:
        """
        Evaluate all conditions in a rule based on the logical operator.

        Args:
            rule: Rule configuration
            attributes: User/context attributes
            flag_key: Flag key for logging

        Returns:
            True if rule conditions are met, False otherwise
        """
        conditions = rule.get("conditions", [])
        if not conditions:
            return False

        logical_operator = LogicalOperator(rule.get("logicalOperator", "AND"))
        rule_name = rule.get("name", "unnamed")

        results = []
        for condition in conditions:
            result = self._evaluate_condition(condition, attributes, flag_key)
            results.append(result)
            attr_disp = condition.get("attribute_key", condition.get("attributeId"))
            self.logger.debug(
                f"Condition in rule '{rule_name}': {attr_disp} {condition.get('operator')} {condition.get('value', condition.get('listValues'))} = {result}"
            )

        if logical_operator == LogicalOperator.AND:
            final_result = all(results)
        else:  # OR
            final_result = any(results)

        self.logger.debug(
            f"Rule '{rule_name}' with {logical_operator.value} operator: {final_result}"
        )
        return final_result

    def _evaluate_condition(
        self, condition: Dict[str, Any], attributes: Dict[str, Any], flag_key: str
    ) -> bool:
        """
        Evaluate a single condition.

        Args:
            condition: Condition configuration
            attributes: User/context attributes
            flag_key: Flag key for logging

        Returns:
            True if condition is met, False otherwise
        """
        attribute_key = condition.get("attribute_key")
        attribute_id = condition.get("attributeId")
        key = attribute_key or attribute_id
        operator = Operator(condition.get("operator"))
        expected_value = condition.get("value")
        list_values = condition.get("listValues", [])

        actual_value = attributes.get(key) if key is not None else None

        if actual_value is None:
            self.logger.debug(
                f"Attribute '{key}' not found in context, condition fails"
            )
            return False

        # Evaluate based on operator
        try:
            if operator == Operator.EQUALS:
                return actual_value == expected_value
            elif operator == Operator.NOT_EQUALS:
                return actual_value != expected_value
            elif operator == Operator.IN:
                return actual_value in list_values
            elif operator == Operator.NOT_IN:
                return actual_value not in list_values
            elif operator == Operator.GREATER_THAN:
                return float(actual_value) > float(expected_value)
            elif operator == Operator.LESS_THAN:
                return float(actual_value) < float(expected_value)
            elif operator == Operator.GREATER_THAN_OR_EQUAL:
                return float(actual_value) >= float(expected_value)
            elif operator == Operator.LESS_THAN_OR_EQUAL:
                return float(actual_value) <= float(expected_value)
            elif operator == Operator.CONTAINS:
                return str(expected_value) in str(actual_value)
            elif operator == Operator.NOT_CONTAINS:
                return str(expected_value) not in str(actual_value)
            else:
                self.logger.warning(f"Unknown operator: {operator}")
                return False
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Error evaluating condition: {e}")
            return False
