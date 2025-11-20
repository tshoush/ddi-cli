import csv
import ast
import click
import json
from .base import BaseProvider
from thefuzz import process

class AWSProvider(BaseProvider):
    """
    Manages AWS-specific operations, focusing on tags and attributes.
    """

    def _get_vpc_export_file_path(self):
        """Gets the VPC export file path from config or prompts the user."""
        aws_config = self.config.get('aws', {})
        vpc_export_file = aws_config.get("vpc_export_file")
        
        if not vpc_export_file:
            vpc_export_file = click.prompt("Please enter the path to the AWS VPC export file (CSV format)")
        
        return vpc_export_file

    def _get_aws_tags_from_csv(self):
        """
        Parses the AWS VPC export CSV and returns a dictionary mapping
        tag keys to a list of VPC IDs that use them.
        Also returns a set of all unique tag keys.
        """
        file_path = self._get_vpc_export_file_path()
        aws_tags_with_vpcs = {} # { "tag_key": ["vpc-123", "vpc-456"] }
        all_unique_aws_tags = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    vpc_id = row.get('VpcId')
                    tags_str = row.get('Tags')
                    
                    if vpc_id and tags_str and tags_str != "[]":
                        try:
                            tags_list = ast.literal_eval(tags_str)
                            for tag in tags_list:
                                tag_key = tag['Key']
                                all_unique_aws_tags.add(tag_key)
                                if tag_key not in aws_tags_with_vpcs:
                                    aws_tags_with_vpcs[tag_key] = []
                                if vpc_id not in aws_tags_with_vpcs[tag_key]:
                                    aws_tags_with_vpcs[tag_key].append(vpc_id)
                        except (ValueError, SyntaxError) as e:
                            click.echo(f"Warning: Could not parse Tags from row: {row}. Error: {e}", err=True)
            return aws_tags_with_vpcs, all_unique_aws_tags
        except FileNotFoundError:
            click.echo(f"Error: File not found at {file_path}", err=True)
            return None, None
        except Exception as e:
            click.echo(f"An error occurred while reading the CSV: {e}", err=True)
            return None, None

    def list_missing_eas(self, infoblox_manager):
        """Compares AWS tags with Infoblox EAs and returns missing ones."""
        click.echo("Fetching AWS tags from source file...")
        aws_tags_with_vpcs, all_unique_aws_tags = self._get_aws_tags_from_csv()
        if all_unique_aws_tags is None:
            return None

        click.echo("Fetching Infoblox Extensible Attributes...")
        ib_eas_defs = infoblox_manager.get_ext_attr_definitions()
        if ib_eas_defs is None:
            return None
            
        ib_ea_names = {ea['name'] for ea in ib_eas_defs}
        
        missing_tags = all_unique_aws_tags - ib_ea_names
        return missing_tags

    def create_missing_eas(self, infoblox_manager):
        """Creates missing Infoblox EAs based on AWS tags."""
        missing = self.list_missing_eas(infoblox_manager)
        if not missing:
            click.echo("No missing Extensible Attributes found. Everything is in sync.")
            return

        click.echo("\nThe following Extensible Attributes will be created in Infoblox:")
        for tag in sorted(missing):
            click.echo(f"- {tag}")
        
        if click.confirm("\nDo you want to proceed with the creation?"):
            for tag_name in sorted(missing):
                infoblox_manager.create_ext_attr_definition(tag_name)
        else:
            click.echo("Operation cancelled.")

    def analyze_eas(self, infoblox_manager):
        """
        Analyzes and finds similarities between AWS tags and Infoblox EAs,
        and prepares a comprehensive report including missing EAs and networks.
        """
        click.echo("Fetching AWS tags and Infoblox EAs for analysis...")
        aws_tags_with_vpcs, all_unique_aws_tags = self._get_aws_tags_from_csv()
        ib_eas_defs = infoblox_manager.get_ext_attr_definitions()

        if all_unique_aws_tags is None or ib_eas_defs is None:
            click.echo("Could not perform analysis due to errors.", err=True)
            return None

        ib_ea_names = {ea['name'] for ea in ib_eas_defs}
        
        # Comprehensive report structure
        report = {
            "all_aws_tags": sorted(list(all_unique_aws_tags)),
            "all_infoblox_eas": sorted(list(ib_ea_names)),
            "missing_eas_in_infoblox": [],
            "potential_duplicates": [],
            "aws_tags_with_networks": aws_tags_with_vpcs
        }

        # Find missing EAs
        missing_tags = all_unique_aws_tags - ib_ea_names
        if missing_tags:
            report["missing_eas_in_infoblox"] = sorted(list(missing_tags))
            click.echo("\nThe following AWS tags are missing as Extensible Attributes in Infoblox:")
            for tag in report["missing_eas_in_infoblox"]:
                click.echo(f"- {tag}")
        else:
            click.echo("No missing Extensible Attributes found. All AWS tags are in sync with Infoblox EAs.")

        # Find potential duplicates
        click.echo("\nFinding potential duplicates (e.g., 'createdby' vs. 'Created_By')...")
        potential_duplicates = []
        for tag in sorted(list(all_unique_aws_tags)):
            best_match = process.extractOne(tag, list(ib_ea_names)) # process.extractOne expects a list
            if best_match and best_match[1] > 80 and best_match[0].lower() == tag.lower() and best_match[0] != tag:
                potential_duplicates.append({
                    "aws_tag": tag,
                    "similar_infoblox_ea": best_match[0],
                    "similarity_score": best_match[1]
                })
                click.echo(f"- Found potential duplicate: AWS Tag '{tag}' is very similar to Infoblox EA '{best_match[0]}'")
        
        if potential_duplicates:
            report["potential_duplicates"] = potential_duplicates
        else:
            click.echo("No obvious duplicates found based on similarity analysis.")
            
        return report

    def sync(self, infoblox_manager):
        """
        Parses the AWS VPC export and syncs the data to Infoblox.
        """
        # This method is now simplified, as the core logic for tags is handled by the 'attributes' commands.
        # The actual network sync logic would go here.
        click.echo("Syncing AWS data...")
        
        # First, check for missing EAs as they are a prerequisite
        missing_eas = self.list_missing_eas(infoblox_manager)
        if missing_eas:
            click.echo("\nWarning: There are AWS tags that do not exist as Infoblox Extensible Attributes.", err=True)
            click.echo("This may cause the sync to fail or be incomplete.", err=True)
            click.echo("Please run 'aws attributes list-missing' and 'aws attributes create-missing' to fix this.", err=True)
            if not click.confirm("Continue with sync anyway?"):
                click.echo("Sync operation cancelled.")
                return

        file_path = self._get_vpc_export_file_path()
        click.echo(f"Parsing and syncing networks from: {file_path}")
        # Placeholder for the actual network sync logic using the CSV file
        click.echo("Network sync logic is a placeholder and has not been fully implemented yet.")
        click.echo("AWS sync process completed.")

    def export_analysis(self, infoblox_manager, base_filename):
        """
        Exports the comprehensive attribute analysis report to JSON and CSV files.
        """
        report = self.analyze_eas(infoblox_manager)

        if not report:
            click.echo("No analysis report to export.")
            return

        # Export to JSON
        json_filename = f"{base_filename}.json"
        try:
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4)
            click.echo(f"Analysis report exported to {json_filename}")
        except IOError as e:
            click.echo(f"Error writing JSON file {json_filename}: {e}", err=True)

        # Export to CSV
        csv_filename = f"{base_filename}.csv"
        try:
            with open(csv_filename, 'w', encoding='utf-8', newline='') as f:
                # Define fieldnames for CSV. This will be more complex due to nested structure.
                # For simplicity, let's flatten some parts for CSV.
                # This is a simplified approach for CSV, a more robust solution might involve
                # creating separate CSVs or more complex flattening.
                writer = csv.writer(f)
                writer.writerow(["Report Section", "Details"])
                
                writer.writerow(["All AWS Tags", ", ".join(report.get("all_aws_tags", []))])
                writer.writerow(["All Infoblox EAs", ", ".join(report.get("all_infoblox_eas", []))])
                writer.writerow(["Missing EAs in Infoblox", ", ".join(report.get("missing_eas_in_infoblox", []))])

                writer.writerow([]) # Empty row for separation
                writer.writerow(["Potential Duplicates"])
                writer.writerow(["AWS Tag", "Similar Infoblox EA", "Similarity Score"])
                for item in report.get("potential_duplicates", []):
                    writer.writerow([item.get("aws_tag", ""), item.get("similar_infoblox_ea", ""), item.get("similarity_score", "")])

                writer.writerow([]) # Empty row for separation
                writer.writerow(["AWS Tags with Networks"])
                writer.writerow(["AWS Tag", "Associated VPC IDs"])
                for tag, vpcs in report.get("aws_tags_with_networks", {}).items():
                    writer.writerow([tag, ", ".join(vpcs)])

            click.echo(f"Analysis report exported to {csv_filename}")
        except IOError as e:
            click.echo(f"Error writing CSV file {csv_filename}: {e}", err=True)

    def search(self, search_term):
        """
        Searches for network resources within AWS.
        """
        click.echo(f"Searching AWS for: {search_term}")
        click.echo("Search functionality is a placeholder and has not been fully implemented yet.")
        # Placeholder for AWS search logic

    def audit(self):
        """
        Performs an audit of network resources in AWS.
        """
        click.echo("Auditing AWS resources...")
        click.echo("Audit functionality is a placeholder and has not been fully implemented yet.")
        # Placeholder for AWS audit logic