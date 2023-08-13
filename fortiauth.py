
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from requests.auth import HTTPBasicAuth
import requests
import csv
import pandas
import os
import termcolor
from datetime import datetime

os.system('color')

listofusers=[]


dateCol=["VPN Approval Expiry Date"]



dh=pandas.to_datetime("today",format='%Y-%m-%d')


#url to be accessed and credentials
url='https://FortiAuthenticator-IP/api/v1/ldapusers/?limit=0'
headers= {'Accept':'application/json'}
auth=HTTPBasicAuth('apiusr','API-TOKEN')

#some cleaning up and formatting "i dont remember what i was doing"
x= requests.get(url, headers=headers, auth=auth,verify=False)
q=x.json()


q.pop('meta')
z=json.dumps(q)
p=json.loads(z)



#opens the .CSV file and searches through it based on username and expiration date.
with open("VPNUsers.csv", 'r') as file:
    csvfile = csv.DictReader(file)
    for row in csvfile:
        for user in p['objects']:
            
            if (str(user['username']) == row['VPN User'].lower()):
                
                row["VPN Approval Expiry Date"]=row["VPN Approval Expiry Date"]=pandas.to_datetime(row["VPN Approval Expiry Date"],dayfirst=True)

                if row["VPN Approval Expiry Date"] >= dh:
                    print(user['username']+" "+str(user['id'])+" did not expire")

                elif row["VPN Approval Expiry Date"] < dh:
                    print(user['username']+" "+str(user['id'])+" expired")
                    listofusers.append(user['username'])
                    print(f'https://FortiAuthenticator-IP/api/v1/ldapusers/{user["id"]}/')
                    delURL=f'https://FortiAuthenticator-IP/api/v1/ldapusers/{user["id"]}/'
                    requests.delete(delURL, headers=headers, auth=auth,verify=False)
                    

                else:
                    print("no expiry date set for user: "+user['username'])

print(termcolor.colored(f"{listofusers} has been deleted", "green"))


#sends a email with the following config if a user/s filled in the list called "listofusers"
if len(listofusers)>0:
    mail_from = "FROM Mail"
    mail_to = "TO MAIL"
    mail_cc="CC MAIL"
    mail_subject = "Remove VPN users from VPN group"
    mail_body = fr"""
    Dears,
    
    Please remove the following users from the VPN user group:
    
    {listofusers}
    
    
    Best regards,"""

    mimemsg = MIMEMultipart()
    mimemsg['From']=mail_from
    mimemsg['To']=mail_to
    mimemsg['Cc']=mail_cc
    mimemsg['Subject']=mail_subject
    mimemsg['X-Priority']='2'
    mimemsg.attach(MIMEText(mail_body))
    connection = smtplib.SMTP(host='SMTP Relay IP',port=587)
    connection.send_message(mimemsg)
    connection.quit()
    print(termcolor.colored("Email sent sucssesfully", "green"))

input("Press any button.... ")