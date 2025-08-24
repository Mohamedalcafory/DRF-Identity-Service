import os

# Create the project structure
project_structure = {
    "pharma_drf_service": {
        "backend": {
            "config": ["__init__.py", "settings.py", "urls.py", "wsgi.py"],
            "core": ["__init__.py", "permissions.py", "middleware.py", "utils.py", "exceptions.py"],
            "accounts": ["__init__.py", "models.py", "serializers.py", "views.py", "urls.py"],
            "sites": ["__init__.py", "models.py", "serializers.py", "views.py", "urls.py"],
            "batches": ["__init__.py", "models.py", "serializers.py", "views.py", "urls.py"],
            "serializations": ["__init__.py", "models.py", "serializers.py", "views.py", "urls.py"],
            "inspections": ["__init__.py", "models.py", "serializers.py", "views.py", "urls.py"],
            "audit": ["__init__.py", "models.py", "signals.py", "middleware.py", "serializers.py", "views.py", "urls.py"],
            "tests": ["__init__.py", "test_auth.py", "test_sites.py", "test_audit.py", "conftest.py"]
        },
        "infra": ["docker-compose.yml"],
        "scripts": ["manage.py"],
        "root_files": ["Makefile", "pyproject.toml", ".env.example", "README.md", ".gitignore", ".pre-commit-config.yaml"]
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