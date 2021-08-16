import telebot
import socket
from threading import Thread
from queue import Queue


class CreateBot:
    @staticmethod
    def create() -> socket:
        """Creating a connection to the server"""
        while True:
            try:
                # network data client
                host = socket.gethostbyname(socket.gethostname())
                port = int(input("Enter bot port: "))
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

                        return client, server, host

                print("Input error server ip")
            except Exception as e:
                    print("Input error: ", e)


# data bot
TOKEN = input("Enter bot token: ")
bot = telebot.TeleBot(TOKEN)
my_id = int(input("Enter your telegram id: "))  


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    greeting = (
        "Functions:\n1)show all ip\n2)stop *ip* *port*",
        "\nexample: 'stop 192.168.1.1 1000'")

    # keyboards
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttom_one = telebot.types.KeyboardButton("show all ip")
    markup.add(buttom_one)

    bot.send_message(my_id, greeting, reply_markup=markup)

@bot.message_handler()
def answer(message):
    if message.from_user.id == my_id:
        message = message.text.lower()
        if message == "show all ip":
            BOT_SOCKET.sendto(message.encode('UTF-8'), SERVER)
        elif message.split()[0] == "stop":  # stopping the client with the entered ip and port
            text = message.split()
            BOT_SOCKET.sendto("stop {} {}".format(text[1], text[2]).encode('UTF-8'), SERVER)
        else: 
            bot.send_message(my_id, "I don't understand you")

def receiving_data(BOT_SOCKET, bot, my_id):
    """receiving data with server\n
        and sending the received data to the client"""
    while True:
        data, addr = BOT_SOCKET.recvfrom(1024)
        data = data.decode('UTF-8')
        bot.send_message(my_id, data)

if __name__ == '__main__':
    q = Queue()

    # data socket
    BOT_SOCKET, SERVER, HOST = CreateBot.create()

    # thread receiving data with server
    th = Thread(target=receiving_data, args=(BOT_SOCKET, bot, my_id, ), daemon=True, name='data from server')
    th.start()

    # start loop bot
    print('bot start')
    bot.polling()
