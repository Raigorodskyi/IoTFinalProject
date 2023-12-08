
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

# cursor.execute(
#     """
#     ALTER TABLE users
#     ADD COLUMN shortName varchar(255)
# """
#     )


# cursor.execute(
#     """
#     UPDATE users SET shortName = 'Itzchak' WHERE fullName = 'Itzchak Tzipor'
# """
#     )

# 
 # sql query to insert data
# cursor.execute("""
#             INSERT INTO users(tagID, fullName, tempThreshold,
#             humidityThreshold, lightIntensityThreshold)
#             values("F356E812",'Itzchak Tzipor', 22.5, 60, 650);
#         """)
 # sql query to insert data
# cursor.execute("""
#             DELETE * FROM users WHERE fullName = "Ibrahim Awad"
#         """)
# # cursor.execute("""
# #     SELECT * FROM users WHERE fullName = 'Ibrahim Awad'  
# #     """)
# # 
# # uwu = cursor.fetchone()
# # print(uwu)


#Inserting Avatars
# cursor.execute("""
#     INSERT INTO users(profilePic)
#     values(LOAD_FILE('assets/Igor.jpg'))
#     WHERE fullName = 'Igor Raigorodskyi';
#         """)


def convertBlobToFile(blob_data, file_path):
    with open(file_path, 'wb') as file:
        file.write(blob_data)

def retrieveBlobFromDB(record_id):
    # Connect to the database
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    # Retrieve BLOB data based on record ID
    cursor.execute("SELECT * FROM users WHERE fullName = ?", [record_id])
    blob_data = cursor.fetchone()[6]

    # Close the database connection
    connection.close()

    return blob_data

# Example: Retrieve BLOB and save it to a file
# record_id = 1  # Replace with the actual record ID
# blob_data = retrieveBlobFromDB("Igor Raigorodskyi")
# print(blob_data)
# file_path = 'output_file.txt'  # Replace with the desired file path
# convertBlobToFile(blob_data, file_path)



# Function for Convert Binary Data  
# to Human Readable Format 
# def convertToBinaryData(filename): 
#       
#     # Convert binary format to images  
#     # or files data 
#     with open(filename, 'rb') as file: 
#         blobData = file.read() 
#     return blobData 
#   
#   
# def insertBLOB(name, photo): 
#     try: 
#           
#         # Using connect method for establishing 
#         # a connection 
#         sqliteConnection = sqlite3.connect('users.db') 
#         cursor = sqliteConnection.cursor() 
#         print("Connected to SQLite") 
#           
#         sqlite_update_query = """UPDATE users SET profilePic = ? WHERE fullName = ?"""
#         updated_data_tuple = (convertToBinaryData(photo), name)
#         cursor.execute(sqlite_update_query, updated_data_tuple)
#         sqliteConnection.commit()
#         print("Record updated successfully")
#         cursor.close() 
#   
#     except sqlite3.Error as error: 
#         print("Failed to insert blob data into sqlite table", error) 
#       
#     finally: 
#         if sqliteConnection: 
#             sqliteConnection.close() 
#             print("the sqlite connection is closed") 
#   
# insertBLOB("Deven Patel", "/home/pi/IoT-Project/assets/Deven.jpg")






# DB user preferences
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def logInWithTag(userTag):
    global username, uTempThreshold, uHumidityThreshold, uLightThreshold
    db_file = "users.db"
    conn = create_connection(db_file)
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM users WHERE tagID = ?", [userTag])
        user = cur.fetchone()

        if not user:
            print("log in failed")
        else:
            userTag = user[1]
            username = user[2]
            uTempThreshold = user[3]
            uHumidityThreshold = user[4]
            uLightThreshold = user[5]
            profilePic = user[6]
            firstName = user[7]
            print(userTag, username, uTempThreshold, uHumidityThreshold, uLightThreshold, profilePic, firstName)

            return user
    finally:
        cur.close()

#
# rows = cursor.fetchall()
# print(rows)
logInWithTag("02FA581B")
logInWithTag("03890B17")
logInWithTag("F356E812")
logInWithTag("D3B08115")
# data = cursor.execute('''SELECT * FROM users''')
# print(data.description)
connection.commit()
connection.close()