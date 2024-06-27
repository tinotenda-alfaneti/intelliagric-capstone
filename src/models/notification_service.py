import http.client
from codecs import encode
import json
import logging
from src import EMAIL_BOUNDARY, INFOBIP_KEY, INFOBIP_BASE_URL
from src.models.chat import Chat

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Notifications:

    def __init__():
        pass
    
    @staticmethod
    #NB: Works with verified numbers only free version - 99 sms left
    def send_sms(contact, message):
        conn = http.client.HTTPSConnection(INFOBIP_BASE_URL)
        payload = json.dumps({
            "messages": [
                {
                    "destinations": [{"to":f"{contact}"}],
                    "from": "ServiceSMS",
                    "text": f"{message}"
                }
            ]
        })
        headers = {
            'Authorization': f'App {INFOBIP_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        conn.request("POST", "/sms/2/text/advanced", payload, headers)
        res = conn.getresponse()
        data = res.read()
        logging.info(f'Send SMS Notification: {data.decode("utf-8")}')

    @staticmethod
    def send_email(to_email, subject, message):
        conn = http.client.HTTPSConnection(INFOBIP_BASE_URL)
        dataList = []
        boundary = EMAIL_BOUNDARY
        crlf = b'\r\n'  # Define CRLF for line breaks

        dataList.append(encode('--' + boundary))
        dataList.append(encode('Content-Disposition: form-data; name="from"'))
        dataList.append(crlf)
        dataList.append(encode("Intelli Agric <tinotenda.alfaneti@ashesi.edu.gh>"))
        dataList.append(crlf)

        dataList.append(encode('--' + boundary))
        dataList.append(encode('Content-Disposition: form-data; name="subject"'))
        dataList.append(crlf) 
        dataList.append(encode(f"{subject}"))
        dataList.append(crlf)

        # Add boundary and content disposition for 'to'
        dataList.append(encode('--' + boundary))
        dataList.append(encode('Content-Disposition: form-data; name="to"'))
        dataList.append(crlf)
        dataList.append(encode("{\"to\":\""+ f'{to_email}' + "\",\"placeholders\":{\"firstName\":\"Farmer\"}}"))
        dataList.append(crlf)

        dataList.append(encode('--' + boundary))
        dataList.append(encode('Content-Disposition: form-data; name="text"'))
        dataList.append(crlf)
        dataList.append(encode("Hi {{firstName}},\n\n" + f"{message}"))
        dataList.append(crlf)

        dataList.append(encode('--' + boundary + '--'))
        dataList.append(crlf)

        body = crlf.join(dataList)
        payload = body

        headers = {
            'Authorization': f'App {INFOBIP_KEY}',
            'Content-Type': 'multipart/form-data; boundary={}'.format(boundary),
            'Accept': 'application/json'
        }

        conn.request("POST", "/email/3/send", payload, headers)
        res = conn.getresponse()
        data = res.read()
        logging.info(f'Send Email Notification: {data.decode("utf-8")}')


    @staticmethod
    def send_notifications(alerts, farms):
        for alert in alerts:
            location = alert['location']
            disease = alert['disease']

            affected_farms = [farm for farm in farms.values() if farm['location'] == location]

            for farm in affected_farms:
                contact = farm.get('contact')
                email = farm.get('email')

                query = "Give me an alert message and a small recommendation for the disease from model. It should be less than 20 words"
                message = Chat.refine_response(query, disease)
                message = f"Alert: There have been multiple cases of {disease} detected in your area. Please take necessary precautions."


                if contact:
                    Notifications.send_sms(contact, message)
                if email:
                    Notifications.send_email(email, "Disease Alert", message)
