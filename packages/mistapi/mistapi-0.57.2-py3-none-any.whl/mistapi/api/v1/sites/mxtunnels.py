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


def preemptSitesMxTunnel(
    mist_session: _APISession, site_id: str, mxtunnel_id: str
) -> _APIResponse:
    """
    API doc: https://www.juniper.net/documentation/us/en/software/mist/api/http/api/utilities/mxedge/preempt-sites-mx-tunnel

    PARAMS
    -----------
    mistapi.APISession : mist_session
        mistapi session including authentication and Mist host information

    PATH PARAMS
    -----------
    site_id : str
    mxtunnel_id : str

    RETURN
    -----------
    mistapi.APIResponse
        response from the API call
    """

    uri = f"/api/v1/sites/{site_id}/mxtunnels/{mxtunnel_id}/preempt_aps"
    resp = mist_session.mist_post(uri=uri)
    return resp
