"""SearchBuilder"""

from opengate_data.utils.utils import validate_type, set_method_call

LIMIT_START_DEF_VALUE = 1
LIMIT_SIZE_DEF_VALUE = 1000


class SearchBuilder:
    """ Search Builder """

    def __init__(self):
        self.body_data: dict = {}
        self.format_data: str | None = None
        self.method_calls: list = []

    def with_filter(self, filter_data: dict) -> 'SearchBuilder':
        """
        Adds a filter to the search.

        Args:
            filter_data (Union[dict, FilterBuilder]): The filter data to apply. Can be a dictionary or a FilterBuilder instance.

        Returns:
            SearchBuilder: Returns itself to allow for method chaining.

        Example:
            search_builder.with_filter(filter_builder.build())
            search_builder.with_filter({
                "and": [
                    {"eq": {"device.operationalStatus": "NORMAL"}},
                    {"like": {"device.communicationModules[].mobile.imei": "351873000102290"}}
                ]
            })
        """
        validate_type(filter_data, dict, "Filter")
        self.body_data["filter"] = filter_data
        return self

    @set_method_call
    def with_select(self, select_data: list[dict]) -> 'SearchBuilder':
        """
        Adds selection criteria to the search.

        Args:
            select_data (list[dict] | SelectBuilder): The selection criteria to apply. Can be a list of dictionaries or a SelectBuilder instance.

        Returns:
            SearchBuilder: Returns itself to allow for method chaining.

        """
        validate_type(select_data, list, "Select")
        self.body_data["select"] = select_data
        return self

    @set_method_call
    def with_limit(self, size: int, start: int = None) -> 'SearchBuilder':
        """
        Adds pagination parameters to the search.

        Args:
            size (int): The number of entities to retrieve per page. Limit size value 1000
            start (int, optional): Page number you request. By default, is 1.

        Returns:
            SearchBuilder: Returns itself to allow for method chaining.

        Example:
            search_builder.with_limit(1000, 2)
        """
        validate_type(size, int, "size")
        if start is None or not isinstance(start, int) or start < 1:
            start = LIMIT_START_DEF_VALUE
        else:
            validate_type(size, int, "start")

        if size > LIMIT_SIZE_DEF_VALUE:
            raise ValueError("Size must be 1000 or less")
        self.body_data.setdefault("limit", {}).update({"start": start, "size": size})
        return self

    def add_by_group(self, field_name: str) -> 'SearchBuilder':
        """
        Adds a field to the group.

        Args:
            field_name (str): The name of the field to group by.

        Returns:
            SearchBuilder: Returns itself to allow for method chaining.

        Example:
            builder.add_by_group("provision.device.model")
            builder.add_by_group("provision.device.software")
        """
        validate_type(field_name, str, "field_name")
        self.body_data.setdefault("group", {"parameters": []}).get("parameters").append({"name": field_name})
        return self

    def add_sort_by(self, field_name: str, order: str) -> 'SearchBuilder':
        """
        Adds a field to the sort.

        Args:
            field_name (str): The name of the field to sort by.
            order (str): The order of sorting, either 'ASCENDING' or 'DESCENDING'.

        Returns:
            SearchBuilder: Returns itself to allow for method chaining.

        Example:
            builder.add_sort_by("datapoints._current.at", "DESCENDING")
            builder.add_sort_by("devices._current.at", "ASCENDING")
        """
        validate_type(field_name, str, "field_name")
        validate_type(order, str, "order")
        if order not in ["ASCENDING", "DESCENDING"]:
            raise ValueError("Order must be 'ASCENDING' or 'DESCENDING'")
        self.body_data.setdefault("sort", {"parameters": []}).get("parameters").append(
            {"name": field_name, "type": order})
        return self
