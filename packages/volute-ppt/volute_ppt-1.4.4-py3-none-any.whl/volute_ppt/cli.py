#!/usr/bin/env python3
"""
Volute-PPT CLI entrypoints for server variants.
"""

def run_ppt_server():
    """Run the PowerPoint server from the command line."""
    from .ppt_server import main
    main()

def run_local_server():
    """Run the local server from the command line."""
    from .server_local import main
    main()

def run_cloud_server():
    """Run the cloud server from the command line."""
    from .cloud_server import main
    main()
