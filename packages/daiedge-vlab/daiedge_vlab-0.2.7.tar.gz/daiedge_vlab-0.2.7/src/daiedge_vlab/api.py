import logging
import requests
import yaml
import os
import io
import json

from threading import Thread
from time import sleep
import time
from .config import OnDeviceTrainingConfig


# Configure logging at the module level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)



class dAIEdgeVLabAPI:
    def __init__(self, config_file=None, url=None, port=None, base_path="", auto_refresh = False):
        """
        Initialize the API client.

        This constructor allows you to instantiate the client either by providing a configuration file
        or by specifying the URL and port directly. The configuration file should include the API URL, port,
        user email, and password.

        Args:
            config_file (str, optional): Path to the YAML configuration file.
            url (str, optional): API host address (if config_file is not provided).
            port (int, optional): API port (if config_file is not provided).
            base_path (str, optional): Base path for the API endpoints. Default is an empty string.
            auto_refresh (bool, optional): Whether to start the token refresh thread. Default is False.

        Raises:
            Exception: If neither a config_file nor url and port are provided,
                       or if the configuration file is missing required fields,
                       or if login fails.
        """
        self.token = None
        self.refresh_token = None
        self.refresh_is_running = False
        self.refresh_thread = None

        # Get a logger instance for this class
        self.logger = logging.getLogger(__name__)

        if config_file is None:
            if url is None or port is None:
                raise Exception("Either config_file or url and port must be provided")
            self.host = url
            self.port = port
            self.base_path = base_path
            self._check_version()
            return

        else:
            with open(config_file, "r") as file:
                content = file.read()
            # Expand environment variables in the file content
            content = os.path.expandvars(content)
            config = yaml.safe_load(content)

            # Retrieve configuration values from the file
            self.host = config.get('api', {}).get('url', None)
            self.port = config.get('api', {}).get('port', None)
            self.base_path = config.get('api', {}).get('base_path', "")
            self.username = config.get('user', {}).get('email', None)
            self.password = config.get('user', {}).get('password', None)

            if self.host is None or self.port is None or self.username is None or self.password is None:
                raise Exception("Invalid config file")

            # Check if API version is supported before attempting login
            self._check_version()
            status = self.login(auto_refresh=auto_refresh)

            if not status:
                raise Exception("Error while logging in.")
            

    def __del__(self):
        """
        Destructor for the API client.

        This method ensures that the refresh thread is stopped and the access token is invalidated.
        """
        self.logout()

    def _build_endpoint(self) -> str:
        """
        Build the full URL for an API endpoint.
        This internal method constructs the full URL for a given API endpoint by combining
        the host, port, base path, and the specific endpoint.
        Returns:
            str: The full URL for the API endpoint.
        """
        if self.base_path != "" and self.base_path is not None:
            return f"https://{self.host}:{self.port}/{self.base_path.lstrip('/').rstrip('/')}"
        else:
            return f"https://{self.host}:{self.port}"
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build the full URL for an API endpoint.
        This internal method constructs the full URL for a given API endpoint by combining
        the host, port, base path, and the specific endpoint.
        Args:
            endpoint (str): The specific API endpoint (e.g., '/api/status').
        Returns:
            str: The full URL for the API endpoint.
        """
        base = self._build_endpoint()
        return f"{base}/{endpoint.lstrip('/').rstrip('/')}"


    def _check_version(self):
        """
        Check the API version and status.

        This internal method verifies that the API version is supported (must be '0.2.0')
        and that the API status is OK. It is called during initialization.
        
        Raises:
            Exception: If the API version is not supported or if the API status is not OK.
        """
        r = self.getAPIStatus()
        if r['version'] != '0.2.0':
            raise Exception("API version not supported, please update the client")
        if r['status'] != 'OK':
            raise Exception("API status not OK")
        
    def _refresh_token(self):   
        """
        Refresh the access token every 10 minutes.

        This internal method is run on a separate thread to refresh the access token every 10 minutes.
        """

        self.refresh_is_running = True
        refresh_interval = 10 * 60  # seconds
        timestamp = time.time()
        while self.refresh_is_running:
            # Check if it's time to refresh
            if time.time() - timestamp > refresh_interval:
                try:
                    self.refresh()
                except Exception as e:
                    self.logger.error(f"Error during token refresh: {e}")
                    self.logger.info("Stopping token refresh thread...")
                    self.logger.info("Please log in again to continue using the API.")
                    self.refresh_is_running = False
                timestamp = time.time()
            sleep(1)  # Sleep to reduce CPU usage

    def login(self, username=None, password=None, auto_refresh = False) -> bool:
        """
        Log in to the API and obtain an access token.

        You can optionally provide a username and password; otherwise, the ones stored during initialization will be used.
        Upon successful login, an access token is stored for future API requests.

        Args:
            username (str, optional): User's email for login.
            password (str, optional): User's password for login.
            auto_refresh (bool, optional): Whether to start the token refresh thread. Default is False.

        Returns:
            bool: True if login is successful, otherwise False.

        Raises:
            Exception: If username or password is missing.
        """
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        if self.username is None or self.password is None:
            raise Exception("Username and password must be provided")
        
        url = self._build_url('/api/users/login')
        r = requests.post(url, json={'email': self.username, 'password': self.password})

        if r.status_code != 200:
            self.logger.error(f"Error while logging in. Please verify your credentials or visit the API status page for more information.")
            return False

        self.token = r.json()['access_token']
        self.refresh_token = r.json()['refresh_token']

        if auto_refresh:
            self.refresh_thread = Thread(target=self._refresh_token)
            self.refresh_thread.daemon = True 
            self.refresh_thread.start()

        return True
    
    def logout(self):
        """
        Log out of the API.

        This method invalidates the access token and stops the refresh thread.
        """
        self.token = None
        self.refresh_token = None
        self.refresh_is_running = False
        if self.refresh_thread is not None:
            self.refresh_thread.join()
    

    def refresh(self) -> bool:
        """
        Refresh the access token.

        This method refreshes the access token using the refresh token obtained during login.
        The new access token is stored for future API requests.

        Returns:
            bool: True if the refresh is successful, otherwise False.
        """
        url = self._build_url('/api/users/token/refresh')

        r = requests.post(url, json={'refresh': self.refresh_token})

        if r.status_code != 200:
            self.logger.error(f"Error while refreshing token. Status : {r.status_code}, {r.text}")
            raise Exception("Error while refreshing token. Please verify your credentials or visit the API status page for more information.")

        self.token = r.json()['access']
        return True

    def startBenchmark(self, target, runtime, model_path, dataset=None, callback=None) -> str:
        """
        Start a new benchmark job.

        This method submits a benchmark job to the API for the given target device and runtime.
        It uploads the model (and optionally a dataset) to be benchmarked. Optionally, a callback function
        can be provided, which will be executed on a separate thread when the benchmark completes.

        Args:
            target (str): The target device identifier.
            runtime (str): The runtime engine to be used.
            model_path (str): Path to the model file.
            dataset (str or binary file, optional): Either a dataset name (string) or a binary file object.
            callback (function, optional): A function to be called with the benchmark result upon completion.

        Returns:
            str: The ID of the created benchmark job.

        Raises:
            Exception: If the dataset provided is neither a string nor a valid binary file.
        """
        url = self._build_url('/api/benchmarks/run')
        headers = {'Authorization': 'Bearer ' + self.token}
        data = {'device': target, 'engine': runtime}

        if dataset is not None:
            if type(dataset) == str:
                data.update({'dataset_name': dataset})
                r = requests.post(url, headers=headers, data=data, files={'model': open(model_path, 'rb')})
            elif isinstance(dataset, (io.IOBase, io.BufferedReader)) and 'b' in dataset.mode:
                r = requests.post(url, headers=headers, data=data, files={'model': open(model_path, 'rb'), 'dataset': dataset})
            else:
                raise Exception("Invalid dataset - must be a string or a binary file")
        else:
            r = requests.post(url, headers=headers, data=data, files={'model': open(model_path, 'rb')})

        if r.status_code != 200:
            self.logger.error(f"Error while starting benchmark. Status : {r.status_code}, {r.json()}")
            return -1
        
        # If a callback is provided and the request is successful, start a thread to wait for the result.
        if callback is not None and r.status_code == 200:
            Thread(target=self.notifyOnBenchmarkResult, args=(r.json()["id"], callback)).start()

        return r.json()["id"]

    def getDatasets(self) -> dict:
        """
        Retrieve the list of available datasets from the API.

        Returns:
            dict: A dictionary containing datasets information.
        """
        url = self._build_url('/api/benchmarks/datasets')
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None
        return r.json()

    def notifyOnBenchmarkResult(self, id, callback) -> None:
        """
        Wait for the benchmark to complete and notify via callback.

        This method is intended to be run on a separate thread. It waits for the benchmark
        identified by 'id' to finish, then calls the provided callback function with the result.

        Args:
            id (str): The benchmark job ID.
            callback (function): The function to be called with the benchmark result.
        """
        result = self.waitBenchmarkResult(id, verbose=True)
        callback(result)

    def getBenchmarkStatus(self, id) -> dict:
        """
        Get the current status of a benchmark job.

        Args:
            id (str): The benchmark job ID.

        Returns:
            dict: A dictionary with the status details of the benchmark job.
        """
        url = self._build_url(f'/api/benchmarks/{id}/status')
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            self.logger.error(f"Error while getting benchmark status. Status : {r.status_code}, {r}")
            return None
        return r.json()

    def getBenchmarkResult(self, id, save_path=None, model_name_only=True) -> dict:
        """
        Retrieve the complete benchmark result.

        This method aggregates the benchmark report, user log, error log, and raw binary output.

        Args:
            id (str): The benchmark job ID.
            save_path (str, optional): If provided, all the results will be saved to this path.
            model_name_only (bool, optional): If True, returns only the trained model name instead of the bytes that represent the model output.

        Returns:
            dict: A dictionary containing 'report', 'user_log', 'error_log', and 'raw_output'.
        """
        report = self.getBenchmarkReport(id, save_path)
        user_log = self.getInfoLog(id, save_path)
        error_log = self.getErrorLog(id, save_path)
        raw_output = self.getBinaryOutput(id, save_path)
        model_output = self.getModelOutput(id, save_path, model_name_only)

        return {'report': report, 'user_log': user_log, 'error_log': error_log, 'raw_output': raw_output, 'model_output': model_output}

    def getBenchmarkReport(self, id, save_path=None) -> dict:
        """
        Retrieve the detailed benchmark report.

        Args:
            id (str): The benchmark job ID.

        Returns:
            dict: A dictionary with the benchmark report details.
        """
        url = self._build_url(f'/api/benchmarks/{id}/results')
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None
        
        if save_path is not None:
            # Save the report to the specified path
            with open(os.path.join(save_path, f"{id}_benchmark_report.json"), 'w') as f:
                json.dump(r.json(), f, indent=4)

        return r.json()
    
    def waitBenchmarkResult(self, id, save_path=None, model_name_only=True, interval=2, verbose=False):
        """
        Wait until the benchmark job is complete.

        This method polls the benchmark status every 'interval' seconds until the status is either
        'success', 'canceled', or 'failed'. Optionally prints the status if verbose is True.

        Args:
            id (str): The benchmark job ID.
            interval (int, optional): Polling interval in seconds. Default is 2.
            verbose (bool, optional): Whether to print status updates. Default is False.

        Returns:
            dict: The complete benchmark result (aggregated report, logs, and raw output).
        """
        status = self.getBenchmarkStatus(id)
        while status['status'] != 'success' and status['status'] != 'canceled' and status['status'] != 'failed':
            status = self.getBenchmarkStatus(id)
            if verbose:
                self.logger.info(f"Benchmark status: {status['status']}")
            sleep(interval)
        return self.getBenchmarkResult(id, save_path, model_name_only)

    def getAvailableConfigurations(self):
        """
        Retrieve available benchmark runner configurations.

        Returns:
            dict: A dictionary containing available runner configurations.
        """
        url = self._build_url('/api/benchmarks/config')
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.get(url, headers=headers)
        configs = r.json().get('runners', {})
        return configs

    def getAPIStatus(self) -> dict:
        """
        Retrieve the API status information.

        This includes details such as API version and overall status.

        Returns:
            dict: A dictionary containing the API status information.
        """
        url = self._build_url('/api/status')
        r = requests.get(url)
        return r.json()

    def getBenchmarks(self) -> dict:
        """
        Retrieve all benchmarks for the authenticated user.

        Returns:
            dict: A dictionary containing all benchmark jobs. Returns None if the request fails.
        """
        url = self._build_url('/api/benchmarks')
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None
        return r.json()
    
    def getBenchmarkInfo(self, id) -> dict:
        """
        Get the general information of a benchmark job.

        Args:
            id (str): The benchmark job ID.

        Returns:
            dict: A dictionary with the information details of the benchmark job.
        """
        url = self._build_url(f'/api/benchmarks/{id}')
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None
        return r.json()

    def getErrorLog(self, id, save_path=None) -> str:
        """
        Retrieve the error log for a specific benchmark job.

        Args:
            id (str): The benchmark job ID.
            save_path (str, optional): If provided, the error log will be saved to this path.

        Returns:
            str: The error log text if available, otherwise None.
        """
        url = self._build_url(f'/api/benchmarks/{id}/error-log')
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None
        
        if save_path is not None:
            # Save the error log to the specified path
            with open(os.path.join(save_path, f"{id}_error_log.txt"), 'w') as f:
                f.write(r.text)
        
        return r.text

    def getInfoLog(self, id, save_path=None) -> str:
        """
        Retrieve the user log for a specific benchmark job.

        Args:
            id (str): The benchmark job ID.
            save_path (str, optional): If provided, the user log will be saved to this path.

        Returns:
            str: The user log text if available, otherwise None.
        """
        url = self._build_url(f'/api/benchmarks/{id}/user-log')
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None
        
        if save_path is not None:
            # Save the user log to the specified path
            with open(os.path.join(save_path, f"{id}_user_log.txt"), 'w') as f:
                f.write(r.text)

        return r.text

    def getBinaryOutput(self, id, save_path=None) -> bytes:
        """
        Retrieve the binary output of a benchmark job.

        Args:
            id (str): The benchmark job ID.
            save_path (str, optional): If provided, the binary output will be saved to this path.

        Returns:
            bytes: The binary output data as bytes if available, otherwise None.
        """
        url = self._build_url(f'/api/benchmarks/{id}/binary')
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None
        
        if save_path is not None:
            # Save the binary output to the specified path
            with open(os.path.join(save_path, f"{id}_raw_output.bin"), 'wb') as f:
                f.write(r.content)
        
        return bytes(r.content)
    
    def getModelOutput(self, id, save_path=None, name_only=True) -> any:
        """
        Retrieve the model output for a specific benchmark job.

        Args:
            id (str): The benchmark job ID.
            save_path (str, optional): If provided, the model output will be saved to this path.
            name_only (bool, optional): If True, returns only the model name instead of the bytes that represent the model output.

        Returns:
            file: The model output as bytes if available, otherwise None.
        """
        url = self._build_url(f'/api/benchmarks/{id}/trained-model')
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None
        
        content_disp = r.headers.get("Content-Disposition", "")
        model_name = None
        if 'filename=' in content_disp:
            model_name = content_disp.split('filename=')[1].strip('"')
            # Fallback to using the ID if no filename is provided
            model_name = os.path.basename(model_name)
            model_name = f"{id}_{model_name}"
        
        if save_path is not None and model_name is not None:
            # Save the model output to the specified path
            with open(os.path.join(save_path, model_name), 'wb') as f:
                f.write(r.content)

        if name_only:
            # If name_only is True, return only the model name
            return model_name

        return bytes(r.content)


    def uploadDataset(self, path) -> str:
        """
        Upload a dataset file to the API.

        Args:
            path (str): The file path of the dataset to be uploaded.

        Returns:
            str: The base name of the uploaded file if successful, otherwise None.
        """
        url = self._build_url('/api/benchmarks/datasets/upload')
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.post(url, headers=headers, files={'dataset': open(path, 'rb')})
        if r.status_code != 207:
            self.logger.error(f"Error while uploading dataset. Status : {r.status_code}, {r.raw}")
            return None
        return os.path.basename(path)

    def deleteDataset(self, name) -> bool:
        """
        Delete a dataset from the API.

        Args:
            name (str): The name of the dataset to be deleted.

        Returns:
            bool: True if the deletion is successful, otherwise False.
        """
        url = self._build_url(f'/api/benchmarks/datasets/{name}')
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.delete(url, headers=headers)
        return r.status_code == 200
    
    def deleteBenchmark(self, id) -> bool:
        """
        Delete a benchmark job from the API.

        Args:
            id (str): The ID of the benchmark job to be deleted.

        Returns:
            bool: True if the deletion is successful, otherwise False.
        """
        url = self._build_url(f'/api/benchmarks/{id}')
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.delete(url, headers=headers)
        return r.status_code == 200
    

    def uploadDatasetIfNotUploaded(self, path) -> str:
        """
        Upload a dataset file to the API if it is not already uploaded.

        Args:
            path (str): The file path of the dataset to be uploaded.

        Returns:
            str: The base name of the uploaded file if successful, otherwise None.
        """
        datasets = self.getDatasets()
        if os.path.basename(path) in datasets:
            print(f"Dataset {os.path.basename(path)} already uploaded.")
            return os.path.basename(path)
        else:
            print(f"Dataset {os.path.basename(path)} not found, uploading...")
            return self.uploadDataset(path)
    

    def startOdtBenchmark(self, target, runtime, model_path, config:OnDeviceTrainingConfig) -> str:
        """
        Start a new benchmark job for ODT.

        This method submits a benchmark job to the API for the given target device and runtime.
        It uploads the model (and optionally a dataset) to be benchmarked. Optionally, a callback function
        can be provided, which will be executed on a separate thread when the benchmark completes.

        Args:
            target (str): The target device identifier.
            runtime (str): The runtime engine to be used.
            model_path (str): Path to the model file.
            dataset (str or binary file, optional): Either a dataset name (string) or a binary file object.
            callback (function, optional): A function to be called with the benchmark result upon completion.

        Returns:
            str: The ID of the created benchmark job.

        Raises:
            Exception: If the dataset provided is neither a string nor a valid binary file.
        """
        url = self._build_url('/api/benchmarks/train')
        headers = {'Authorization': 'Bearer ' + self.token}
        data = {'device': target, 'engine': runtime}


        # Validate the configuration
        if not config.validate_config(config.config):
            raise ValueError("Configuration validation failed: see missing keys above")
        
        datasets = self.getDatasets()

        # Upload the dataset if not already uploaded
        if config.config["input"]["train_file"] not in datasets:
            if os.path.isfile(config.input_spec["train_file"]):
                dataset_ref = self.uploadDatasetIfNotUploaded(config.input_spec["train_file"])
                config.config["input"]["train_file"] = dataset_ref
                print(f"Dataset input.train_file {dataset_ref} uploaded.")
            else:
                raise Exception(f"Input train file {config.input_spec['train_file']} not found and not uploaded")

        if config.config["input"]["test_file"] not in datasets:
            if os.path.isfile(config.input_spec["test_file"]):
                dataset_ref = self.uploadDatasetIfNotUploaded(config.input_spec["test_file"])
                config.config["input"]["test_file"] = dataset_ref
                print(f"Dataset input.test_file {dataset_ref} uploaded.")
            else:
                raise Exception(f"Input test file {config.input_spec['test_file']} not found and not uploaded")
        
        if config.output_spec["train_file"] not in datasets:
            if os.path.isfile(config.output_spec["train_file"]):
                dataset_ref = self.uploadDatasetIfNotUploaded(config.output_spec["train_file"])
                config.config["output"]["train_file"] = dataset_ref
                print(f"Dataset output.train_file {dataset_ref} uploaded.")
            else:
                raise Exception(f"Output train file {config.output_spec['train_file']} not found and not uploaded")
            
        if config.output_spec["test_file"] not in datasets:
            if os.path.isfile(config.output_spec["test_file"]):
                dataset_ref = self.uploadDatasetIfNotUploaded(config.output_spec["test_file"])
                config.config["output"]["test_file"] = dataset_ref
                print(f"Dataset output.test_file {dataset_ref} uploaded.")
            else:
                raise Exception(f"Output test file {config.output_spec['test_file']} not found and not uploaded")

        # Start ODT benchmark
        r = requests.post(url, headers=headers, data=data, files={'model': open(model_path, 'rb'), 'config': config.get_config_str()})
        
        if r.status_code != 200:
            self.logger.error(f"Error while starting ODT benchmark. Status : {r.status_code}, {r.json()}")
            return -1
        
        return r.json()["id"]