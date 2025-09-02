import os
import subprocess
import tempfile
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional
from pathlib import Path
import json

from .templateconfig import TemplateConfigProvider, TemplateInitInfo, ProjectType, ProjectConfig

class ProcessingStep(Enum):
    """Enum for processing steps."""
    PRE_PROCESSING = "Pre-processing"
    POST_PROCESSING = "Post-processing"

class TemplateProvider:
    """Manages template locations and access."""

    def __init__(self, base_template_path: Optional[Path] = None):
        if base_template_path is None:
            # Default to a 'templates' directory in the package
            self.base_path = Path(__file__).parent / "templates"
        else:
            self.base_path = base_template_path

    def get_template_path(self, project_type: ProjectType) -> Path:
        """Get the template path for a specific project type."""
        template_path = self.base_path / project_type.value
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found for {project_type.value}")
        return template_path


class ProjectTemplate(ABC):
    """Base class for project templates."""

    def __init__(self, config: ProjectConfig, template_provider: TemplateProvider):
        self.config = config
        self.template_provider = template_provider
        self.template_path = template_provider.get_template_path(config.project_type)
        self.config_provider = TemplateConfigProvider(self.template_path, self.config)

    @abstractmethod
    def validate_parameters(self) -> bool:
        """Validate the project parameters."""
        pass
    def get_init_info(self) -> TemplateInitInfo:
        """Get template initialization information."""
        return self.config_provider.get_init_info()

    def get_run_command(self) -> str:
        """Get run command."""
        init_info = self.config_provider.get_init_info()
        return init_info.run_tool.command
    
    def get_entry_point_url(self) -> str:
        """Get entry point url for the template."""
        init_info = self.config_provider.get_init_info()
        return init_info.entry_point_url
    
    @abstractmethod
    def generate_structure(self) -> None:
        """Generate the project structure."""
        pass

    @abstractmethod
    def setup_testing(self) -> None:
        """Setup testing infrastructure."""
        pass

    def initialize(self) -> bool:
        """Initialize the project."""
        try:
            if not self.validate_parameters():
                raise ValueError("Invalid project parameters")

            self.run_pre_processing()
            self.generate_structure()
            self.setup_testing()
            self.run_post_processing()
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Failed to initialize project: {str(e)}")
            return False

    def run_pre_processing(self) -> None:
        """Run pre-processing script if available."""
        init_info = self.get_init_info()
        if init_info.pre_processing and init_info.pre_processing.script:
            self._run_processing_script(init_info.pre_processing.script, ProcessingStep.PRE_PROCESSING)
        else:
            pass

    def run_post_processing(self) -> None:
        """Run post-processing script if available."""
        init_info = self.get_init_info()
        if init_info.post_processing and init_info.post_processing.script:
            self._run_processing_script(init_info.post_processing.script, ProcessingStep.POST_PROCESSING)

    def wait_for_post_process_completed(self, timeout: int = 30) -> bool:
        """Wait for post-processing completion with a timeout.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if post-processing completed successfully, False otherwise
        """
        status_file = self.config.output_path / "post_process_status.lock"
        
        # Check if post-processing was even initiated
        init_info = self.get_init_info()
        if not (init_info.post_processing and init_info.post_processing.script):
            return True
            
        start_time = time.time()
        while time.time() - start_time < timeout:
            if status_file.exists():
                status = status_file.read_text().strip()
                if status == "SUCCESS":
                    return True
                elif status == "FAILED":
                    return False
                # If still running, continue waiting
            # Status file may not exist yet, so we continue waiting
            time.sleep(0.5)
            
        # Timeout reached
        return False

    def _run_processing_script(self, script_content: str, process_type: str) -> None:
        """Run a processing script with the given content in the background.
        
        Args:
            script_content: The content of the script to run
            process_type: The type of processing ("Pre-processing" or "Post-processing")
        """
        # Create a temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as temp_file:
            temp_file.write(script_content)
            temp_file.flush()
            script_path = temp_file.name

        try:
            os.chmod(script_path, 0o755)
            
            # If this is post-processing, run it in a background process
            if process_type.value == ProcessingStep.POST_PROCESSING.value:
                status_file = self.config.output_path / "post_process_status.lock"
                log_file = self.config.output_path / "post_process.log"
                
                # Create a wrapper script that manages status file and runs the actual script
                with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as wrapper_file:
                    wrapper_content = f"""#!/bin/bash
# Write RUNNING status to file
echo "RUNNING" > "{status_file}"

# Run the actual script
"{script_path}" > "{log_file}" 2>&1
EXIT_CODE=$?

# Check if successful
if [ $EXIT_CODE -eq 0 ]; then
    echo "SUCCESS" > "{status_file}"
else
    echo "FAILED" > "{status_file}"
    echo "Process failed with exit code $EXIT_CODE" >> "{log_file}"
fi

# Clean up the original script file
rm -f "{script_path}"

# Clean up self
rm -f "$0"
"""
                    wrapper_file.write(wrapper_content)
                    wrapper_file.flush()
                    wrapper_path = wrapper_file.name
                
                os.chmod(wrapper_path, 0o755)
                
                print(f"Starting {process_type} in background...")
                
                # Use nohup to make the process immune to hangups when the shell closes
                try:
                    res = subprocess.Popen(
                        ['nohup', wrapper_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL,
                        start_new_session=True,  # Detach from parent process
                        preexec_fn=os.setpgrp    # Ensure process is in its own process group
                    )
                except (OSError, ValueError, subprocess.SubprocessError) as e:
                    # Fall back to a simpler version without process group isolation
                    print(f"Warning: Could not use process isolation, falling back to simple execution: {str(e)}")
                    res = subprocess.Popen(
                        ['nohup', wrapper_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL,
                        start_new_session=True
                    )
                
            else:
                # For pre-processing, run synchronously
                result = subprocess.run(
                    [script_path],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if result.stderr:
                    print(f"{process_type} errors:\n{result.stderr}")
                
                # Clean up the temporary script file
                Path(script_path).unlink()

        except subprocess.CalledProcessError as e:
            print(f"{process_type} failed with exit code {e.returncode}")
            print(f"Error output:\n{e.stderr}")
            
            # For pre-processing, we want to halt on error
            if process_type == "Pre-processing":
                # Clean up the temporary script file
                Path(script_path).unlink()
                raise
            else:
                # For post-processing failures in background mode, the wrapper script will handle it
                pass

class ProjectTemplateFactory:
    """Factory for creating project templates."""

    def __init__(self):
        self._template_classes: Dict[ProjectType, type[ProjectTemplate]] = {}
        self.template_provider = TemplateProvider()

    def register_template(self, project_type: ProjectType,
                          template_class: type[ProjectTemplate]) -> None:
        """Register a new template class for a project type."""
        self._template_classes[project_type] = template_class

    def create_template(self, config: ProjectConfig) -> ProjectTemplate:
        """Create a template instance for the specified project type."""
        template_class = self._template_classes.get(config.project_type)
        if not template_class:
            raise ValueError(f"---> No template registered for {config.project_type.value}")
        return template_class(config, self.template_provider)


class ProjectInitializer:
    """Main project initialization orchestrator."""

    def __init__(self):
        self.template_factory = ProjectTemplateFactory()
        # Register frontend framework templates
        self.template_factory.register_template(ProjectType.ANDROID, AndroidTemplate)
        self.template_factory.register_template(ProjectType.ANGULAR, AngularTemplate)
        self.template_factory.register_template(ProjectType.ASTRO, AstroTemplate)
        self.template_factory.register_template(ProjectType.FLUTTER, FlutterTemplate)
        self.template_factory.register_template(ProjectType.KOTLIN, KotlinTemplate)
        self.template_factory.register_template(ProjectType.LIGHTNINGJS, LightningjsTemplate)
        self.template_factory.register_template(ProjectType.NATIVESCRIPT, NativeScriptTemplate)
        self.template_factory.register_template(ProjectType.NEXTJS, NextJSTemplate)
        self.template_factory.register_template(ProjectType.SOLANANEXTJS, SolanaNextJSTemplate)
        self.template_factory.register_template(ProjectType.NUXT, NuxtTemplate)
        self.template_factory.register_template(ProjectType.QWIK, QwikTemplate)
        self.template_factory.register_template(ProjectType.REACT, ReactTemplate)
        self.template_factory.register_template(ProjectType.REACT_NATIVE, ReactNativeTemplate)
        self.template_factory.register_template(ProjectType.REMIX, RemixTemplate)
        self.template_factory.register_template(ProjectType.REMOTION, RemotionTemplate)
        self.template_factory.register_template(ProjectType.SLIDEV, SlidevTemplate)
        self.template_factory.register_template(ProjectType.SVELTE, SvelteTemplate)
        self.template_factory.register_template(ProjectType.TYPESCRIPT, TypeScriptTemplate)
        self.template_factory.register_template(ProjectType.VITE, ViteTemplate)
        self.template_factory.register_template(ProjectType.VUE, VueTemplate)
        # Register backend framework templates
        self.template_factory.register_template(ProjectType.DJANGO, DjangoTemplate)
        self.template_factory.register_template(ProjectType.DOTNET, DotNetTemplate)
        self.template_factory.register_template(ProjectType.EXPRESS, ExpressTemplate)
        self.template_factory.register_template(ProjectType.FASTAPI, FastAPITemplate)
        self.template_factory.register_template(ProjectType.FLASK, FlaskTemplate)
        self.template_factory.register_template(ProjectType.SPRINGBOOT, SpringBootTemplate)
        # Register database templates
        self.template_factory.register_template(ProjectType.POSTGRESQL, PostgreSQLTemplate)
        self.template_factory.register_template(ProjectType.MONGODB, MongoDBTemplate)
        self.template_factory.register_template(ProjectType.MYSQL, MySQLTemplate)
        self.template_factory.register_template(ProjectType.SQLITE, SQLiteTemplate)
        self.template_factory.register_template(ProjectType.NATIVE, CommonTemplate)
        self.template = None
    def initialize_project(self, config: ProjectConfig) -> bool:
        """Initialize a project using the appropriate template."""
        self.template = self.template_factory.create_template(config)
        
        return self.template.initialize()

    def wait_for_post_process_completed(self, timeout: int = 30) -> bool:
        """Wait for post-processing completion with a timeout.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if post-processing completed successfully, False otherwise
        """
        if self.template is None:
            raise ValueError("Project not initialized")
        return self.template.wait_for_post_process_completed(timeout)

    @staticmethod
    def load_config(config_path: Path) -> ProjectConfig:
        """Load project configuration from a JSON file."""
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            return ProjectConfig(
                name=config_data['name'],
                version=config_data['version'],
                description=config_data['description'],
                author=config_data['author'],
                project_type=ProjectType.from_string(config_data['project_type']),
                output_path=Path(config_data['output_path']),
                parameters=config_data.get('parameters', {})
            )


class AndroidTemplate(ProjectTemplate):
    """Template implementation for Android projects."""

    def validate_parameters(self) -> bool:
        # No required parameters for basic template, but we'll support optional ones
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Android projects may have hidden files
        )

    def setup_testing(self) -> None:
        # Testing is already configured in the template
        pass

class CommonTemplate(ProjectTemplate):
    """Template implementation for Angular projects."""

    def validate_parameters(self) -> bool:
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True
        )

    def setup_testing(self) -> None:
        pass


class AngularTemplate(ProjectTemplate):
    """Template implementation for Angular projects."""

    def validate_parameters(self) -> bool:
        # Angular template has predetermined configurations, no required parameters
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True
        )

    def setup_testing(self) -> None:
        # Angular testing is already configured in the standard template
        pass


