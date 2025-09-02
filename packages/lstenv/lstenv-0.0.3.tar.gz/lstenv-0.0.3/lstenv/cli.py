import argparse
import sys
from pathlib import Path

from .core import (
    generate_example_env,
    sync_env_files,
    audit_env_files,
    print_audit_report,
    get_colored_output,
    write_env_file,
)


def main():
    parser = argparse.ArgumentParser(
        description="Generate, sync, and audit .env files by scanning Python code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lstenv generate
  lstenv generate --example-file .env.template
  lstenv sync --example-file .env.template
  lstenv sync --clean
  lstenv audit --example-file .env.template
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    generate_parser = subparsers.add_parser(
        'generate',
        help='Generate .env.example from Python files'
    )
    generate_parser.add_argument(
        '--directory', '-d',
        type=Path,
        default=Path.cwd(),
        help='Directory to scan (default: current directory)'
    )
    generate_parser.add_argument(
        '--example-file',
        type=str,
        default='.env.example',
        help='Name of example file to generate (default: .env.example)'
    )
    generate_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed scanning information'
    )
    
    sync_parser = subparsers.add_parser(
        'sync',
        help='Sync .env with .env.example'
    )
    sync_parser.add_argument(
        '--directory', '-d',
        type=Path,
        default=Path.cwd(),
        help='Directory to work in (default: current directory)'
    )
    sync_parser.add_argument(
        '--clean',
        action='store_true',
        help='Remove variables not in .env.example'
    )
    sync_parser.add_argument(
        '--example-file',
        type=str,
        default='.env.example',
        help='Name of example file to sync with (default: .env.example)'
    )
    sync_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed scanning information'
    )
    
    audit_parser = subparsers.add_parser(
        'audit',
        help='Audit .env files and show report'
    )
    audit_parser.add_argument(
        '--directory', '-d',
        type=Path,
        default=Path.cwd(),
        help='Directory to audit (default: current directory)'
    )
    audit_parser.add_argument(
        '--example-file',
        type=str,
        default='.env.example',
        help='Name of example file to audit (default: .env.example)'
    )
    audit_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed scanning information'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'generate':
            return handle_generate(args.directory, args.example_file, args.verbose)
        elif args.command == 'sync':
            return handle_sync(args.directory, args.clean, args.example_file, args.verbose)
        elif args.command == 'audit':
            return handle_audit(args.directory, args.example_file, args.verbose)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except ValueError as e:
        print(f"{get_colored_output('Error:', '31')} {e}")
        return 1
    except IOError as e:
        print(f"{get_colored_output('Error:', '31')} {e}")
        return 1
    except Exception as e:
        print(f"{get_colored_output('Error:', '31')} Unexpected error: {e}")
        return 1
    
    return 0


def handle_generate(directory: Path, example_file: str, verbose: bool = False) -> int:
    print(f"Scanning Python files in {directory}...")
    
    if verbose:
        print(f"Verbose mode: Will show detailed file-by-file scanning information")
    
    env_vars = generate_example_env(directory, verbose=verbose)
    
    if not env_vars:
        print(f"{get_colored_output('No environment variables found', '36')}")
        print("No environment variables found")
        return 0
    
    example_path = directory / example_file
    write_env_file(example_path, env_vars, preserve_comments=False)
    
    print(f"{get_colored_output('Generated', '32')} {example_file} file with {len(env_vars)} variables")
    print(f"File location: {example_path}")
    print(f"Variables found:")
    
    api_vars = [var for var in env_vars.keys() if 'api' in var.lower()]
    db_vars = [var for var in env_vars.keys() if 'database' in var.lower() or 'db' in var.lower()]
    config_vars = [var for var in env_vars.keys() if 'config' in var.lower()]
    other_vars = [var for var in env_vars.keys() if var not in api_vars + db_vars + config_vars]
    
    if api_vars:
        print(f"  API/Tokens ({len(api_vars)}): {', '.join(api_vars)}")
    if db_vars:
        print(f"  Database ({len(db_vars)}): {', '.join(db_vars)}")
    if config_vars:
        print(f"  Configuration ({len(config_vars)}): {', '.join(config_vars)}")
    if other_vars:
        print(f"  Other ({len(other_vars)}): {', '.join(other_vars)}")
    
    print(f"\nDone.")
    
    return 0


def handle_sync(directory: Path, clean: bool, example_file: str, verbose: bool = False) -> int:
    env_path = directory / ".env"
    example_path = directory / example_file
    
    if not example_path.exists():
        print(f"{get_colored_output('Error:', '31')} {example_file} file not found")
        return 1
    
    print(f"Syncing .env with {example_file}...")
    
    env_vars = sync_env_files(directory, clean, example_file, verbose=verbose)
    write_env_file(env_path, env_vars)
    
    action = "Cleaned" if clean else "Synced"
    print(f"{get_colored_output(action, '32')} .env file with {len(env_vars)} variables")
    print(f"File location: {env_path}")
    
    if clean:
        print(f"Removed variables not present in {example_file}")
    
    return 0


def handle_audit(directory: Path, example_file: str, verbose: bool = False) -> int:
    env_path = directory / ".env"
    example_path = directory / example_file
    
    if not env_path.exists() and not example_path.exists():
        print(f"{get_colored_output('No .env files found', '36')}")
        return 0
    
    print(f"Auditing environment files in {directory}...")
    present, missing, unused = audit_env_files(directory, example_file, verbose=verbose)
    print_audit_report(present, missing, unused, example_file, verbose=verbose)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
