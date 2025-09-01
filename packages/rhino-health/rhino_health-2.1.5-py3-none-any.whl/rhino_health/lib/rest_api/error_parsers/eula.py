from rhino_health.lib.rest_api.error_parsers.error_parser import ErrorParser

EULA_ERROR_MESSAGES = [
    "Updated EULA needs to be accepted",
    "EULA not accepted",
]


class EULAErrorParser(ErrorParser):
    """
    Parses the error message for EULA not signed and returns a message for the user to sign in on their browser
    """

    def parse(self, api_response):
        try:
            # TODO: We should introduce error codes or error categories in the cloud backend to avoid needing to check
            # specific messages
            errors = api_response.parsed_response.get("errors")
            if api_response.status_code == 401 and (
                (
                    isinstance(errors, list)
                    and any(
                        [
                            error.get("message") in EULA_ERROR_MESSAGES
                            for error in api_response.parsed_response["errors"]
                        ]
                    )
                )
                or api_response.parsed_response.get("detail") in EULA_ERROR_MESSAGES
            ):
                for error in errors or []:
                    error["__parsed"] = True
                return [
                    f"Please login to {api_response.session.rhino_cloud.get_dashboard_url()} and accept the EULA before proceeding"
                ]
        except:
            pass
        return None
