from rhino_health.lib.rest_api.error_parsers.error_parser import ErrorParser


class GeneralErrorParser(ErrorParser):
    """
    Parses a general Backend
    """

    def parse(self, api_response):
        try:
            errors = api_response.parsed_response["errors"]
            error_messages = []
            for error in errors:
                if error.get("__parsed", False):
                    continue
                try:
                    error_messages.append(error["message"])
                    error["__parsed"] = True
                except:
                    pass
            return error_messages
        except:
            return None
