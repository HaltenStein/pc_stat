import socket
import psutil as ps
import sys
from distutils import spawn
from subprocess import Popen, PIPE
from os import environ
from threading import Thread
from queue import Queue
from client_json_model import StatisticsPC
from stat_loging import add_info


class CreateClient:
    @staticmethod
    def connecting_server() -> socket:
        """Creating a connection to the server"""
        while True:
            try:
                # network data client
                host = socket.gethostbyname(socket.gethostname())
                port = 11110  #defolt port from this app 
                client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                client.bind((host, port))

                # network data server
                server_ip = input("Enter server ip: ")
                check_ip = server_ip.split('.')
                if len(check_ip) == 4:
                    for digit in check_ip:
                        if 0 > int(digit) or int(digit) > 256:
                            break
                    else:
                        server_port = int(input("Enter server port: "))   
                        server = (server_ip, server_port)

                        print(host, "\n[ Client Started ]")
                        return server, client, host

                print('Input error server ip')
            except Exception as e:
                    print("Input error: ", e)


class Client:
    # sample json code with PC data
    PC_EXAMP = StatisticsPC.parse_raw(StatisticsPC.example())

    def __init__(self, server: list, client: socket, host: str,
                     OS:str, NVIDIA_SMI: str) -> None:
        self.server = server
        self.client = client
        self.host = host
        self.OS = OS
        self.NVIDIA_SMI = NVIDIA_SMI

    def get_cpu_stat(self) -> None:
        """Получение статистики от процессора\n
        Getting statistics from CPU"""
        self.PC_EXAMP.PC[0].cpu_percent = ps.cpu_percent()
        self.PC_EXAMP.PC[0].full_memory = ps.virtual_memory().total
        self.PC_EXAMP.PC[0].used_memory = ps.virtual_memory().percent
        if self.OS == 'linux':
            self.PC_EXAMP.PC[0].temperature = ps.sensors_temperatures()
        self.PC_EXAMP.ip = self.host

    def get_gpu_stat(self) -> None:
        """Получение статистики от видеокарты\n
            Getting statistics from GPU\n
            Only NVIDIA"""
        try:  # get stat GPU from nvidia-smi.exe utility
            p = Popen([self.NVIDIA_SMI,"""--query-gpu=index,name,temperature.gpu,utilization.gpu,memory.total,memory.used""", "--format=csv,noheader,nounits"], stdout=PIPE)
        except Exception as e:
            print(e)
        else:
            stdout, stderror = p.communicate()
            output = stdout.decode('UTF-8')
            output = output.split(', ')

            self.PC_EXAMP.GPU[0].id = output[0]
            self.PC_EXAMP.GPU[0].name = output[1]
            self.PC_EXAMP.GPU[0].GPU_temp = output[2]
            self.PC_EXAMP.GPU[0].GPU_util = output[3]
            self.PC_EXAMP.GPU[0].mem_total = output[4]
            self.PC_EXAMP.GPU[0].mem_used = output[5]

    def send_stat(self) -> list:
        self.get_cpu_stat() 
        self.get_gpu_stat()
        add_info(self.PC_EXAMP)  # logging in file '.log'
        self.client.sendto(self.PC_EXAMP.json().encode('UTF-8'), self.server)


def receiving_data(client, q):
    """thread receiving data from the server"""
    while True:
        data, addr = client.recvfrom(1024)
        q.put(data)


if __name__ == '__main__':
    OS = sys.platform  # platform name

    # search for the video card utility
    if OS == "win32":
        NVIDIA_SMI = spawn.find_executable('nvidia-smi')
        if NVIDIA_SMI is None:
            NVIDIA_SMI = """%s\\Program Files\\
                NVIDIA Corporation\\NVSMI\\nvidia-smi.exe""" % environ['systemdrive']
    else:
        NVIDIA_SMI = "nvidia-smi"

    # socket data client
    data_server, data_client, host = CreateClient.connecting_server()

    # thread receiving data from the server
    q = Queue()
    th = Thread(target=receiving_data, args=(data_client, q, ), daemon=True, name='data from server')
    th.start()
    
    # creating an instance of the class and starting a loop for sending statistics
    send_stat = Client(data_server, data_client, host, OS, NVIDIA_SMI)

    # main loop
    operating_mode = 'send statistics'
    while operating_mode != 'close':
        if operating_mode == 'send statistics':
            send_stat.send_stat()
        elif operating_mode == '2':
            # ToDo sending a '.log' file to the server
            operating_mode = 'send statistics'  
        operating_mode = q.get().decode('UTF-8')
        q.task_done()

    data_client.sendto('close'.encode('UTF-8'), data_server)
    data_client.close()
