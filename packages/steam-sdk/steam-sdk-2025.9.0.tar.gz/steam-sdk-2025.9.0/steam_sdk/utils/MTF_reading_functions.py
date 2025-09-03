import requests
import pandas as pd
import numpy as np
import os

def read_MTF_equipment(credentials_path: str, eq_code: str):
    """
    Retrieves custom fields data from a CMMSX MTF equipment API endpoint
    and returns a dictionary of custom field labels and their values.

    Args:
        credentials_path (str): The file path to the credentials file
            containing the CERN login username and password, separated
            by a newline.
        eq_code (str): The equipment code for the MTF equipment to retrieve
            custom fields data for.

    Returns:
        df (pandas Dataframe): A Dataframe of custom field labels and
            their corresponding values and units for the specified MTF equipment.

    Raises:
        Exception: If the path to the credential path leads to no valid file.
        Exception: If errors occur in the returned dataset from the API endpoint.
    """
    # raise exception if path is not specified
    if not os.path.isfile(credentials_path):
        raise Exception(f'Path to MTF credential file is invalid! Check if you have the entry MTF_credentials_path in '
                        f'your settings.xxxx.yaml file. If you dont have a MTF credential file contact the steam team.')

    # Parse the credentials file and set up headers for authentication
    with open(credentials_path, 'r') as file:
        username = file.readline().strip()
        password = file.readline().strip()
    headers = {"INFOR_USER": username, "INFOR_PASSWORD": password}

    # Make the request to the MTF equipment API endpoint
    session = requests.Session()
    session.headers.update(headers)
    base_url = "https://cmmsx.cern.ch/WSHub/REST/apis"
    result = session.get(base_url + f"/equipment/{eq_code}")
    result.raise_for_status()
    data = result.json()

    # Check for errors in the returned dataset
    if data["errors"]:
        raise Exception("Errors in returned dataset: " + str(data["errors"]))
    data = data['data']

    # # Extract custom fields data and into a dictionary
    # dict_customFields = {}
    # for custom_field in data['customField']:
    #     dict_customFields[custom_field['label']] = custom_field['value']

    # parse data into pandas dataframe
    custom_fields = data['customField']
    field_table = [(c['label'], c['value'], c['uom']) for c in custom_fields]
    df = pd.DataFrame(field_table, columns=["Field", "Value", "Unit"])

    # convert the "Values" column to float
    df['Value'] = df['Value'].replace('', np.nan)  # replace empty str with NaN
    df['Value'] = df['Value'].astype(float)

    return df


