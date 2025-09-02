"""
--------------------------------------------------------------------------------
------------------------- Mist API Python CLI Session --------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistapi_python

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
This module is providing some functions to simplify Mist API use.
"""

import json
import sys
from typing import Any

from tabulate import tabulate

import mistapi
from mistapi.__api_response import APIResponse as _APIResponse
from mistapi.__logger import console
from mistapi.__models.privilege import Privileges


###########################################
def _search_org(orgs, org_id):
    i = 0
    for org in orgs:
        if org["org_id"] == org_id:
            return i
        i += 1
    return None


def _test_choice(val, val_max):
    try:
        val_int = int(val)
        if val_int >= 0 and val_int <= val_max:
            return val_int
        else:
            return -1
    except ValueError:
        return -2


###########################################
#### DECORATOR
def is_authenticated(func):
    """
    decorator to test if the mistapi.APISession is authenticated
    """

    def wrapper(*args, **kwargs):
        mist_session = args[0]
        if mist_session.get_authentication_status():
            return func(*args, **kwargs)
        else:
            console.critical("Not authenticated... Exiting...")
            console.critical('Please une the "login()" function first...')

    return wrapper


###########################################
#### CLI SELECTIONS
def _forge_privileges(mist_session: mistapi.APISession, msp_id: str) -> Privileges:
    """
    Function to generate user privileges for Orgs belonging to a MSP Account

    PARAMS
    -----------
    mist_session: mistapi.APISession
        mistapi session including authentication and Mist host information
    msp_id : str
        msp_id of the MSP account to use to generate the privileges

    RETURN
    -----------
    list
        List of ORG privileges
    """
    resp = mistapi.api.v1.msps.orgs.listMspOrgs(mist_session, msp_id)
    orgs = mistapi.get_all(mist_session, resp)
    custom_privileges = []
    for org in orgs:
        custom_privileges.append(mist_session.get_privilege_by_org_id(org["id"]))
    return Privileges(custom_privileges)


@is_authenticated
def _select_msp(mist_session: mistapi.APISession) -> Privileges:
    """
    Function to list all the Mist MSPs allowed for the current user
    and ask to pick one. Return the list org ORG privileges based
    on the user selection

    PARAMS
    -----------
    mist_session : mistapi.APISession
        mistapi session including authentication and Mist host information

    RETURN
    -----------
    list
        List of ORG privileges
    """
    msp_accounts = [
        priv for priv in mist_session.privileges if priv.get("scope") == "msp"
    ]
    if len(msp_accounts) == 0:
        return mist_session.privileges
    else:
        msp_accounts = sorted(msp_accounts, key=lambda x: x.get("name").lower())
        while True:
            i = -1
            print("\r\nAvailable MSP Accounts:")
            for privilege in msp_accounts:
                i += 1
                print(f"{i}) {privilege.get('name')} (id: {privilege.get('msp_id')})")
            print()
            print("n) Orgs not linked to an MSP account")
            print()
            resp = input(
                f'\r\nSelect the MSP Account to use (0 to {i}, "n" for None, or "q" to quit): '
            )
            if resp == "q":
                sys.exit(0)
            elif resp.lower() == "n":
                standalone: list = []
                for priv in mist_session.privileges:
                    msp = [
                        msp
                        for msp in msp_accounts
                        if msp.get("msp_id") == priv.get("msp_id", "xyz")
                    ]
                    if not msp:
                        standalone.append(priv)
                return Privileges(standalone)
                # return [priv for priv in mist_session.privileges if not priv.get("msp_id")]
            else:
                tested_val = _test_choice(resp, i)
                if tested_val >= 0:
                    return _forge_privileges(
                        mist_session, msp_accounts[tested_val].get("msp_id")
                    )
                elif tested_val == -1:
                    print(f"{resp} is not part of the possibilities.")
                elif tested_val == -2:
                    print("Only numbers are allowed.")


