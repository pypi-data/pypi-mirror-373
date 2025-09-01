import logging
import os
import re
import signal
import socket
from time import sleep
from typing import Callable, List, Tuple, Union

from .api_method import ApiMethod
from .config_field import ConfigField
from .device import Device
from .exceptions import (
    AuthenticationException,
    AuthorizationException,
    CommunicationException,
    ConfigNotSetException,
    InvalidIPException,
    EmptyParamsException,
    MessageSizeException,
    MutedSystemException,
    SetDatetimeException,
    UnusableSocketException,
)


# Get library-specific logger to prevent duplication
_logger = logging.getLogger("ipio")


class IPIO:
    MAX_MESSAGE_SIZE: int = 1023
    SOCKET_TIMEOUT: int = 5
    CONNECTION_TRIAL_COUNT: int = 2

    def __init__(
        self,
        ip: str,
        username: str,
        password: str,
        application_port: int,
    ):
        try:
            # for the command line/console application
            signal.signal(signal.SIGINT, self.signal_handler)
        except ValueError as e:
            _logger.info(f"Signal is only for CLI usage: {e}")

        self.ip: str = ip
        self.username: str = username
        self.password: str = password

        self.application_port: int = application_port
        self.sock: socket.socket = self._connect()

    @staticmethod
    def _validate_ip_only(ip_address: str) -> bool:
        """Validates IP address without netmask."""
        regex = r"^((25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$"
        return bool(re.match(regex, ip_address))

    def _connect(self) -> socket.socket:
        """
        method to connect to the device, called automatically in constructor
        :raises UnusableSocketException: for authentication returning empty params
        :raises EmptyParamsException: for authorize returning empty socket
        :return: the socket connection
        """
        accept_sock: socket.socket = IPIO._establish_socket_connection(
            self.ip, self.application_port
        )

        params: List[str] = IPIO._authenticate(
            accept_sock, self.username, self.password
        )

        if not params:
            raise EmptyParamsException("Empty params during login...")

        port: int = int(params[2])
        token: str = params[3]
        sock, authorize_params = IPIO._authorize(self.ip, port, token)
        # immediately close the acceptance socket as well
        accept_sock.close()

        if not sock:
            raise UnusableSocketException("Unusable socket during login...")

        return sock

    @staticmethod
    def _establish_socket_connection(ip: str, port: int) -> socket.socket:
        """
        Unfortunately, there is an arbitrary sleep time in the connection establishing
        If you just try to send one connection request after another it just refuses

        :param ip: IPIO device ip
        :param port: application or connection acceptance port
        :raise socket.sockettimeout: connection timeout exception on socket.connect
        :return: newly created socket for operation
        """
        # so we get the same time of trial as the socket timeout
        trial_count: int = IPIO.SOCKET_TIMEOUT * IPIO.CONNECTION_TRIAL_COUNT
        sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(IPIO.SOCKET_TIMEOUT)

        while trial_count > 0:
            try:
                sock.connect((ip, port))
                return sock
            except ConnectionRefusedError as e:
                _logger.warning(
                    f"{e}: Too soon for another connection. Trying again... {trial_count}"
                )
                sleep(0.1)
            except socket.timeout as e:
                _logger.warning(f"{e}: Socket connection timedout")
                sock.close()
                raise socket.timeout(e)
            finally:
                trial_count -= 1
        return sock

    @staticmethod
    def _send_message(
        sock: socket.socket, msg: str, wait_for_response: bool = True
    ) -> str:
        """
        For sending standard messages to IPIO

        :param sock: socket connection to send the message over on
        :param msg: message to be sent, cannot be larger than IPIO.MAX_MESSAGE_SIZE
        :param wait_for_response: fire and forget or wait for a response?
        :raise MessageSizeException: for exceeding the IPIO.MAX_MESSAGE_SIZE
        :return:
        """
        byte_msg: bytes = msg.encode("utf-8")
        if len(byte_msg) > IPIO.MAX_MESSAGE_SIZE:
            raise MessageSizeException(
                f"Single message cannot be larger than {IPIO.MAX_MESSAGE_SIZE}"
            )
        sock.sendall(byte_msg)
        response: str = ""
        if wait_for_response:
            response = sock.recv(1024).decode("utf-8")
        return response

    @staticmethod
    def _parse_response(response: str) -> Tuple[str, List[str]]:
        """
        get the response between the gt and lt markers
        the format is <API_METHOD;param1,param2,param3...>

        :param response: the response received from the IPIO
        :return: return the method for checking and also return the parameter list
        """

        # markers
        start_marker: str = "<"
        end_marker: str = ">"

        # marker indices for slicing
        start: int = response.index(start_marker) + len(start_marker)
        end: int = response.index(end_marker, start + 1)

        # get rid of the markers and structure the response
        # try:
        response = response[start:end]
        method: str = response.split(";")[0]
        params: str = response.split(";")[1]
        params_list: List[str] = params.split(",")
        return method, params_list
        # except:
        #    return "_", response

    @staticmethod
    def _authenticate(accept_sock: socket.socket, username: str, password: str) -> List:
        """
        the response from IPIO is something like this;
        <login;ok,1,57803,BDC313853F8090D94BBF14D9BAD4D7D5>

        ok is for success
        1 is the active connection count
        57803 is the port
        last item is the token for the authorization

        after authorization, new port and token should be valid for short while
        after that the port should be closed and token should be destroyed

        :param accept_sock: application or acceptance socks
        :param username: username for the IPIO
        :param password: passsword for the username
        :raise AuthenticationException: For authentication errors
        :return:
        """
        msg: str = f"<{ApiMethod.AUTHENTICATE};{username},{password}>"
        response: str = IPIO._send_message(accept_sock, msg)
        method, params = IPIO._parse_response(response)
        success: str = params[0]
        if method != ApiMethod.AUTHENTICATE or success != "ok":
            raise AuthenticationException(
                f"Couldn't authenticate with username: {username}. {method}:{success}"
            )
        return params

    @staticmethod
    def _authorize(ip: str, port: int, token: str) -> Tuple[socket.socket, List[str]]:
        """
        :param port: port for the new connection
        :param token: this is generated only for this port and for a short time
        :raise AuthorizationException: for authorization errors
        :return:
        """
        new_sock: socket.socket = IPIO._establish_socket_connection(ip=ip, port=port)
        msg: str = f"<{ApiMethod.AUTHORIZE};{token}>"
        response: str = IPIO._send_message(new_sock, msg)
        method, params = IPIO._parse_response(response)
        success: str = params[0]

        if method != ApiMethod.AUTHORIZE or success != "ok":
            raise AuthorizationException(
                f"Authorization unsuccessful. {method}:{success}"
            )

        return new_sock, params

    def set_output_as_bulk(self, output_string: str) -> str:
        """
        set the outputs in one go. Any one output can take one of three values;
        0=LOW
        1=HIGH
        2=PULSE
        3=NO_CHANGE
        :param output_string: 8 char string
        :return: return the parameters in the form of 8 char string
        """
        msg: str = f"<{ApiMethod.SET_OUTPUT_BULK};{output_string}>"
        response: str = IPIO._send_message(self.sock, msg)
        method, params = IPIO._parse_response(response)
        if method != ApiMethod.SET_OUTPUT_BULK:
            # Check if this is actually a mute condition or just a communication error
            if method == "error" and len(params) > 0 and "muted" in params[0].lower():
                raise MutedSystemException(
                    f"System is muted, could not set outputs to {output_string}"
                )
            else:
                raise CommunicationException(
                    f"Unexpected response: expected {ApiMethod.SET_OUTPUT_BULK}, got {method}"
                )
        return params[0]

    def get_output_as_bulk(self) -> str:
        """
        get the outputs in one go
        :return: return the parameters in the form of 8 char string
        """
        msg: str = f"<{ApiMethod.GET_OUTPUT_BULK}>"
        response: str = IPIO._send_message(self.sock, msg)
        method, params = IPIO._parse_response(response)
        if method != ApiMethod.GET_OUTPUT_BULK:
            raise MutedSystemException("System is muted, could not get outputs as bulk")
        return params[0]

    def set_output(self, pin: int, val: int) -> List[str]:
        """
        :param pin: which relay to update
        :param val: 0 for OFF, 1 for ON, 2 for PULSE, 3 for NO_CHANGE
        :return: return the parameters in the form pin,val
        """
        msg: str = f"<{ApiMethod.SET_OUTPUT};{pin},{val}>"
        response: str = IPIO._send_message(self.sock, msg)
        method, params = IPIO._parse_response(response)
        if method != ApiMethod.SET_OUTPUT:
            # Check if this is actually a mute condition or just a communication error
            if method == "error" and len(params) > 0 and "muted" in params[0].lower():
                raise MutedSystemException(
                    f"System is muted, could not set output DO{pin} to {val}"
                )
            else:
                raise CommunicationException(
                    f"Unexpected response: expected {ApiMethod.SET_OUTPUT}, got {method}"
                )
        return params

    def set_led(self, pin: int, val: int) -> List[str]:
        """
        :param pin: which led to update
        :param val: 0 for OFF, 1 for ON, 2 for PULSE, 3 for NO_CHANGE
        :return: return sent message
        """
        msg: str = f"<{ApiMethod.SET_LED};{pin},{val}>"
        response: str = IPIO._send_message(self.sock, msg)
        method, params = IPIO._parse_response(response)
        return params

    def set_mute(self, val: int) -> str:
        """
        Set mute from software side
        :param val: 0 for OFF, 1 for ON
        :return: return sent message
        """
        msg: str = f"<{ApiMethod.SET_MUTE};{val}>"
        return IPIO._send_message(self.sock, msg)

    def get_output(self, pin: int) -> List[str]:
        """
        :param pin: which relay to query for
        :return: return a list with first item as pin number and second as state
        """
        msg: str = f"<{ApiMethod.GET_OUTPUT};{pin}>"
        response: str = IPIO._send_message(self.sock, msg)
        method, params = IPIO._parse_response(response)
        return params

    def get_input(self, pin: int) -> List[str]:
        """
        :param pin: which input to query for
        :return: return the state of output as <get_output;1,0>
                 which would mean relay 1 is OFF
        """
        msg: str = f"<{ApiMethod.GET_INPUT};{pin}>"
        response: str = IPIO._send_message(self.sock, msg)
        method, params = IPIO._parse_response(response)
        return params

    def get_input_as_bulk(self) -> str:
        """
        :return: return the state of output as <get_output;1,0>
                 which would mean relay 1 is OFF
        """
        msg: str = f"<{ApiMethod.GET_INPUT_BULK}>"
        response: str = IPIO._send_message(self.sock, msg)
        method, params = IPIO._parse_response(response)
        return params[0]

    def get_version(self) -> str:
        """
        :return: return the firmware version
        """
        msg: str = f"<{ApiMethod.GET_VERSION}>"
        response: str = IPIO._send_message(self.sock, msg)
        _, params = IPIO._parse_response(response)
        version: str = params[0]
        return version

    def set_datetime(self, datetime: str) -> List[str]:
        """
        :return: set the datetime with 2015-11-23 08:10:40 format
        """
        msg: str = f"<{ApiMethod.SET_DATETIME};{datetime}>"
        response: str = IPIO._send_message(self.sock, msg)
        method, params = IPIO._parse_response(response)
        if method != ApiMethod.SET_DATETIME or params[0] != datetime:
            raise SetDatetimeException(
                f"Couldn't set datetime to: {datetime}:{params[0]}"
            )
        return params

    def get_datetime(
        self,
    ) -> List[str]:
        """
        :return: return the MAC address
        """
        msg: str = f"<{ApiMethod.GET_DATETIME}>"
        response: str = IPIO._send_message(self.sock, msg)
        _, params = IPIO._parse_response(response)
        return params

    def get_mac(self) -> str:
        """
        :return: return the MAC address
        """
        msg: str = f"<{ApiMethod.GET_MAC}>"
        response: str = IPIO._send_message(self.sock, msg)
        _, params = IPIO._parse_response(response)
        mac: str = params[0]
        return mac

    def generate_mac(self) -> str:
        """
        :return: generate a mac address
        """
        msg: str = f"<{ApiMethod.GENERATE_MAC}>"
        response: str = IPIO._send_message(self.sock, msg)
        _, params = IPIO._parse_response(response)
        mac: str = params[0]
        return mac

    def set_connection_timeout(self, timeout: int = 10000) -> None:
        """
        :param timeout: how much to wait for a connection before deciding it is closed
        """
        response: str = self.set_config(ConfigField.CONNECTION_TIMEOUT, timeout)
        method, params = IPIO._parse_response(response)
        config_field_name: str = params[0]
        if (
            method != ApiMethod.SET_CONFIG
            or config_field_name != ConfigField.CONNECTION_TIMEOUT
        ):
            raise ConfigNotSetException(
                f"Unable to set connection_timeout to {timeout}"
            )

    def get_connection_timeout(self) -> int:
        """
        :return: retrieve connection timeout in ms
        """
        connection_timeout: str = self.get_config(ConfigField.CONNECTION_TIMEOUT)
        return int(connection_timeout)

    def set_port_provisioning_timeout(self, timeout: int = 10000) -> None:
        """
        :param timeout: how much to wait for a connection before closing the socket
        """
        response: str = self.set_config(ConfigField.PORT_PROVISIONING_TIMEOUT, timeout)
        method, params = IPIO._parse_response(response)
        config_field_name: str = params[0]
        if (
            method != ApiMethod.SET_CONFIG
            or config_field_name != ConfigField.PORT_PROVISIONING_TIMEOUT
        ):
            raise ConfigNotSetException(
                f"Unable to set port_provisioning_timeout to {timeout}"
            )

    def get_port_provisioning_timeout(self) -> int:
        """
        :return: retrieve port provisioning timeout in ms
        """
        port_provisioning_timeout: str = self.get_config(
            ConfigField.PORT_PROVISIONING_TIMEOUT
        )
        return int(port_provisioning_timeout)

    def set_recovery_preset(self, preset: str = "33333310") -> None:
        """
        :param preset: default preset doesn't change the pins lights the yellow
        indicator and turns off the red
        """
        response: str = self.set_config(ConfigField.RECOVERY_PRESET, preset)
        method, params = IPIO._parse_response(response)
        config_field_name: str = params[0]
        if (
            method != ApiMethod.SET_CONFIG
            or config_field_name != ConfigField.RECOVERY_PRESET
        ):
            raise ConfigNotSetException(f"Unable to set recovery preset to {preset}")

    def get_recovery_preset(self) -> str:
        """
        :return: get recovery preset
        """
        recovery_preset: str = self.get_config(ConfigField.RECOVERY_PRESET)
        return recovery_preset

    def set_emergency_preset(self, preset: str = "00000002") -> None:
        """
        :param preset: default preset assumes all pins set to unsafe positions,
        yellow light turned off and red light blinks
        """
        response: str = self.set_config(ConfigField.EMERGENCY_PRESET, preset)
        method, params = IPIO._parse_response(response)
        config_field_name: str = params[0]
        if (
            method != ApiMethod.SET_CONFIG
            or config_field_name != ConfigField.EMERGENCY_PRESET
        ):
            raise ConfigNotSetException(f"Unable to set emergency preset to {preset}")

    def get_emergency_preset(self) -> str:
        """
        :return: get emergency preset
        """
        emergency_preset: str = self.get_config(ConfigField.EMERGENCY_PRESET)
        return emergency_preset

    def set_mute_preset(self, preset: str = "11111101") -> None:
        """
        :param preset: default preset assumes all pins set to safe positions,
        yellow light turned off and red light turned on
        """
        response: str = self.set_config(ConfigField.MUTE_PRESET, preset)
        method, params = IPIO._parse_response(response)
        config_field_name: str = params[0]
        if (
            method != ApiMethod.SET_CONFIG
            or config_field_name != ConfigField.MUTE_PRESET
        ):
            raise ConfigNotSetException(f"Unable to set mute preset to {preset}")

    def get_mute_preset(self) -> str:
        """
        :return: get mute preset
        """
        mute_preset: str = self.get_config(ConfigField.MUTE_PRESET)
        return mute_preset

    def set_mute_input(self, pin_number: int = 1) -> None:
        response: str = self.set_config(ConfigField.MUTE_INPUT, pin_number)
        method, params = IPIO._parse_response(response)
        config_field_name: str = params[0]
        if (
            method != ApiMethod.SET_CONFIG
            or config_field_name != ConfigField.MUTE_INPUT
        ):
            raise ConfigNotSetException(f"Unable to set mute input to {pin_number}")

    def get_mute_input(self) -> int:
        """
        :return: mute input DI
        """
        mute_input: str = self.get_config(ConfigField.MUTE_INPUT)
        return int(mute_input)

    def set_config(self, config_param: str, val: Union[int, str]) -> str:
        """
        Send the config message then return the response as raw. This should only be
        used as intermediary method for the higher level counterpart.

        :param config_param: config name
        :param val: the value to be set
        :return: return the raw message for the higher level function to process
        """
        msg: str = f"<{ApiMethod.SET_CONFIG};{config_param},{val}>"
        return IPIO._send_message(self.sock, msg)

    def set_ip(self, ip: str) -> None:
        """
        you need to reset the W5500 device after the reset
        :param ip: ip address of the IPIO
        :return: None
        """

        if not IPIO._validate_ip_only(ip):
            raise InvalidIPException(f"This is not in the correct IPV4 format: {ip}")

        response: str = self.set_config(ConfigField.IP, ip)
        method, params = IPIO._parse_response(response)
        config_field_name: str = params[0]
        if method != ApiMethod.SET_CONFIG or config_field_name != ConfigField.IP:
            raise ConfigNotSetException(f"Unable to set the IP to {ip}")

    def get_ip(self) -> str:
        """
        :return: ip
        """
        ip: str = self.get_config(ConfigField.IP)
        return ip

    def set_netmask(self, netmask: str) -> None:
        """
        :param netmask: netmask address of the IPIO
        :return: None
        """
        if not IPIO._validate_ip_only(netmask):
            raise InvalidIPException(
                f"This is not in the correct IPV4 format: {netmask}"
            )

        response: str = self.set_config(ConfigField.NETMASK, netmask)
        method, params = IPIO._parse_response(response)
        config_field_name: str = params[0]
        if method != ApiMethod.SET_CONFIG or config_field_name != ConfigField.NETMASK:
            raise ConfigNotSetException(f"Unable to set the netmask to {netmask}")

    def get_netmask(self) -> str:
        """
        :return: netmask
        """
        netmask: str = self.get_config(ConfigField.NETMASK)
        return netmask

    def set_gateway(self, gateway: str) -> None:
        """
        :param gateway: gateway or router address for the network IPIO is in
        :return: None
        """

        if not IPIO._validate_ip_only(gateway):
            raise InvalidIPException(
                f"This is not in the correct IPV4 format: {gateway}"
            )

        response: str = self.set_config(ConfigField.GATEWAY, gateway)
        method, params = IPIO._parse_response(response)
        config_field_name: str = params[0]
        if method != ApiMethod.SET_CONFIG or config_field_name != ConfigField.GATEWAY:
            raise ConfigNotSetException(f"Unable to set the IP to {gateway}")

    def get_gateway(self) -> str:
        """
        :return: gateway
        """
        gateway: str = self.get_config(ConfigField.GATEWAY)
        return gateway

    def set_username(self, username: str) -> None:
        """
        :param username: default io admin username
        :return: None
        """
        response: str = self.set_config(ConfigField.USERNAME, username)
        method, params = IPIO._parse_response(response)
        config_field_name: str = params[0]
        if method != ApiMethod.SET_CONFIG or config_field_name != ConfigField.USERNAME:
            raise ConfigNotSetException(f"Unable to set the username to {username}")

    def get_username(self) -> str:
        """
        :return: admin username
        """
        username: str = self.get_config(ConfigField.USERNAME)
        return username

    def set_password(self, password: str) -> None:
        """
        :param password: password for the io admin user
        :return: None
        """
        response: str = self.set_config(ConfigField.PASSWORD, password)
        method, params = IPIO._parse_response(response)
        config_field_name: str = params[0]
        if method != ApiMethod.SET_CONFIG or config_field_name != ConfigField.PASSWORD:
            raise ConfigNotSetException(f"Unable to set the password to {password}")

    def get_password(self) -> str:
        """
        :return: admin password
        """
        password: str = self.get_config(ConfigField.PASSWORD)
        return password

    def set_service_username(self, service_username: str = "ioserv") -> None:
        """
        :param service_username: default io service username
        :return: None
        """
        response: str = self.set_config(ConfigField.SERVICE_USERNAME, service_username)
        method, params = IPIO._parse_response(response)
        config_field_name: str = params[0]
        if (
            method != ApiMethod.SET_CONFIG
            or config_field_name != ConfigField.SERVICE_USERNAME
        ):
            raise ConfigNotSetException(
                f"Unable to set the service username to {service_username}"
            )

    def get_service_username(self) -> str:
        """
        :return: service user username
        """
        service_username: str = self.get_config(ConfigField.SERVICE_USERNAME)
        return service_username

    def set_service_password(self, service_password: str) -> None:
        """
        :param service_password: service_password for the io service user
        :return: None
        """
        response: str = self.set_config(ConfigField.SERVICE_PASSWORD, service_password)
        method, params = IPIO._parse_response(response)
        config_field_name: str = params[0]
        if (
            method != ApiMethod.SET_CONFIG
            or config_field_name != ConfigField.SERVICE_PASSWORD
        ):
            raise ConfigNotSetException(
                f"Unable to set the service_password to {service_password}"
            )

    def get_service_password(self) -> str:
        """
        :return: service user password
        """
        service_password: str = self.get_config(ConfigField.SERVICE_PASSWORD)
        return service_password

    def set_application_port(self, port: int) -> None:
        """
        :param application port
        """
        response: str = self.set_config(ConfigField.APPLICATION_PORT, port)
        method, params = IPIO._parse_response(response)
        config_field_name: str = params[0]
        if (
            method != ApiMethod.SET_CONFIG
            or config_field_name != ConfigField.APPLICATION_PORT
        ):
            raise ConfigNotSetException(f"Unable to set application port to {port}")

    def get_application_port(self) -> int:
        """
        :return: application port
        """
        application_port: str = self.get_config(ConfigField.APPLICATION_PORT)
        return int(application_port)

    def set_pulse_interval(self, interval: int = 500) -> None:
        """
        :param interval: on/off interval in milliseconds
        :return: None
        """
        response: str = self.set_config(ConfigField.PULSE_INTERVAL, interval)
        method, params = IPIO._parse_response(response)
        config_field_name: str = params[0]
        if (
            method != ApiMethod.SET_CONFIG
            or config_field_name != ConfigField.PULSE_INTERVAL
        ):
            raise ConfigNotSetException(f"Unable to set pulse interval to {interval}")

    def get_pulse_interval(self) -> int:
        """
        :return: int pulse interval in ms
        """
        interval: str = self.get_config(ConfigField.PULSE_INTERVAL)
        return int(interval)

    def get_config(self, config_param: str) -> str:
        """
        Get the configuration setting in the storage

        :param config_param: config name
        :return: return preset value
        """
        msg: str = f"<{ApiMethod.GET_CONFIG};{config_param}>"
        response: str = IPIO._send_message(self.sock, msg)
        _, params = IPIO._parse_response(response)
        return params[-1]

    def signal_handler(self, sig, frame):
        self.monitor(0, None)
        self.close()
        exit(0)

    def monitor(self, val: int, printer_function: Callable[[str], None]) -> None:
        """
        start/stop the monitoring using 1 and 0
        """
        msg: str = f"<{ApiMethod.MONITOR};{val}>"
        byte_msg: bytes = msg.encode("utf-8")
        self.sock.sendall(byte_msg)

        while val == 1:
            single_response = self.sock.recv(1024).decode("latin-1")
            _logger.info(single_response)
            printer_function(single_response)
            if single_response == f"<{ApiMethod.GET_LOG}>":
                break

    def clear_logs(self) -> List[str]:
        """
        clear the logs this should be used for testing and debugging purposes
        """
        # response: str = IPIO._send_message(self.sock, msg)
        msg: str = f"<{ApiMethod.CLEAR_LOG}>"
        response: str = IPIO._send_message(self.sock, msg)
        _, params = IPIO._parse_response(response)
        return params

    def get_logs(self) -> List[str]:
        """
        :return: return the firmware version
        """
        msg: str = f"<{ApiMethod.GET_LOG}>"
        byte_msg: bytes = msg.encode("utf-8")
        self.sock.sendall(byte_msg)
        response: List[str] = []
        single_response: str = ""
        while single_response != "<get_log>":
            single_response = self.sock.recv(1024).decode("latin-1")
            response.append(single_response)
        return response

    def reset(self, device: Device) -> None:
        """
        resets the device or the ethernet controller

        :param device: 0 for stm32 1 for w5500
        """
        msg: str = f"<{ApiMethod.RESET};{device}>"
        IPIO._send_message(self.sock, msg, wait_for_response=False)

    def update(self, file_name: str) -> bool:
        def crc32mpeg2(chunks, crc=0xFFFFFFFF):
            for buf in chunks:
                for val in buf:
                    crc ^= val << 24
                    for _ in range(8):
                        crc = (
                            ((crc << 1) & 0xFFFFFFFF)
                            if (crc & 0x80000000) == 0
                            else (((crc << 1) & 0xFFFFFFFF) ^ 0x104C11DB7)
                        )
            return crc & 0xFFFFFFFF

        file_stats = os.stat(file_name)
        file_size = file_stats.st_size
        file_in_chunks = []

        with open(file_name, "rb") as f:
            while content := f.read(1024):
                file_in_chunks.append(content)

        crc = crc32mpeg2(file_in_chunks)

        try:
            response = IPIO._send_message(self.sock, "<update>")
            _logger.info(f"[Update Progress: Initiated]: {response}")

            response = IPIO._send_message(self.sock, str(file_size))
            _logger.info(f"[Update Progress: Size Sent]: {response}")

            for fic in file_in_chunks:
                self.sock.sendall(fic)
                response = self.sock.recv(1024).decode("utf-8")
                _logger.info(f"[Update Progress: Sending File...]: {response}")
            response = self.sock.recv(1024).decode("utf-8")
            _logger.info(f"[Update Progress: File Sent]: {response}")
            response = IPIO._send_message(self.sock, str(crc), wait_for_response=False)
            _logger.info("[Update Progress: Completed]")
            return True
        except socket.timeout:
            _logger.info(
                "[Update Progress: Interrupted by socket.timeout, try again...]"
            )
            return False

    def close(self) -> None:
        """
        close the socket connection
        """
        self.sock.close()
