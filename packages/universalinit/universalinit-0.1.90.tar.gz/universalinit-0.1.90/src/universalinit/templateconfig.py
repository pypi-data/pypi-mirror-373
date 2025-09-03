from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml


class ProjectType(Enum):
    """Supported project types."""
    # Frontend frameworks
    ANDROID = "android"
    ANGULAR = "angular"
    ASTRO = "astro"
    FLUTTER = "flutter"
    IOS = "ios"
    KOTLIN = "kotlin"
    LIGHTNINGJS = "lightningjs"
    NATIVESCRIPT = "nativescript"
    NEXTJS = "nextjs"
    SOLANANEXTJS = "solananextjs"
    NODE = "node"
    NUXT = "nuxt"
    PYTHON = "python"
    QWIK = "qwik"
    REACT = "react"
    REACT_NATIVE = "reactnative"
    REMIX = "remix"
    REMOTION = "remotion"
    SLIDEV = "slidev"
    SVELTE = "svelte"
    TYPESCRIPT = "typescript"
    VITE = "vite"
    VUE = "vue"

    # Backend frameworks
    DJANGO = "django"
    DOTNET = "dotnet"
    EXPRESS = "express"
    FASTAPI = "fastapi"
    FLASK = "flask"
    SPRINGBOOT = "springboot"

    # Databases
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    NATIVE = "native"
    @classmethod
    def from_string(cls, value: str) -> 'ProjectType':
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Unsupported project type: {value}")

@dataclass
class ProjectConfig:
    """Configuration for project initialization."""
    name: str
    version: str
    description: str
    author: str
    project_type: ProjectType
    output_path: Path
    parameters: Dict[str, Any]

    def _get_default_db_user(self) -> str:
        """Get default database user based on project type."""
        default_users = {
            ProjectType.POSTGRESQL: 'kaviapostgres',
            ProjectType.MONGODB: 'kaviamongodb',
            ProjectType.MYSQL: 'kaviamysql',
            ProjectType.SQLITE: 'kaviasqlite',
        }
        return default_users.get(self.project_type, 'dbuser')

    def get_replaceable_parameters(self) -> Dict[str, str]:
        """Get dictionary of replaceable parameters."""
        project_name = self.name
        if self.project_type in [ProjectType.SPRINGBOOT]:
            # Replace hyphens and spaces with underscores, remove special characters
            project_name = self.name.replace('-', '').replace(' ', '').replace('_', '')
            # Ensure it starts with a letter (Java requirement)
            if project_name and not project_name[0].isalpha():
                project_name = 'App' + project_name
        
        replacements = {
            'KAVIA_TEMPLATE_PROJECT_NAME': project_name,
            'KAVIA_PROJECT_DESCRIPTION': self.description,
            'KAVIA_PROJECT_AUTHOR': self.author,
            'KAVIA_PROJECT_VERSION': self.version,
            'KAVIA_USE_TYPESCRIPT': str(self.parameters.get('typescript', False)).lower(),
            'KAVIA_STYLING_SOLUTION': self.parameters.get('styling_solution', 'css'),
            'KAVIA_PROJECT_DIRECTORY': str(self.output_path),
            'KAVIA_DB_NAME': self.parameters.get('database_name', self.name.replace('-', '_')),
            'KAVIA_DB_USER': self.parameters.get('database_user', self._get_default_db_user()),
            'KAVIA_DB_PASSWORD': self.parameters.get('database_password', 'kaviadefaultpassword'),
            'KAVIA_DB_PORT': str(self.parameters.get('database_port', 5000)),
        }
        return replacements

    def replace_parameters(self, content: str) -> str:
        """Replace parameters in content."""
        replacements = self.get_replaceable_parameters()
        for key, value in replacements.items():
            str_value = str(value)
            content = content.replace(f"${key}", str_value)
            content = content.replace(f"{{{key}}}", str_value)
        return content


@dataclass
class ProcessingScript:
    """Post processing configuration."""
    script: str

@dataclass
class BuildCommand:
    """Build command configuration."""
    command: str
    working_directory: str

