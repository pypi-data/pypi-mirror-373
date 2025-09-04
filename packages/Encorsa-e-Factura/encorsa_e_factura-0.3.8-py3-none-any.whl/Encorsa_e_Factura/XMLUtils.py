import xml.etree.ElementTree as ET
import os


def find_nodes_by_path(root, path, namespaces):
    """
    Find nodes in an XML tree using an absolute path, accounting for the root node.
    :param root: The root node of the XML tree.
    :param path: The absolute path to find nodes, starting from the root.
    :param namespaces: A dictionary mapping namespace prefixes to URIs.
    :return: A list of all nodes matching the path. Empty if no match is found.
    """
    def _find_recursive(node, parts, namespaces):
        # If there are no more parts, return the current node
        # This is the base case of the recursive function
        if not parts:
            return [node]

        # Get the next parts of the path
        # If there are no next parts, set next_parts to an empty list
        # This is the recursive case of the function
        next_parts = parts[1:] if len(parts) > 1 else []

        # Get the current part of the path
        part = parts[0]
        # If the part contains a namespace prefix, replace it with the corresponding URI
        if ':' in part:
            # Split the part into prefix and tag
            prefix, tag = part.split(':', 1)
            # Get the URI corresponding to the prefix
            uri = namespaces.get(prefix, '')
            # Replace the part with the full namespace URI and tag
            # Example: replace 'ubl:Invoice' with '{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice'
            # This is the format ElementTree uses for namespaces
            part = f"{{{uri}}}{tag}"

        # At the first level, compare part with the root's tag; check if the tag ends with the part
        # This check is made to account for the path starting with the root node
        if node == root:
            # If the root node's tag ends with the part, remove the first part from the list of parts
            if node.tag.endswith(part):
                # Update the part and next_parts based on the root node's tag
                part = parts[1]
                # If there are more than 2 parts, update next_parts accordingly
                next_parts = parts[2:] if len(parts) > 2 else []
                # Same as before, replace the part with the full namespace URI and tag if necessary
                if ':' in part:
                    prefix, tag = part.split(':', 1)
                    uri = namespaces.get(prefix, '')
                    part = f"{{{uri}}}{tag}"

        found_nodes = []
        # Recursively search for nodes matching the current part in the children of the current node
        for child in node:
            if child.tag.endswith(part):
                found_nodes.extend(_find_recursive(
                    child, next_parts, namespaces))
        return found_nodes

    # Normalize and split the path, removing the initial '/' if present
    parts = path[1:].split('/') if path.startswith('/') else path.split('/')

    # Start the recursive search from the root with the given path parts
    matched_nodes = _find_recursive(root, parts, namespaces)

    return matched_nodes


class XMLDataExtractorItemLists:
    def __init__(self, xml_tree, result_dict, namespaces=None):
        self.xml_tree = xml_tree
        self.result_dict = result_dict
        self.namespaces = namespaces if namespaces is not None else {}

    def extract_list_data(self, parent_path, columns):
        """
        Extract data from the XML tree for a list of items.
        :param parent_path: The path to the parent node of the list.
        :param columns: A list of tuples containing the path to the data and the corresponding column name.
            The column name is the field guid from WebCon that will be used in the body for the API request.
        :return: A list of dictionaries, where each dictionary contains the extracted data for an item in the list.
        """
        list_data = []
        # Try to find the parent node based on the parent_path
        child_row_nodes = find_nodes_by_path(
            self.xml_tree, parent_path, self.namespaces)
        # For each child node, extract the data based on the columns
        for row_node in child_row_nodes:
            row_data = {}
            # For each column, extract the data
            # The column_path is the path is a sub-path of the parent_path
            for column_path, column_name in columns:
                # If the column_path contains an '@', then it is an attribute
                if '@' in column_path:
                    # Split the path and attribute name by the '@' character which separates the path from the attribute name
                    element_path, attribute_name = column_path.rsplit('@', 1)
                    child = find_nodes_by_path(
                        row_node, element_path, self.namespaces)
                    # If the child list is not empty, then extract the attribute value
                    if len(child) > 0:
                        child = child[0]
                    # If the child list is empty, then the attribute value is None
                    else:
                        child = None
                    # Extract the attribute value
                    value = child.get(
                        attribute_name) if child is not None else None
                else:
                    # If the column_path does not contain an '@', then it is a sub-element
                    child = find_nodes_by_path(
                        row_node, column_path, self.namespaces)
                    # If the child list is not empty, then extract the text value
                    if len(child) > 0:
                        child = child[0]
                    else:
                        child = None
                    # Extract the text value only if the child list is not empty
                    # Otherwise, the value is None
                    # The strip() method is used to remove leading and trailing whitespaces
                    value = child.text.strip() if child is not None and child.text is not None else None
                row_data[column_name] = value
            list_data.append(row_data)

        return list_data

    def extract_all_lists(self):
        all_lists_data = {}
        # For each item list, extract the data
        for list_id, info in self.result_dict.items():
            parent_path, columns = info
            # Extract the data for the current list
            all_lists_data[list_id] = self.extract_list_data(
                parent_path, columns)
        return all_lists_data