class AstroTemplate(ProjectTemplate):
    """Template implementation for Astro projects."""

    def validate_parameters(self) -> bool:
        # Define which parameters are allowed (not required)
        allowed_params = {'typescript', 'integration_tailwind', 'integration_react', 
                         'integration_vue', 'integration_svelte'}
        # If no parameters provided, that's fine
        if not self.config.parameters:
            return True
        # All provided parameters should be in the allowed list
        return all(param in allowed_params for param in self.config.parameters.keys())

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Include hidden files like .gitignore
        )

    def setup_testing(self) -> None:
        # Astro testing is already configured in the standard template
        pass


class DjangoTemplate(ProjectTemplate):
    """Template implementation for Django projects."""

    def validate_parameters(self) -> bool:
        # Define which parameters are allowed (not required)
        allowed_params = {}
        # If no parameters provided, that's fine
        if not self.config.parameters:
            return True
        # All provided parameters should be in the allowed list
        return all(param in allowed_params for param in self.config.parameters.keys())

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Include hidden files like .gitignore
        )

    def setup_testing(self) -> None:
        pass


class DotNetTemplate(ProjectTemplate):
    """Template implementation for DotNet projects."""

    def validate_parameters(self) -> bool:
        # Define which parameters are allowed (not required)
        allowed_params = {}
        # If no parameters provided, that's fine
        if not self.config.parameters:
            return True
        # All provided parameters should be in the allowed list
        return all(param in allowed_params for param in self.config.parameters.keys())

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Include hidden files like .gitignore
        )

    def setup_testing(self) -> None:
        pass


