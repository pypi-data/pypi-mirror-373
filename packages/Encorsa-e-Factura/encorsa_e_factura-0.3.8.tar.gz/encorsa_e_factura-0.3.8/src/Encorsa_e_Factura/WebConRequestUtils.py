import json
import traceback
import requests

try:
    from .XMLUtils import *
except ImportError:
    from XMLUtils import *


def create_webcon_body(parameters, xml_b64, pdf_b64, xml_file_data, id, cui, template_xml_path, wfd_id_duplicate, namespaces, document_type, id_anaf, iso_data_creare):

    processor = XMLProcessor(template_xml_path, xml_file_data, namespaces)
    all_lists_data, extracted_data = processor.process_xml()

    item_lists_json = create_list_of_dicts(all_lists_data)
    form_fields_json = create_form_filed_json(extracted_data)

    form_fields_json.extend([
        {
            "guid": parameters['id_field_guid'],
            "svalue": id
        },
        {
            "guid": parameters['cui_field_guid'],
            "svalue": cui
        }
    ])

    body = {
        "workflow": {
            "guid": parameters['webcon_wfid'],
        },
        "formType": {
            "guid": parameters['webcon_wfdid'],
        },
        "formFields": form_fields_json,
        "itemLists": item_lists_json,
        "attachments": [
            {
                "name": "fisierXML.xml",
                "content": xml_b64
            },
            {
                "name": "fisierPDF.pdf",
                "content": pdf_b64
            }
        ],
        "businessEntity": {
            "id": parameters['webcon_bentity']
        }
    }

    if "webcon_parent_wfdid" in parameters and parameters['webcon_parent_wfdid'] is not None and parameters['webcon_parent_wfdid'] not in ['', 0]:
        body["parentInstanceId"] = parameters['webcon_parent_wfdid']

    add_value_to_form_field(
        parameters, "duplicate_wfdid_field_guid", body, wfd_id_duplicate)
    add_value_to_form_field(
        parameters, "tipInregistrare_Nota_sau_Factura", body, document_type)
    add_value_to_form_field(parameters, "ID_Descarcare_ANAF", body, id_anaf)
    add_value_to_form_field(
        parameters, "Data_Creare_ANAF", body, iso_data_creare)

    return body


def add_value_to_form_field(parameters, parameter_key, body, value):
    if value is None:
        value = ''

    value = str(value)

    if parameter_key in parameters and parameters[parameter_key] is not None and parameters[parameter_key] not in ['', 0]:
        found = False
        for body_field in body["formFields"]:
            if body_field["guid"] == parameters[parameter_key]:
                body_field["svalue"] = value
                found = True
                break
        if not found:
            body["formFields"].append(
                {"guid": parameters[parameter_key], "svalue": value})


def create_list_of_dicts(data_dict):
    result_list = []
    for item_list_guid, rows in data_dict.items():
        item_list_wrapper = {}
        item_list_wrapper['guid'] = item_list_guid
        row_lists = []
        for row in rows:
            row_dict = {}
            cells_list = []
            for cell_guid, cell_value in row.items():  # Iterate over the items in the row dictionary
                cell_dict = {
                    'guid': cell_guid, 'svalue': cell_value if cell_value is not None else ''}
                cells_list.append(cell_dict)
            row_dict['cells'] = cells_list
            row_lists.append(row_dict)
        item_list_wrapper['rows'] = row_lists
        result_list.append(item_list_wrapper)
    return result_list


def create_form_filed_json(extracted_data):
    form_fields = []
    for key, value in extracted_data.items():
        field = {'guid': key, 'svalue': value if value is not None else ''}
        form_fields.append(field)
    return form_fields


"""
Această funcție obține un token de autentificare de la serviciul WebCon
"""
def get_webcon_token(base_url, client_id, client_secret):
    try:
        # Step 1: Fetch available API versions
        versions_url = f"{base_url}/api/data"
        response = requests.get(versions_url, proxies={"http": None, "https": None})
        response.raise_for_status()

        api_versions = response.json().get("apiVersions", [])
        if not api_versions:
            print("Error at getting WebCon TOKEN: No API versions returned from server.")
            raise Exception("No API versions returned from server.")

        # Step 2: Find minimum version (ignoring 'beta')
        numeric_versions = [
            float(v["version"]) for v in api_versions if v["version"] != "beta"
        ]
        if not numeric_versions:
            print("Error at getting WebCon TOKEN: No numeric API versions found.")
            raise Exception("No numeric API versions found.")

        min_version = min(numeric_versions)

        # Step 3: Decide login method
        if min_version < 5.0:
            # Legacy login
            login_url = f"{base_url}/api/login"
            headers = {"Content-Type": "application/json"}
            payload = {"clientId": client_id, "clientSecret": client_secret}

            resp = requests.post(
                login_url, headers=headers, data=json.dumps(payload), proxies={"http": None, "https": None}
            )
            if resp.status_code != 200:
                print(f"Error at getting WebCon TOKEN: HTTP {resp.status_code} - {resp.text}")
                raise Exception(f"HTTP {resp.status_code} - {resp.text}")

            token = resp.json().get("token")
            if not token:
                print("Error at getting WebCon TOKEN: Legacy login response does not contain 'token'.")
                raise Exception("Legacy login response does not contain 'token'.")
            return token

        else:
            # OAuth2 login
            token_url = f"{base_url}/api/oauth2/token"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            payload = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            }

            resp = requests.post(
                token_url, headers=headers, data=payload, proxies={"http": None, "https": None}
            )
            if resp.status_code != 200:
                print(f"Error at getting WebCon TOKEN: HTTP {resp.status_code} - {resp.text}")
                raise Exception(f"HTTP {resp.status_code} - {resp.text}")

            access_token = resp.json().get("access_token")
            if not access_token:
                print("Error at getting WebCon TOKEN: OAuth2 login response does not contain 'access_token'.")
                raise Exception("OAuth2 login response does not contain 'access_token'.")
            return access_token

    except Exception as e:
        print(f"Error at getting WebCon TOKEN: {str(e)}")
        raise Exception(f"Error at getting WebCon TOKEN: {str(e)}")



