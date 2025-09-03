import os, yaml
import json
import requests
from typing import Dict, Any
from dataflow.configuration import ConfigurationManager

def load_yaml_text(contents) -> Dict[str, Any]:
    """
    Fetching profiles/connections from connection manager API using the user name.

    Args:
        Dict of filenames loaded from profiles.yml
    
    Returns:
        Profiles/Connections as Dict
    """  
    # Initialize configuration manager to get API endpoint
    try:
        config = ConfigurationManager('/dataflow/app/auth_config/dataflow_auth.cfg')
        connection_manager_api = config.get_config_value('auth', 'connection_manager_api')
    except Exception as e:
        raise Exception(f"Failed to load configuration: {e}")

    try:
        profiles = yaml.load(contents, Loader=yaml.SafeLoader)
    except Exception as e:
        return f"Unable to load profiles: {e}"
    
    connection_names = [connection_name for connection_name in profiles]
    
    for connection_name in connection_names:
        try:
            # Call API with specific conn_id parameter
            response = requests.get(
                connection_manager_api,
                params={'conn_id': connection_name}
            )

            if response.status_code == 404:
                print(f"Connection {connection_name} not found! Ensure it exists in dataflow connection page")
                continue

            response.raise_for_status()
            secrets = response.json()
            
            profiles[connection_name] = {
                'target' : 'default',
                'outputs': {
                    'default': {
                        'host'   : f'{secrets["host"]}',
                        'user'   : f'{secrets["login"]}',
                        'pass'   : f'{secrets["password"]}',
                        'port'   : secrets["port"],
                        'threads': 1,
                        'type'   : 'postgres',
                        'dbname' : f'{secrets["schemas"]}',
                        'schema' : 'public'
                    }
                }
            }
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch connection {connection_name}")
            continue
        except KeyError as e:
            print(f"Missing required field in connection {connection_name}: {e}")
            continue
        except Exception as e:
            print(f"Error processing connection {connection_name}: {e}")
            continue
            
    return profiles