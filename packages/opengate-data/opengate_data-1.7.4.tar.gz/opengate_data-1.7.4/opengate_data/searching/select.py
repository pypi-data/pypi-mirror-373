from opengate_data.utils.utils import validate_type


class SelectBuilder:
    """ Select Builder """

    def __init__(self):
        self._select_fields = []
        self._mode = None

    def add(self, name: str, fields=None):
        """
        Adds a field or a named field group to the select clause.

        There are two exclusive modes of use:

        - **Simple mode** (for Time series and Data sets):
            Use `.add("field_name")` to include raw fields.

        - **Extended mode** (for structured searches):
            Use `.add(name, fields)` where `fields` is a list of:
                - strings (field names), or
                - tuples like (field, alias)

        Args:
            name (str): The field name (simple mode) or data source name (extended mode).
            fields (list, optional): A list of fields or (field, alias) tuples.

        Returns:
            SelectBuilder: Returns itself to allow for method chaining.

        Example (simple mode):
            SelectBuilder().add("Gross volume").add("High temperature")

        Example (extended mode):
            SelectBuilder().add("provision.device.identifier", [
                ("value", "id"),
                ("date", "date_alias")
            ]).add("provision.device.location", ["value.postal"])

        Note:
        You cannot mix both modes in the same instance.
        """
        validate_type(name, str, "name")

        # --- Simple Mode (Datasets y timeseries)  ---

        if fields is None:
            if self._mode is None:
                self._mode = "simple"
            elif self._mode != "simple":
                raise ValueError("Cannot mix simple and extended select modes in the same SelectBuilder")

            if name not in self._select_fields:
                self._select_fields.append(name)
            return self

        # --- Extended Mode (Rests of searching)  ---

        if self._mode is None:
            self._mode = "extended"
        elif self._mode != "extended":
            raise ValueError("Cannot mix simple and extended select modes in the same SelectBuilder")

        validate_type(fields, list, "fields")
        processed_fields = []

        for field in fields:
            if isinstance(field, str):
                processed_fields.append({"field": field})
            elif isinstance(field, tuple):
                validate_type(field[0], str, "field[0]")
                if len(field) > 1:
                    validate_type(field[1], str, "field[1]")
                    processed_fields.append({"field": field[0], "alias": field[1]})
                else:
                    processed_fields.append({"field": field[0]})
            else:
                raise ValueError("Each field must be a string or a tuple with optional alias")

        existing_entry = next((e for e in self._select_fields if e["name"] == name), None)

        if existing_entry:
            for pf in processed_fields:
                if pf not in existing_entry["fields"]:
                    existing_entry["fields"].append(pf)
        else:
            self._select_fields.append({"name": name, "fields": processed_fields})

        return self

    def build(self):
        """
        Returns the built select list.

        Returns:
            list: List of field names or list of dicts depending on the mode.
        """
        if not self._select_fields:
            raise ValueError("No select criteria have been added")
        return self._select_fields