def create_invoice_instance(parameters, token, body):
    proxies = {"http": None, "https": None}

    try:
        # Step 1: Get available API versions
        versions_url = f"{parameters['webcon_base_url']}/api/data"
        resp_versions = requests.get(versions_url, proxies=proxies)
        if resp_versions.status_code != 200:
            print(f"Error at getting WebCon API versions: HTTP {resp_versions.status_code} - {resp_versions.text}")
            raise Exception(f"Failed to fetch API versions: {resp_versions.text}")

        api_versions = resp_versions.json().get("apiVersions", [])
        if not api_versions:
            print("Error at getting WebCon API versions: No versions returned")
            raise Exception("No API versions returned from server.")

        # Step 2: Pick maximum numeric version
        numeric_versions = [float(v["version"]) for v in api_versions if v["version"] != "beta"]
        if not numeric_versions:
            print("Error at getting WebCon API versions: No numeric versions found")
            raise Exception("No numeric API versions found.")

        max_version = str(max(numeric_versions))

        # Step 3: Build URL with max version
        url = (
            f"{parameters['webcon_base_url']}/api/data/{max_version}/db/"
            f"{parameters['webcon_dbid']}/elements?path={parameters['webcon_path']}"
            f"&mode={parameters['webcon_mode']}"
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        # Step 4: Call WebCon API
        response = requests.post(url, headers=headers, data=json.dumps(body), proxies=proxies)

        if response.status_code == 200:
            if "json" not in response.headers.get("Content-Type", "").lower():
                error_message = (
                    "Failed to create WebCon invoice instance. The response is not in JSON format\n"
                    f"Response: {response.text}\n"
                    f"Headers: {response.headers}\n"
                    f"Status code: {response.status_code}\n"
                )
                print(error_message)
                raise Exception(error_message)
            return response.json()
        else:
            error_message = (
                "Failed to create WebCon invoice instance.\n"
                f"Response: {response.text}\n"
                f"Headers: {response.headers}\n"
                f"Status code: {response.status_code}\n"
            )
            if "json" in response.headers.get("Content-Type", "").lower():
                try:
                    error_message += f"JSON: {response.json()}\n"
                except Exception:
                    pass
            print(error_message)
            raise Exception(error_message)

    except Exception as e:
        error_message = (
            f"Failed to create WebCon invoice instance. An unexpected error occurred: {str(e)}\n"
            f"Body: {body}\n"
        )
        detailed_error = traceback.format_exc()
        print(error_message + "\n" + detailed_error)
        raise Exception(error_message + "\n" + detailed_error)


"""
Functia trebuie sa isi ia datele dintr-un raport cu facturi care
contine numai doua coloane: ID-factura si CUI, fara a schimba ordinea lor
"""
def check_if_invoice_exists(parameters, token, invoice_id, supplier_company_id):
    proxies = {"http": None, "https": None}

    try:
        # Step 1: Get available API versions
        versions_url = f"{parameters['webcon_base_url']}/api/data"
        resp_versions = requests.get(versions_url, proxies=proxies)
        if resp_versions.status_code != 200:
            print(f"Error at getting WebCon API versions: HTTP {resp_versions.status_code} - {resp_versions.text}")
            raise Exception(f"Failed to fetch API versions: {resp_versions.text}")

        api_versions = resp_versions.json().get("apiVersions", [])
        if not api_versions:
            print("Error at getting WebCon API versions: No versions returned")
            raise Exception("No API versions returned from server.")

        numeric_versions = [float(v["version"]) for v in api_versions if v["version"] != "beta"]
        if not numeric_versions:
            print("Error at getting WebCon API versions: No numeric versions found")
            raise Exception("No numeric API versions found.")

        max_version = str(max(numeric_versions))

        # Step 2: Build API URL with max version
        base_url = f"{parameters['webcon_base_url']}/api/data/{max_version}"
        url = (
            f"{base_url}/db/{parameters['webcon_dbid']}/applications/"
            f"{parameters['webcon_report_app_id']}/reports/{parameters['webcon_report_id']}"
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        filters = {
            f"{parameters['invoice_id_url_filter']}": invoice_id,
            f"{parameters['supplier_company_id_url_filter']}": supplier_company_id,
            "page": 1,
            "size": 1,
        }

        # Step 3: Call WebCon API
        response = requests.get(url, headers=headers, params=filters, proxies=proxies)
        response.raise_for_status()
        data = response.json()
        count = len(data.get("rows", []))

    except Exception as err:
        error_message = f"Failed to get Invoices list from WebCon report. An unexpected error occurred: {str(err)}"
        detailed_error = traceback.format_exc()
        print(error_message + "\n" + detailed_error)
        raise Exception(error_message + "\n" + detailed_error)

    # Step 4: Evaluate response
    if count <= 0:
        return False, 0
    else:
        max_id = min(data["rows"], key=lambda x: x["id"]).get("id", 0)
        return True, max_id if max_id else 0