@is_authenticated
def select_org(mist_session: mistapi.APISession, allow_many=False) -> list:
    """
    Function to list all the Mist Orgs allowed for the current user
    and ask to pick one or many. Return the Org ID(s) of the selected
    org(s)

    PARAMS
    -----------
    mist_session : mistapi.APISession
        mistapi session including authentication and Mist host information
    allow_many : bool
        If user is allowed to select multiple orgs. Default is False

    RETURN
    -----------
    list
        list of the selected Org ID(s)
    """
    data = _select_msp(mist_session)
    data = [d for d in data if d.get("name")]
    data = sorted(data, key=lambda x: x.get("name").lower())
    while True:
        i = -1
        org_ids: list[str] = []
        resp_ids: list[str] = []
        print("\r\nAvailable organizations:")
        for privilege in data:
            if (
                privilege.get("scope") == "org"
                and privilege.get("org_id") not in org_ids
            ):
                i += 1
                org_ids.append(privilege.get("org_id"))
                print(f"{i}) {privilege.get('name')} (id: {privilege.get('org_id')})")

        orgs_with_sites: list[dict] = []
        for privilege in data:
            if (
                privilege.get("scope") == "site"
                and privilege.get("org_id") not in org_ids
            ):
                index = _search_org(orgs_with_sites, privilege.get("org_id"))
                if index is None:
                    i += 1
                    org_ids.append(privilege.get("org_id"))
                    print(
                        f"{i}) {privilege.get('name')} (id: {privilege.get('org_id')})"
                    )
                    orgs_with_sites.append(
                        {
                            "org_id": privilege.get("org_id"),
                            "name": privilege.get("name"),
                            "sites": [
                                {
                                    "site_id": privilege.get("site_id"),
                                    "name": privilege.get("name"),
                                }
                            ],
                        }
                    )
                else:
                    orgs_with_sites[index]["sites"].append(
                        {
                            "site_id": privilege.get("site_id"),
                            "name": privilege.get("name"),
                        }
                    )

        if allow_many:
            resp = input(
                f'\r\nSelect an Org (0 to {i}, "0,1" for sites 0 and 1,'
                f' "a" for all, "b" for back or "q" to quit): '
            )
        else:
            resp = input(f'\r\nSelect an Org (0 to {i}, "b" for back or "q" to quit): ')
        if resp.lower() == "b":
            return select_org(mist_session)
        elif resp.lower() == "q":
            sys.exit(0)
        elif resp.lower() == "a" and allow_many:
            return org_ids
        else:
            selection_validated = True
            resp_splitted = resp.split(",")
            if not allow_many and len(resp_splitted) > 1:
                print(f"Only one org is allowed, you selected {len(resp_splitted)}")
                return select_org(mist_session, allow_many)
            for num in resp_splitted:
                tested_val = _test_choice(num, i)
                if tested_val >= 0:
                    resp_ids.append(org_ids[tested_val])
                if tested_val == -1:
                    print(f"{num} is not part of the possibilities.")
                    selection_validated = False
                if tested_val == -2:
                    print("Only numbers are allowed.")
                    selection_validated = False
            if selection_validated:
                return resp_ids


