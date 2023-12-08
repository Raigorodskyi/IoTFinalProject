#Dash related inputs
import dash.dependencies
import dash_daq as daq
from dash import html, Input, Output, dcc, Dash, State
import dash_bootstrap_components as dbc

#Time for the email replies
import time
from datetime import datetime

#Board-related inputs
import RPi.GPIO as GPIO
import Freenove_DHT as DHT

#Email
import email.utils
from datetime import datetime, timedelta
import smtplib, ssl
import imaplib
import easyimap as imap
from email.header import decode_header
import email
import traceback
from bluepy.btle import Scanner
import mysql.connector
from mysql.connector import Error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication

#Bluetooth and random(for client_id)
import random
import bluetooth

#MQTT-broker
from paho.mqtt import client as mqtt_client

# For DataBase
import sqlite3
from sqlite3 import Error

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

smtp_server = "imap.gmail.com"
email_port = 587 #gmail
sender_email = '2003igorok@gmail.com'
sender_password = 'vukx tyxh ytnf kbzr'
receiver_email = 'raigorodskyi@gmail.com'

#LED-pin
ledPin = 19
GPIO.setup(ledPin, GPIO.OUT, initial=GPIO.LOW)
#Motor
Motor1 = 27
Motor2 = 22
Motor3 = 5
GPIO.setup(Motor1, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor2, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor3, GPIO.OUT, initial=GPIO.LOW)
#DHT-11
DHTPin = 17
dht = DHT.DHT(DHTPin) #create a DHT class object
dht.readDHT11()

global currentTempValue, currentHumidity, currLightInt
currentTempValue = 0.0
currentTemperature = 0
currentHumidity = 0
currLightInt = 500.0

# To be used for user preferences
global currentTag, tagID, username, userTemp, humidityThr, lightThr, profilePic
currentTag = "NaN"
tagID = "NaN"
username = " "
userTemp = 27.0
humidityThr = 0
lightThr = 400
profilePic = "avatar.png"

global fan_should_be_on
fan_should_be_on = False
emailSent = False
emailLightSent = False
global emailReceived
emailReceived = False
global message, message2
message=''
message2=''

thermometerColour = "#ff0800"

# Var For Reading Email
receiverEmail = 'raigorodskyi@gmail.com'

broker = '192.168.0.179' #at home
#broker = '172.20.10.3' #hotspot
port = 1883
topic = "lightIntensity"
topic2 = "currentTag"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(3, 100)}'
password = 'aaaaaaaa'

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])

# Web page title
app.title = 'SmartHome'

# Page header containing Logo and future Log-In feature
header = html.Header(children=[
    html.Section(children=[
        html.Div(id='Logotype', children=[
            html.Img(src=app.get_asset_url('logoo.png'), width='40%'),
            html.Div(style={'background-color': '#212529', 'width': '60%'})
        ], style={'display': 'flex'}),
    ])
])

userInfo = html.Div(children=[
    html.Div(
        [
            html.Div(style={'text-align': 'center'}, children=[
                html.Img(id="avatar", src=app.get_asset_url(profilePic), width='50%', height='50%', className=" mb-3",
                         style={'border-radius': '0%'})
            ]),
            dbc.Row(
                [
                    dbc.Col(html.Div("Your Full Name: "), className='fw-bold'),
                    dbc.Col(html.Div(dbc.Input(id="username", placeholder="Log in for preferences", size="md", className=" mb-4",
                                               readonly=True,style={'position':'relative','width': '180px','height': '40px', 'border-radius': '0%'})
                                     )),
                ]),
            dbc.Row(
                [
                    dbc.Col(html.Div("Temperature should be below: "), className='fw-bold'),
                    dbc.Col(html.Div(dbc.Input(id="tempThreshold", placeholder=" ", size="md",
                                              className="mb-3", readonly=True,
                                               style={'position':'relative','width': '180px','height': '40px', 'border-radius': '0%'})
                                     )),
                ]),
            dbc.Row(
                [
                    dbc.Col(html.Div("Humidity should be around: "), className='fw-bold'),
                    dbc.Col(html.Div(dbc.Input(id="humidityThreshold", placeholder=" ", size="md",
                                              className="mb-3", readonly=True,
                                               style={'position':'relative','width': '180px','height': '40px', 'border-radius': '0%'}),
                                     
                                     )),
                ]),
            dbc.Row(
                [
                    dbc.Col(html.Div("Light Intensity should be above: "), className='fw-bold'),
                    dbc.Col(html.Div(dbc.Input(id='lightIntensity', placeholder=" ", size="md",
                                              className="mb-3", readonly=True,
                                               style={'position':'relative','width': '180px','height': '40px', 'border-radius': '0%'})
                                     )),
                ])
        ]),
    
], style={'border-radius':'0%','margin-left':'auto','margin-right':'auto', 'border':'1px solid #ccc', 'font-weight':'bold'}, className='w-25')

