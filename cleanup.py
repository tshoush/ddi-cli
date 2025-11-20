
import logging
import os
import json
from ddi.config import load_config
from ddi.infoblox import InfobloxManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """Main function to clean up Infoblox resources."""
    config_data = load_config()
    if not config_data:
        return

    try:
        infoblox_config = config_data.get('infoblox', {})
        infoblox_manager = InfobloxManager(
            grid_master_ip=infoblox_config.get('grid_master_ip'),
            wapi_version=infoblox_config.get('wapi_version'),
            admin_name=infoblox_config.get('admin_name'),
            password=infoblox_config.get('password'),
            network_view=infoblox_config.get('network_view', 'All')
        )
    except Exception as e:
        logging.error(f"Failed to initialize Infoblox manager: {e}")
        return

    # EAs to delete, based on the mock data
    ea_names_to_delete = [
        "STNOStatus-VPCAssociation", "Name", "Associate-with", "dud",
        "STNOStatus-VPCAttachment", "createdby", "tfc_created", "owner",
        "project", "RequestedBy", "Propagate-to", "STNOStatus-VPCPropagation",
        "environment", "cloudservice", "Description", "location", "NewTag"
    ]

    logging.info("Starting cleanup of Extensible Attributes...")
    for ea_name in ea_names_to_delete:
        try:
            if infoblox_manager.delete_ext_attr_definition(ea_name):
                logging.info(f"Successfully deleted EA: {ea_name}")
        except Exception as e:
            logging.error(f"Error deleting EA {ea_name}: {e}")
    logging.info("Extensible Attributes cleanup finished.")

    # Networks to delete, based on the mock data
    networks_to_delete = [
        "13.212.224.0/23",
        "13.216.140.0/23"
    ]

    logging.info("Starting cleanup of Networks...")
    for network in networks_to_delete:
        try:
            if infoblox_manager.delete_network(network):
                logging.info(f"Successfully deleted Network: {network}")
        except Exception as e:
            logging.error(f"Error deleting network {network}: {e}")
    logging.info("Networks cleanup finished.")


if __name__ == "__main__":
    main()