class ExpressTemplate(ProjectTemplate):
    """Template implementation for Express projects."""

    def validate_parameters(self) -> bool:
        # Define which parameters are allowed (not required)
        allowed_params = {'typescript'}
        # If no parameters provided, that's fine
        if not self.config.parameters:
            return True
        # All provided parameters should be in the allowed list
        return all(param in allowed_params for param in self.config.parameters.keys())

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Include hidden files like .gitignore
        )

    def setup_testing(self) -> None:
        pass


class FastAPITemplate(ProjectTemplate):
    """Template implementation for FastAPI projects."""

    def validate_parameters(self) -> bool:
        # Define which parameters are allowed (not required)
        allowed_params = {}
        # If no parameters provided, that's fine
        if not self.config.parameters:
            return True
        # All provided parameters should be in the allowed list
        return all(param in allowed_params for param in self.config.parameters.keys())

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Include hidden files like .gitignore
        )

    def setup_testing(self) -> None:
        pass


class FlaskTemplate(ProjectTemplate):
    """Template implementation for Flask projects."""

    def validate_parameters(self) -> bool:
        # Define which parameters are allowed (not required)
        allowed_params = {}
        # If no parameters provided, that's fine
        if not self.config.parameters:
            return True
        # All provided parameters should be in the allowed list
        return all(param in allowed_params for param in self.config.parameters.keys())

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Include hidden files like .gitignore
        )

    def setup_testing(self) -> None:
        pass

