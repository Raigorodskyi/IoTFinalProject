
# import random
# 
# from paho.mqtt import client as mqtt_client
# 
# 
# broker = '192.168.0.179'
# port = 1883
# topic = "lightIntensity"
# # generate client ID with pub prefix randomly
# client_id = f'python-mqtt-{random.randint(0, 100)}'
# username = 'Meow'
# password = 'jvvjv'
# 
# 
# def connect_mqtt() -> mqtt_client:
#     def on_connect(client, userdata, flags, rc):
#         if rc == 0:
#             print("Connected to MQTT Broker!")
#         else:
#             print("Failed to connect, return code %d\n", rc)
# 
#     client = mqtt_client.Client(client_id)
#     client.username_pw_set(username, password)
#     client.on_connect = on_connect
#     client.connect(broker, port)
#     return client
# 
# 
# def subscribe(client: mqtt_client):
#     def on_message(client, userdata, msg):
#         print(msg.payload.decode())
#         print(int(msg.payload.decode()) -2)
#         return int(msg.payload.decode())
#     client.subscribe(topic)
#     client.on_message = on_message
#     
# 
# 
# def run():
#     client = connect_mqtt()
#     subscribe(client)
#     client.loop_forever()
# 
# 
# if __name__ == '__main__':
#     run()


import sqlite3
import mysql.connector

connection = sqlite3.connect('users.db')
# 
cursor = connection.cursor()

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS users (
#     userID INTEGER PRIMARY KEY AUTOINCREMENT, tagID varchar(16),
#     fullName varchar(255),
#     tempThreshold decimal(2,1),
#     humidityThreshold decimal(2,1),
#     lightIntensityThreshold INTEGER,
#     profilePic blob
# )
# """)

# 
#  # sql query to insert data
# cursor.execute("""
#             INSERT INTO users
#             VALUES (3, 'EemaScha', 22, 55, 600);
#         """)
cursor.execute("""
    SELECT * FROM users WHERE user_id IS 3
    """)
# 
rows = cursor.fetchall()
print(rows)

connection.commit()
connection.close()