# Step 1 - Extract the template data


class XMLTemplateParser:
    def __init__(self, xml_tree, namespaces):
        self.xml_tree = xml_tree
        self.namespaces = namespaces

    def parse_template(self):
        template_data = {}

        def traverse(node, path='', isParentList=False, parentListID=""):
            # Skip nodes that are not Element (e.g., comments or processing instructions)
            if not isinstance(node.tag, str):
                return

            # Handling namespace and local name
            ns_uri = None
            node_tag = node.tag
            if node.tag.startswith('{'):
                ns_uri, node_tag = node.tag[1:].split("}", 1)
                namespace_prefix = None
                for prefix, uri in self.namespaces.items():
                    if uri == ns_uri:
                        namespace_prefix = prefix
                        break
                current_path = f"{path}/{namespace_prefix}:{node_tag}" if namespace_prefix else f"{path}/{node_tag}"
            else:
                current_path = f"{path}/{node_tag}"

            node_list_id = node.attrib.get("itemList", "")
            node_is_list = node_list_id != ""

            if node_is_list and isParentList:
                print(
                    "Template incorrectly configured. You cannot have nested lists in template configuration!")
                raise Exception(
                    "Template incorrectly configured. You cannot have nested lists in template configuration!")

            for attr_name, attr_value in node.attrib.items():
                if attr_name == "itemList":
                    continue

                # Handling attributes with potential namespaces
                attr_ns_uri = None
                attr_localname = attr_name
                if attr_name[0] == "{":
                    attr_ns_uri, attr_localname = attr_name[1:].split("}", 1)
                    attr_namespace_prefix = None
                    for prefix, uri in self.namespaces.items():
                        if uri == attr_ns_uri:
                            attr_namespace_prefix = prefix
                            break
                    full_attr_name = f"{attr_namespace_prefix}:{attr_localname}" if attr_namespace_prefix else attr_localname
                else:
                    full_attr_name = attr_localname

                if node_is_list:
                    template_data[f"{current_path}@{full_attr_name}"] = (
                        attr_value, node_list_id)
                elif isParentList:
                    template_data[f"{current_path}@{full_attr_name}"] = (
                        attr_value, parentListID)
                else:
                    template_data[f"{current_path}@{full_attr_name}"] = (
                        attr_value, "")

            if node.text and node.text.strip():
                if node_is_list:
                    template_data[current_path] = (
                        node.text.strip(), node_list_id)
                elif isParentList:
                    template_data[current_path] = (
                        node.text.strip(), parentListID)
                else:
                    template_data[current_path] = (node.text.strip(), "")

            for child in node:
                if node_is_list:
                    traverse(child, current_path, True, node_list_id)
                elif isParentList:
                    traverse(child, current_path, True, parentListID)
                else:
                    traverse(child, current_path, False, "")

        traverse(self.xml_tree.getroot())
        return template_data

# Step 2 - Extract the data from the XML file with form fields values