class SpringBootTemplate(ProjectTemplate):
    """Template implementation for Spring Boot projects."""

    def validate_parameters(self) -> bool:
        # Spring Boot has simpler requirements, most configuration is in the template
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True
        )

    def setup_testing(self) -> None:
        # Spring Boot testing is already configured in the template
        pass

class FlutterTemplate(ProjectTemplate):
    """Template implementation for Flutter projects."""

    def validate_parameters(self) -> bool:
        # Flutter has simpler requirements, most configuration is in the template
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()

        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True # Flutter relies on hidden files
        )

    def setup_testing(self) -> None:
        # Flutter testing is already configured in the standard template
        pass


class KotlinTemplate(ProjectTemplate):
    """Template implementation for Kotlin projects."""

    def validate_parameters(self) -> bool:
        # No required parameters for basic template, but we'll support optional ones
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Kotlin projects may have hidden files
        )

    def setup_testing(self) -> None:
        # Testing is already configured in the template
        pass


class LightningjsTemplate(ProjectTemplate):
    """Template implementation for LightningJS projects."""

    def validate_parameters(self) -> bool:
        # Lightningjs has no required parameters for basic setup
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Include .gitignore, .eslintrc, etc.
        )

    def setup_testing(self) -> None:
        # Testing is already configured in the Lightningjs template
        pass


