import smtplib
import func_timeout
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 587
SMTP_USERNAME = "xxxx@yahoo.com"
SMTP_PASSWORD = "xxsss"
EMAIL_FROM = "xxxx@yahoo.com"
EMAIL_TO = ["xxxx@yahoo.com"]
#EMAIL_TO = ["xxxx@yahoo.com", "aaaaa@qq.com"]


class Email:
    """利用yahoo邮箱发送邮件"""
    def __init__(self):
        pass

    @func_timeout.func_set_timeout(300)
    def sent_email(self, title, content):
        try:
            msg = MIMEText(content, 'html', 'utf-8')
            msg['Subject'] = title
            msg['From'] = EMAIL_FROM
            # msg['To'] = EMAIL_TO
            debuglevel = True
            mail = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            mail.set_debuglevel(debuglevel)
            mail.starttls()
            mail.login(SMTP_USERNAME, SMTP_PASSWORD)
            mail.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
            mail.quit()
        except:
            pass