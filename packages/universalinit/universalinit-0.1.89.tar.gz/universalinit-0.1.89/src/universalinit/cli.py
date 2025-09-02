import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any

from universalinit.templateconfig import TemplateInitInfo
from universalinit.universalinit import ProjectConfig, ProjectType, ProjectInitializer


def parse_parameters(params_str: str) -> Dict[str, Any]:
    if not params_str:
        return {}

    params = {}
    for param in params_str.split(','):
        if '=' not in param:
            continue
        key, value = param.split('=', 1)
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit() and value.count('.') == 1:
            value = float(value)
        params[key.strip()] = value
    return params


def create_project_config(args) -> ProjectConfig:
    """Create ProjectConfig from CLI arguments."""
    return ProjectConfig(
        name=args.name,
        version=args.version,
        description=args.description,
        author=args.author,
        project_type=ProjectType.from_string(args.type),
        output_path=Path(args.output),
        parameters=parse_parameters(args.parameters)
    )

def create_minimal_project_config(project_type: str, parameters: str = None) -> ProjectConfig:
    """Create minimal ProjectConfig just for retrieving template info."""
    return ProjectConfig(
        name="temp",
        version="0.0.0",
        description="",
        author="temp",
        project_type=ProjectType.from_string(project_type),
        output_path=Path("/tmp"),
        parameters=parse_parameters(parameters) if parameters else {}
    )

def make_path_absolute(path: str, base_path: Path) -> str:
    """Convert a relative path to absolute path."""
    return str(base_path / path)

def template_init_info_to_dict(init_info: TemplateInitInfo, project_path: Path) -> dict:
    """Convert TemplateInitInfo to a dictionary with absolute paths for JSON serialization."""

    return {
        "configure_environment":{
            "command": init_info.configure_environment.command if init_info.configure_environment else '',
            "working_directory": init_info.configure_environment.working_directory if init_info.configure_environment else '',
        },
        "build_cmd": {
            "command": init_info.build_cmd.command,
            "working_directory": init_info.build_cmd.working_directory
        },
        "install_dependencies": {
            "command": init_info.install_dependencies.command,
            "working_directory": init_info.install_dependencies.working_directory
        },
        "env_config": {
            "environment_initialized": init_info.env_config.environment_initialized,
            "node_version": init_info.env_config.node_version,
            "npm_version": init_info.env_config.npm_version
        },
        "init_files": [make_path_absolute(f, project_path) for f in init_info.init_files],
        "init_minimal": init_info.init_minimal,
        "openapi_generation": {
            "command": init_info.openapi_generation.command,
            "working_directory": init_info.openapi_generation.working_directory
        },
        "run_tool": {
            "command": init_info.run_tool.command,
            "working_directory": init_info.run_tool.working_directory
        },
        "test_tool": {
            "command": init_info.test_tool.command,
            "working_directory": init_info.test_tool.working_directory
        },
        "init_style": init_info.init_style,
        "linter_script": init_info.linter_script,
        "pre_processing": {
            "script": init_info.pre_processing.script
        },
        "post_processing": {
            "script": init_info.post_processing.script
        }
    }

def output_json(success: bool, message: str, template_info: TemplateInitInfo = None, project_path: Path = None):
    """Helper function to format JSON output."""
    result = {
        "success": success,
        "message": message,
        "template_config": template_init_info_to_dict(template_info, project_path) if template_info and project_path else {}
    }
    print("[OUTPUT]")
    print(json.dumps(result, indent=2))
    return 0 if success else 1

def output_get_run_command(project_type: str, run_command: str):
    """Output the run command for a specific project type."""
    result = {
        "success": True,
        "project_type": project_type,
        "run_command": run_command
    }
    print(json.dumps(result, indent=2))
    return 0

def handle_get_run_command(args):
    """Handle the --get-run-command option."""
    initializer = ProjectInitializer()
    
    try:
        # Create minimal config just to get template info
        config = create_minimal_project_config(args.type, args.parameters)
        
        # Create template instance to get init info
        template = initializer.template_factory.create_template(config)
        init_info = template.get_init_info()
        
        # Extract run command
        run_command = init_info.run_tool.command if init_info.run_tool else ""
        
        if not run_command:
            print(json.dumps({
                "success": False,
                "project_type": args.type,
                "message": f"No run command defined for project type: {args.type}"
            }, indent=2))
            return 1
        
        return output_get_run_command(args.type, run_command)
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "project_type": args.type,
            "message": f"Error retrieving run command: {str(e)}"
        }, indent=2))
        return 1

