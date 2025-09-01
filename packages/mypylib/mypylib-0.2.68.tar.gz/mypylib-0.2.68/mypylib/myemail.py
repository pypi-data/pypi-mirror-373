import sys
import smtplib
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from os.path import basename
from pathlib import Path


def send_mail(send_from, 
              send_to, 
              subject, 
              text, 
              files=None,
              server="smtp.gmail.com",
              username="williamchen180@gmail.com",
              password="amcn tyic ualm mtto"):
    """
    Send an email with optional file attachments.

    Parameters:
    send_from (str): The email address of the sender.
    send_to (list): A list of recipient email addresses.
    subject (str): The subject of the email.
    text (str): The body text of the email.
    files (list, optional): A list of file paths to attach to the email. Defaults to None.
    server (str, optional): The SMTP server to use for sending the email. Defaults to "smtp.gmail.com".
    username (str, optional): The username for the SMTP server. Defaults to "williamchen180@gmail.com".
    password (str, optional): The password for the SMTP server. Defaults to "amcn tyic ualm mtto".

    Returns:
    None
    """
    assert isinstance(send_to, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = ','.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    # print(f'files: {files}')
    for f in files or []:
        # print(f)
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)


    smtp = smtplib.SMTP(server)
    smtp.ehlo()  # 驗證SMTP伺服器
    smtp.starttls()  # 建立加密傳輸
    # smtp.login("williamchen180@gmail.com", "uzcnaxarquvxszya")  # 登入寄件者gmail
    smtp.login(username, password)  # 登入寄件者gmail
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python email.py <subject> <text> <file1> <file2> ...")
        sys.exit(1)
    
    send_mail('williamchen180@gmail.com',
              # ['u3971777@gmail.com', 'mickeyboy777@gmail.com'],
              ['williamchen180@gmail.com'],
              sys.argv[1],
              sys.argv[2],
              sys.argv[3:])



