"""
eXonware - Enterprise Python Ecosystem

A comprehensive namespace package for enterprise-grade Python frameworks and tools.

This package serves as the central hub for all eXonware projects:
- xSystem: Enterprise-grade Python framework with 24 serialization formats ✅ AVAILABLE
- xQuery: Advanced database abstraction (coming soon)
- xData: Big data processing framework (coming soon)
- xNode: Enterprise Node.js toolkit (coming soon)
- xAction: Workflow automation engine (coming soon)
- xSchema: Universal schema validation (coming soon)

🚀 QUICK START:
  import exonware
  exonware.install_all()  # Auto-installs all available packages
  
🎯 OR INSTALL INDIVIDUALLY:
  pip install exonware-xsystem  # 24 serialization formats

Visit https://exonware.com for more information.
"""

__version__ = "1.0.0"
__author__ = "Eng. Muhammad AlShehri"
__email__ = "connect@exonware.com"
__company__ = "eXonware.com"
__license__ = "MIT"

# Namespace package marker
__path__ = __import__('pkgutil').extend_path(__path__, __name__)

# Project registry
PROJECTS = {
    "xsystem": {
        "name": "xSystem",
        "package": "exonware-xsystem", 
        "description": "Enterprise-grade Python framework with 24 serialization formats, AI-powered performance optimization, military-grade security",
        "status": "available",
        "version": "0.0.1a",
        "github": "https://github.com/Exonware/xsystem",
        "pypi": "https://pypi.org/project/exonware-xsystem/",
        "docs": "https://github.com/Exonware/xsystem/tree/main/docs"
    },
    "xquery": {
        "name": "xQuery",
        "package": "xlib-xquery",
        "description": "Advanced database abstraction with intelligent query optimization", 
        "status": "coming_soon",
        "github": "https://github.com/exonware/xquery",
        "docs": "https://github.com/exonware/xquery/tree/main/docs"
    },
    "xdata": {
        "name": "xData", 
        "package": "xlib-xdata",
        "description": "High-performance data processing with streaming capabilities",
        "status": "coming_soon",
        "github": "https://github.com/exonware/xdata",
        "docs": "https://github.com/exonware/xdata/tree/main/docs"
    },
    "xnode": {
        "name": "xNode",
        "package": "xlib-xnode", 
        "description": "TypeScript-first enterprise tools for Node.js applications",
        "status": "coming_soon",
        "github": "https://github.com/exonware/xnode",
        "docs": "https://github.com/exonware/xnode/tree/main/docs"
    },
    "xaction": {
        "name": "xAction",
        "package": "xlib-xaction",
        "description": "Intelligent automation and workflow orchestration",
        "status": "coming_soon", 
        "github": "https://github.com/exonware/xaction",
        "docs": "https://github.com/exonware/xaction/tree/main/docs"
    },
    "xschema": {
        "name": "xSchema",
        "package": "xlib-xschema",
        "description": "Cross-language schema validation and transformation",
        "status": "coming_soon",
        "github": "https://github.com/exonware/xschema", 
        "docs": "https://github.com/exonware/xschema/tree/main/docs"
    }
}

def list_projects(status_filter=None):
    """
    List all eXonware projects.
    
    Args:
        status_filter (str, optional): Filter by status ('available', 'coming_soon')
    
    Returns:
        dict: Dictionary of projects matching the filter
    """
    if status_filter:
        return {k: v for k, v in PROJECTS.items() if v["status"] == status_filter}
    return PROJECTS.copy()

def get_project_info(project_name):
    """
    Get information about a specific project.
    
    Args:
        project_name (str): Name of the project (e.g., 'xsystem')
    
    Returns:
        dict: Project information or None if not found
    """
    return PROJECTS.get(project_name.lower())

def install_instructions(project_name=None):
    """
    Get installation instructions for a project or all projects.
    
    Args:
        project_name (str, optional): Specific project name
    
    Returns:
        str: Installation instructions
    """
    if project_name:
        project = get_project_info(project_name)
        if not project:
            return f"Project '{project_name}' not found."
        
        if project["status"] == "available":
            return f"pip install {project['package']}"
        else:
            return f"{project['name']} is coming soon. Stay tuned!"
    
    # Return instructions for all available projects
    available = list_projects("available")
    if not available:
        return "No projects are currently available for installation."
    
    instructions = ["Available projects:"]
    for key, project in available.items():
        instructions.append(f"  pip install {project['package']}  # {project['name']}")
    
    return "\n".join(instructions)

# Convenience functions
def available_projects():
    """Get all available projects."""
    return list_projects("available")

def coming_soon_projects():
    """Get all coming soon projects."""
    return list_projects("coming_soon")

# Export public API
__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "__company__",
    "__license__",
    "PROJECTS",
    "list_projects",
    "get_project_info", 
    "install_instructions",
    "available_projects",
    "coming_soon_projects"
]
