from .utils import validate_type


class Expressions:
    @staticmethod
    def eq(field, value):
        """
        Adds an equality condition to the filter.

        Args:
            field (str): The field to compare.
            value (any): The value to compare against.

        Returns:
            dict: The equality condition.

        Example:
            eq("device.operationalStatus", "NORMAL")
        """
        validate_type(field, str, "Field eq")
        return {"eq": {field: value}}

    @staticmethod
    def neq(field, value):
        """
        Adds a not-equal condition to the filter.

        Args:
            field (str): The field to compare.
            value (any): The value to compare against.

        Returns:
            dict: The not-equal condition.

        Example:
            neq("device.operationalStatus", "ERROR")
        """
        validate_type(field, str, "Field neq")
        return {"neq": {field: value}}

    @staticmethod
    def like(field, value):
        """
        Adds a like condition to the filter.

        Args:
            field (str): The field to compare.
            value (str): The regex pattern to match.

        Returns:
            dict: The like condition.

        Example:
            like("device.name", "device_.*")
        """
        validate_type(field, str, "Field like")
        validate_type(value, str, "Value like")
        return {"like": {field: value}}

    @staticmethod
    def gt(field, value):
        """
        Adds a greater-than condition to the filter.

        Args:
            field (str): The field to compare.
            value (any): The value to compare against.

        Returns:
            dict: The greater-than condition.

        Example:
            gt("device.batteryLevel", 50)
        """
        validate_type(field, str, "Field gt")
        return {"gt": {field: value}}

    @staticmethod
    def lt(field, value):
        """
        Adds a less-than condition to the filter.

        Args:
            field (str): The field to compare.
            value (any): The value to compare against.

        Returns:
            dict: The less-than condition.

        Example:
            lt("device.batteryLevel", 20)
        """
        validate_type(field, str, "Field lt")
        return {"lt": {field: value}}

    @staticmethod
    def gte(field, value):
        """
        Adds a greater-than-or-equal condition to the filter.

        Args:
            field (str): The field to compare.
            value (any): The value to compare against.

        Returns:
            dict: The greater-than-or-equal condition.

        Example:
            gte("device.batteryLevel", 80)
        """
        validate_type(field, str, "Field gte")
        return {"gte": {field: value}}

    @staticmethod
    def lte(field, value):
        """
        Adds a less-than-or-equal condition to the filter.

        Args:
            field (str): The field to compare.
            value (any): The value to compare against.

        Returns:
            dict: The less-than-or-equal condition.

        Example:
            lte("device.batteryLevel", 30)
        """
        validate_type(field, str, "Field lte")
        return {"lte": {field: value}}

    @staticmethod
    def in_(field, values):
        """
        Adds an in condition to the filter.

        Args:
            field (str): The field to compare.
            values (list): The list of values to compare against.

        Returns:
            dict: The in condition.

        Example:
            in_("device.name", ["device_1", "device_2"])
        """
        validate_type(field, str, "Field in")
        validate_type(values, list, "Value in")
        return {"in": {field: values}}

    @staticmethod
    def nin(field, values):
        """
        Adds a not-in condition to the filter.

        Args:
            field (str): The field to compare.
            values (list): The list of values to compare against.

        Returns:
            dict: The not-in condition.

        Example:
            nin("device.name", ["device_3", "device_4"])
        """
        validate_type(field, str, "Field nin")
        validate_type(values, list, "Value nin")
        return {"nin": {field: values}}

    @staticmethod
    def exists(field, value):
        """
        Adds an existed condition to the filter.

        Args:
            field (str): The field to check for existence.

        Returns:
            dict: The existed condition.
            value (any): The value to compare against.

        Example:
            exists("device.location", False)
        """
        validate_type(field, str, "Field exists")
        return {"exists": {field: value}}
