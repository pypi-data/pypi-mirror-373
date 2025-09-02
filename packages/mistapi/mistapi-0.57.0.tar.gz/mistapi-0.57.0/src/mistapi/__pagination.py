"""
--------------------------------------------------------------------------------
------------------------- Mist API Python CLI Session --------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistapi_python

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from mistapi import APISession as _APISession
from mistapi.__api_response import APIResponse as _APIResponse


def get_next(mist_session: _APISession, response: _APIResponse) -> _APIResponse | None:
    """
    Get the next page when previous response does not include all the items

    PARAMS
    -----------
    mist_session :  mistapi.APISession
        mistapi session including authentication and Mist host information
    response : mistapi.APIResponse
        mistapi previous response to use

    RETURN
    -----------
    mistapi.APIResponse
        response from the API call passed in parameter
    """
    if response.next:
        return mist_session.mist_get(response.next)
    else:
        return None


def get_all(mist_session: _APISession, response: _APIResponse) -> list:
    """
    Retrieve and return all the items after a first request

    PARAMS
    -----------
    mist_session :  mistapi.APISession
        mistapi session including authentication and Mist host information
    response : mistapi.APIResponse
        mistapi previous response to use

    RETURN
    -----------
    list
        list of all the items
    """
    data: list = []
    if isinstance(response.data, list):
        data = list(response.data)
        while response.next:
            tmp = get_next(mist_session, response)
            if tmp:
                response = tmp
                data += response.data
    elif isinstance(response.data, dict) and "results" in response.data:
        data = response.data["results"].copy()
        while response.next:
            tmp = get_next(mist_session, response)
            if tmp:
                response = tmp
                data += response.data["results"]
    return data
