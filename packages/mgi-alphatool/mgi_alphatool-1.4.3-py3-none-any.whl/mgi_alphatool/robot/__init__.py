import requests

class Robot:
    """
    Represents a robot that can execute protocols. This class provides methods to interact with the robot,
    including submitting protocols for execution.
    """
    def __init__(self, ip: str, port: int = 41950):
        """
        Initializes a Robot object with the specified IP address and port.

        Args:
            ip (str): The IP address of the robot.
            port (int, optional): The port number to connect to on the robot. Defaults to 41950.
        """
        self.ip = ip
        self.port = port

        # Test if robot is reachable
        try:
            self.system_info = self.__get_sys_info(ip, port)
        except Exception as e:
            raise RuntimeError(f"Failed to connect to robot at {ip}:{port}")

    def __get_sys_info(self, ip: str, port: int):
        """
        Retrieves the system information from the robot.

        Args:
            ip (str): The IP address of the robot.
            port (int): The port number to connect to on the robot.

        Returns:
            dict: The system information of the robot.
        """
        url = f"http://{ip}:{port}/system/system-info"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def __create_protocol(self, ip: str, port: int, data: str):
        """
        Creates a protocol on the robot.

        Args:
            ip (str): The IP address of the robot.
            port (int): The port number to connect to on the robot.
            data (str): The protocol data to be created.

        Returns:
            str: The ID of the created protocol.
        """
        files = {'files': ("temp.json", data, "application/json")}
        form_data = {'skipCheck': True}
        url = f"http://{ip}:{port}/protocols"
        response = requests.post(url, files=files, data=form_data)
        response.raise_for_status()
        result = response.json()
        
        if result['success'] == False:
            raise Exception(result['message'])
        
        return result['data']['id']
    
    def __create_run(self, ip: str, port: int, protocol_id: str):
        """
        Creates a run on the robot based on a protocol.

        Args:
            ip (str): The IP address of the robot.
            port (int): The port number to connect to on the robot.
            protocol_id (str): The ID of the protocol to create a run for.

        Returns:
            str: The ID of the created run.
        """
        url = f"http://{ip}:{port}/runs"
        data = {
            'data': {
                'protocolId': protocol_id
            }
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        
        if result['success'] == False:
            raise Exception(result['message'])
        
        return result['data']['id']
    
    def __start_run(self, ip: str, port: int, run_id: str, skip_init: bool = False):
        """
        Starts a run on the robot.

        Args:
            ip (str): The IP address of the robot.
            port (int): The port number to connect to on the robot.
            run_id (str): The ID of the run to start.
            skip_init (bool, optional): If True, skips the initialization phase of the run. Defaults to False.

        Returns:
            str: The message indicating the start of the run.
        """
        url = f"http://{ip}:{port}/runs/{run_id}/actions"
        data = {
            'data': {
                'actionType': 'play',
                'skipPipInit': skip_init,
                'skipModuleInit': True
            }
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()

        if result['success'] == False:
            raise Exception(result['message'])
        
        return result['message']

    def submit(self, data: str, skip_init: bool = False):
        """
        Submits a protocol to the robot for execution.

        This method checks the robot's status, creates a protocol, a run, and starts the run. It can optionally skip the initialization phase.

        Args:
            data (str): The protocol data to be submitted.
            skip_init (bool, optional): If True, skips the robot initialization phase. Defaults to False.
        """
        # Check robot status
        system_info = self.__get_sys_info(self.ip, self.port)
        if system_info['data']['isInitialized'] == False:
            raise RuntimeError("Robot is not initialized. Please initialize the robot first.")
        
        # Create protocol
        protocol_id = self.__create_protocol(self.ip, self.port, data)
        
        # Create run
        run_id = self.__create_run(self.ip, self.port, protocol_id)

        # Start run
        self.__start_run(self.ip, self.port, run_id, skip_init)
