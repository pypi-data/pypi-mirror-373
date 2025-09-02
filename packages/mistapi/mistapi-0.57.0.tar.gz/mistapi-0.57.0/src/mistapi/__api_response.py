"""
--------------------------------------------------------------------------------
------------------------- Mist API Python CLI Session --------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistapi_python

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
This module manages API responses
"""

from requests import Response
from requests.structures import CaseInsensitiveDict

from mistapi.__logger import console, logger


class APIResponse:
    """
    Class used to pass API Responses
    """

    def __init__(
        self, response: Response | None, url: str, proxy_error: bool = False
    ) -> None:
        """
        PARAMS
        -----------
        response : requests.Response
            Response from the request
        url : str
            URL of the HTTP Request
        """
        self.raw_data: str = ""
        self.data: dict = {}
        self.url: str = url
        self.next: str | None = None
        self.headers: CaseInsensitiveDict[str] | None = None
        self.status_code: int | None = None
        self.proxy_error: bool = proxy_error

        if response is not None:
            self.headers = response.headers
            self.status_code = response.status_code

            logger.info(
                f"apiresponse:__init__:response status code: {response.status_code}"
            )
            console.debug(f"Response Status Code: {response.status_code}")

            try:
                self.raw_data = str(response.content)
                self.data = response.json()
                self._check_next()
                logger.debug("apiresponse:__init__:HTTP response processed")
                if self.status_code >= 400 or (
                    isinstance(self.data, dict) and self.data.get("error")
                ):
                    logger.error(f"apiresponse:__init__:response = {response}")
                    console.debug(f"Response: {self.data}")
            except Exception as err:
                logger.error(
                    f"apiresponse:__init__:unable to process HTTP Response: \r\n{err}"
                )

    def _check_next(self) -> None:
        logger.debug("apiresponse:_check_next")
        if "next" in self.data:
            self.next = self.data["next"]
            logger.debug(f"apiresponse:_check_next:set next to {self.next}")
        elif self.headers:
            total_str = self.headers.get("X-Page-Total")
            limit_str = self.headers.get("X-Page-Limit")
            page_str = self.headers.get("X-Page-Page")
            if total_str and limit_str and page_str:
                try:
                    total = int(total_str)
                    limit = int(limit_str)
                    page = int(page_str)
                    if limit * page < total:
                        uri = f"/api/{self.url.split('/api/')[1]}"
                        self.next = uri.replace(f"page={page}", f"page={page + 1}")
                        logger.debug(f"apiresponse:_check_next:set next to {self.next}")
                except ValueError:
                    logger.error(
                        f"apiresponse:_check_next:"
                        f"unable to convert total({total_str})/limit({limit_str})/page({page_str}) to int"
                    )
                    logger.error(
                        "apiresponse:_check_next:Exception occurred", exc_info=True
                    )
                    console.error(
                        f"Unable to convert total "
                        f"({total_str})/limit({limit_str})/page({page_str}) to int"
                    )
