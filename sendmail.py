import smtplib
from email.mime.text import MIMEText


# функция для отправки e-mail юзера вместе с его текущим результатом по тесту
def send_email(username, text, result):
    sender = "email@mail.ru"
    password = "password"
    server = smtplib.SMTP('smtp.mail.ru', 587)
    server.starttls()
    server.login(sender, password)
    msg_result = f"\n\nРезультат прохождения теста:\n{result}"
    msg = MIMEText(text + msg_result)
    msg["Subject"] = f"Need help @{username}"
    server.sendmail(sender, sender, msg.as_string())
