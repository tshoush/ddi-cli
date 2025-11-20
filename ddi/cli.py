import click
import sys
import os
import questionary
import datetime
import logging
from ddi.config import load_config, save_config, ConfigurationError
from ddi.infoblox import InfobloxManager
from ddi.providers.aws import AWSProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ddi-cli.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Provider mapping
PROVIDER_CLASSES = {
    'aws': AWSProvider,
    # 'azure': AzureProvider, # Future providers will be added here
}

def prompt_numbered_list(title, options):
    """
    Displays a numbered list of options and prompts the user to select one.
    Returns the selected option string.
    """
    click.echo(f"\n{title}")
    for i, option in enumerate(options, 1):
        click.echo(f"{i}. {option}")
    
    while True:
        choice = click.prompt(f"Enter choice (1-{len(options)})", type=int)
        if 1 <= choice <= len(options):
            return options[choice - 1]
        click.echo(f"Invalid choice. Please enter a number between 1 and {len(options)}.")

def display_config_dashboard(infoblox_config):
    """Displays the configuration dashboard."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    grid_master = infoblox_config.get('grid_master_ip', 'Not Set')
    if grid_master == 'YOUR_INFOBLOX_IP': grid_master = 'Not Set'
    
    admin = infoblox_config.get('admin_name', 'Not Set')
    if admin == 'YOUR_INFOBLOX_USERNAME': admin = 'Not Set'
    
    password = infoblox_config.get('password')
    if password and password != 'YOUR_INFOBLOX_PASSWORD':
        password_display = '********'
    else:
        password_display = 'Not Set'

    print("\n+--------------------------------------------------+")
    print("|           DDI CLI Configuration Setup            |")
    print("+--------------------------------------------------+")
    print("|                                                  |")
    print(f"|  1. Grid Master IP:  {grid_master:<28} |")
    print(f"|  2. Admin Name:      {admin:<28} |")
    print(f"|  3. Password:        {password_display:<28} |")
    print("|                                                  |")
    print("|  4. Continue                                     |")
    print("|  q. Quit                                         |")
    print("|                                                  |")
    print("+--------------------------------------------------+")

@click.group(invoke_without_command=True)
@click.option('--network-view', default=None, help='The Infoblox network view to operate on.')
@click.pass_context
def main(ctx, network_view):
    """
    A CLI tool to sync network data from cloud providers to Infoblox.
    """
    try:
        config = load_config()
    except ConfigurationError as e:
        logger.error(f"Configuration Error: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    
    if 'infoblox' not in config:
        config['infoblox'] = {}

    infoblox_config = config['infoblox']
    
    changes_made = False
    
    # Always check/prompt for credentials if we are in interactive mode (no subcommand)
    # or if they are missing.
    interactive_mode = ctx.invoked_subcommand is None
    
    if interactive_mode:
        while True:
            display_config_dashboard(infoblox_config)
            choice = click.prompt("Enter choice", default='4', show_default=False)
            
            if choice == '1':
                current_ip = infoblox_config.get('grid_master_ip')
                if current_ip == 'YOUR_INFOBLOX_IP': current_ip = None
                new_ip = click.prompt('Enter Infoblox Grid Master IP', default=current_ip)
                if new_ip != current_ip:
                    infoblox_config['grid_master_ip'] = new_ip
                    changes_made = True
            
            elif choice == '2':
                # Handle legacy 'username' key if present
                if 'username' in infoblox_config and not 'admin_name' in infoblox_config:
                    infoblox_config['admin_name'] = infoblox_config.pop('username')
                
                current_admin = infoblox_config.get('admin_name')
                if current_admin == 'YOUR_INFOBLOX_USERNAME': current_admin = None
                new_admin = click.prompt('Enter Infoblox Admin Name', default=current_admin)
                if new_admin != current_admin:
                    infoblox_config['admin_name'] = new_admin
                    changes_made = True
            
            elif choice == '3':
                current_password = infoblox_config.get('password')
                if current_password == 'YOUR_INFOBLOX_PASSWORD': current_password = None
                
                password_prompt = 'Enter Infoblox Password'
                if current_password:
                    password_prompt += ' [********]'
                
                new_password = click.prompt(password_prompt, hide_input=True, default='', show_default=False)
                if new_password:
                    infoblox_config['password'] = new_password
                    changes_made = True
            
            elif choice == '4':
                # Validate before continuing
                gm = infoblox_config.get('grid_master_ip')
                an = infoblox_config.get('admin_name')
                pw = infoblox_config.get('password')
                
                if not gm or gm == 'YOUR_INFOBLOX_IP' or \
                   not an or an == 'YOUR_INFOBLOX_USERNAME' or \
                   not pw or pw == 'YOUR_INFOBLOX_PASSWORD':
                    click.echo("Error: Missing required configuration. Please set all fields.")
                    click.pause()
                    continue
                break
            
            elif choice.lower() == 'q':
                sys.exit(0)
             
    else:
        # Non-interactive mode: only prompt if missing
        if not infoblox_config.get('grid_master_ip') or infoblox_config.get('grid_master_ip') == 'YOUR_INFOBLOX_IP':
             infoblox_config['grid_master_ip'] = click.prompt('Enter Infoblox Grid Master IP')
             changes_made = True
        
        if 'username' in infoblox_config and not 'admin_name' in infoblox_config:
            infoblox_config['admin_name'] = infoblox_config.pop('username')

        if not infoblox_config.get('admin_name') or infoblox_config.get('admin_name') == 'YOUR_INFOBLOX_USERNAME':
            infoblox_config['admin_name'] = click.prompt('Enter Infoblox Admin Name')
            changes_made = True
            
        if not infoblox_config.get('password') or infoblox_config.get('password') == 'YOUR_INFOBLOX_PASSWORD':
            infoblox_config['password'] = click.prompt('Enter Infoblox Password', hide_input=True)
            changes_made = True

    if changes_made:
        if click.confirm('Do you want to save these settings to config.json?'):
            save_config(config)
            click.echo("Configuration saved.")

    grid_master_ip = infoblox_config['grid_master_ip']
    admin_name = infoblox_config['admin_name']
    password = infoblox_config['password']
    wapi_version = infoblox_config.get('wapi_version', '2.13.1')

    # --- Network View Selection ---
    if network_view is None:
        if interactive_mode:
            # Ask user if they want to select a view or use default 'All'
            action = prompt_numbered_list(
                "Select Network View?",
                ['Default (All)', 'Select from Infoblox']
            )
            
            if action == 'Select from Infoblox':
                # Initialize temporary manager to fetch views
                temp_manager = InfobloxManager(grid_master_ip, wapi_version, admin_name, password, 'All')
                try:
                    click.echo("Fetching network views from Infoblox...")
                    views = temp_manager.get_network_views()
                    if views:
                        view_names = sorted([view['name'] for view in views])
                        network_view = prompt_numbered_list(
                            "Select the Infoblox Network View:",
                            view_names
                        )
                    else:
                        click.echo("No network views found or error fetching them. Defaulting to 'All'.")
                        network_view = 'All'
                except Exception as e:
                    logger.error(f"Error fetching network views: {e}")
                    click.echo(f"Error fetching network views: {e}")
                    network_view = 'All'
            else:
                network_view = 'All'
        else:
            network_view = 'All'

    ctx.obj = {
        'config': config,
        'infoblox_manager': InfobloxManager(grid_master_ip, wapi_version, admin_name, password, network_view),
        'network_view': network_view
    }
    logger.info("Configuration loaded successfully.")
    logger.info(f"Grid Master: {grid_master_ip}")
    if network_view != 'All':
        logger.info(f"Operating on Network View: {network_view}")

    # If no subcommand is invoked, default to the menu
    if interactive_mode:
        ctx.invoke(menu)

# --- Provider Commands ---

@main.group()
@click.pass_context
def aws(ctx):
    """Commands for AWS."""
    provider_name = 'aws'
    provider_class = PROVIDER_CLASSES.get(provider_name)
    if not provider_class:
        click.echo(f"Error: Provider '{provider_name}' not found.")
        exit(1)
    
    # Store the provider instance in the context
    ctx.obj['provider'] = provider_class(ctx.obj['config'])

@aws.command()
@click.pass_context
def sync(ctx):
    """Sync AWS VPC data to Infoblox."""
    ctx.obj['provider'].sync(ctx.obj['infoblox_manager'])

@aws.command()
@click.argument('search_term')
@click.pass_context
def search(ctx, search_term):
    """Search for a resource in AWS."""
    ctx.obj['provider'].search(search_term)

@aws.command()
@click.pass_context
def audit(ctx):
    """Audit AWS resources."""
    ctx.obj['provider'].audit()

@aws.group()
@click.pass_context
def attributes(ctx):
    """Manage AWS Tags and Infoblox Extensible Attributes."""
    pass

@attributes.command(name='list-missing')
@click.pass_context
def list_missing(ctx):
    """List AWS tags that are missing as Infoblox EAs."""
    provider = ctx.obj['provider']
    infoblox_manager = ctx.obj['infoblox_manager']
    missing = provider.list_missing_eas(infoblox_manager)
    if missing:
        click.echo("The following AWS tags are missing as Extensible Attributes in Infoblox:")
        for tag in sorted(missing):
            click.echo(f"- {tag}")
    elif missing is not None:
        click.echo("No missing Extensible Attributes found. All AWS tags are in sync with Infoblox EAs.")

@attributes.command(name='create-missing')
@click.pass_context
def create_missing(ctx):
    """Create missing Infoblox EAs from AWS tags."""
    provider = ctx.obj['provider']
    infoblox_manager = ctx.obj['infoblox_manager']
    provider.create_missing_eas(infoblox_manager)

@attributes.command(name='analyze')
@click.pass_context
def analyze(ctx):
    """Analyze and find similarities between AWS tags and Infoblox EAs."""
    provider = ctx.obj['provider']
    infoblox_manager = ctx.obj['infoblox_manager']
    provider.analyze_eas(infoblox_manager)

@attributes.command(name='export')
@click.pass_context
def export(ctx):
    """Export the attribute analysis to JSON and CSV files."""
    provider = ctx.obj['provider']
    infoblox_manager = ctx.obj['infoblox_manager']

    # Generate default filename with date
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"extended-attributes_{timestamp}"

    base_filename = click.prompt(
        "Enter base filename for export (without extension)",
        default=default_filename
    )

    # Call provider method to export
    provider.export_analysis(infoblox_manager, base_filename)
    click.echo(f"Analysis exported to {base_filename}.json and {base_filename}.csv")



# --- Future provider command groups would go here ---
# @main.group()
# @click.pass_context
# def azure(ctx):
#     """Commands for Azure."""
#     ...

# --- Global Commands ---

@main.command()
@click.argument('search_term')
@click.pass_context
def search(ctx, search_term):
    """Search for a resource across all configured cloud providers."""
    click.echo(f"--- Starting global search for '{search_term}' ---")
    config = ctx.obj['config']
    for provider_name, provider_class in PROVIDER_CLASSES.items():
        if provider_name in config:
            click.echo(f"\n--- Searching in {provider_name.upper()} ---")
            provider = provider_class(config)
            provider.search(search_term)
    click.echo("\n--- Global search complete ---")


@main.command()
@click.pass_context
def audit(ctx):
    """Audit resources across all configured cloud providers."""
    click.echo(f"--- Starting global audit ---")
    config = ctx.obj['config']
    for provider_name, provider_class in PROVIDER_CLASSES.items():
        if provider_name in config:
            click.echo(f"\n--- Auditing in {provider_name.upper()} ---")
            provider = provider_class(config)
            provider.audit()
    click.echo("\n--- Global audit complete ---")


def _get_command_from_path(path):
    cmd = main
    for part in path:
        cmd = cmd.get_command(None, part)
    return cmd

def _display_menu(path, network_view):
    """Clears the screen and displays the menu for the given path."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    view_str = f"[{network_view}]"
    breadcrumbs = " > ".join(['Home', view_str] + path)
    
    current_command = _get_command_from_path(path)
    
    if not isinstance(current_command, click.Group):
        print("Error: Not a valid menu level.")
        return None

    commands = sorted(current_command.commands.items())
    
    # Calculate width based on breadcrumbs or fixed minimum
    width = max(len(breadcrumbs) + 4, 50)
    
    print(f"\n+{'-' * width}+")
    print(f"| {breadcrumbs:<{width-2}} |")
    print(f"+{'-' * width}+")
    print(f"|{' ' * width}|")

    for i, (name, cmd) in enumerate(commands, 1):
        help_text = cmd.get_short_help_str()
        print(f"|  {i}. {name.capitalize():<{width-6}} |")
        if help_text:
            # Truncate help text if too long for simple display
            max_help_len = width - 8
            if len(help_text) > max_help_len:
                help_text = help_text[:max_help_len-3] + "..."
            print(f"|     - {help_text:<{width-9}} |")
        print(f"|{' ' * width}|")
        
    print(f"|  0. Back{' ' * (width-10)} |")
    print(f"|  q. Quit{' ' * (width-10)} |")
    print(f"|{' ' * width}|")
    print(f"+{'-' * width}+")
    
    return commands