class NativeScriptTemplate(ProjectTemplate):
    """Template implementation for NativeScript projects."""

    def validate_parameters(self) -> bool:
        # No required parameters for the basic NativeScript template
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # NativeScript uses hidden files
        )

    def setup_testing(self) -> None:
        # Testing configuration is included in the template
        pass


class NextJSTemplate(ProjectTemplate):
    """Template implementation for NextJS projects."""

    def validate_parameters(self) -> bool:
        # NextJS has similar configuration patterns as React
        required_params = {'typescript', 'styling_solution'}
        for param in required_params:
            if param not in self.config.parameters:
                self.config.parameters[param] = True if param == 'typescript' else 'css'
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Include .gitignore, .eslintrc, etc.
        )

    def setup_testing(self) -> None:
        # Testing is already configured in the NextJS template
        pass


class SolanaNextJSTemplate(ProjectTemplate):
    """Template implementation for Solana-NextJS projects."""

    def validate_parameters(self) -> bool:
        required_params = {'typescript', 'styling_solution'}
        for param in required_params:
            if param not in self.config.parameters:
                self.config.parameters[param] = True if param == 'typescript' else 'css'
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Include .gitignore, .eslintrc, etc.
        )

    def setup_testing(self) -> None:
        # Testing is already configured in the NextJS template
        pass


class NuxtTemplate(ProjectTemplate):
    """Template implementation for Nuxt projects."""

    def validate_parameters(self) -> bool:
        # Nuxt template has predetermined configurations, similar to Vue
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True
        )

    def setup_testing(self) -> None:
        # Testing is already configured in the template
        pass


class QwikTemplate(ProjectTemplate):
    """Template implementation for Qwik projects."""

    def validate_parameters(self) -> bool:
        # Qwik template has predetermined configurations, no required parameters
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Qwik may have important hidden files like .vscode
        )

    def setup_testing(self) -> None:
        # Testing is already configured in the template
        pass


# Example implementation for React projects
class ReactTemplate(ProjectTemplate):
    """Template implementation for React projects."""

    def validate_parameters(self) -> bool:
        required_params = {'typescript', 'styling_solution'}
        return all(param in self.config.parameters for param in required_params)

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()

        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True
        )

    def setup_testing(self) -> None:
        # Setup Jest and React Testing Library
        test_setup_path = self.template_path / "test-setup"
        if test_setup_path.exists():
            FileSystemHelper.copy_template(
                test_setup_path,
                self.config.output_path / "test",
                {'{KAVIA_TEMPLATE_PROJECT_NAME}': self.config.name}
            )


class ReactNativeTemplate(ProjectTemplate):
    """Template implementation for React projects."""

    def validate_parameters(self) -> bool:
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()

        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True
        )

    def setup_testing(self) -> None:
        pass


class RemixTemplate(ProjectTemplate):
    """Template implementation for Remix projects."""

    def validate_parameters(self) -> bool:
        # Required parameters for Remix projects
        required_params = {'typescript', 'styling_solution'}
        return all(param in self.config.parameters for param in required_params)

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()

        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements, 
            include_hidden=True
        )

    def setup_testing(self) -> None:
        # Setup testing for Remix if test-setup directory exists
        test_setup_path = self.template_path / "test-setup"
        if test_setup_path.exists():
            FileSystemHelper.copy_template(
                test_setup_path,
                self.config.output_path / "test",
                {'{KAVIA_TEMPLATE_PROJECT_NAME}': self.config.name}
            )


class RemotionTemplate(ProjectTemplate):
    """Template implementation for Remotion projects."""

    def validate_parameters(self) -> bool:
        # Remotion is TypeScript-based by default, no required parameters
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True
        )

    def setup_testing(self) -> None:
        # Testing is already configured in the template
        pass


class SlidevTemplate(ProjectTemplate):
    """Template implementation for Slidev presentations."""

    def validate_parameters(self) -> bool:
        # Slidev has simpler requirements, most configuration is in the template
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Slidev uses hidden files like .gitignore, netlify.toml, vercel.json
        )

    def setup_testing(self) -> None:
        # Slidev testing is configured through the package.json in the template
        pass


