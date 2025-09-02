import json


class ImportConfigurations:
    def __init__(
        self,
        threads=1,
        batch=1000,
        skip_first_rows=1,
        table_lock=False,
        no_type_check=False,
        record_delimiter="\n",
        field_delimiter=";",
        optionally_enclosed_by='"',
        escape_character="\\",
        date_format="YYYY-MM-DD",
        time_format="HH24:MI:SS",
        timestamp_format="YYYY-MM-DD HH24:MI:SS.FF7",
        fail_on_invalid_data=False,
    ):
        self.threads = threads
        self.batch = batch
        self.skip_first_rows = skip_first_rows
        self.table_lock = table_lock  ## CURRENTLY NOT SUPPORTED
        self.no_type_check = no_type_check
        self.record_delimiter = record_delimiter
        self.field_delimiter = field_delimiter
        self.optionally_enclosed_by = optionally_enclosed_by
        self.escape_character = escape_character
        self.date_format = date_format
        self.time_format = time_format
        self.timestamp_format = timestamp_format
        self.fail_on_invalid_data = fail_on_invalid_data  ## CURRENTLY NOT SUPPORTED

    def to_dict(self):
        return {
            "threads": self.threads,
            "batch": self.batch,
            "skip_first_rows": self.skip_first_rows,
            "table_lock": self.table_lock,
            "no_type_check": self.no_type_check,
            "record_delimiter": self.record_delimiter,
            "field_delimiter": self.field_delimiter,
            "optionally_enclosed_by": self.optionally_enclosed_by,
            "escape_character": self.escape_character,
            "date_format": self.date_format,
            "time_format": self.time_format,
            "timestamp_format": self.timestamp_format,
            "fail_on_invalid_data": self.fail_on_invalid_data,
        }

    def to_json(self):
        return json.dumps(self.to_dict())
