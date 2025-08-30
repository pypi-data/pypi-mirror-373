#!/usr/bin/env python3
"""
CLI Generator that creates Click-based CLI commands based on RegistryFactory generated methods
"""

import os
import sys
import inspect
from typing import Any, Dict, List, Set, Optional
from pathlib import Path

from lineagentic_kg.utils.logging_config import get_logger, log_function_call, log_function_result, log_error_with_context
from lineagentic_kg.registry.factory import RegistryFactory


class CLIGenerator:
    """Generates Click-based CLI commands based on RegistryFactory methods"""
    
    def __init__(self, registry_path: str, output_dir: str = "generated_cli"):
        self.logger = get_logger("lineagentic.cli.generator")
        self.registry_path = registry_path
        self.output_dir = Path(output_dir)
        
        self.logger.info("Initializing CLIGenerator", registry_path=registry_path, output_dir=output_dir)
        
        try:
            self.factory = RegistryFactory(registry_path)
            
            # Create output directory
            self.output_dir.mkdir(exist_ok=True)
            self.logger.debug("Created output directory", output_dir=str(self.output_dir))
            
            # Create a temporary writer instance to get the actual method names
            self._temp_writer = None
            
            self.logger.info("CLIGenerator initialized successfully")
            
        except Exception as e:
            log_error_with_context(self.logger, e, "CLIGenerator initialization")
            raise
        
    def _get_temp_writer(self):
        """Get a temporary writer instance to inspect available methods"""
        if self._temp_writer is None:
            self.logger.debug("Creating temporary writer instance for method inspection")
            # Create a temporary writer with dummy connection
            self._temp_writer = self.factory.create_writer("bolt://localhost:7687", "neo4j", "password")
        return self._temp_writer
    
    def _get_method_name_for_entity(self, entity_name: str, operation: str) -> str:
        """Get method name for entity operation using the same logic as Neo4jWriterGenerator"""
        return f"{operation}_{entity_name.lower()}"
    
    def _get_method_name_for_aspect(self, aspect_name: str, operation: str) -> str:
        """Get method name for aspect operation using the same logic as Neo4jWriterGenerator"""
        return f"{operation}_{aspect_name.lower()}_aspect"
        
    def generate_all(self):
        """Generate all CLI files"""
        log_function_call(self.logger, "generate_all")
        
        try:
            self.logger.info("Generating CLI commands from RegistryFactory...")
            
            # Generate files
            self.logger.debug("Generating factory wrapper")
            self._generate_factory_wrapper()
            
            self.logger.debug("Generating entity commands")
            self._generate_entity_commands()
            
            self.logger.debug("Generating aspect commands")
            self._generate_aspect_commands()
            
            self.logger.debug("Generating utility commands")
            self._generate_utility_commands()
            
            self.logger.debug("Generating main CLI")
            self._generate_main_cli()
            
            self.logger.debug("Generating requirements")
            self._generate_requirements()
            
            self.logger.debug("Generating README")
            self._generate_readme()
            

            
            self.logger.info("Generated CLI files successfully", output_dir=str(self.output_dir))
            log_function_result(self.logger, "generate_all", output_dir=str(self.output_dir))
            
        except Exception as e:
            log_error_with_context(self.logger, e, "generate_all")
            raise
    
    def _generate_factory_wrapper(self):
        """Generate factory wrapper for CLI dependency injection"""
        wrapper_content = '''#!/usr/bin/env python3
"""
Factory wrapper for CLI dependency injection
"""

import os
import sys
from typing import Optional

# Add parent directory to path to import registry modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lineagentic_kg.registry.factory import RegistryFactory


class FactoryWrapper:
    """Wrapper for RegistryFactory with singleton pattern"""
    
    _instance: Optional['FactoryWrapper'] = None
    _factory: Optional[RegistryFactory] = None
    _writer = None
    
    def __init__(self):
        # Try multiple possible registry paths
        possible_paths = [
            os.getenv("REGISTRY_PATH"),
            "../config/main_registry.yaml",
            "../../config/main_registry.yaml",
            "config/main_registry.yaml",
            os.path.join(os.path.dirname(__file__), "..", "config", "main_registry.yaml"),
            os.path.join(os.path.dirname(__file__), "..", "..", "config", "main_registry.yaml")
        ]
        
        registry_path = None
        for path in possible_paths:
            if path and os.path.exists(path):
                registry_path = path
                break
        
        if not registry_path:
            raise FileNotFoundError(f"Registry file not found. Tried paths: {possible_paths}")
        
        self._factory = RegistryFactory(registry_path)
        
        # Set methods based on registry configuration
        self._factory.entity_methods = list(self._factory.registry.get('entities', {}).keys())
        self._factory.aspect_methods = list(self._factory.registry.get('aspects', {}).keys())
        self._factory.utility_methods = list(self._factory.registry.get('utility_functions', {}).keys())
    
    def get_writer_instance(self):
        """Get or create writer instance"""
        if self._writer is None:
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            self._writer = self._factory.create_writer(uri, user, password)
        return self._writer
    
    @classmethod
    def get_instance(cls) -> 'FactoryWrapper':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


def get_factory_instance() -> RegistryFactory:
    """Get factory instance for dependency injection"""
    return FactoryWrapper.get_instance()._factory


def get_writer_instance():
    """Get writer instance for dependency injection"""
    return FactoryWrapper.get_instance().get_writer_instance()
'''
        
        # Write factory wrapper file
        with open(self.output_dir / "factory_wrapper.py", "w") as f:
            f.write(wrapper_content)
        
        print(f"✅ Generated factory_wrapper.py")
    
    def _generate_entity_commands(self):
        """Generate entity CLI commands"""
        commands_content = '''#!/usr/bin/env python3
"""
Entity CLI commands
"""

import click
import json
from typing import Any, Dict, Optional
import factory_wrapper


def _get_writer():
    """Get writer instance"""
    return factory_wrapper.get_writer_instance()


def _get_factory():
    """Get factory instance"""
    return factory_wrapper.get_factory_instance()


# Entity commands
'''
        
        # Generate entity commands dynamically from registry
        entities = self.factory.registry.get('entities', {})
        for entity_name in sorted(entities.keys()):
            entity_config = entities[entity_name]
            properties = entity_config.get('properties', [])
            method_name = self._get_method_name_for_entity(entity_name, "get")
            upsert_method_name = self._get_method_name_for_entity(entity_name, "upsert")
            delete_method_name = self._get_method_name_for_entity(entity_name, "delete")
            
            # Generate get command
            commands_content += f'''
@click.command()
@click.argument('urn')
@click.option('--output', '-o', default='json', type=click.Choice(['json', 'table', 'yaml']), help='Output format')
def get_{entity_name.lower()}(urn: str, output: str):
    """Get {entity_name} entity by URN"""
    try:
        writer = _get_writer()
        
        method_name = "{method_name}"
        if not hasattr(writer, method_name):
            click.echo(f"❌ Entity type '{entity_name}' not found", err=True)
            return
        
        method = getattr(writer, method_name)
        result = method(urn)
        
        if result is None:
            click.echo(f"❌ {entity_name} with URN '{{urn}}' not found", err=True)
            return
        
        if output == 'json':
            click.echo(json.dumps(result, indent=2))
        elif output == 'table':
            click.echo(f"URN: {{urn}}")
            for key, value in result.items():
                click.echo(f"{{key}}: {{value}}")
        elif output == 'yaml':
            import yaml
            click.echo(yaml.dump(result, default_flow_style=False))
    except Exception as e:
        click.echo(f"❌ Error: {{str(e)}}", err=True)
'''
            
            # Generate upsert command
            commands_content += f'''

@click.command()
'''
            
            # Add options for entity properties
            for prop in properties:
                # Convert camelCase to lowercase for CLI options
                cli_option = prop.lower()
                commands_content += f'''@click.option('--{cli_option}', help='{prop}')
'''
            
            commands_content += f'''@click.option('--additional-properties', help='Additional properties as JSON string')
@click.option('--output', '-o', default='json', type=click.Choice(['json', 'table', 'yaml']), help='Output format')
def upsert_{entity_name.lower()}({', '.join([prop.lower() for prop in properties])}, additional_properties: Optional[str], output: str):
    """Upsert {entity_name} entity"""
    try:
        writer = _get_writer()
        
        method_name = "{upsert_method_name}"
        if not hasattr(writer, method_name):
            click.echo(f"❌ Entity type '{entity_name}' not found", err=True)
            return
        
        method = getattr(writer, method_name)
        
        # Prepare parameters
        params = {{}}
'''
            
            # Add parameters for entity properties
            for prop in properties:
                # Convert camelCase to lowercase for CLI options
                cli_option = prop.lower()
                commands_content += f'''        if {cli_option} is not None:
            params['{prop}'] = {cli_option}
'''
            
            commands_content += f'''
        # Add additional properties if provided
        if additional_properties:
            try:
                # Handle both string and dict parameters
                if isinstance(additional_properties, str):
                    additional_props = json.loads(additional_properties)
                else:
                    additional_props = additional_properties
                params.update(additional_props)
            except json.JSONDecodeError:
                click.echo("❌ Invalid JSON in additional-properties", err=True)
                return
        
        # Call the generated method - URN will be generated automatically
        result_urn = method(**params)
        
        # Get the created/updated entity
        get_method_name = "{method_name}"
        get_method = getattr(writer, get_method_name)
        entity_data = get_method(result_urn)
        
        result = {{
            "urn": result_urn,
            "properties": entity_data or {{}},
            "last_updated": entity_data.get('lastUpdated') if entity_data else None
        }}
        
        if output == 'json':
            click.echo(json.dumps(result, indent=2))
        elif output == 'table':
            click.echo(f"URN: {{result_urn}}")
            click.echo(f"Status: Created/Updated")
            if entity_data:
                for key, value in entity_data.items():
                    click.echo(f"{{key}}: {{value}}")
        elif output == 'yaml':
            import yaml
            click.echo(yaml.dump(result, default_flow_style=False))
    except Exception as e:
        click.echo(f"❌ Error: {{str(e)}}", err=True)
'''
            
            # Generate delete command
            commands_content += f'''

@click.command()
'''
            
            # Add options for entity properties (same as upsert)
            for prop in properties:
                # Convert camelCase to lowercase for CLI options
                cli_option = prop.lower()
                commands_content += f'''@click.option('--{cli_option}', help='{prop}')
'''
            
            commands_content += f'''@click.option('--additional-properties', help='Additional properties as JSON string')
def delete_{entity_name.lower()}({', '.join([prop.lower() for prop in properties])}, additional_properties: Optional[str]):
    """Delete {entity_name} entity by auto-generated URN"""
    try:
        writer = _get_writer()
        
        method_name = "{delete_method_name}"
        if not hasattr(writer, method_name):
            click.echo(f"❌ Entity type '{entity_name}' not found", err=True)
            return
        
        method = getattr(writer, method_name)
        
        # Prepare parameters (same as upsert to generate the same URN)
        params = dict()
'''
            
            # Add parameters for entity properties
            for prop in properties:
                # Convert camelCase to lowercase for CLI options
                cli_option = prop.lower()
                commands_content += f'''        if {cli_option} is not None:
            params['{prop}'] = {cli_option}
'''
            
            commands_content += f'''
        # Add additional properties if provided
        if additional_properties:
            try:
                # Handle both string and dict parameters
                if isinstance(additional_properties, str):
                    additional_props = json.loads(additional_properties)
                else:
                    additional_props = additional_properties
                params.update(additional_props)
            except json.JSONDecodeError:
                click.echo("❌ Invalid JSON in additional-properties", err=True)
                return
        
        # Generate URN from parameters using factory
        factory = _get_factory()
        # Find the correct URN generator key by searching through available generators
        urn_generator = None
        entity_name_lower = '{entity_name}'.lower()
        
        # Try different possible mappings to find the right URN generator
        possible_keys = [
            '{entity_name}',  # Exact match
            '{entity_name[0].lower() + entity_name[1:]}',  # camelCase (CorpUser -> corpUser)
            entity_name_lower,  # all lowercase
        ]
        
        for key in possible_keys:
            if key in factory.urn_generators:
                urn_generator = factory.urn_generators.get(key)
                break
        if urn_generator:
            urn = urn_generator(**params)
        else:
            click.echo(f"❌ No URN generator found for {entity_name}", err=True)
            return
        
        # Call the DELETE method with the generated URN
        method(urn)
        
        click.echo(f"✅ {entity_name} deleted successfully")
    except Exception as e:
        click.echo(f"❌ Error: {{str(e)}}", err=True)
'''
        
        # Write entity commands file
        with open(self.output_dir / "entity_commands.py", "w") as f:
            f.write(commands_content)
        
        print(f"✅ Generated entity_commands.py")
    
    def _generate_aspect_commands(self):
        """Generate aspect CLI commands"""
        commands_content = '''#!/usr/bin/env python3
"""
Aspect CLI commands
"""

import click
import json
from typing import Any, Dict, Optional
import factory_wrapper


def _get_writer():
    """Get writer instance"""
    return factory_wrapper.get_writer_instance()


def _get_factory():
    """Get factory instance"""
    return factory_wrapper.get_factory_instance()


# Aspect commands
'''
        
        # Generate aspect commands dynamically from registry
        aspects = self.factory.registry.get('aspects', {})
        for aspect_name in sorted(aspects.keys()):
            aspect_config = aspects[aspect_name]
            aspect_type = aspect_config.get('type', 'versioned')
            properties = aspect_config.get('properties', [])
            required_props = aspect_config.get('required', [])
            method_name = self._get_method_name_for_aspect(aspect_name, "get")
            upsert_method_name = self._get_method_name_for_aspect(aspect_name, "upsert")
            delete_method_name = self._get_method_name_for_aspect(aspect_name, "delete")
            
            # Generate get command
            commands_content += f'''
@click.command()
@click.argument('entity_label')
@click.argument('entity_urn')
'''
            
            if aspect_type == 'timeseries':
                commands_content += f'''@click.option('--limit', default=100, help='Limit for timeseries aspects')
'''
            
            commands_content += f'''@click.option('--output', '-o', default='json', type=click.Choice(['json', 'table', 'yaml']), help='Output format')
def get_{aspect_name.lower()}_aspect(entity_label: str, entity_urn: str'''
            
            if aspect_type == 'timeseries':
                commands_content += f''', limit: int'''
            
            commands_content += f''', output: str):
    """Get {aspect_name} aspect for entity"""
    try:
        writer = _get_writer()
        
        method_name = "{method_name}"
        if not hasattr(writer, method_name):
            click.echo(f"❌ Aspect '{aspect_name}' not found", err=True)
            return
        
        method = getattr(writer, method_name)
'''
            
            if aspect_type == 'timeseries':
                commands_content += f'''        result = method(entity_label, entity_urn, limit)
'''
            else:
                commands_content += f'''        result = method(entity_label, entity_urn)
'''
            
            commands_content += f'''
        if result is None:
            click.echo(f"❌ {aspect_name} aspect not found", err=True)
            return
        
        response = {{
            "entity_label": entity_label,
            "entity_urn": entity_urn,
            "aspect_name": "{aspect_name}",
            "payload": result
        }}
        
        if output == 'json':
            click.echo(json.dumps(response, indent=2))
        elif output == 'table':
            click.echo(f"Entity Label: {{entity_label}}")
            click.echo(f"Entity URN: {{entity_urn}}")
            click.echo(f"Aspect: {{aspect_name}}")
            if isinstance(result, list):
                click.echo(f"Records: {{len(result)}}")
                for i, record in enumerate(result):
                    click.echo(f"  Record {{i+1}}:")
                    for key, value in record.items():
                        click.echo(f"    {{key}}: {{value}}")
            else:
                for key, value in result.items():
                    click.echo(f"{{key}}: {{value}}")
        elif output == 'yaml':
            import yaml
            click.echo(yaml.dump(response, default_flow_style=False))
    except Exception as e:
        click.echo(f"❌ Error: {{str(e)}}", err=True)
'''
            
            # Generate upsert command
            commands_content += f'''

@click.command()
'''
            
            # Add entity creation parameters based on aspect configuration
            entity_creation = aspect_config.get('entity_creation', {})
            if entity_creation:
                required_params = entity_creation.get('required_params', [])
                optional_params = entity_creation.get('optional_params', [])
                
                # Add required entity parameters
                for param in required_params:
                    commands_content += f'''@click.option('--{param}', required=True, help='{param} (required for entity creation)')
'''
                
                # Add optional entity parameters
                for param in optional_params:
                    commands_content += f'''@click.option('--{param}', help='{param} (optional for entity creation)')
'''
            
            # Add options for aspect properties (excluding type-specific ones)
            for prop in properties:
                # Skip version if it's a versioned aspect (we'll add it separately)
                if aspect_type == 'versioned' and prop == 'version':
                    continue
                # Skip timestamp_ms if it's a timeseries aspect (we'll add it separately)
                if aspect_type == 'timeseries' and prop == 'timestamp_ms':
                    continue
                
                if prop in required_props:
                    commands_content += f'''@click.option('--{prop}', required=True, help='{prop} (required)')
'''
                else:
                    commands_content += f'''@click.option('--{prop}', help='{prop}')
'''
            
            # Add type-specific options
            if aspect_type == 'versioned':
                commands_content += f'''@click.option('--version', type=int, help='Version (for versioned aspects)')
'''
            elif aspect_type == 'timeseries':
                commands_content += f'''@click.option('--timestamp-ms', type=int, help='Timestamp in milliseconds (for timeseries aspects)')
'''
            
            commands_content += f'''@click.option('--output', '-o', default='json', type=click.Choice(['json', 'table', 'yaml']), help='Output format')
def upsert_{aspect_name.lower()}_aspect('''
            
            # Add entity creation parameters to function signature
            first_param = True
            entity_params_added = set()  # Track which entity parameters we've added
            
            if entity_creation:
                required_params = entity_creation.get('required_params', [])
                optional_params = entity_creation.get('optional_params', [])
                
                # Add required entity parameters
                for param in required_params:
                    if first_param:
                        commands_content += f'''{param}: str'''
                        first_param = False
                    else:
                        commands_content += f''', {param}: str'''
                    entity_params_added.add(param)
                
                # Add optional entity parameters
                for param in optional_params:
                    if first_param:
                        commands_content += f'''{param}: Optional[str]'''
                        first_param = False
                    else:
                        commands_content += f''', {param}: Optional[str]'''
                    entity_params_added.add(param)
            
            # Add parameters for aspect properties (excluding type-specific ones)
            for prop in properties:
                # Skip version if it's a versioned aspect (we'll add it separately)
                if aspect_type == 'versioned' and prop == 'version':
                    continue
                # Skip timestamp_ms if it's a timeseries aspect (we'll add it separately)
                if aspect_type == 'timeseries' and prop == 'timestamp_ms':
                    continue
                # Skip properties that are already added as entity parameters
                if prop in entity_params_added:
                    continue
                
                # Use lowercase parameter names to match Click's conversion
                if first_param:
                    commands_content += f'''{prop.lower()}: Optional[str]'''
                    first_param = False
                else:
                    commands_content += f''', {prop.lower()}: Optional[str]'''
            
            # Add type-specific parameters
            if aspect_type == 'versioned':
                if first_param:
                    commands_content += f'''version: Optional[int]'''
                    first_param = False
                else:
                    commands_content += f''', version: Optional[int]'''
            elif aspect_type == 'timeseries':
                if first_param:
                    commands_content += f'''timestamp_ms: Optional[int]'''
                    first_param = False
                else:
                    commands_content += f''', timestamp_ms: Optional[int]'''
            
            # Add output parameter
            if first_param:
                commands_content += f'''output: str'''
            else:
                commands_content += f''', output: str'''
            
            commands_content += f'''):
    """Upsert {aspect_name} aspect"""
    try:
        writer = _get_writer()
        factory = _get_factory()
        
        method_name = "{upsert_method_name}"
        if not hasattr(writer, method_name):
            click.echo(f"❌ Aspect '{aspect_name}' not found", err=True)
            return
        
        method = getattr(writer, method_name)
        
        # Prepare parameters - URN will be auto-generated by factory
        params = {{}}
        
        # Get aspect configuration
        aspect_config = factory.registry.get('aspects', {{}}).get('{aspect_name}', {{}})
        
        # Add entity creation parameters
        entity_creation = aspect_config.get('entity_creation', {{}})
        if entity_creation:
            required_params = entity_creation.get('required_params', [])
            optional_params = entity_creation.get('optional_params', [])
            
            # Add required entity parameters
            for param in required_params:
                param_value = locals().get(param)
                if param_value is not None:
                    params[param] = param_value
            
            # Add optional entity parameters
            for param in optional_params:
                param_value = locals().get(param)
                if param_value is not None:
                    params[param] = param_value
        
        # Add all aspect-specific fields to payload
        aspect_properties = aspect_config.get('properties', [])
        aspect_type = aspect_config.get('type', 'standard')
        
        payload = {{}}
        for prop in aspect_properties:
            # Skip properties that are entity creation parameters (they're handled separately)
            if entity_creation:
                required_params = entity_creation.get('required_params', [])
                optional_params = entity_creation.get('optional_params', [])
                if prop in required_params or prop in optional_params:
                    continue
            
            # Get the parameter value - Click converts camelCase to lowercase
            param_value = locals().get(prop.lower()) if locals().get(prop.lower()) is not None else locals().get(prop)
            if param_value is not None:
                payload[prop] = param_value
        
        params["payload"] = payload
        
        # Add optional parameters - only for versioned aspects
        if aspect_type == 'versioned' and version is not None:
            params["version"] = version
        

        
        # Call the generated method
        result = method(**params)
        
        response = {{
            "aspect_name": "{aspect_name}",
            "payload": payload,
            "status": "created/updated"
        }}
        
        if output == 'json':
            click.echo(json.dumps(response, indent=2))
        elif output == 'table':
            click.echo(f"Aspect: {aspect_name}")
            click.echo("Status: Created/Updated")
            for key, value in payload.items():
                click.echo(f"{{key}}: {{value}}")
        elif output == 'yaml':
            import yaml
            click.echo(yaml.dump(response, default_flow_style=False))
    except Exception as e:
        click.echo(f"❌ Error: {{str(e)}}", err=True)
'''
            
            # Generate delete command
            commands_content += f'''

@click.command()
'''
            
            # Add entity creation parameters based on aspect configuration (same as upsert)
            entity_creation = aspect_config.get('entity_creation', {})
            if entity_creation:
                required_params = entity_creation.get('required_params', [])
                optional_params = entity_creation.get('optional_params', [])
                
                # Add required entity parameters
                for param in required_params:
                    commands_content += f'''@click.option('--{param}', required=True, help='{param} (required for entity creation)')
'''
                
                # Add optional entity parameters
                for param in optional_params:
                    commands_content += f'''@click.option('--{param}', help='{param} (optional for entity creation)')
'''
            
            # Add options for aspect properties (same as upsert)
            for prop in properties:
                # Skip version if it's a versioned aspect (we'll add it separately)
                if aspect_type == 'versioned' and prop == 'version':
                    continue
                # Skip timestamp_ms if it's a timeseries aspect (we'll add it separately)
                if aspect_type == 'timeseries' and prop == 'timestamp_ms':
                    continue
                
                if prop in required_props:
                    commands_content += f'''@click.option('--{prop}', required=True, help='{prop} (required)')
'''
                else:
                    commands_content += f'''@click.option('--{prop}', help='{prop}')
'''
            
            # Add type-specific options
            if aspect_type == 'versioned':
                commands_content += f'''@click.option('--version', type=int, help='Version (for versioned aspects)')
'''
            elif aspect_type == 'timeseries':
                commands_content += f'''@click.option('--timestamp-ms', type=int, help='Timestamp in milliseconds (for timeseries aspects)')
'''
            
            commands_content += f'''def delete_{aspect_name.lower()}_aspect('''
            
            # Add entity creation parameters to function signature
            first_param = True
            if entity_creation:
                required_params = entity_creation.get('required_params', [])
                optional_params = entity_creation.get('optional_params', [])
                
                # Add required entity parameters
                for param in required_params:
                    if first_param:
                        commands_content += f'''{param}: str'''
                        first_param = False
                    else:
                        commands_content += f''', {param}: str'''
                
                # Add optional entity parameters
                for param in optional_params:
                    if first_param:
                        commands_content += f'''{param}: Optional[str]'''
                        first_param = False
                    else:
                        commands_content += f''', {param}: Optional[str]'''
            
            # Add parameters for aspect properties (same as upsert)
            for prop in properties:
                # Skip version if it's a versioned aspect (we'll add it separately)
                if aspect_type == 'versioned' and prop == 'version':
                    continue
                # Skip timestamp_ms if it's a timeseries aspect (we'll add it separately)
                if aspect_type == 'timeseries' and prop == 'timestamp_ms':
                    continue
                # Skip properties that are already added as entity parameters
                if entity_creation:
                    required_params = entity_creation.get('required_params', [])
                    optional_params = entity_creation.get('optional_params', [])
                    if prop in required_params or prop in optional_params:
                        continue
                
                # Use lowercase parameter names to match Click's conversion
                if first_param:
                    commands_content += f'''{prop.lower()}: Optional[str]'''
                    first_param = False
                else:
                    commands_content += f''', {prop.lower()}: Optional[str]'''
            
            # Add type-specific parameters
            if aspect_type == 'versioned':
                if first_param:
                    commands_content += f'''version: Optional[int]'''
                    first_param = False
                else:
                    commands_content += f''', version: Optional[int]'''
            elif aspect_type == 'timeseries':
                if first_param:
                    commands_content += f'''timestamp_ms: Optional[int]'''
                    first_param = False
                else:
                    commands_content += f''', timestamp_ms: Optional[int]'''
            
            commands_content += f'''):
    """Delete {aspect_name} aspect by auto-generated URN"""
    try:
        writer = _get_writer()
        
        method_name = "{delete_method_name}"
        if not hasattr(writer, method_name):
            click.echo(f"❌ Aspect '{aspect_name}' not found", err=True)
            return
        
        method = getattr(writer, method_name)
        
        # Prepare parameters (same as upsert to generate the same URN)
        params = {{}}
        
        # Add entity creation parameters
        entity_creation = aspect_config.get('entity_creation', {{}})
        if entity_creation:
            required_params = entity_creation.get('required_params', [])
            optional_params = entity_creation.get('optional_params', [])
            
            # Add required entity parameters
            for param in required_params:
                param_value = locals().get(param)
                if param_value is not None:
                    params[param] = param_value
            
            # Add optional entity parameters
            for param in optional_params:
                param_value = locals().get(param)
                if param_value is not None:
                    params[param] = param_value
        
        # Add all aspect-specific fields to payload
        aspect_properties = aspect_config.get('properties', [])
        aspect_type = aspect_config.get('type', 'standard')
        
        payload = {{}}
        for prop in aspect_properties:
            # Skip properties that are entity creation parameters (they're handled separately)
            if entity_creation:
                required_params = entity_creation.get('required_params', [])
                optional_params = entity_creation.get('optional_params', [])
                if prop in required_params or prop in optional_params:
                    continue
            
            # Get the parameter value - Click converts camelCase to lowercase
            param_value = locals().get(prop.lower()) if locals().get(prop.lower()) is not None else locals().get(prop)
            if param_value is not None:
                payload[prop] = param_value
        
        params["payload"] = payload
        
        # Add optional parameters - only for versioned aspects
        if aspect_type == 'versioned' and version is not None:
            params["version"] = version
        
        # Generate entity URN from entity creation parameters
        factory = _get_factory()
        entity_urn = None
        entity_label = ''
        entity_type = ''
        
        if entity_creation:
            entity_type = entity_creation.get('entity_type', '').lower()
            entity_label = entity_creation.get('entity_type', '')
            urn_generator = factory.urn_generators.get(entity_type)
            if urn_generator:
                # Create entity params for URN generation
                entity_params = {{}}
                for param in required_params + optional_params:
                    param_value = locals().get(param)
                    if param_value is not None:
                        entity_params[param] = param_value
                
                entity_urn = urn_generator(**entity_params)
            else:
                click.echo(f"❌ No URN generator found for entity type {{entity_type}}", err=True)
                return
        
        if not entity_urn:
            click.echo(f"❌ Could not generate entity URN for {aspect_name}", err=True)
            return
        
        # Call the DELETE method with entity_label and entity_urn
        method(entity_label, entity_urn)
        
        click.echo(f"✅ {aspect_name} aspect deleted successfully")
    except Exception as e:
        click.echo(f"❌ Error: {{str(e)}}", err=True)
'''
        
        # Write aspect commands file
        with open(self.output_dir / "aspect_commands.py", "w") as f:
            f.write(commands_content)
        
        print(f"✅ Generated aspect_commands.py")
    
    def _generate_utility_commands(self):
        """Generate utility CLI commands"""
        commands_content = '''#!/usr/bin/env python3
"""
Utility CLI commands
"""

import click
import json
from typing import Any, Dict, Optional
import factory_wrapper


def _get_factory():
    """Get factory instance"""
    return factory_wrapper.get_factory_instance()


# Utility commands
@click.command()
@click.argument('function_name')
@click.option('--parameters', help='Function parameters as JSON string')
@click.option('--output', '-o', default='json', type=click.Choice(['json', 'table', 'yaml']), help='Output format')
def utility(function_name: str, parameters: Optional[str], output: str):
    """Execute utility function"""
    try:
        factory = _get_factory()
        
        utility_functions = factory.utility_functions
        if function_name not in utility_functions:
            available_functions = list(utility_functions.keys())
            click.echo(f"❌ Utility function '{function_name}' not found. Available: {available_functions}", err=True)
            return
        
        # Parse parameters
        params = {}
        if parameters:
            try:
                # Handle both string and dict parameters
                if isinstance(parameters, str):
                    params = json.loads(parameters)
                else:
                    params = parameters
            except json.JSONDecodeError as e:
                click.echo(f"❌ Invalid JSON in parameters: {e}", err=True)
                return
        
        # Execute function
        func = utility_functions[function_name]
        result = func(**params)
        
        response = {
            "result": result,
            "function_name": function_name
        }
        
        if output == 'json':
            click.echo(json.dumps(response, indent=2))
        elif output == 'table':
            click.echo(f"Function: {function_name}")
            click.echo(f"Result: {result}")
        elif output == 'yaml':
            import yaml
            click.echo(yaml.dump(response, default_flow_style=False))
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)


@click.command()
def list_utilities():
    """List available utility functions"""
    try:
        factory = _get_factory()
        utility_functions = factory.utility_functions
        
        click.echo("Available utility functions:")
        if utility_functions:
            for func_name in sorted(utility_functions.keys()):
                click.echo(f"  - {func_name}")
        else:
            click.echo("  No utility functions available")
    except Exception as e:
        click.echo(f"❌ Error: {{str(e)}}", err=True)


@click.command()
def health():
    """Health check"""
    try:
        factory = _get_factory()
        
        response = {
            "status": "healthy",
            "registry_loaded": True,
            "available_entities": list(factory.registry.get('entities', {}).keys()),
            "available_aspects": list(factory.registry.get('aspects', {}).keys()),
            "available_utilities": list(factory.registry.get('utility_functions', {}).keys())
        }
        
        click.echo(json.dumps(response, indent=2))
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
'''
        
        # Write utility commands file
        with open(self.output_dir / "utility_commands.py", "w") as f:
            f.write(commands_content)
        
        print(f"✅ Generated utility_commands.py")
    
    def _generate_main_cli(self):
        """Generate main CLI application"""
        cli_content = '''#!/usr/bin/env python3
"""
Main CLI application
"""

import click
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import entity_commands
import aspect_commands
import utility_commands


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """RegistryFactory CLI - Command line interface for metadata operations"""
    pass


# Add entity commands
'''
        
        # Add entity commands dynamically from registry
        entities = self.factory.registry.get('entities', {})
        for entity_name in sorted(entities.keys()):
            cli_content += f'''cli.add_command(entity_commands.get_{entity_name.lower()}, name='get-{entity_name.lower()}')
cli.add_command(entity_commands.upsert_{entity_name.lower()}, name='upsert-{entity_name.lower()}')
cli.add_command(entity_commands.delete_{entity_name.lower()}, name='delete-{entity_name.lower()}')
'''
        
        # Add aspect commands dynamically from registry
        aspects = self.factory.registry.get('aspects', {})
        for aspect_name in sorted(aspects.keys()):
            cli_content += f'''cli.add_command(aspect_commands.get_{aspect_name.lower()}_aspect, name='get-{aspect_name.lower()}-aspect')
cli.add_command(aspect_commands.upsert_{aspect_name.lower()}_aspect, name='upsert-{aspect_name.lower()}-aspect')
cli.add_command(aspect_commands.delete_{aspect_name.lower()}_aspect, name='delete-{aspect_name.lower()}-aspect')
'''
        
        # Add utility commands
        cli_content += '''
# Add utility commands
cli.add_command(utility_commands.utility, name='utility')
cli.add_command(utility_commands.list_utilities, name='list-utilities')
cli.add_command(utility_commands.health, name='health')


if __name__ == '__main__':
    cli()
'''
        
        # Write main CLI file
        with open(self.output_dir / "lineagentic_cli.py", "w") as f:
            f.write(cli_content)
        
        print(f"✅ Generated lineagentic_cli.py")
    
    def _generate_requirements(self):
        """Generate requirements.txt"""
        requirements_content = '''click==8.1.7
neo4j==5.28.2
python-dotenv==1.1.1
PyYAML==6.0.2
rich==13.7.0
tabulate==0.9.0
'''
        
        with open(self.output_dir / "requirements.txt", "w") as f:
            f.write(requirements_content)
        
        print(f"✅ Generated requirements.txt")
    

    
    def _generate_readme(self):
        """Generate README.md"""
        readme_content = f'''# RegistryFactory CLI

This is an auto-generated command-line interface based on the RegistryFactory methods.

## Installation

```bash
pip install -r requirements.txt
python lineagentic_cli.py --help
```

## Configuration

Set environment variables (optional - the CLI will auto-detect the registry path):
```bash
export REGISTRY_PATH="config/main_registry.yaml"  # Optional - auto-detected if not set
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
```

## Available Commands

### Health Check
```bash
lineagentic-kg health
```

### Entity Commands
'''
        
        # Add entity commands dynamically from registry
        entities = self.factory.registry.get('entities', {})
        for entity_name in sorted(entities.keys()):
            readme_content += f'''
#### {entity_name.title()}
```bash
# Get {entity_name} by URN
lineagentic-kg get-{entity_name.lower()} <urn> [--output json|table|yaml]

# Upsert {entity_name}
lineagentic-kg upsert-{entity_name.lower()} [--property value] [--additional-properties '{{"key": "value"}}']

# Delete {entity_name} by URN
lineagentic-kg delete-{entity_name.lower()} <urn>
```
'''
        
        readme_content += '''
### Aspect Commands
'''
        
        # Add aspect commands dynamically from registry
        aspects = self.factory.registry.get('aspects', {})
        for aspect_name in sorted(aspects.keys()):
            aspect_config = aspects[aspect_name]
            aspect_type = aspect_config.get('type', 'versioned')
            
            if aspect_type == 'timeseries':
                readme_content += f'''
#### {aspect_name.title()} (Timeseries)
```bash
# Get {aspect_name} aspect
lineagentic-kg get-{aspect_name.lower()}-aspect <entity_label> <entity_urn> [--limit 100] [--output json|table|yaml]

# Upsert {aspect_name} aspect
lineagentic-kg upsert-{aspect_name.lower()}-aspect [--entity-label label] [--entity-urn urn] [--property value] [--timestamp-ms 1234567890]

# Delete {aspect_name} aspect
lineagentic-kg delete-{aspect_name.lower()}-aspect <entity_label> <entity_urn>
```
'''
            else:
                readme_content += f'''
#### {aspect_name.title()} (Versioned)
```bash
# Get {aspect_name} aspect
lineagentic-kg get-{aspect_name.lower()}-aspect <entity_label> <entity_urn> [--output json|table|yaml]

# Upsert {aspect_name} aspect
lineagentic-kg upsert-{aspect_name.lower()}-aspect [--entity-label label] [--entity-urn urn] [--property value] [--version 1]

# Delete {aspect_name} aspect
lineagentic-kg delete-{aspect_name.lower()}-aspect <entity_label> <entity_urn>
```
'''
        
        readme_content += '''
### Utility Commands
```bash
# List available utility functions
lineagentic-kg list-utilities

# Execute utility function
lineagentic-kg utility <function_name> [--parameters '{"param": "value"}']

# Health check
lineagentic-kg health
```

## Examples

### Create a Dataset
```bash
lineagentic-kg upsert-dataset --name "my_dataset" --platform "mysql" --source "production"
```

### Add Schema Metadata
```bash
lineagentic-kg upsert-schema-metadata-aspect --entity-label "Dataset" --entity-urn "urn:li:dataset:(urn:li:dataPlatform:mysql,my_dataset,PROD)" --fields '[{"fieldPath": "id", "type": "INTEGER"}]'
```

### Get Entity Information
```bash
lineagentic-kg get-dataset "urn:li:dataset:(urn:li:dataPlatform:mysql,my_dataset,PROD)" --output table
```

## Generated Files

- `lineagentic_cli.py` - Main CLI application
- `entity_commands.py` - Entity operation commands
- `aspect_commands.py` - Aspect operation commands
- `utility_commands.py` - Utility function commands
- `factory_wrapper.py` - RegistryFactory wrapper for dependency injection
- `requirements.txt` - Python dependencies
- `setup.py` - Package installation script
- `README.md` - This file
'''
        
        with open(self.output_dir / "README.md", "w") as f:
            f.write(readme_content)
        
        print(f"✅ Generated README.md")


def main():
    """Main function to generate CLI files"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate CLI commands from RegistryFactory")
    parser.add_argument("--registry-path", default="config/main_registry.yaml", 
                       help="Path to registry configuration file")
    parser.add_argument("--output-dir", default="generated_cli", 
                       help="Output directory for generated files")
    
    args = parser.parse_args()
    
    generator = CLIGenerator(args.registry_path, args.output_dir)
    generator.generate_all()


if __name__ == "__main__":
    main()