def main():
    parser = argparse.ArgumentParser(
        description='Universal Project Initializer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  # Initialize a new project:
  uniinit --name my-app --type react --author "Kavia" --output ./my-react-app --parameters typescript=true,styling_solution=styled-components
  
  # Get run command for a framework:
  uniinit --get-run-command --type react
  uniinit --get-run-command --type nextjs --parameters typescript=true
  
  # More initialization examples:
  uniinit --name myservice --type python --author "Kavia" --output ./myservice --parameters async=true,use_fastapi=true
  uniinit --name my-vue-app --type vue --author "Kavia" --output ./my-vue-app
  uniinit --name my-flutter-app --type flutter --author "Kavia" --output ./my-flutter-app
  uniinit --name my-android-app --type android --author "Kavia" --output ./my-android-app --parameters min_sdk=24,target_sdk=34,gradle_version=8.12
  uniinit --name my-astro-site --type astro --author "Kavia" --output ./my-astro-site --parameters typescript=true
  uniinit --name my-django-site --type django --author "Kavia" --output ./my-django-site
  uniinit --name my-dotnet-api --type dotnet --author "Kavia" --output ./my-dotnet-api
  uniinit --name my-express-site --type express --author "Kavia" --output ./my-express-site --parameters typescript=true
  uniinit --name my-fastapi-site --type fastapi --author "Kavia" --output ./my-fastapi-site
  uniinit --name my-flask-site --type flask --author "Kavia" --output ./my-flask-site
  uniinit --name my-springboot-site --type springboot --author "Kavia" --output ./my-springboot-site
  uniinit --name my-vite-app --type vite --author "Kavia" --output ./my-vite-app --parameters typescript=true
  uniinit --name my-nextjs-app --type nextjs --author "Kavia" --output ./my-nextjs-app
  uniinit --name my-solana-nextjs-app --type solananextjs --author "Kavia" --output ./my-nextjs-app
  uniinit --name my-nuxt-app --type nuxt --author "Kavia" --output ./my-nuxt-app
  uniinit --name my-ns-app --type nativescript --author "Kavia" --output ./my-ns-app --parameters typescript=true
  uniinit --name my-slides --type slidev --author "Kavia" --output ./my-slides
  uniinit --name my-svelte-app --type svelte --author "Kavia" --output ./my-svelte-app
  uniinit --name my-remix-app --type remix --author "Kavia" --output ./my-remix-app --parameters typescript=true,styling_solution=tailwind
  uniinit --name my-ts-app --type typescript --author "Kavia" --output ./my-ts-app
  uniinit --name my-remotion-app --type remotion --author "Kavia" --output ./my-remotion-app
  uniinit --name my-angular-app --type angular --author "Kavia" --output ./my-angular-app
  uniinit --name my-qwik-app --type qwik --author "Kavia" --output ./my-qwik-app
  uniinit --name my-kotlin-app --type kotlin --author "Kavia" --output ./my-kotlin-app
  uniinit --name my-lightningjs-app --type lightningjs --author "Kavia" --output ./my-lightningjs-app
  uniinit --name my-rn-app --type reactnative --author "Kavia" --output ./my-rn-app
  uniinit --name my-postgres --type postgresql --author "Kavia" --output ./my-postgres --parameters database_name=myapp,database_user=appuser,database_password=secure123,database_port=5000
  uniinit --name my-mongo --type mongodb --author "Kavia" --output ./my-mongo --parameters database_name=myapp,database_user=appuser,database_password=dbpass,database_port=5000
  uniinit --name my-mysql --type mysql --author "Kavia" --output ./my-mysql --parameters database_name=myapp,database_user=root,database_password=secure123,database_port=5000
  uniinit --name my-sqlite --type sqlite --author "Kavia" --output ./my-sqlite --parameters database_name=myapp,database_user=root,database_password=secure123



Available project types:
  - android
  - angular
  - astro
  - django
  - dotnet
  - express
  - fastapi
  - flask
  - springboot
  - flutter
  - ios
  - kotlin
  - lightningjs
  - nativescript
  - nextjs
  - solananextjs
  - node
  - nuxt
  - python
  - qwik
  - react
  - reactnative
  - remix
  - remotion
  - slidev
  - svelte
  - typescript
  - vite
  - vue
  - postgresql
  - mongodb
  - mysql
  - sqlite
    """
)

    # Special command for getting run command
    parser.add_argument('--get-run-command', action='store_true', 
                        help='Get the run command for a specific project type')
    
    # Required for normal operation, optional for get-run-command
    parser.add_argument('--name', help='Project name')
    parser.add_argument('--version', default='0.1.0', help='Project version (default: 0.1.0)')
    parser.add_argument('--description', default='', help='Project description')
    parser.add_argument('--author', help='Project author')
    parser.add_argument('--type', help='Project type (react, ios, android, python, node, etc.)')
    parser.add_argument('--output', help='Output directory path')
    parser.add_argument('--parameters', help='Additional parameters as key=value pairs, comma-separated')
    parser.add_argument('--config', help='Path to JSON config file (overrides other arguments)')

    args = parser.parse_args()

    # Handle special get-run-command mode
    if args.get_run_command:
        if not args.type:
            print(json.dumps({
                "success": False,
                "message": "Error: --type is required when using --get-run-command"
            }, indent=2))
            return 1
        return handle_get_run_command(args)
    
    # Normal project initialization mode
    if not args.name or not args.author or not args.type or not args.output:
        parser.error("--name, --author, --type, and --output are required for project initialization")
    
    initializer = ProjectInitializer()

    try:
        config = create_project_config(args)

        template = initializer.template_factory.create_template(config)
        init_info = template.get_init_info()

        print(f"\nInitializing {config.project_type.value} project: {config.name}")
        print(f"Output directory: {config.output_path}")
        print("\nTemplate configuration:")
        print(f"Build command: {init_info.build_cmd.command}")
        print(f"Required environment:")
        if hasattr(init_info.env_config, 'node_version'):
            print(f"  Node.js: {init_info.env_config.node_version}")
        if hasattr(init_info.env_config, 'npm_version'):
            print(f"  npm: {init_info.env_config.npm_version}")

        success = initializer.initialize_project(config)

        if success:
            return output_json(True, "Project initialized successfully!", init_info, config.output_path)
        else:
            return output_json(False, "Project initialization failed", init_info, config.output_path)

    except Exception as e:
        return output_json(False, f"Error: {str(e)}")

if __name__ == '__main__':
    main()