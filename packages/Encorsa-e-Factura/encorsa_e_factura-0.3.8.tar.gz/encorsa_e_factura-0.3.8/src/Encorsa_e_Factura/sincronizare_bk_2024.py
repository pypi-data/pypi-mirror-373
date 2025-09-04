from io import BytesIO
import base64
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import requests
import zipfile
from requests.auth import HTTPBasicAuth
import argparse
from datetime import datetime
import re
import time
import traceback

try:
    from .XMLUtils import *
except:
    from XMLUtils import *

try:
    from .WebConRequestUtils import *
except:
    from WebConRequestUtils import *

namespaces = {
    'ubl': "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    'qdt': "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDataTypes-2",
    'cac': "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    'cbc': "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

nota_namespaces = {
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "ccts": "urn:un:unece:uncefact:documentation:2",
    "default": "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2",
    "qdt": "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDataTypes-2",
    "udt": "urn:oasis:names:specification:ubl:schema:xsd:UnqualifiedDataTypes-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


xpath_CUI = './cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID'
xpath_CUI2 = './cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID'
xpath_ID = './cbc:ID'


def get_token_with_refresh(refresh_token, clientID, clientSecret, parameters):
    url = "https://logincert.anaf.ro/anaf-oauth2/v1/token"
    auth = HTTPBasicAuth(clientID, clientSecret)
    data = {
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    try:
        proxies = {
            'http': None,
            'https': None
        }

        if "proxi_pt_anaf_https" in parameters and parameters["proxi_pt_anaf_https"] != None and parameters["proxi_pt_anaf_https"] != "":
            proxies["https"] = parameters["proxi_pt_anaf_https"]

        if "proxi_pt_anaf_http" in parameters and parameters["proxi_pt_anaf_http"] != None and parameters["proxi_pt_anaf_http"] != "":
            proxies["http"] = parameters["proxi_pt_anaf_http"]

        response = requests.post(url, auth=auth, data=data, proxies=proxies)
        # This checks for HTTP errors and raises an exception if any
        response.raise_for_status()

        json_response = response.json()  # Attempt to parse JSON response

        if 'access_token' in json_response:
            return json_response['access_token']
        else:
            # Handle cases where 'access_token' is not in response
            error_message = "Error at getting ANAF aceess token. Access token not found in the response."
            print(error_message)
            raise Exception(error_message)
    except Exception as e:
        # Catch all other errors
        error_message = f"Error at getting ANAF access token. Error message: {str(e)}"
        detailed_error = traceback.format_exc()
        print(error_message)
        print(detailed_error)
        raise Exception(f"{error_message}\n{detailed_error}")


def get_lista_paginata_mesaje(token, start_time, end_time, cif, pagina, filter=None, parameters={}):
    url = f"https://api.anaf.ro/prod/FCTEL/rest/listaMesajePaginatieFactura?startTime={start_time}&endTime={end_time}&cif={cif}&pagina={pagina}"
    if filter is not None:
        if filter != "":
            url += "&filtru=" + filter

    headers = {'Authorization': f'Bearer {token}'}
    try:
        proxies = {
            'http': None,
            'https': None
        }

        if "proxi_pt_anaf_https" in parameters and parameters["proxi_pt_anaf_https"] != None and parameters["proxi_pt_anaf_https"] != "":
            proxies["https"] = parameters["proxi_pt_anaf_https"]

        if "proxi_pt_anaf_http" in parameters and parameters["proxi_pt_anaf_http"] != None and parameters["proxi_pt_anaf_http"] != "":
            proxies["http"] = parameters["proxi_pt_anaf_http"]

        response = requests.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()  # Ridică o excepție pentru coduri de răspuns HTTP eronate
        return response.json()
    except Exception as e:
        error_message = f"Error at getting messages for page {pagina}. Error message: {str(e)}"
        detalied_error = traceback.format_exc()
        print(error_message)
        print(detalied_error)
        return {'eroare': error_message + '\n' + detalied_error} 


def get_all_messages(token, start_time, end_time, cif, filter=None, parameters={}):
    all_messages = []  # Lista pentru a stoca toate mesajele
    current_page = 1  # Indexul paginii curente începe de la 0

    # Încercăm să obținem mesajele de pe prima pagină pentru a verifica dacă există date
    first_page_response = get_lista_paginata_mesaje(
        token, start_time, end_time, cif, current_page, filter=filter, parameters=parameters)

    # Verificăm dacă răspunsul conține o eroare
    if "eroare" in first_page_response:
        if 'Nu exista mesaje' in first_page_response["eroare"]:
            print(first_page_response["eroare"])
            exit(0)
        error_message = "Error at getting all messages from ANAF: " + \
            first_page_response["eroare"]
        print(error_message)
        raise Exception(error_message)

    # Dacă există mesaje, continuăm să le adunăm din toate paginile
    total_pages = first_page_response['numar_total_pagini']
    all_messages.extend(first_page_response['mesaje'])

    # Continuăm cu următoarele pagini, dacă există
    for current_page in range(2, total_pages + 1):
        response = get_lista_paginata_mesaje(
            token, start_time, end_time, cif, current_page, filter=filter, parameters=parameters)
        if "eroare" in response:
            if 'Nu exista mesaje' in response["eroare"]:
                print(response["eroare"])
                exit(0)
            else:
                error_message = "Error at getting all messages from ANAF: " + \
                    response["eroare"]
                print(error_message)
                raise Exception(error_message)
        all_messages.extend(response['mesaje'])

    return all_messages


"""
Această funcție descarcă o arhivă ZIP de la ANAF folosind un ID de factură
și extrage un fișier specificat prin nume_fisier din aceasta. 
"""


def descarca_factura_si_extrage_fisier(token, id, nume_fisier, parameters):
    try:
        url = f"https://api.anaf.ro/prod/FCTEL/rest/descarcare?id={id}"
        headers = {'Authorization': f'Bearer {token}'}

        proxies = {
            'http': None,
            'https': None
        }

        if "proxi_pt_anaf_https" in parameters and parameters["proxi_pt_anaf_https"] != None and parameters["proxi_pt_anaf_https"] != "":
            proxies["https"] = parameters["proxi_pt_anaf_https"]

        if "proxi_pt_anaf_http" in parameters and parameters["proxi_pt_anaf_http"] != None and parameters["proxi_pt_anaf_http"] != "":
            proxies["http"] = parameters["proxi_pt_anaf_http"]

        response = requests.get(url, headers=headers, proxies=proxies)

        # Verify the response status code
        if response.status_code != 200:
            # Raise an exception for non-200 status codes with the HTTP status code
            error_message = f"Error while downloading ZIP archive with the XML. Code: {response.status_code}"
            print(error_message)
            raise Exception(error_message)

        # Create a BytesIO object from the response content
        zip_in_memory = BytesIO(response.content)

        try:
            # Open the ZIP archive
            with zipfile.ZipFile(zip_in_memory, 'r') as zip_ref:
                # Check if the file exists in the archive
                if nume_fisier in zip_ref.namelist():
                    # Extract the specified file content
                    with zip_ref.open(nume_fisier) as fisier:
                        content_bytes = fisier.read()
                        # Decode bytes into a string using UTF-8
                        content_string = content_bytes.decode('utf-8')
                        return content_string
                else:
                    # File not found in the archive, handle according to your preference
                    error_message = f"File '{nume_fisier}' not found in the ZIP archive"
                    print(error_message)
                    raise Exception(error_message)
        except zipfile.BadZipFile as zp_err:
            # Handle a bad ZIP file error
            error_message = f"Error while extracting ZIP archive with the XML. Message: {zp_err}"
            detalied_error = traceback.format_exc()
            print(error_message)
            print(detalied_error)
            raise Exception(error_message + '\n' + detalied_error)
    except Exception as e:
        # Handle other errors
        error_message = f"Error while downloading ZIP archive with the XML. Message: {e}"
        detalied_error = traceback.format_exc()
        print(error_message)
        print(detalied_error)
        raise Exception(error_message + '\n' + detalied_error)


def xml_to_pdf_to_base64(xml_data, parameters, document_type):
    """
    Funcția trimite date XML către un serviciu web al ANAF pentru a fi convertite
    într-un document PDF, apoi encodează conținutul binar al PDF-ului obținut în format Base64
    """

    if document_type == "Invoice":
        url = "https://webservicesp.anaf.ro/prod/FCTEL/rest/transformare/FACT1/DA"
    elif document_type == "CreditNote":
        url = "https://webservicesp.anaf.ro/prod/FCTEL/rest/transformare/FCN/DA"
    else:
        raise ValueError("Invalid document type for XML to PDF conversion." + f" Document type: {document_type}")
    
    headers = {'Content-Type': 'text/plain'}
    proxies = {'http': None, 'https': None}

    # Set proxies if provided in parameters
    if "proxi_pt_anaf_https" in parameters and parameters["proxi_pt_anaf_https"]:
        proxies["https"] = parameters["proxi_pt_anaf_https"]
    if "proxi_pt_anaf_http" in parameters and parameters["proxi_pt_anaf_http"]:
        proxies["http"] = parameters["proxi_pt_anaf_http"]

    # Retry logic
    max_retries = 5
    attempts = 0

    # Encode the XML data to UTF-8 bytes to ensure compatibility
    xml_data = xml_data.encode('utf-8')

    while attempts < max_retries:
        try:
            response = requests.post(
                url, headers=headers, data=xml_data, proxies=proxies)
            if response.status_code != 200:
                response.raise_for_status()

            # Directly check if the response is JSON
            if "application/json" in response.headers.get('Content-Type', ''):
                print("JSON response received, retrying..." + str(response.content))
                # Print the whole response for debugging
                attempts += 1
                # Sleep for 1 second before retrying
                time.sleep(1)
                continue
            else:
                # Assume the response is the binary content of the PDF
                pdf_content = response.content
                # Encode the PDF content to Base64
                base64_encoded_pdf = base64.b64encode(pdf_content)
                return base64_encoded_pdf.decode('utf-8')
        except Exception as e:
            error_message = f"Error when converting the XML to PDF: {str(e)}"
            detalied_error = traceback.format_exc()
            print(error_message + '\n' + detalied_error)
            attempts += 1

    print("Maximum retries reached, PDF content could not be retrieved.")
    raise Exception("Maximum retries reached, PDF content could not be retrieved.")


def send_to_WebCon(parameters, token, messages, xml_template_file_path, xml_nota_template_file_path=None):
    wtoken = get_webcon_token(
        parameters['webcon_base_url'], parameters['webcon_clientID'], parameters['webcon_clientSecret'])
    current_message = 1

    for message in messages:
        # print(f'Processing message {current_message} of {len(messages)}')
        try:
            id_solicitare = message["id_solicitare"]
            id = message["id"]
            tip_factura = message["tip"]
            iso_data_creare = datetime.strptime(
                message["data_creare"], "%Y%m%d%H%M")

            filtru_facturi = parameters.get(
                'ANAF_invoice_type_filter_E_T_P_R', '')

            if filtru_facturi != '':
                if tip_factura != filtru_facturi:
                    print(
                        f"Skipping invoice with ANAF_ID: {id}, because type filters are applied. The filter is: {filtru_facturi})")
                    continue
            else:
                if tip_factura != "FACTURA TRIMISA" and tip_factura != "FACTURA PRIMITA":
                    print(
                        f"Skipping invoice with ANAF_ID: {id}. The message type is not <FACTURA TRIMISA> or <FACTURA PRIMITA>")
                    continue

            xml_text = descarca_factura_si_extrage_fisier(
                token, str(id), f"{id_solicitare}.xml", parameters)

            # Se actualizeaza namespace-urile din XML
            # Este posibil ca XML-ul sa aiba namespace-uri diferite de cele standard
            # In trecut, au fost identificate cazuri in care namespace-urile erau declarate gresit
            xml_text = update_xml_namespaces(xml_text)

            # Se verifica daca factura preluata exista deja in WebCon pe baza cheii unice formate din ID-factura si CUI
            root = ET.fromstring(xml_text)
            # Se verifica tag-ului nodului root din XML si se elimina ce se afla intre acolade
            root_tag = root.tag
            if '}' in root_tag:
                root_tag = root_tag.split('}', 1)[1]

            local_namespaces = {}
            local_xml_template_file_path = ""
            document_type = ""

            if root_tag == 'Invoice':
                if xml_template_file_path is None or xml_template_file_path == "":
                    print('Skipping invoice with ANAF_ID: ' + id +
                          ' because there is no Invoice template file path provided.')
                    continue
                document_type = "Invoice"
                local_namespaces = namespaces
                local_xml_template_file_path = xml_template_file_path
            elif root_tag == 'CreditNote':
                if xml_nota_template_file_path is None or xml_nota_template_file_path == "":
                    print('Skipping invoice with ANAF_ID: ' + id +
                          ' because there is no Credit Note template file path provided.')
                    continue
                document_type = "CreditNote"
                local_namespaces = nota_namespaces
                local_xml_template_file_path = xml_nota_template_file_path
            else:
                print('Skipping invoice with ANAF_ID: ' + id +
                      ' because it is not an Invoice or Credit Note.')
                continue

            invoice_id_element = root.find(xpath_ID, local_namespaces)
            company_id_element = root.find(xpath_CUI, local_namespaces)
            company_id_element2 = root.find(xpath_CUI2, local_namespaces)
            company_id = ""

            if invoice_id_element is None:
                print(
                    f'Cannot get {document_type} ID from XML, skipping {document_type}. ID from ANAF: ' + id)
                continue
            else:
                invoice_id_element = invoice_id_element.text

            if company_id_element is None:
                if company_id_element2 is None:
                    print(
                        f'Cannot get {document_type} Supplier Company ID, skipping {document_type}. ID from ANAF: ' + id)
                else:
                    company_id = company_id_element2.text
            else:
                company_id = company_id_element.text

            ifInvoiceExists, wfd_id_duplicate = check_if_invoice_exists(
                parameters, wtoken, invoice_id_element, company_id)
            if (parameters['how_to_handle_duplicates'] == 'SKIP'):
                if ifInvoiceExists:
                    print(
                        f"Skipping {document_type} with ID: {invoice_id_element}, COMPANY ID: {company_id}, because it already exists in WebCon.")
                    continue

            pdf_content = xml_to_pdf_to_base64(xml_text, parameters, document_type)
            xml_bytes = str(xml_text).encode('utf-8')
            base64_encoded_xml = base64.b64encode(xml_bytes)
            base64_string_xml = base64_encoded_xml.decode('utf-8')

            body = create_webcon_body(parameters, base64_string_xml, pdf_content, xml_text, invoice_id_element, company_id,
                                      local_xml_template_file_path, wfd_id_duplicate, local_namespaces, document_type, id, iso_data_creare)
            response = create_invoice_instance(parameters, wtoken, body)
            print(
                f"{document_type} instance created with SUCCESS having WFD_ID: < {response['id']} >.")
        except Exception as ex:
            # Preparing and printing a detailed error message
            error_details = f"Error at processing message: {message}.\nError message: {str(ex)}"
            detalied_error = traceback.format_exc()
            print(error_details)
            print(detalied_error)
            raise Exception(error_details + '\n' + detalied_error)
        current_message += 1


def read_json_parameters(file_path):
    """Read and return the parameters stored in a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            file_content = file.read().strip()
            parameters = json.loads(file_content)
            return parameters
    except FileNotFoundError:
        error_message = f"Error: The file {file_path} was not found."
        detalied_error = traceback.format_exc()
        print(error_message + '\n' + detalied_error)
        raise Exception(error_message + '\n' + detalied_error)
    except json.JSONDecodeError:
        error_message = f"Error: The file {file_path} contains invalid JSON."
        detalied_error = traceback.format_exc()
        print(error_message + '\n' + detalied_error)
        raise Exception(error_message + '\n' + detalied_error)
    except Exception as ex:
        error_message = f"Error: The file {file_path} cannot opened/used. " + str(ex)
        detalied_error = traceback.format_exc()
        print(error_message + '\n' + detalied_error)
        raise Exception(error_message + '\n' + detalied_error)


def update_xml_namespaces(xml_string, namespaces_dict=None):
    """
    Update namespaces in the root element of an XML string based on the type of document (Invoice or CreditNote).

    Args:
        xml_string (str): The original XML string.
        namespaces_dict (dict): A dictionary containing namespace dictionaries for 'Invoice' and 'CreditNote'.

    Returns:
        str: Updated XML string with namespaces adjusted based on the document type.
    """

    full_namespaces_dict = {
        'Invoice': {
            'xmlns': "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
            'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
            'xmlns:qdt': "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDataTypes-2",
            'xmlns:udt': "urn:oasis:names:specification:ubl:schema:xsd:UnqualifiedDataTypes-2",
            'xmlns:cac': "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            'xmlns:cbc': "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            'xmlns:cec': "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            'xmlns:ccts': "urn:un:unece:uncefact:documentation:2",
        },
        'CreditNote': {
            'xmlns': "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2",
            'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
            'xmlns:qdt': "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDataTypes-2",
            'xmlns:udt': "urn:oasis:names:specification:ubl:schema:xsd:UnqualifiedDataTypes-2",
            'xmlns:cac': "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            'xmlns:cbc': "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            'xmlns:cec': "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            'xmlns:ccts': "urn:un:unece:uncefact:documentation:2",
        }
    }
    if namespaces_dict is None:
        namespaces_dict = full_namespaces_dict

    # Parse the original XML string into an Element
    root = ET.fromstring(xml_string)

    # Determine the document type from the root tag
    document_type = root.tag
    if '}' in document_type:
        document_type = document_type.split('}', 1)[1]

    # Get the full namespace dictionary for the document type
    namespaces_dict = full_namespaces_dict[document_type]

    start_tag = f'<{document_type}'
    end_tag = '>'

    # Find the start and end of the root element's opening tag
    start_pos = xml_string.find(start_tag)
    if start_pos == -1:
        print(f"Document type tag not found in XML string: {document_type}")
        raise ValueError("Document type tag not found in XML string.")

    end_pos = xml_string.find(end_tag, start_pos)
    if end_pos == -1:
        print(f"Closing '>' of the root tag not found.")
        raise ValueError("Closing '>' of the root tag not found.")

    # Extract the whole root tag
    root_tag_full = xml_string[start_pos:end_pos + 1]
    
    updated_root = update_namespaces_from_node(root_tag_full, namespaces_dict)
    new_xml = xml_string.replace(root_tag_full, updated_root)

    # Check if the final string contains special invisible characters and remove them like &#xD;
    new_xml = new_xml.replace('&#xD;', '')

    return new_xml


def update_namespaces_from_node(node_string, namespace_replacements):
    """
    Extracts and optionally updates namespaces from the provided XML node string.

    Args:
        node_string (str): The XML node string containing namespace declarations.
        namespace_replacements (dict): Dictionary of namespaces with potential replacements.

    Returns:
        str: XML node string with updated namespaces.
    """
    # Regex to find any attribute that follows the pattern [name]="[URI]"
    namespace_pattern = re.compile(
        r'(\s(?P<attribute>[a-zA-Z0-9_:]+)="(?P<uri>[^"]+)")')
    
    # A list with all the attributes that match the pattern
    found_attributes = []

    # Function to replace namespaces in the match with those from the dictionary
    def replace_namespace(match):
        attribute = match.group('attribute')  # Attribute name (e.g., xmlns, xsi:schemaLocation)
        # Add the attribute to the list of found attributes
        found_attributes.append(attribute)
        uri = match.group('uri')
        # Check if the attribute is in the replacements dictionary and replace URI if present
        if attribute in namespace_replacements:
            return f' {attribute}="{namespace_replacements[attribute]}"'
        else:
            # Handle the specific case for URIs containing "../../"
            if '../../' in uri:
                # Remove spaces and split the URI, then take the first part before "../../"
                uri = uri.split("../../")[0].strip()
            return f' {attribute}="{uri}"'

    # Replace found namespaces in the node string with potential replacements from the dictionary
    updated_node_string = namespace_pattern.sub(replace_namespace, node_string)

    # Check if there are any missing attributes from the dictionary and add them
    for attribute, uri in namespace_replacements.items():
        if attribute not in found_attributes:
            # Add the missing attribute to the end of the node string with newline and indentation
            updated_node_string = updated_node_string.rstrip('>') + f'\n            {attribute}="{uri}">'

    return updated_node_string


def startRunning(json_file_path, xml_template_file_path, xml_nota_template_file_path=None):

    # Read parameters from the JSON file
    parameters = read_json_parameters(json_file_path)

    try:
        unix_timestamp_from = datetime.fromisoformat(
            parameters['get_invoices_from_timestamp'])
        unix_timestamp_to = datetime.fromisoformat(
            parameters['get_invoices_to_timestamp'])

        unix_timestamp_from = int(unix_timestamp_from.timestamp() * 1000)
        unix_timestamp_to = int(unix_timestamp_to.timestamp() * 1000)
        print(unix_timestamp_from)
        print(unix_timestamp_to)

        token_aux = get_token_with_refresh(
            parameters['refresh_token_anaf'], parameters['efactura_clientID'], parameters['efactura_clientSecret'], parameters)

        # get message filter
        messages = get_all_messages(token_aux, str(unix_timestamp_from), str(
            unix_timestamp_to), parameters['cod_fiscal_client'], parameters=parameters)
        send_to_WebCon(parameters, token_aux, messages,
                       xml_template_file_path, xml_nota_template_file_path)
    except Exception as ex:
        error_message = f"Error in main function: {str(ex)}"
        detalied_error = traceback.format_exc()
        print(error_message + '\n' + detalied_error)
        raise Exception(error_message + '\n' + detalied_error)


def startRunningCLI():
    # Create the parser
    parser = argparse.ArgumentParser(
        description="Run the Encorsa_e_Factura synchronization process.")

    # Add arguments
    parser.add_argument('jsonFilePath', type=str,
                        help='The path to the JSON configuration file.')
    parser.add_argument('xmlFilePath', type=str,
                        help='The path to the XML template file to be processed for Invoices.')
    parser.add_argument('--notaXMLFilePath', type=str,
                        help='The path to the XML template file to be processed for Credit Notes.')

    # Parse arguments
    args = parser.parse_args()

    # Read parameters from the JSON file
    parameters = read_json_parameters(args.jsonFilePath)

    try:
        unix_timestamp_from = datetime.fromisoformat(
            parameters['get_invoices_from_timestamp'])
        unix_timestamp_to = datetime.fromisoformat(
            parameters['get_invoices_to_timestamp'])

        unix_timestamp_from = int(unix_timestamp_from.timestamp() * 1000)
        unix_timestamp_to = int(unix_timestamp_to.timestamp() * 1000)
        print(unix_timestamp_from)
        print(unix_timestamp_to)

        token_aux = get_token_with_refresh(
            parameters['refresh_token_anaf'], parameters['efactura_clientID'], parameters['efactura_clientSecret'], parameters=parameters)

        # get message filter
        messages = get_all_messages(token_aux, str(unix_timestamp_from), str(
            unix_timestamp_to), parameters['cod_fiscal_client'])
        send_to_WebCon(parameters, token_aux, messages,
                       args.xmlFilePath, args.notaXMLFilePath)
    except Exception as ex:
        error_message = f"Error in main function: {str(ex)}"
        detalied_error = traceback.format_exc()
        print(error_message + '\n' + detalied_error)
        raise Exception(error_message + '\n' + detalied_error)