class SvelteTemplate(ProjectTemplate):
    """Template implementation for Svelte projects."""

    def validate_parameters(self) -> bool:
        # Svelte has simpler requirements, most configuration is in the template
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True
        )

    def setup_testing(self) -> None:
        # Testing is already configured in the template
        pass


class TypeScriptTemplate(ProjectTemplate):
    """Template implementation for TypeScript projects."""

    def validate_parameters(self) -> bool:
        # TypeScript has simpler requirements, module configurations can be optional
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True
        )

    def setup_testing(self) -> None:
        # TypeScript testing is already configured in the template
        pass


class ViteTemplate(ProjectTemplate):
    """Template implementation for Vite projects."""

    def validate_parameters(self) -> bool:
        # Vite has no required parameters for basic setup
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True
        )

    def setup_testing(self) -> None:
        # Testing is configured in the template
        pass


class VueTemplate(ProjectTemplate):
    """Template implementation for Vue projects."""

    def validate_parameters(self) -> bool:
        # Vue template has predetermined configurations, no required parameters
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True
        )

    def setup_testing(self) -> None:
        # Testing is already configured in the template
        pass


class PostgreSQLTemplate(ProjectTemplate):
    """Template implementation for PostgreSQL database projects."""

    def validate_parameters(self) -> bool:
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        base_path = Path(__file__).parent / "common"
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True,
            extra_files=[
                str(Path.joinpath(base_path, 'db_visualizer')),
                str(Path.joinpath(base_path, 'backup_db.sh')),
                str(Path.joinpath(base_path, 'restore_db.sh')),
            ],
        )

    def setup_testing(self) -> None:
        pass


class MongoDBTemplate(ProjectTemplate):
    """Template implementation for MongoDB database projects."""

    def validate_parameters(self) -> bool:
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        base_path = Path(__file__).parent / "common"

        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True,
            extra_files=[
                str(Path.joinpath(base_path, 'db_visualizer')),
                str(Path.joinpath(base_path, 'backup_db.sh')),
                str(Path.joinpath(base_path, 'restore_db.sh')),
            ],
        )

    def setup_testing(self) -> None:
        pass


class MySQLTemplate(ProjectTemplate):
    """Template implementation for MySQL database projects."""

    def validate_parameters(self) -> bool:
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        base_path = Path(__file__).parent / "common"
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True,
            extra_files=[
                str(Path.joinpath(base_path, 'db_visualizer')),
                str(Path.joinpath(base_path, 'backup_db.sh')),
                str(Path.joinpath(base_path, 'restore_db.sh')),
            ],
        )

    def setup_testing(self) -> None:
        pass


class SQLiteTemplate(ProjectTemplate):
    """Template implementation for SQLite database projects."""

    def validate_parameters(self) -> bool:
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        base_path = Path(__file__).parent / "common"
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True,
            extra_files=[
                str(Path.joinpath(base_path, 'db_visualizer')),
                str(Path.joinpath(base_path, 'backup_db.sh')),
                str(Path.joinpath(base_path, 'restore_db.sh')),
            ],
        )

    def setup_testing(self) -> None:
        pass