class XMLDataProcessorFormFields:
    def __init__(self, data_xml_tree, template_keys, namespaces):
        """
        Initialize the XMLDataProcessorFormFields object.
        :param data_xml_tree: The XML tree containing the data.
        :param template_keys: A dictionary containing the template keys and their corresponding paths in the XML tree.
        The keys in the dictionary are the paths in the XML tree, and the values are tuples containing the key name and an empty string.
        The first element of the tuple is the form filed guid from WebCon that will be used in the body for the API request.
        The second element of the tuple is empty string and does not have any use for now.
        :param namespaces: A dictionary containing the namespace prefixes and their corresponding URIs.
        """
        self.data_xml_tree = data_xml_tree
        self.template_keys = template_keys
        self.namespaces = namespaces

    def apply_template(self):
        """
        Extract data from the XML tree based on the template keys.
        :return: A dictionary containing the extracted data.
        """
        # Initialize an empty dictionary to store the extracted data
        # The keys are the form field guids from WebCon, and the values are the extracted data
        # This dictionary will be used to construct the body for the API request with the form fields values
        extracted_data = {}
        # For each path in the template keys, extract the data from the XML tree
        for path, (key, _) in self.template_keys.items():
            # If the path contains an '@', then it is an attribute
            if "@" in path:
                # Split the path and attribute name by the '@' character which separates the path from the attribute name
                element_path, attribute_name = path.rsplit('@', 1)
                # Find the node in the XML tree based on the element_path
                node = find_nodes_by_path(
                    self.data_xml_tree, element_path, self.namespaces)
                # If the node list is not empty, then extract the attribute value
                if len(node) > 0:
                    node = node[0]
                else:
                    node = None
                # Extract the attribute value
                if node is not None:
                    # Access the attribute directly
                    attr_value = node.get(attribute_name)
                    if attr_value:
                        # Store the attribute value in the extracted data dictionary
                        extracted_data[key] = attr_value
            else:
                # Adjusted for ET: find the first node that matches the path
                node = find_nodes_by_path(
                    self.data_xml_tree, path, self.namespaces)
                # Same as before, extract the text value only if the node list is not empty
                if len(node) > 0:
                    node = node[0]
                else:
                    node = None
                # Extract the text value
                if node is not None:
                    # Access the text directly
                    # The strip() method is used to remove leading and trailing whitespaces
                    value = node.text.strip() if node.text else None
                    # Store the text value in the extracted data dictionary
                    extracted_data[key] = value

        return extracted_data

# Main Class for XML Processing


class XMLProcessor:
    def __init__(self, template_xml_path, xml_string_file_data, namespaces):
        self.template_xml_path = template_xml_path
        self.xml_string_file_data = xml_string_file_data
        self.namespaces = namespaces

    def process_xml(self):
        # Parse the XML template
        tree = ET.parse(self.template_xml_path)
        # Assuming XMLTemplateParser and XMLDataProcessor can work with an ElementTree object
        template_parser = XMLTemplateParser(tree, self.namespaces)
        template_form_fields_data = template_parser.parse_template()

        # Dictionary to store removed elements
        removed_elements = {}

        # Iterate over the original dictionary
        for key, (first_val, second_val) in template_form_fields_data.copy().items():
            if second_val != "":
                if second_val not in removed_elements:
                    removed_elements[second_val] = [(key, first_val)]
                else:
                    removed_elements[second_val].append((key, first_val))
                del template_form_fields_data[key]

        item_lists_dict = {}

        for key, paths_list in removed_elements.items():
            common_prefix = os.path.commonprefix(
                [path[0] for path in paths_list])
            common_base_path = common_prefix.rsplit('/', 1)[0]

            for path, value in paths_list:
                paths_list[paths_list.index((path, value))] = (
                    path.replace(common_base_path, ''), value)

            item_lists_dict[key] = (common_base_path, paths_list)

        # Parse the XML data
        data_tree = ET.fromstring(self.xml_string_file_data)

        # Assuming XMLDataProcessor and XMLDataProcessorFormFields can work with an Element (root) object
        data_processor = XMLDataProcessorFormFields(
            data_tree, template_form_fields_data, self.namespaces)
        form_fields_data = data_processor.apply_template()

        extractor = XMLDataExtractorItemLists(
            data_tree, item_lists_dict, self.namespaces)
        all_lists_data = extractor.extract_all_lists()

        return all_lists_data, form_fields_data
