import conf                           # IMPORTING CONF.PY FILE 
from boltiot import Sms, Bolt,Email   # IMPORTING THE SMS , EMAIL AND BOLT MODULE
import json,time                         # IMPORTING JSON - TO CONVERT RESPONSE 

def main_process():

    maximum_limit = 28.0 # SENSOR LIMIT IN CELSIUS 
    mybolt = Bolt(conf.API_KEY, conf.DEVICE_ID) # TO GET THE BOLT MODULE
    sms = Sms(conf.SID, conf.AUTH_TOKEN, conf.TO_NUMBER, conf.FROM_NUMBER) 
    mailer = Email(conf.MAILGUN_API_KEY,conf.SANDBOX_URL,conf.SENDER_EMAIL,conf.RECIPIENT_EMAIL)

    is_Fire = False # INITIALLY FIRE ISN'T PRESENT ASSUMPTION 

    status = json.loads(mybolt.isOnline())  # TO GET THE STATUS OF THE BOLT MODULE 
    print("Status Check : ",status["value"])  

    if status["value"] != "offline":   # ONLY IF THE MODULE IS ONLINE , WE PROCEED 
        while True: 
            print ("Reading sensor value")
            response = mybolt.analogRead('A0')   # READING THE SENSOR DATA 
            data = json.loads(response)  # USED TO CONVERT THE RESPONSE INTO PYTHON DICTIONARY 

            try:
                flag = 1
                sensor_value = int(data['value'])  
                temp1 = (100*sensor_value)/1024  # CONVERTING TEMPERATURE INTO CELSIUS
                print("Sensor value is: " + str(temp1))  # PRINTING THE SENSOR VALUE 

                while temp1 > maximum_limit:  # IF THE TEMP VALUE > GIVEN VALUE IE THERE IS FIRE
                    if flag == 1: 
                        response = sms.send_sms("Attention !! Fire in college")  # SMS IS SENT TO THE MOBILE NUMBER MENTIONED 
                        print("Response received from Twilio is: " + str(response)) 
                        print("Status of SMS at Twilio is :" + str(response.status))

                        response_mail = mailer.send_email("Alert", "There is fire in the college")  # MAIL IS SENT TO THE MAIL ID MENTIONED
                        response_text = json.loads(response_mail.text)
                        print("Response received from Mailgun is: " + str(response_text['message']))
                    
                    # SETTING THE VALUE OF BOTH BUZZER AND LED IS SET TO 'HIGH'
                    mybolt.digitalWrite('1', 'HIGH')
                    mybolt.digitalWrite('2', 'HIGH')
                    response = mybolt.analogRead('A0') 
                    data = json.loads(response)
                    sensor_value = int(data['value'])
                    temp1 = (100*sensor_value)/1024 
                    print("Sensor value is: " + str(temp1))
                    flag = 0
                    is_Fire = True

                # AFTER ALERT HAS BEEN SENT , SET IT TO LOW
                mybolt.digitalWrite('2', 'LOW') 
                mybolt.digitalWrite('1', 'LOW')
                if is_Fire:
                      print("Response received from Twilio is: " + str(response))
                      print("Status of SMS at Twilio is :" + str(response.status))
            except Exception as e:
                print ("Error occured: Below are the details")
                print (e)
            time.sleep(10)
    else:
        print("Device is Offline")

if __name__ == '__main__':
    main_process()
