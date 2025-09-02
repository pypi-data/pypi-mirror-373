import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


def scan_python_files(directory: Path = None, verbose: bool = False) -> Set[str]:
    if directory is None:
        directory = Path.cwd()
    elif isinstance(directory, str):
        directory = Path(directory)
    
    if not directory.exists():
        raise ValueError(f"Directory does not exist: {directory}")
    
    env_vars = set()
    python_files = list(directory.rglob("*.py"))
    
    if verbose:
        print(f"Found {len(python_files)} Python files to scan")
        print(f"Excluded directories: .venv/, __pycache__/, .git/, node_modules/")
    
    python_files = [
        f for f in python_files 
        if "lstenv" not in str(f) 
        and ".venv" not in str(f)
        and "venv" not in str(f)
        and "__pycache__" not in str(f)
        and ".git" not in str(f)
        and "node_modules" not in str(f)
    ]
    
    patterns = [
        r'os\.getenv\(["\']([^"\']+)["\']',
        r'os\.environ\[["\']([^"\']+)["\']\]',
        r'os\.environ\.get\(["\']([^"\']+)["\']',
        r'os\.environ\.get\(["\']([^"\']+)["\'],\s*[^)]+\)',
        r'getenv\(["\']([^"\']+)["\']',
        r'environ\[["\']([^"\']+)["\']\]',
    ]
    
    for file_path in python_files:
        try:
            content = file_path.read_text(encoding='utf-8')
            
            if any(skip_pattern in content.lower() for skip_pattern in ['mock', 'test_', 'pytest']):
                if verbose:
                    print(f"  Skipped: {file_path.name} (test file)")
                continue
                
            file_vars = set()
            for pattern in patterns:
                matches = re.findall(pattern, content)
                filtered_matches = [
                    match for match in matches 
                    if len(match) > 1
                    and not match.isdigit()
                    and not match.startswith('_')
                ]
                file_vars.update(filtered_matches)
            
            if verbose:
                if file_vars:
                    print(f"  Scanning: {file_path.name}")
                    print(f"    Found: {', '.join(sorted(file_vars))}")
                else:
                    print(f"  Scanning: {file_path.name}")
                    print(f"    No environment variables found")
            
            env_vars.update(file_vars)
                
        except (UnicodeDecodeError, IOError, PermissionError):
            if verbose:
                print(f"  Skipped: {file_path.name} (permission/encoding error)")
            continue
    
    return env_vars


def parse_env_file(file_path: Path) -> Dict[str, str]:
    if not file_path.exists():
        return {}
    
    env_vars = {}
    try:
        content = file_path.read_text(encoding='utf-8')
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                if key and key not in env_vars:
                    env_vars[key] = value
    except (UnicodeDecodeError, IOError, PermissionError):
        pass
    
    return env_vars


def write_env_file(file_path: Path, env_vars: Dict[str, str], preserve_comments: bool = True):
    if preserve_comments and file_path.exists():
        try:
            existing_content = file_path.read_text(encoding='utf-8')
            lines = existing_content.split('\n')
            
            new_lines = []
            existing_keys = set()
            
            for line in lines:
                if line.strip() and not line.strip().startswith('#') and '=' in line:
                    key = line.split('=', 1)[0].strip()
                    existing_keys.add(key)
                    if key in env_vars:
                        new_lines.append(f"{key}={env_vars[key]}")
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            for key, value in env_vars.items():
                if key not in existing_keys:
                    new_lines.append(f"{key}={value}")
            
            content = '\n'.join(new_lines)
        except (UnicodeDecodeError, IOError, PermissionError):
            content = '\n'.join(f"{key}={value}" for key, value in env_vars.items())
    else:
        content = '\n'.join(f"{key}={value}" for key, value in env_vars.items())
    
    try:
        file_path.write_text(content, encoding='utf-8')
    except (IOError, PermissionError):
        raise IOError(f"Cannot write to file: {file_path}")


def generate_example_env(directory: Path = None, verbose: bool = False) -> Dict[str, str]:
    env_vars = scan_python_files(directory, verbose=verbose)
    example_vars = {}
    
    for var in sorted(env_vars):
        example_vars[var] = ""
    
    return example_vars


def sync_env_files(directory: Path = None, clean: bool = False, example_file: str = ".env.example", verbose: bool = False) -> Dict[str, str]:
    if directory is None:
        directory = Path.cwd()
    
    env_path = directory / ".env"
    example_path = directory / example_file
    
    example_vars = parse_env_file(example_path)
    env_vars = parse_env_file(env_path)
    
    if clean:
        env_vars = {k: v for k, v in env_vars.items() if k in example_vars}
    else:
        for key in example_vars:
            if key not in env_vars:
                env_vars[key] = ""
    
    return env_vars


def audit_env_files(directory: Path = None, example_file: str = ".env.example", verbose: bool = False) -> Tuple[Set[str], Set[str], Set[str]]:
    if directory is None:
        directory = Path.cwd()
    
    env_path = directory / ".env"
    example_path = directory / example_file
    
    env_vars = set(parse_env_file(env_path).keys())
    example_vars = set(parse_env_file(example_path).keys())
    code_vars = scan_python_files(directory)
    
    present = env_vars & example_vars
    missing = example_vars - env_vars
    unused = env_vars - code_vars
    
    return present, missing, unused


def get_colored_output(text: str, color_code: str) -> str:
    return f"\033[{color_code}m{text}\033[0m"


def print_audit_report(present: Set[str], missing: Set[str], unused: Set[str], example_file: str = ".env.example", verbose: bool = False):
    print("Environment Variables Audit Report")
    print("=" * 50)
    
    total_vars = len(present) + len(missing) + len(unused)
    
    if verbose:
        print(f"\nTotal variables found: {total_vars}")
        print(f"Variables in .env: {len(present)}")
        print(f"Variables in {example_file}: {len(present) + len(missing)}")
        print(f"Variables in code: {len(present) + len(missing) + len(unused)}")
    
    if present:
        print(f"\n{get_colored_output('Present', '32')} ({len(present)}):")
        for var in sorted(present):
            print(f"  {var}")
    
    if missing:
        print(f"\n{get_colored_output('Missing', '33')} ({len(missing)}):")
        for var in sorted(missing):
            print(f"  {var}")
        print(f"  Use 'lstenv sync' to add missing variables")
    
    if unused:
        print(f"\n{get_colored_output('Unused', '31')} ({len(unused)}):")
        for var in sorted(unused):
            print(f"  {var}")
        print(f"  Use 'lstenv sync --clean' to remove unused variables")
    
    if not present and not missing and not unused:
        print(f"\n{get_colored_output('No variables found', '36')}")
        print("  No environment variables found")
    
    print(f"\nSummary:")
    print(f"  Total variables: {total_vars}")
    print(f"  Present: {len(present)}")
    print(f"  Missing: {len(missing)}")
    print(f"  Unused: {len(unused)}")
    
    if missing:
        print(f"\nRecommendations:")
        print(f"  Add missing variables to .env file")
        print(f"  Use 'lstenv sync' to automatically sync")
    
    print()