class FileSystemHelper:
    """Helper class for file system operations."""

    @staticmethod
    def _apply_replacements(text: str, replacements: Dict[str, str]) -> str:
        """Apply variable replacements to text."""
        for key, value in replacements.items():
            text = text.replace(f"${key}", str(value))
            text = text.replace(f"{{{key}}}", str(value))
        return text

    @staticmethod
    def _apply_path_replacements(path: Path, replacements: Dict[str, str]) -> Path:
        """Apply variable replacements to file path."""
        path_str = str(path)
        for key, value in replacements.items():
            path_str = path_str.replace(f"${key}", str(value))
            path_str = path_str.replace(f"{{{key}}}", str(value))
        return Path(path_str)

    @staticmethod
    def _copy_file(src: Path, dst: Path, replacements: Dict[str, str]) -> None:
        """Copy a single file with variable replacement."""
        # Apply replacements to destination path
        dst = FileSystemHelper._apply_path_replacements(dst, replacements)
        
        # Ensure parent directories exist
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Try to read as text and apply replacements
            content = src.read_text()
            content = FileSystemHelper._apply_replacements(content, replacements)
            dst.write_text(content)
        except UnicodeDecodeError:
            # Just copy the file as is if it can't be decoded as text
            dst.write_bytes(src.read_bytes())

    @staticmethod
    def _should_skip_file(item: Path, excluded_files: set, include_hidden: bool) -> bool:
        """Check if a file should be skipped."""
        # Skip excluded files
        if item.name in excluded_files:
            return True
        
        # Skip python special files
        if item.name.startswith('__') and item.name.endswith('__'):
            return True
        
        # Skip hidden files if not included
        if not include_hidden and item.name.startswith('.') and item.is_file():
            return True
        
        return False

    @staticmethod
    def _copy_directory_contents(src_dir: Path, dst_dir: Path, replacements: Dict[str, str], excluded_files: set = None, include_hidden: bool = True) -> None:
        """Copy directory contents with variable replacement."""

        if excluded_files is None:
            excluded_files = set()
        
        for item in src_dir.rglob("*"):
            # Skip files based on rules
            if FileSystemHelper._should_skip_file(item, excluded_files, include_hidden):
                continue
            
            relative_path = item.relative_to(src_dir)
            destination = dst_dir / relative_path
            
            if item.is_dir():
                destination.mkdir(exist_ok=True, parents=True)
            else:
                FileSystemHelper._copy_file(item, destination, replacements)

    @staticmethod
    def copy_template(src: Path, dst: Path, replacements: Dict[str, str], 
                     include_hidden: bool = False, extra_files: List[str] = None) -> None:
        """Copy template files with variable replacement."""
        if not src.exists():
            raise FileNotFoundError(f"Template path {src} does not exist")

        if not dst.exists():
            dst.mkdir(parents=True)

        # Define files to exclude
        excluded_files = {'config.yml'}  # Add config.yml to exclusions
        
        # Copy main template contents
        FileSystemHelper._copy_directory_contents(src, dst, replacements, excluded_files, include_hidden)
        
        # Process extra files and directories
        if extra_files:
            for extra_path_str in extra_files:
                extra_path = Path(extra_path_str)
                if not extra_path.exists():
                    continue
                
                if extra_path.is_file():
                    # Copy single file to destination root
                    dest_file = dst / extra_path.name
                    FileSystemHelper._copy_file(extra_path, dest_file, replacements)
                
                elif extra_path.is_dir():
                    # Copy directory preserving its name
                    dest_dir = dst / extra_path.name
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    FileSystemHelper._copy_directory_contents(
                        extra_path, dest_dir, replacements
                    )


def main():
    initializer = ProjectInitializer()

    # Register templates
    factory = initializer.template_factory
    config = ProjectConfig(
        name="my-react-app",
        version="1.0.0",
        description="A new React application",
        author="John Doe",
        project_type=ProjectType.REACT,
        output_path=Path("./output"),
        parameters={
            "typescript": True,
            "styling_solution": "styled-components"
        }
    )

    template = factory.create_template(config)
    init_info = template.get_init_info()

    # Print out the initialization configuration
    print("\nTemplate Initialization Configuration:")
    print(f"Build Command: {init_info.build_cmd.command}")
    print(f"Working Directory: {init_info.build_cmd.working_directory}")
    print(f"\nEnvironment:")
    print(f"Node Version: {init_info.env_config.node_version}")
    print(f"NPM Version: {init_info.env_config.npm_version}")
    print(f"\nInit Minimal: {init_info.init_minimal}")
    print(f"\nRun Tool Command: {init_info.run_tool.command}")
    print(f"Test Tool Command: {init_info.test_tool.command}")

    success = initializer.initialize_project(config)
    print(f"\nProject initialization {'successful' if success else 'failed'}")


if __name__ == "__main__":
    main()