# Card that displays the Temperature and Humidity
# Used ID's: current-thermometer, current-humidity
climateCard = html.Div(children=[

    dcc.Interval(id='interval', interval=3000, n_intervals=0),  #update every 3 seconds
    html.Div(children='Environment:', style={'font-weight':'bold', 'font-size': 'xx-large'}, className='widgetTitle'),
    html.Div(children=[
                           html.Div(id='motorEmail', children=[], style={'font-weight':'bold'})
                       ]),
    
    
    html.Div(children=[
        html.Div(id='thermometre', children=[
            daq.Thermometer(
                id='current-thermometer',
                label='Temperature',
                labelPosition='bottom',
                value=currentTemperature,
                min=10,
                max=30,
                className="custom-thermometer",
                color=thermometerColour,
                showCurrentValue=True,
                units="C",
            ), 
        ]),

        html.Div(id='humidity', children=[
            daq.Gauge(
                color={"gradient": True,
                       "ranges": {"#0000ff": [0, 25], "#87cefa": [25, 30], "#90ee90": [30, 60], "#ff7f00": [60, 70],
                                  "#e60026": [70, 100]}},
                showCurrentValue=True,
                id='current-humidity',
                units="%",
                value=currentHumidity,
                label='Humidity',
                max=100,
                min=0,
                className="custom-humidity"
            ),
        ]),
    ])
], style={'border-radius':'0%','margin-left':'auto','margin-right':'auto', 'border':'1px solid #ccc', 'font-weight':'bold'}, className='w-25')

# Card that controls the LED
# Used ID: led-power-button
ledCard = html.Div(children=[
    html.Div(children='Light Status:', style={'font-weight':'bold', 'font-size': 'xx-large'}, className='widgetTitle'),
    html.Div(children=[
                           html.Div(id='lightEmail', children=[], style={'font-weight':'bold'})
                       ]),
    html.Div(children=[
        html.Div(children=[], id='turnOnLed', style={'margin-left': '40%', 'padding-top': '55px'}),
        daq.GraduatedBar(
            color={"gradient": True, "ranges": {"blue": [0, 250], "green": [250, 400], "yellow" : [400, 700], "red": [700, 1025] }},
            id='currLightInt',
            label='Light Intensity',
            showCurrentValue=True,
            value=5,
            step=10,
            max=1025,
            min=0,
            className="h-25"

        )
    ])
], style={'border-radius':'0%','left-padding': '10px', 'border':'1px solid #ccc'}, className='w-25')

# Card that controls the Fan
# Used ID: fan-power-button
fanBTCard = html.Div(children=[
    html.Div(children='Fan Status:', style={'font-weight':'bold', 'font-size': 'xx-large'}, className='widgetTitle'),
    html.Div(children=[
        html.Div(children=[], id='fanIcon', style={'margin-left': '35%', 'padding-top': '55px'}),
    ]),
#     html.Div(children=[
#     html.Div(children='Bluetooth Devices Found:', id="btString", className=' ms-3'),
#     ], style={'border-radius':'0%', 'border':'1px solid #ccc', 'padding-top': '85px'},
#              className="h-25")
    
    
], style={'border-radius':'0%','left-padding': '10px', 'border':'1px solid #ccc'}, className='w-25 ')

# Page body that assembles all the components
body = html.Main(children=[
    dbc.Row([
        userInfo,
        climateCard,
        ledCard,
        fanBTCard,
    ], className='mb-3'),
])

# Page layout that assembles Header, Body and Footer
app.layout = html.Div(id="userInterface", children=[
    header,
    body
], style= {'background-color': '#536878'})

# Temperature and Humidity Reading and Displaying
@app.callback(
    Output('current-thermometer', 'value'),
    Output('current-humidity', 'value'),
    Input('interval', 'n_intervals'))
def getSensorData(n_intervals):
    global thermometerColour
    dht.readDHT11()
    currentTemperature = dht.temperature
#     if currentTemperature < 17:
#         thermometerColour = "#00ffff"
#     elif currentTemperature >= 17 and currentTemperature < 26:
#         thermometerColour = "#ff8c00"
#     elif currentTemperature < 17:
#         thermometerColour = "#ff6347"
#         
    currentTempValue = dht.temperature
    currentHumidity = dht.humidity
    return currentTemperature, currentHumidity

@app.callback(
    Output('current-thermometer', 'color'),
    [Input('current-thermometer', 'value')]
)
def update_therm_col(val):
    if val >= 26:
        return 'red'
    elif val >= 17 and val < 26:
        return '#90ee90'
    elif val < 17:
        return 'blue'


