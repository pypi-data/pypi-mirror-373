import os
import json

class OnDeviceTrainingConfig:
    """
    Configuration class for On-Device Training (ODT) benchmarks.

    Can be initialized with:
      - A filesystem path to a .json file,
      - A raw JSON string,
      - A Python dict representing the config, or
      - None, to create an empty config and set values manually.
    """
    def __init__(self, config=None):
        # No config: initialize empty and expect manual setters
        if config is None:
            self.config = {}
            self.learning_parameters = {}
            self.input_spec = {}
            self.output_spec = {}
            return

        # Dict provided: use directly
        if isinstance(config, dict):
            parsed = config
        # String provided: determine if path or JSON text
        elif isinstance(config, str) and os.path.isfile(config):
            with open(config, 'r', encoding='utf-8') as f:
                raw = f.read()
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON from file: {e}")
        elif isinstance(config, str):
            try:
                parsed = json.loads(config)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON from string: {e}")
        else:
            raise TypeError("`config` must be None, a dict, a path to a JSON file, or a JSON-formatted string")

        # Validate structure
        if not self.validate_config(parsed):
            raise ValueError("Configuration validation failed: see missing keys above")

        # Store and expose sections
        self.config = parsed
        self.learning_parameters = parsed.get("learning_parameters", {})
        self.input_spec = parsed.get("input", {})
        self.output_spec = parsed.get("output", {})

    @staticmethod
    def validate_config(config: dict) -> bool:
        """
        Validate that `config` contains all required sections and keys and that none of the key values are None.
        Prints any missing or None-valued keys and returns False in those cases.
        """
        required = {
            "learning_parameters": {"batch_size", "epochs"},
            "input": {"name", "shape", "dtype", "train_file", "test_file"},
            "output": {"name", "shape", "dtype", "train_file", "test_file"},
        }
        missing = []

        for section, keys in required.items():
            if section not in config:
                missing.append(section)
                continue

            subsection = config[section]
            if not isinstance(subsection, dict):
                missing.append(f"{section} (should be a dict)")
                continue

            for key in keys:
                if key not in subsection:
                    missing.append(f"{section}.{key}")
                elif subsection[key] is None:
                    missing.append(f"{section}.{key} cannot be None")

        if missing:
            print("Configuration issues found:")
            for m in missing:
                print(f"  • {m}")
            return False
        return True

    def set_learning_parameters(self, batch_size, epochs, **kwargs):
        """
        Set or update learning parameters.
        Accepts batch_size (int), epochs (int), and any custom key=value pairs.
        """
        params = {"batch_size": batch_size, "epochs": epochs}
        params.update(kwargs)
        self.learning_parameters = params
        self.config["learning_parameters"] = params

    def set_input_config(self, name, shape, dtype, train_file, test_file):
        """
        Set or update input configuration.
        """
        inp = {
            "name": name,
            "shape": shape,
            "dtype": dtype,
            "train_file": train_file,
            "test_file": test_file
        }
        self.input_spec = inp
        self.config["input"] = inp

    def set_output_config(self, name, shape, dtype, train_file, test_file):
        """
        Set or update output configuration.
        """
        out = {
            "name": name,
            "shape": shape,
            "dtype": dtype,
            "train_file": train_file,
            "test_file": test_file
        }
        self.output_spec = out
        self.config["output"] = out

    def get_config_str(self):
        """
        Return the current configuration as a JSON-formatted string.
        """
        if self.validate_config(self.config):
            return json.dumps(self.config, indent=4)
        else:
            raise ValueError("Configuration validation failed: see missing keys above")
        
    def get_input_data_files(self):
        """
        Return a list of all train_file and test_file paths from input and output specs.
        """
        files = []
        # Collect from input spec
        if "train_file" in self.input_spec:
            files.append(self.input_spec["train_file"])
        if "test_file" in self.input_spec:
            files.append(self.input_spec["test_file"])
        # Collect from output spec
        if "train_file" in self.output_spec:
            files.append(self.output_spec["train_file"])
        if "test_file" in self.output_spec:
            files.append(self.output_spec["test_file"])
        return files
    

    

        
