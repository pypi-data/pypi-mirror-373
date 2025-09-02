# PYTHON_ARGCOMPLETE_OK
from ara_cli.ara_command_parser import action_parser
from ara_cli.error_handler import AraError
from ara_cli.version import __version__
from ara_cli.ara_command_action import (
    create_action,
    delete_action,
    rename_action,
    list_action,
    list_tags_action,
    prompt_action,
    chat_action,
    template_action,
    fetch_templates_action,
    read_action,
    reconnect_action,
    read_status_action,
    read_user_action,
    set_status_action,
    set_user_action,
    classifier_directory_action,
    scan_action,
    autofix_action,
    extract_action
)
from . import error_handler
import argcomplete
import sys
from os import getenv


def define_action_mapping():
    return {
        "create": create_action,
        "delete": delete_action,
        "rename": rename_action,
        "list": list_action,
        "list-tags": list_tags_action,
        "prompt": prompt_action,
        "chat": chat_action,
        "template": template_action,
        "fetch-templates": fetch_templates_action,
        "read": read_action,
        "reconnect": reconnect_action,
        "read-status": read_status_action,
        "read-user": read_user_action,
        "set-status": set_status_action,
        "set-user": set_user_action,
        "classifier-directory": classifier_directory_action,
        "scan": scan_action,
        "autofix": autofix_action,
        "extract": extract_action
    }


def handle_invalid_action(args):
    raise AraError("Invalid action provided. Type ara -h for help", error_code=1)


def is_debug_mode_enabled():
    """Check if debug mode is enabled via environment variable."""
    return getenv('ARA_DEBUG', '').lower() in ('1', 'true', 'yes')


def setup_parser():
    """Create and configure the argument parser."""
    parser = action_parser()
    
    # Show examples when help is called
    if any(arg in sys.argv for arg in ["-h", "--help"]):
        parser.add_examples = True
    
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode for detailed error output"
    )
    
    return parser


def configure_debug_mode(args, env_debug_mode):
    """Configure debug mode based on arguments and environment."""
    if (hasattr(args, 'debug') and args.debug) or env_debug_mode:
        error_handler.debug_mode = True


def should_show_help(args):
    """Check if help should be displayed."""
    return not hasattr(args, "action") or not args.action


def execute_action(args, action_mapping):
    """Execute the specified action."""
    action = action_mapping.get(args.action, handle_invalid_action)
    action(args)


def cli():
    debug_mode = is_debug_mode_enabled()
    
    try:
        parser = setup_parser()
        action_mapping = define_action_mapping()
        
        argcomplete.autocomplete(parser)
        args = parser.parse_args()
        
        configure_debug_mode(args, debug_mode)
        
        if should_show_help(args):
            parser.print_help()
            return
            
        execute_action(args, action_mapping)
        
    except KeyboardInterrupt:
        print("\n[INFO] Operation cancelled by user", file=sys.stderr)
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e:
        error_handler.handle_error(e, context="cli")


if __name__ == "__main__":
    cli()