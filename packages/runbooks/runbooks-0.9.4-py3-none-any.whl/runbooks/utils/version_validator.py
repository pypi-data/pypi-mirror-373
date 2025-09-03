"""
Version Management Validation Utilities

This module provides utilities to detect and prevent version drift across
the runbooks package and its modules.
"""

import importlib
import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Avoid circular imports by defining central version directly
CENTRAL_VERSION = "0.9.3"  # Must match runbooks.__init__.__version__


class VersionDriftError(Exception):
    """Raised when version drift is detected in CI/CD pipeline."""
    pass


def get_all_module_versions() -> Dict[str, str]:
    """
    Collect versions from all runbooks modules.
    
    Returns:
        Dict mapping module names to their reported versions
    """
    modules = [
        "runbooks",
        "runbooks.finops",
        "runbooks.operate", 
        "runbooks.security",
        "runbooks.cfat",
        "runbooks.inventory",
        "runbooks.remediation",
        "runbooks.vpc",
        "runbooks.sre",
        "runbooks.cloudops"
    ]
    
    versions = {}
    
    for module_name in modules:
        try:
            # Import the module
            module = importlib.import_module(module_name)
            
            # Get version
            if hasattr(module, '__version__'):
                versions[module_name] = module.__version__
            else:
                versions[module_name] = "No version found"
                
        except ImportError as e:
            versions[module_name] = f"Import error: {e}"
        except Exception as e:
            versions[module_name] = f"Error: {e}"
            
    return versions


def check_pyproject_version() -> Tuple[bool, str, str]:
    """
    Check if pyproject.toml version matches centralized version.
    
    Returns:
        Tuple of (is_matching, pyproject_version, central_version)
    """
    try:
        from importlib.metadata import version as _pkg_version
        pyproject_version = _pkg_version("runbooks")
        return (pyproject_version == CENTRAL_VERSION, pyproject_version, CENTRAL_VERSION)
    except Exception as e:
        return (False, f"Error reading pyproject.toml: {e}", CENTRAL_VERSION)


def validate_version_consistency(strict: bool = False) -> Dict[str, any]:
    """
    Validate version consistency across all modules.
    
    Args:
        strict: If True, raise VersionDriftError on inconsistencies
        
    Returns:
        Dictionary with validation results
        
    Raises:
        VersionDriftError: If strict=True and inconsistencies found
    """
    results = {
        "central_version": CENTRAL_VERSION,
        "module_versions": get_all_module_versions(),
        "pyproject_check": check_pyproject_version(),
        "inconsistencies": [],
        "all_consistent": True
    }
    
    # Check module versions
    for module_name, module_version in results["module_versions"].items():
        if module_name == "runbooks":
            continue  # Skip root module
            
        if isinstance(module_version, str) and not module_version.startswith(("Error:", "No version", "Import error:")):
            if module_version != CENTRAL_VERSION:
                inconsistency = {
                    "module": module_name,
                    "expected": CENTRAL_VERSION,
                    "found": module_version,
                    "type": "module_version_mismatch"
                }
                results["inconsistencies"].append(inconsistency)
                results["all_consistent"] = False
    
    # Check pyproject.toml
    is_matching, pyproject_version, _ = results["pyproject_check"]
    if not is_matching and not pyproject_version.startswith("Error:"):
        inconsistency = {
            "module": "pyproject.toml",
            "expected": CENTRAL_VERSION,
            "found": pyproject_version,
            "type": "pyproject_version_mismatch"
        }
        results["inconsistencies"].append(inconsistency)
        results["all_consistent"] = False
    
    # Raise error in strict mode
    if strict and not results["all_consistent"]:
        error_msg = f"Version drift detected:\n"
        for inc in results["inconsistencies"]:
            error_msg += f"  - {inc['module']}: expected {inc['expected']}, got {inc['found']}\n"
        raise VersionDriftError(error_msg)
    
    return results


def print_version_report() -> None:
    """Print a formatted version consistency report."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        
        console = Console()
        validation_results = validate_version_consistency()
        
        # Header
        console.print(Panel(
            f"[bold blue]Version Management Report[/bold blue]\n"
            f"Central Version: [green]{validation_results['central_version']}[/green]",
            title="Runbooks Version Validation"
        ))
        
        # Module versions table
        table = Table(title="Module Version Status")
        table.add_column("Module", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Status", style="magenta")
        
        for module_name, version in validation_results["module_versions"].items():
            if isinstance(version, str) and version.startswith(("Error:", "No version", "Import error:")):
                status = "[red]Error[/red]"
                version_display = f"[red]{version}[/red]"
            elif version == validation_results["central_version"]:
                status = "[green]✓ OK[/green]"
                version_display = f"[green]{version}[/green]"
            else:
                status = "[red]✗ Mismatch[/red]"
                version_display = f"[red]{version}[/red]"
                
            table.add_row(module_name, version_display, status)
        
        console.print(table)
        
        # Pyproject.toml check
        is_matching, pyproject_version, central_version = validation_results["pyproject_check"]
        if is_matching:
            console.print("[green]✓ pyproject.toml version matches central version[/green]")
        else:
            console.print(f"[red]✗ pyproject.toml version mismatch: {pyproject_version} vs {central_version}[/red]")
        
        # Overall status
        if validation_results["all_consistent"]:
            console.print("\n[bold green]✓ All versions are consistent[/bold green]")
        else:
            console.print("\n[bold red]✗ Version inconsistencies detected[/bold red]")
            for inc in validation_results["inconsistencies"]:
                console.print(f"  - {inc['module']}: expected {inc['expected']}, got {inc['found']}")
                
    except ImportError:
        # Fallback without Rich
        validation_results = validate_version_consistency()
        
        print(f"=== Version Management Report ===")
        print(f"Central Version: {validation_results['central_version']}")
        print()
        
        print("Module Versions:")
        for module_name, version in validation_results["module_versions"].items():
            status = "OK" if version == validation_results["central_version"] else "MISMATCH"
            print(f"  {module_name}: {version} ({status})")
        
        is_matching, pyproject_version, _ = validation_results["pyproject_check"]
        pyproject_status = "OK" if is_matching else "MISMATCH"
        print(f"  pyproject.toml: {pyproject_version} ({pyproject_status})")
        
        if validation_results["all_consistent"]:
            print("\n✓ All versions are consistent")
        else:
            print("\n✗ Version inconsistencies detected:")
            for inc in validation_results["inconsistencies"]:
                print(f"  - {inc['module']}: expected {inc['expected']}, got {inc['found']}")


def cli_main():
    """CLI entry point for version validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate runbooks version consistency")
    parser.add_argument("--strict", action="store_true", 
                       help="Exit with error code if inconsistencies found")
    
    args = parser.parse_args()
    
    try:
        print_version_report()
        
        if args.strict:
            validate_version_consistency(strict=True)
            
    except VersionDriftError as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()