# Fan Control Callback Logic
@app.callback(
    Output('fanIcon', 'children'),
    Input('interval', 'n_intervals')
)
def toggleFan(n_intervals):
    if fan_should_be_on:
#         GPIO.output(Motor1,GPIO.HIGH)
#         GPIO.output(Motor2,GPIO.LOW)
#         GPIO.output(Motor3,GPIO.HIGH)
        img = html.I(className="fa-solid fa-wind fa-fade", style={'font-size': '10rem', 'color': '#00bfff'})
        return img
    else:
#         GPIO.output(Motor1,GPIO.LOW)
#         GPIO.output(Motor2,GPIO.LOW)
#         GPIO.output(Motor3,GPIO.LOW)
        img = html.I(className="fa-solid fa-wind", style={'font-size': '10rem', 'color': '#C8C8C8'})
        return img


# LED Control Callback Logic
@app.callback(
    Output('turnOnLed', 'children'),
    [Input('currLightInt', 'value')]
)
def lightIntensityCheck(value):
    if int(value) < int(lightThr):
        img = html.I(className="fa-solid fa-bolt fa-fade", style={'font-size': '10rem', 'color': '#f8d31b'})
        return img
    else:
        GPIO.output(ledPin, GPIO.LOW)
        img = html.I(className="fa-solid fa-bolt", style={'font-size': '10rem', 'color': '#C8C8C8'})
        return img

@app.callback(
    Output('lightEmail', 'children'),
    Input('interval', 'n_intervals'),
    [Input('currLightInt', 'value')])
def lightUpdate(n_intervals,value):
    global emailLightSent, lightThr
    global message2

    if int(value) < int(lightThr) and not emailLightSent:
        send_email_light()
        emailLightSent = True
        message2 = 'Email has been sent for Light'
        GPIO.output(ledPin, GPIO.HIGH)
        return message2
    elif int(value) < int(lightThr) and emailLightSent:
        message2 = 'Email has been sent for Light'
        GPIO.output(ledPin, GPIO.HIGH)
        return message2
    elif int(value) > int(lightThr):
        emailLightSent = False
        GPIO.output(ledPin, GPIO.LOW)
        print('Cur Light: ',int(value),' Light Tresh: ',int(lightThr))
        message2 = ' '

        return message2

@app.callback(
    Output('motorEmail', 'children'),
    Input('interval', 'n_intervals'),
     [Input('current-thermometer', 'value')])
def temperatureUpdate(n_intervals,value):
    global emailSent, emailReceived, last_emailReceived_time, fan_should_be_on, currentTag
    fan_on = checkFanReply()
    global message

    if float(value) > float(userTemp) and not emailSent:
        send_email_fan()
        emailSent = True  
        if emailSent:
            message = 'Email for fan has been sent'
    if fan_on and float(value) > float(userTemp):
        fan_should_be_on = True
        print("Fan toggled")
        message = 'Response received: Fan is ON'
    elif float(value) < float(userTemp):
        fan_should_be_on = False
        emailSent = False
        emailReceived = False
        print(value)
        message = ' '

    return message


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(msg.payload.decode())

        global currLightInt
        global tagID
        
        # Check the topic and store the message in the corresponding variable
        if msg.topic == topic:
            currLightInt = msg.payload.decode()
        elif msg.topic == topic2:
            tagID = msg.payload.decode()
        print("LightInt: " + currLightInt + " TagId:" + tagID)
    topics = [topic, topic2]
    client.subscribe([(topic, 0) for topic in topics])
    client.on_message = on_message

    
@app.callback(Output('currLightInt', 'value'),
                Output('currLightInt', 'label'),
              Input('interval', 'n_intervals'))
def updateLightIntensity(n_intervals):
    global currLightInt
    resultLabel = "Illumination: "+str(currLightInt)
    return currLightInt, resultLabel

@app.callback(
              Output('username', 'value'),
              Output('tempThreshold', 'value'),
              Output('humidityThreshold', 'value'),
              Output('lightIntensity', 'value'),
              Output('avatar', 'src'),
              Input('interval', 'n_intervals'))
def updateUserInfo(n_n_intervals):
    global tagID, currentTag, username,userTemp,humidityThr,lightThr, profilePic, emailSent, emailReceived
    buttonText='Open Menu'
    if tagID != "NaN" and currentTag != tagID:
        currentTag = tagID
        user = logInWithTag(currentTag)
        username = user[2]
        userTemp = user[3]
        humidityThr = user[4]
        lightThr = user[5]
        profilePic = user[7] + ".png"
        emailSent = False
        emailReceived = False
        
        sendEmailEnter()
    print("Current Tag: " + currentTag + " TagId = " + tagID)
    print(username + " " + profilePic)
    return  username, userTemp, humidityThr, lightThr, app.get_asset_url(profilePic)

