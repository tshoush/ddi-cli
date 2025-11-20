import requests

class InfobloxManager:
    def __init__(self, grid_master_ip, wapi_version, admin_name, password, network_view='All'):
        self.base_url = f"https://{grid_master_ip}/wapi/v{wapi_version}"
        self.auth = (admin_name, password)
        self.network_view = network_view
        self.verify_ssl = False  # In a production environment, you'd want to use proper SSL verification

        if not self.verify_ssl:
            requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    @property
    def _request_params(self):
        if self.network_view == 'All':
            return {}
        return {'network_view': self.network_view}

    def get_network_views(self):
        """Fetches all network views from Infoblox."""
        url = f"{self.base_url}/networkview"
        try:
            # This call should not be filtered by network view
            response = requests.get(url, auth=self.auth, verify=self.verify_ssl)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Infoblox: {e}")
            return None

    def sync_network(self, network_data):
        """
        Placeholder for syncing a network to Infoblox.
        When implemented, this will use self._request_params.
        """
        print(f"Syncing network: {network_data} in view: {self.network_view}")
        # In a real implementation, you would make WAPI calls here to create/update networks.
        # Example:
        # url = f"{self.base_url}/network"
        # response = requests.post(url, auth=self.auth, json=network_data, 
        #                          params=self._request_params, verify=self.verify_ssl)
        pass

    def get_ext_attr_definitions(self):
        """Fetches all extensible attribute definitions from Infoblox."""
        url = f"{self.base_url}/extensibleattributedef"
        try:
            response = requests.get(url, auth=self.auth, verify=self.verify_ssl)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching extensible attribute definitions: {e}")
            return None

    def create_ext_attr_definition(self, name, attr_type="STRING", comment="Created by ddi-cli"):
        """Creates a new extensible attribute definition."""
        url = f"{self.base_url}/extensibleattributedef"
        payload = {
            "name": name,
            "type": attr_type,
            "comment": comment
        }
        try:
            response = requests.post(url, auth=self.auth, json=payload, 
                                     params=self._request_params, verify=self.verify_ssl)
            response.raise_for_status()
            print(f"Successfully created Extensible Attribute: {name}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating extensible attribute '{name}': {e}")
            if e.response:
                print(f"Response: {e.response.text}")
            return None

    def delete_ext_attr_definition(self, name):
        """Deletes an extensible attribute definition by name."""
        # First, get the reference of the EA
        url = f"{self.base_url}/extensibleattributedef"
        params = {'name': name}
        try:
            response = requests.get(url, auth=self.auth, params=params, verify=self.verify_ssl)
            response.raise_for_status()
            ea_defs = response.json()
            if not ea_defs:
                print(f"Extensible attribute '{name}' not found.")
                return False
            
            ea_ref = ea_defs[0]['_ref']
            
            # Now delete it
            del_url = f"{self.base_url}/{ea_ref}"
            del_response = requests.delete(del_url, auth=self.auth, verify=self.verify_ssl)
            del_response.raise_for_status()
            print(f"Successfully deleted Extensible Attribute: {name}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error deleting extensible attribute '{name}': {e}")
            if e.response:
                print(f"Response: {e.response.text}")
            return False

    def delete_network(self, network):
        """Deletes a network by its CIDR."""
        # First, get the reference of the network
        url = f"{self.base_url}/network"
        params = {'network': network}
        if self.network_view != 'All':
            params['network_view'] = self.network_view
            
        try:
            response = requests.get(url, auth=self.auth, params=params, verify=self.verify_ssl)
            response.raise_for_status()
            networks = response.json()
            if not networks:
                print(f"Network '{network}' not found in view '{self.network_view}'.")
                return False
            
            network_ref = networks[0]['_ref']
            
            # Now delete it
            del_url = f"{self.base_url}/{network_ref}"
            del_response = requests.delete(del_url, auth=self.auth, verify=self.verify_ssl)
            del_response.raise_for_status()
            print(f"Successfully deleted Network: {network}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error deleting network '{network}': {e}")
            if e.response:
                print(f"Response: {e.response.text}")
            return False
