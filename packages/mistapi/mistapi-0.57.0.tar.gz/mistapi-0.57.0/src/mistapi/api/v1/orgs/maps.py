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


def importOrgMapsFile(
    mist_session: _APISession,
    org_id: str,
    auto_deviceprofile_assignment: bool | None = None,
    csv: str | None = None,
    file: str | None = None,
    json: dict | None = None,
) -> _APIResponse:
    """
    API doc: https://www.juniper.net/documentation/us/en/software/mist/api/http/api/orgs/maps/import-org-maps

    PARAMS
    -----------
    mistapi.APISession : mist_session
        mistapi session including authentication and Mist host information

    PATH PARAMS
    -----------
    org_id : str

    BODY PARAMS
    -----------
    auto_deviceprofile_assignment : bool
        Whether to auto assign device to deviceprofile by name
    csv : str
        path to the file to upload. CSV file for ap name mapping, optional
    file : str
        path to the file to upload. Ekahau or ibwave file
    json : dict

    RETURN
    -----------
    mistapi.APIResponse
        response from the API call
    """

    multipart_form_data = {
        "auto_deviceprofile_assignment": auto_deviceprofile_assignment,
        "csv": csv,
        "file": file,
        "json": json,
    }
    uri = f"/api/v1/orgs/{org_id}/maps/import"
    resp = mist_session.mist_post_file(uri=uri, multipart_form_data=multipart_form_data)
    return resp
