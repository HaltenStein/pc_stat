import socket
from time import sleep
from queue import Queue
from threading import Thread
from server_json_model import StatisticsPC


class CreatingServer:
    """Сreating a server socket"""
    @staticmethod
    def create() -> socket:
        while True:
            try:
                # network data server
                host = socket.gethostbyname(socket.gethostname())
                port = int(input("Enter server port: "))
                server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                server.bind((host, port))

                # data bot
                bot_ip = input("Enter bot ip: ")
                check_ip = bot_ip.split('.')
                if len(check_ip) == 4:
                    for digit in check_ip:
                        if 0 > int(digit) or int(digit) > 256:
                            break
                    else:
                        bot_port = int(input("Enter bot port: "))
                        bot = (bot_ip, bot_port)

                        print(host, "\n[ Server Started ]")
                        return server, bot, host

                print('Input error bot ip')
            except Exception as e:
                    print("Input error: ", e)


class SendData:
    clients: list = []
    def __init__(self, server, q):
        self.server = server
        self.q: Queue = q

    def send_settings(self):
        while True:
            sleep(5)
            if not self.q.empty():
                self.clients = self.q.get()
            if len(self.clients) != 0: 
                for addr in self.clients:
                    self.server.sendto('send statistics'.encode('UTF-8'), addr)
            

class Server:
    """
    Starting the server and getting statistics from devices
    """
    clients:list = []  # list addres clients
    statistics: dict = {}  # dictionary for statistics of connected clients

    def __init__(self, data_server, data_bot, host, q):
        self.server: socket = data_server
        self.bot: list = data_bot
        self.host: str = host
        self.q: Queue = q

    def _getting_data(self):
        try:
            self.raw_data, addr = self.server.recvfrom(1024)
            self.addr_on_del = addr
            if addr not in self.clients and addr[1] != self.bot[1]:
                self.clients.append(addr)  # send addres in list
                message = "А new client is connected\nIP: {}\nPORT: {}".format(addr[0], addr[1])
                self.server.sendto(message.encode('UTF-8'), self.bot)

                self.q.put(self.clients)  # add clients data to the queue
        except Exception as e:
            print('server error: ', e)

    def handle_data(self):
        self._getting_data()
        data = self.raw_data.decode('UTF-8')
        
        # from bot
        if data == 'show all ip':  # send list clients
            text_list_client = ""
            if len(self.clients) != 0:
                for i in range(len(self.clients)):
                    text_list_client += "{}) ip: {}, port: {}\n".format(i+1,
                                     self.clients[i][0], self.clients[i][1]) 
            else:
                text_list_client = "no clients connected"
            self.server.sendto(text_list_client.encode('UTF-8'), self.bot)
        elif data == '2':
            pass
        elif data.split()[0] == 'stop': 
            data = data.split()
            for addr in self.clients:
                if data[1] in addr and data[2] == str(addr[1]):
                    self.server.sendto("close".encode('UTF-8'), (data[1], int(data[2])))
                    break
            else:
                self.server.sendto('Input error data client'.encode('UTF-8'), self.bot)

        elif data == "close":  # from a client with message to bot
            self.clients.remove(self.addr_on_del)
            self.server.sendto('connection terminated with the client'.encode(
                                                                'UTF-8'), self.bot)
            
        else:  # from a client with statistics pc
            data = StatisticsPC.parse_raw(data)

            if data.ip not in self.statistics:  # adding a new pc
                self.statistics[data.ip] = {'CPU': [], 'Mem': []}
            self.statistics[data.ip]['CPU'].append(data.PC[0].cpu_percent)
            self.statistics[data.ip]['Mem'].append(data.PC[0].used_memory)

            # sending a warning to the bot
            if sum(self.statistics[data.ip]['CPU'][-10:]) > 850:
                warning_text = """On the computer 'ip: {}' high CPU usage""".format(data.ip)
                self.server.sendto(warning_text.encode('UTF-8'), self.bot)
            if sum(self.statistics[data.ip]['Mem'][-10:]) > 850:
                warning_text = """On the computer 'ip: {}' uses a lot of memory""".format(data.ip)
                self.server.sendto(warning_text.encode('UTF-8'), self.bot)

    def close_connect(self):
        self.server.close()

 
if __name__ == '__main__':
    q = Queue()
    data_server, data_bot, host = CreatingServer.create()

    # thread of sending settings to the client
    send_data = SendData(data_server, q)
    th = Thread(target=send_data.send_settings)
    th.start()

    # creating and running an instance of the Server class in a loop
    connect = Server(data_server, data_bot, host, q)
    while True:
        connect.handle_data()
