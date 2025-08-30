import os
import json
import platformdirs
import re

def set_api_key(key):
	"""
	Set the API key for Hunter.how.
	
	Args:
		key (str): The API key to set.
	"""
	
	if not re.match(r'^[a-z0-9]{64}$', key):
		raise ValueError("Invalid API key format. It should be a 64-character alphanumeric string.")
 
	config_dir = platformdirs.user_config_dir("hunter_how")
	os.makedirs(config_dir, exist_ok=True)
	config_file_path = os.path.join(config_dir, "config.json")

	with open(config_file_path, 'w') as config_file:
		json.dump({"api_key": key}, config_file)

def get_api_key():
	"""
	Load the API key from the configuration file.
	
	Returns:
		str: The API key if it exists, otherwise None.
	"""

	config_dir = platformdirs.user_config_dir("hunter_how")
	config_file_path = os.path.join(config_dir, "config.json")

	if not os.path.exists(config_file_path):
		return None

	with open(config_file_path, 'r') as config_file:
		config = json.load(config_file)
		return config.get("api_key")