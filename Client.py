import socket
import xml.etree.ElementTree as xml
from find_kuka_points import main
# Функция отправки "нулевых значений"
def default_send_data():
    Message.text = str("PC:172.31.1.150")
    Frame_x.text = str(0)
    Frame_y.text = str(0)
    Frame_z.text = str(0)
    Length_points.text = str(0)


# Функция отправки текста (сообщения)
def send_message(message):
    Message.text = str(message)


x_position = []
y_position = []
z_position = []

# socket - настройка
client = socket.socket()
client.connect(("172.31.1.147", 54601))

client.setblocking(1)
# инициализация XML - файла
Sensor = xml.Element('Sensor')
Message = xml.SubElement(Sensor, 'Message')
Frame_x = xml.SubElement(Sensor, 'Frame_x')
Frame_y = xml.SubElement(Sensor, 'Frame_y')
Frame_z = xml.SubElement(Sensor, 'Frame_z')
Length_points = xml.SubElement(Sensor, 'Length_points')
# Запись в XML - файл (запись, чтение, открытие и т.д.)
tree = xml.ElementTree(Sensor)
tree.write("Sample_2.xml")
tree = xml.parse("Sample_2.xml")
root = tree.getroot()
file = open("Sample_2.xml", "rb")
stream = file.read(65536)
count = 0
i = 0
sum1 = 0
con = 0
Flag_connect = False
pos_kuka_x = None
pos_kuka_y = None
pos_kuka_z = None


while True:
    while not Flag_connect and con < 20:
        try:
            Flag_connect = True
            client.connect(("172.31.1.147", 54601))
        except ConnectionRefusedError:
            Flag_connect = False
            con += 1
            print("reconnecting...")
        if Flag_connect:
            print("Successful connection.")
            break
    if not Flag_connect and con == 20:
        print("Connection failed. Attempts:", con)
        break
    command = client.recv(10)
    command = command.decode('utf-8')
    # ЕСЛИ ПОЛУЧАЕМ "" - СОЕДИНЕНИЕ РАЗОРВАНО: ОСТАНАВЛИВАЕМ ПРОГРАММУ
    if command == '33':
        print("33")
        while(pos_kuka_x == None):
            Message.text = str("X")
            tree = xml.ElementTree(Sensor)
            tree.write("Sample_2.xml")
            file = open("Sample_2.xml", "rb")
            stream = file.read(65536)
            client.send(stream)
            pos_kuka_x = client.recv(10)

        while(pos_kuka_y == None):
            Message.text = str("Y")
            tree = xml.ElementTree(Sensor)
            tree.write("Sample_2.xml")
            file = open("Sample_2.xml", "rb")
            stream = file.read(65536)
            client.send(stream)
            pos_kuka_y = client.recv(10)

        while(pos_kuka_z == None):
            Message.text = str("Z")
            tree = xml.ElementTree(Sensor)
            tree.write("Sample_2.xml")
            file = open("Sample_2.xml", "rb")
            stream = file.read(65536)
            client.send(stream)
            pos_kuka_z = client.recv(10)

        print("kuka_x:", pos_kuka_x)
        print("kuka_y:", pos_kuka_y)
        print("kuka_z:", pos_kuka_z)

    if command == '':
        print("Conection is terminated")
        client.close()
        break

    # ЕСЛИ ПОЛУЧАЕМ '555' - ОТКЛЮЧАЕМСЯ ОТ СЕРВЕРА
    if command == '555':
        print("Client is disconnected.")
        client.close()
        break
    # ЕСЛИ ПОЛУЧАЕМ '22' - ОТПРАВЛЯЕМ КОЛИЧЕСТВО ТОЧЕК
    if command == '22':
        # OpenCV - получаем данные о координатах
        points = main()
        len_points = len(points)  # Length of array with KUKA points
        array = points  # KUKA points
        default_send_data()
        Length_points.text = str(len_points)

        tree = xml.ElementTree(Sensor)
        tree.write("Sample_2.xml")
        file = open("Sample_2.xml", "rb")
        stream = file.read(65536)
        client.send(stream)
        command = '0'

    # ЕСЛИ ПОЛУЧАЕМ '1' - НАЧИНАЕМ ПЕРЕДАЧУ КООРДИНАТ
    if command == '1':
        if count < len_points:
            x_position.append(array[i][0])
            y_position.append(array[i][1])
            #z_position = 60.91

            print("X = ", x_position[i], "Y = ", y_position[i], "Z = ", z_position)

            Frame_x.text = str(x_position[i])
            Frame_y.text = str(y_position[i])
            #Frame_z.text = str(60.91)

            tree = xml.ElementTree(Sensor)
            tree.write("Sample_2.xml")
            file = open("Sample_2.xml", "rb")
            stream = file.read(65536)
            client.send(stream)
            count = count + 1
            i = i + 1
            print("i:", i, "\n")
            print("count:", count)
            command = '0'
        if count == len_points + 1:
            client.close()
            break


print(count, "\n")