@dataclass
class InstallDependenciesCommand:
    """Configuration to install dependencies."""
    command: str
    working_directory: str

@dataclass
class EnvironmentConfig:
    """Environment configuration."""
    environment_initialized: bool
    node_version: str = ""
    npm_version: str = ""
    flutter_version: str = ""
    dart_version: str = ""
    java_version: str = ""
    gradle_version: str = ""
    android_sdk_version: str = ""

@dataclass
class ConfigureEnvironment:
    """Run Environment configuration"""
    command: str
    working_directory: str
    
@dataclass
class RunTool:
    """Run tool configuration."""
    command: str
    working_directory: str

@dataclass
class TestTool:
    """Test tool configuration."""
    command: str
    working_directory: str

@dataclass
class OpenapiGenerationTool:
    """Openapi Generation tool"""
    command: str
    working_directory: str

@dataclass
class TemplateInitInfo:
    """Complete template initialization information."""
    build_cmd: BuildCommand
    install_dependencies: InstallDependenciesCommand
    env_config: EnvironmentConfig
    init_files: List[str]
    init_minimal: str
    run_tool: RunTool
    test_tool: TestTool
    init_style: str
    linter_script: str
    pre_processing: ProcessingScript
    post_processing: ProcessingScript
    entry_point_url: Optional[str] = None
    openapi_generation: Optional[OpenapiGenerationTool] = None
    configure_environment: Optional[ConfigureEnvironment] = None

class TemplateConfigProvider:
    """Provides template initialization configuration."""
    def __init__(self, template_path: Path, config: ProjectConfig):
        self.template_path = template_path
        self.config_path = template_path / "config.yml"
        self.project_config = config

    def get_init_info(self) -> TemplateInitInfo:
        """Get template initialization information."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found at {self.config_path}")

        with open(self.config_path, 'r') as f:
            data = f.read()
            data = self.project_config.replace_parameters(data)

            config_data = yaml.safe_load(data)

        return TemplateInitInfo(
            configure_environment=ConfigureEnvironment(
                command=config_data.get('configure_environment', {}).get('command', ''),
                working_directory=config_data.get('configure_environment', {}).get('working_directory', '')
            ) if 'configure_environment' in config_data else None,
            build_cmd=BuildCommand(
                command=config_data['build_cmd']['command'],
                working_directory=config_data['build_cmd']['working_directory']
            ),
            install_dependencies=InstallDependenciesCommand(
                command=config_data['install_dependencies']['command'],
                working_directory=config_data['install_dependencies']['working_directory']
            ),
            env_config=EnvironmentConfig(
                environment_initialized=config_data['env']['environment_initialized'],
                node_version=config_data['env'].get('node_version', ''),
                npm_version=config_data['env'].get('npm_version', ''),
                flutter_version=config_data['env'].get('flutter_version', ''),
                dart_version=config_data['env'].get('dart_version', ''),
                java_version=config_data['env'].get('java_version', ''),
                gradle_version=config_data['env'].get('gradle_version', ''),
                android_sdk_version=config_data['env'].get('android_sdk_version', '')
            ),
            init_files=config_data.get('init_files', []),
            init_minimal=config_data['init_minimal'],
            openapi_generation=OpenapiGenerationTool (
                command=config_data.get('openapi_generation', {}).get('command', ''),
                working_directory=config_data.get('openapi_generation', {}).get('working_directory', '')
            ),
            run_tool=RunTool(
                command=config_data['run_tool']['command'],
                working_directory=config_data['run_tool']['working_directory']
            ),
            entry_point_url=config_data.get('entry_point_url', None),
            test_tool=TestTool(
                command=config_data['test_tool']['command'],
                working_directory=config_data['test_tool']['working_directory']
            ),
            init_style=config_data.get('init_style', ''),
            linter_script=config_data['linter']['script_content'],
            pre_processing=ProcessingScript(
                script=config_data.get('pre_processing', {}).get('script', '')
            ),
            post_processing=ProcessingScript(
                script=config_data.get('post_processing', {}).get('script', '')
            )
        )
