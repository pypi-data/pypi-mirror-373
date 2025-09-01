import json
import re

from rhino_health.lib.rest_api.error_parsers.error_parser import ErrorParser

NESTED_MESSAGE_MATCHER = re.compile(r"Error getting [\w\s]+: ReverseRpcError: [\w]+@[\w\s]+: ")


class ReverseRPCErrorParser(ErrorParser):
    """
    Parses the nested reverse rpc errors and returns the underlying error
    """

    def parse(self, api_response):
        try:
            errors = api_response.parsed_response["errors"]
            cleaned_errors = []
            for error in errors:
                try:
                    nested_dataset_response = NESTED_MESSAGE_MATCHER.sub("", error["message"])
                    error_data = json.loads(nested_dataset_response)
                    cleaned_errors.append(error_data.get("message", error_data))
                    error["__parsed"] = True
                except:
                    pass
            return cleaned_errors
        except:
            return None