# DB user preferences
def createDBConnection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

# @app.callback(
#     Output('btString', 'children'),
#     Input('interval', 'n_intervals'))
# def check_bluetooth(n_intervals):
# 
#     print("Scanning bluetooth...")
#     message2 = ('Bluetooth Devices Found: ' + str(len(bluetooth.discover_devices(Lookup_names=True))))
# 
#     return message2

def sendEmailEnter():
    global username
    subject = "Someone came in"
    currtime = time.strftime("%H:%M", (time.localtime()))
    body = username + " came in at " +str(currtime)+'.'
    # Create the MIME object
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # Attach the body to the email
    msg.attach(MIMEText(body, "plain"))

    # Send the email
    with smtplib.SMTP(smtp_server, email_port) as server:
        server.ehlo()  # Can be omitted
        server.starttls()
        server.ehlo()  # Can be omitted
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

def send_email_light():

    subject = "It is too dark"
    currtime = time.strftime("%H:%M", (time.localtime()))
    body = "It is too dark in the room, the light is ON at " +str(currtime)+'.'
    # Create the MIME object
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # Attach the body to the email
    msg.attach(MIMEText(body, "plain"))

    # Send the email
    with smtplib.SMTP(smtp_server, email_port) as server:
        server.ehlo()  # Can be omitted
        server.starttls()
        server.ehlo()  # Can be omitted
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        
        
def send_email_fan():
    
    subject = "It is getting hot"
    currTime = time.strftime("%H:%M", (time.localtime()))
    body = "The temperature exceeded " +str(userTemp)+"°C at " + currTime + ". Would you like to turn on the fan?"
    # Create the MIME object
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # Attach the body to the email
    msg.attach(MIMEText(body, "plain"))

    # Send the email
    with smtplib.SMTP(smtp_server, email_port) as server:
        server.ehlo()  # Can be omitted
        server.starttls()
        server.ehlo()  # Can be omitted
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        
        
def send_email_fan_newUser():
    
    subject = "It is getting hot"
    currTime = time.strftime("%H:%M", (time.localtime()))
    body = "The temperature is still exceeding " +str(userTemp)+"°C at " + currTime + ". Would you still like to keep the fan on?"
    # Create the MIME object
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # Attach the body to the email
    msg.attach(MIMEText(body, "plain"))

    # Send the email
    with smtplib.SMTP(smtp_server, email_port) as server:
        server.ehlo()  # Can be omitted
        server.starttls()
        server.ehlo()  # Can be omitted
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())    
        
        
def checkFanReply():
    global emailReceived
    sender_email = '2003igorok@gmail.com'
    sender_password = 'vukx tyxh ytnf kbzr'
    # Connect to the Gmail server
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(sender_email, sender_password)
    
    # Select the mailbox (inbox in this case)
    mail.select("inbox")

    # Search for all emails and get the latest one
    status, messages = mail.search(None, 'ALL')
    if status == 'OK':
        email_ids = messages[0].split()
        if email_ids:
            latest_email_id = email_ids[-1]
            print(latest_email_id)
            # Fetch the latest email
            status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
            if status == 'OK':
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                # Get the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8")

                # Get the email date
                email_date = email.utils.parsedate(msg.get("Date"))
                if email_date:
                    email_datetime = datetime(*email_date[:6])
                    print(email_datetime)
                    current_datetime = datetime.now()
                    print(current_datetime)

                    # Check if the email is received within the last 30 seconds
                    if (current_datetime - email_datetime).total_seconds() <= 60:
                        # Get the email body
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')

                        # Check if the subject is "It is getting hot" and the body contains "YES"
                        if "It is getting hot" in subject and "YES" in body.upper():
                            print("there is a yes in the email")
                            emailReceived = True
                            return True

    # Close the connection
    mail.close()
    mail.logout()
    emailReceived = False
    return False

def logInWithTag(userTag):
    global username, userTemp, humidityThr, lightThr, profilePic
    db_file = "users.db"
    conn = createDBConnection(db_file)
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM users WHERE tagID = ?", [userTag])
        user = cur.fetchone()

        if not user:
            print("log in failed")
        else:
            userTag = user[1]
            username = user[2]
            userTemp = user[3]
            humidityThr = user[4]
            lightThr = user[5]
            profilePic = user[7] + ".png"
            print(userTag, username, userTemp, humidityThr, lightThr, profilePic)

            return user
    finally:
        cur.close()



def main():
     client = connect_mqtt()
     subscribe(client)
     client.loop_start()
     
     app.run_server(debug=True, host='localhost', port=8051)

main()