@main.command()
@click.pass_context
def menu(ctx):
    """Enter interactive, menu-driven mode."""
    
    infoblox_manager = ctx.obj['infoblox_manager']
    network_view = ctx.obj['network_view']
    
    path = []
    
    while True:
        try:
            commands = _display_menu(path, network_view)
            if commands is None:
                path.pop()
                continue

            choice = input("\nEnter your choice: ")

            if choice.lower() == 'q':
                break
            
            if choice == '0':
                if path:
                    path.pop()
                else:
                    break # Exit if at home
                continue

            try:
                choice_index = int(choice) - 1
                if not (0 <= choice_index < len(commands)):
                    raise ValueError()
            except ValueError:
                input("Invalid choice. Press Enter to continue...")
                continue

            selected_name, selected_cmd = commands[choice_index]
            
            if isinstance(selected_cmd, click.Group):
                path.append(selected_name)
            else:
                # This is an executable command
                # We need to invoke it directly using click's invoke mechanism
                # But first we might need arguments
                
                params_to_prompt = [p for p in selected_cmd.params if isinstance(p, click.Argument)]
                kwargs = {}
                
                try:
                    for param in params_to_prompt:
                        arg_val = input(f"Enter value for '{param.name}': ")
                        kwargs[param.name] = arg_val
                except (KeyboardInterrupt, EOFError):
                    print("\nCommand cancelled.")
                    continue

                print(f"\nExecuting: {selected_name}\n")
                
                # Invoke the command
                try:
                    ctx.invoke(selected_cmd, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing command: {e}")
                    print(f"Error: {e}")

                input("\nPress Enter to return to the menu...")

        except (KeyboardInterrupt, EOFError):
            break
    print("Exiting interactive menu.")


if __name__ == '__main__':
    main()
