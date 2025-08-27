import os

# Create the project structure
project_structure = {
    "drf_identity_service": {
        "config": ["__init__.py", "settings.py", "urls.py", "wsgi.py", "asgi.py"],
        "core": ["__init__.py", "permissions.py", "middleware.py", "utils.py", "exceptions.py"],
        "accounts": ["__init__.py", "models.py", "serializers.py", "views.py", "urls.py", "admin.py", "apps.py"],
        "audit": ["__init__.py", "middleware.py", "urls.py", "apps.py"],
        "root_files": ["manage.py", "Makefile", "pyproject.toml", "docker-compose.yml", "Dockerfile", "README.md", "Documentation.md", "project-plan.md", "quick-start.md"]
    }
}

def print_structure(structure, indent=0):
    for key, value in structure.items():
        print("  " * indent + key + "/")
        if isinstance(value, dict):
            print_structure(value, indent + 1)
        elif isinstance(value, list):
            for file in value:
                print("  " * (indent + 1) + file)

print("Project Structure:")
print_structure(project_structure)