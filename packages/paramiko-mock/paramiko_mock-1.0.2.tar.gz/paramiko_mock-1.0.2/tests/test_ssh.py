import paramiko
from io import StringIO
from src.ParamikoMock.mocked_env import ParamikoMockEnviron
from src.ParamikoMock.ssh_mock import SSHClientMock, SSHCommandMock, SSHCommandFunctionMock, SSHResponseMock
from src.ParamikoMock.sftp_mock import SFTPClientMock, SFTPFileMock 
from unittest.mock import patch

# Functions below are examples of what an application could look like
def example_function_1():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Some example of connection
    client.connect('some_host',
                    port=22,
                    username='root',
                    password='root',
                    banner_timeout=10)
    stdin, stdout, stderr = client.exec_command('ls -l')
    return stdout.read()

def example_function_2():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Some example of connection
    client.connect('some_host_2',
                    port=4826,
                    username='root',
                    password='root',
                    banner_timeout=10)
    stdin, stdout, stderr = client.exec_command('sudo docker ps')
    return stdout.read()

def example_function_3():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Some example of connection
    client.connect('some_host_3',
                    port=22,
                    username='root',
                    password='root',
                    banner_timeout=10)
    stdin, stdout, stderr = client.exec_command('custom_command --param1 value1')
    return stdout.read()

def example_function_multiple_calls():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Some example of connection
    client.connect('some_host',
                    port=22,
                    username='root',
                    password='root',
                    banner_timeout=10)
    client.exec_command('ls -l')
    client.exec_command('ls -al')

# Actual tests
# -- This ensures that the ParamikoMock is working as expected
def test_example_function_1():
    ParamikoMockEnviron().add_responses_for_host('some_host', 22, {
        'ls -l': SSHCommandMock('', 'ls output', '')
    }, 'root', 'root')
    with patch('paramiko.SSHClient', new=SSHClientMock): 
        output = example_function_1()
        assert output == 'ls output'

def test_example_function_2():
    ssh_mock = SSHClientMock()
    ParamikoMockEnviron().add_responses_for_host('some_host_2', 4826, {
        'sudo docker ps': SSHCommandMock('', 'docker-ps-output', '')
    }, 'root', 'root')
    # patch the paramiko.SSHClient with the mock
    with patch('paramiko.SSHClient', new=SSHClientMock): 
        output = example_function_2()
        assert output == 'docker-ps-output'

def test_example_function_3():
    # We can also use a custom command processor
    def custom_command_processor(ssh_client_mock: SSHClientMock, command: str):
        # Parse the command and do something with it
        if 'param1' in command and 'value1' in command:
            return StringIO(''), StringIO('value1'), StringIO('')
    
    # You can use a regexp expresion to match the command with the custom processor
    ParamikoMockEnviron().add_responses_for_host('some_host_3', 22, {
        r're(custom_command .*)': SSHCommandFunctionMock(custom_command_processor) # This is a regexp command
    }, 'root', 'root')
    # patch the paramiko.SSHClient with the mock
    with patch('paramiko.SSHClient', new=SSHClientMock): 
        output = example_function_3()
        assert output == 'value1'
    ParamikoMockEnviron().cleanup_environment()

def test_example_function_verify_commands_were_called():
    ParamikoMockEnviron().add_responses_for_host('some_host', 22, {
        're(ls.*)': SSHCommandMock('', 'ls output', '')
    }, 'root', 'root')
    with patch('paramiko.SSHClient', new=SSHClientMock):
        example_function_multiple_calls()
        # Use the assert commands to define the expected commands
        ParamikoMockEnviron().assert_command_executed_on_index('some_host', 22, 'ls -l', 0)
        ParamikoMockEnviron().assert_command_executed_on_index('some_host', 22, 'ls -al', 1)
        ParamikoMockEnviron().assert_command_was_executed('some_host', 22, 'ls -l')
        ParamikoMockEnviron().assert_command_was_executed('some_host', 22, 'ls -al')
        ParamikoMockEnviron().assert_command_was_not_executed('some_host', 22, 'ls -alx')
    ParamikoMockEnviron().cleanup_environment()

class MyCustomSSHResponse(SSHResponseMock):
    def __init__(self, *args, **kwargs):
        pass
        # You can initialize any custom attributes here
    
    def __call__(self, ssh_client_mock: SSHClientMock, command:str) -> tuple[StringIO, StringIO, StringIO]:
        # any custom logic here, you can use the command to determine the output 
        # or the ssh_client_mock to get information about the connection
        command_output = ssh_client_mock.device.host + ' ' + command
        # Output should be in the form of (stdin, stdout, stderr)
        return StringIO(""), StringIO(command_output), StringIO("")

def test_custom_class():
    ParamikoMockEnviron().add_responses_for_host('some_host', 22, {
        're(ls.*)': MyCustomSSHResponse()
    }, 'root', 'root')
    with patch('paramiko.SSHClient', new=SSHClientMock):
        output = example_function_1()
        assert output == 'some_host ls -l'
    ParamikoMockEnviron().cleanup_environment()