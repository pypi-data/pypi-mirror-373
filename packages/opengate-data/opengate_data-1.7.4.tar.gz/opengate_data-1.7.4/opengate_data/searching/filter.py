import json
from opengate_data.utils.utils import validate_type
from opengate_data.utils.expressions import Expressions


class FilterBuilder(Expressions):
    """ Filter Builder """
    def __init__(self):
        super().__init__()
        self.filter = {}
        self.current_condition = None
        self.method_calls = []

    def _add_condition(self, condition):
        self.current_condition = condition
        return self

    def and_(self, *conditions):
        """
        Combines conditions using the logical AND operator.

        Args:
            *conditions: The conditions to combine.

        Returns:
            FilterBuilder: Returns itself to allow for method chaining.

        Example:
            builder.and_(eq("device.operationalStatus", "NORMAL"),
                like("device.name", "device_.*")
            )
        """
        for condition in conditions:
            validate_type(condition, (dict, Expressions), "condition")

        if self.current_condition:
            self.filter["and"] = [self.current_condition] + [
                condition if isinstance(condition, dict) else condition.build() for condition in conditions]
            self.current_condition = None
        else:
            self.filter["and"] = [
                condition if isinstance(condition, dict) else condition.build() for condition in conditions]
        return self

    def or_(self, *conditions):
        """
        Combines conditions using the logical OR operator.

        Args:
            *conditions: The conditions to combine.

        Returns:
            FilterBuilder: Returns itself to allow for method chaining.

        Example:
            builder.or_(eq("device.operationalStatus", "NORMAL"),
                like("device.name", "device_.*")
            )
        """
        for condition in conditions:
            validate_type(condition, (dict, Expressions), "condition")

        if self.current_condition:
            self.filter["or"] = [self.current_condition] + [
                condition if isinstance(condition, dict) else condition.build() for condition in conditions]
            self.current_condition = None
        else:
            self.filter["or"] = [
                condition if isinstance(condition, dict) else condition.build() for condition in conditions]
        return self

    def build(self):
        """
        Builds the final filter.

        Returns:
            dict: The final filter.

        Raises:
            ValueError: If there is an incomplete condition.

        Example:
            builder.build()
        """
        if self.current_condition:
            raise ValueError("Incomplete filter: missing 'and_' or 'or_'")
        return self.filter
