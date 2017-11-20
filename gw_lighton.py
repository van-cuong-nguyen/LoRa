import serial
import time
import binascii
import paho.mqtt.publish as publish
import paho.mqtt.client as paho
import base64
from time import sleep

msg_seq=0
port = serial.Serial("COM1", baudrate=57600)
lamp_status="off"
def send_command_to_lamp(status):
        if status=="on":
                command="Rx 2 020312013231\r\n"
        if status=="off":
                command="Rx 2 020312003230\r\n"
        port.write(bytes(command,'UTF-8'))
        print("sent commmand:"+command+" to lamp")
        
def on_subscribe(client, userdata, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))


def on_message(client, userdata, msg):
        msg_content=(msg.payload).decode('utf-8')
        topic=msg.topic
        print("topic:"+topic+",msg:"+msg_content)
        if (topic=="lamp_downlink"):
                global msg_seq
               # msg_content="DWL,"+"0099"+";"+msg_content
                port.write(bytes(msg_content,'UTF-8'))
                print("sent request:"+msg_content)
                msg_seq+=1
                header=msg_content[0:3]
                payload=msg_content[6:len(msg_content)]
                if header=="DWL":
                        global lamp_status;
                        if payload.find("0:on")!=-1:
                                lamp_status="on"
                                send_command_to_lamp(lamp_status)
                        if payload.find("0:off")!=-1:
                                lamp_status="off"
                                send_command_to_lamp(lamp_status)
                
                if header=="REQ":
                        publish.single("lamp_uplink", "UPL00;0:"+lamp_status, hostname="140.114.89.66")
                        
                        
                        
        
                        
client = paho.Client()
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect("140.114.89.66", 1883)
client.subscribe("lamp_downlink", qos=1)
client.loop_start()

while port:
        raw_data=(port.readline()).strip()  # remove space at the end
        #print(raw_data)
        try:    
                in_data=raw_data.decode('utf-8');
                
                print(in_data)
                publish.single("lamp_uplink", in_data, hostname="140.114.89.66")
        except ValueError:
                print ("Oops ! received packet is peccable");