@is_authenticated
def select_site(
    mist_session: mistapi.APISession, org_id=None, allow_many=False
) -> list:
    """
    Function to list all the Sites from a Mist Org and ask user to pick one
    or many. Return the Site ID(s) of the selected site(s)

    PARAMS
    -----------
    mist_session : mistapi.APISession
        mistapi session including authentication and Mist host information
    org_id : str
        Org ID to request
    allow_many : bool
        If user is allowed to select multiple orgs. Default is False

    RETURN
    -----------
    list
        list of the selected Site ID(s)
    """
    i = -1
    site_ids = []
    site_choices = []
    resp_ids = []
    org_access = False

    if org_id is None:
        org_id = select_org(mist_session)[0]

    for privilege in mist_session.privileges:
        if privilege.get("scope") == "org" and privilege.get("org_id") == org_id:
            org_access = True
        if privilege.get("scope") == "site" and privilege.get("org_id") == org_id:
            site_choices.append(
                {"id": privilege.get("site_id"), "name": privilege.get("name")}
            )

    if not site_choices or org_access:
        response = mistapi.api.v1.orgs.sites.listOrgSites(mist_session, org_id)
        site_choices = mistapi.get_all(mist_session, response)

    site_choices = sorted(site_choices, key=lambda x: x["name"].lower())
    print("\r\nAvailable sites:")
    for site in site_choices:
        i += 1
        site_ids.append(site["id"])
        print(f"{i}) {site['name']} (id: {site['id']})")
    if allow_many:
        resp = input(
            f'\r\nSelect a Site (0 to {i}, "0,1" for sites 0 and 1, "a" for all, or q to exit): '
        )
    else:
        resp = input(f"\r\nSelect a Site (0 to {i}, or q to exit): ")

    if resp.lower() == "q":
        sys.exit(0)
    elif resp.lower() == "a" and allow_many:
        return site_ids
    else:
        splitted_resp = resp.split(",")
        if not allow_many and len(splitted_resp) > 1:
            print(f"Only one site is allowed, you selected {len(splitted_resp)}")
            return select_site(mist_session, org_id, allow_many)
        for num in splitted_resp:
            tested_val = _test_choice(num, i)
            if tested_val >= 0:
                resp_ids.append(site_choices[tested_val]["id"])
            if tested_val == -1:
                print(f"{num} is not part of the possibilities.")
                return select_site(mist_session, org_id, allow_many)
            if tested_val == -2:
                print("Only numbers are allowed.")
                return select_site(mist_session, org_id, allow_many)
        return resp_ids


###########################################
def extract_field(json_data: dict, field: str) -> Any:
    """
    function to extract the value of a key from complex JSON object

    PARAMS
    -----------
    json_data : dict
        the JSON object containing the value
    field : str
        the full path of the key we are looking for.
        e.g. parent.child.key

    RETURNS
    -----------
    any
        the value of the key, or "N/A" if the key is not found
    """
    split_field = field.split(".")
    cur_field = split_field[0]
    next_fields = ".".join(split_field[1:])
    if cur_field in json_data:
        if len(split_field) > 1:
            return extract_field(json_data[cur_field], next_fields)
        else:
            return json_data[cur_field]
    else:
        return "N/A"


def save_to_csv(
    csv_file: str, data: list, fields: list, csv_separator: str = ","
) -> None:
    """
    Write a list of lists in a CSV file

    PARAMS
    -----------
    csv_file : str
        path to the CSV file where to save the data
    data : list
        list containing the lists to save
    fields : list
        list of the columns headers
    csv_separator : str
        character to use to separate the cells. Default is ","
    """
    print("saving to file...")
    with open(csv_file, "w") as f:
        for column in fields:
            f.write(f"{column}{csv_separator}")
        f.write("\r\n")
        for row in data:
            for field in row:
                if field is None:
                    f.write("")
                else:
                    f.write(field)
                f.write(csv_separator)
            f.write("\r\n")


def _json_to_array(json_data: dict, fields: list) -> list:
    data = []
    for field in fields:
        data.append(json_data.get(field, ""))
    return data


def display_list_of_json_as_table(data_list: list, fields: list) -> None:
    """
    Function using tabulate to display a list as a table

    PARAMS
    -----------
    data_list : list
        list to display
    fields : list
        List of fields to display.
    """
    table = []
    for data in data_list:
        table.append(_json_to_array(data, fields))
    print(tabulate(table, headers=fields))


def pretty_print(response: _APIResponse, fields: list | None = None) -> None:
    """
    Function using tabulate to display a mistapi Response content as a table

    PARAMS
    -----------
    response : _APIResponse
        Response from a mistapi Request to the Mist Cloud
    fields : list
        List of fields to display.
        If None, the function automatically detects all the available fields
    """
    if hasattr(response, "data") and "result" in response.data:
        data = response.data["result"]
    elif hasattr(response, "data"):
        data = response.data
    else:
        data = response
    print("")
    if isinstance(data, list):
        if fields is None:
            fields = ["keys"]
        print(tabulate(data, headers=fields))
    elif isinstance(data, dict):
        print(json.dumps(data, sort_keys=True, indent=4, separators=(",", ": ")))
    else:
        print(data)
    print("")
