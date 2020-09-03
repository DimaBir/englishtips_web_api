import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
mail_content = "REBOOT at: " + dt_string

#The mail addresses and password
sender_address = 'englishtips.server@gmail.com'
sender_pass = 'itsang86'
receiver_address = 'dvlasenko86@gmail.com'

#Setup the MIME
message = MIMEMultipart()
message['From'] = sender_address
message['To'] = receiver_address
message['Subject'] = '--- ENGLISH TIPS SERVER ---'   #The subject line

#The body and the attachments for the mail
message.attach(MIMEText(mail_content, 'plain'))

#Create SMTP session for sending the mail
session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
session.starttls() #enable security
session.login(sender_address, sender_pass) #login with mail_id and password

text = message.as_string()

session.sendmail(sender_address, receiver_address, text)
session.quit()