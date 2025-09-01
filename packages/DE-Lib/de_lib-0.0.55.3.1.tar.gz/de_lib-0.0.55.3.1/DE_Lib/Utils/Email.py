import smtplib
import os.path
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


class EMAIL:
    def __init__(self):
        ...

    def send_email(self, par: dict):
        msg, result = None, None
        try:
            self.__setProperty(par)

            # Definindo o cabeçalho do email
            msg = MIMEMultipart()
            msg["From"] = self.FROM
            msg["To"] = self.TO
            msg["Cc"] = self.CC
            msg["Bcc"] = self.BCC
            msg["Subject"] = self.SUBJECT

            # Definindo o texto (corpo) da mensagem
            text = MIMEText(self.BODY, self.SUBTYPEBODY, self.CHARSET)

            # Definindo os arquivos a serem anexados
            if self.FILES:
                for file in self.FILES:
                    if os.path.isfile(file):
                        basename = os.path.basename(file)
                        subtipo = mimetypes.guess_type(file)[0].split("/", 1)[1]
                        buffer = open(file, 'rb')
                        part = MIMEApplication(buffer.read(), _subtype=subtipo)
                        part.add_header(_name="Content-Disposition", _value="attachment", filename=basename)
                        msg.attach(part)

            # Enviando email
            smtp = smtplib.SMTP(self.HOST, self.PORT)
            smtp.send_message(msg)
            smtp.quit()
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def __setProperty(self, par):
        msg, result = None, None
        try:
            self.TO = par["to"]
            self.FROM = par["from"]
            self.SUBJECT = par["subject"]
            self.CC = par["cc"]
            self.BCC = par["bcc"]
            self.BODY = par["body"]
            self.FILES = par["files"]
            self.HOST = par["host"]
            self.PORT = par["port"]
            self.SUBTYPEBODY = par["subtypebody"]
            self.CHARSET = par["charset"]
            self.ERROR = None

        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @property
    def TO(self):
        return self.__to

    @TO.setter
    def TO(self, value):
        self.__to = value

    @property
    def FROM(self):
        return self.__from

    @FROM.setter
    def FROM(self, value):
        self.__from = value

    @property
    def CC(self):
        return self.__cc

    @CC.setter
    def CC(self, value):
        self.__cc = value

    @property
    def BCC(self):
        return self.__bcc

    @BCC.setter
    def BCC(self, value):
        self.__bcc = value

    @property
    def SUBJECT(self):
        return self.__subject

    @SUBJECT.setter
    def SUBJECT(self, value):
        self.__subject = value

    @property
    def BODY(self):
        return self.__body

    @BODY.setter
    def BODY(self, value):
        self.__body = value

    @property
    def FILES(self):
        return self.__files

    @FILES.setter
    def FILES(self, value):
        if isinstance(value, list):
            self.__files = value
        else:
            self.__files = value.split(",")

    @property
    def HOST(self):
        return self.__host

    @HOST.setter
    def HOST(self, value):
        self.__host = value

    @property
    def PORT(self):
        return self.__port

    @PORT.setter
    def PORT(self, value):
        self.__port = value

    @property
    def ERROR(self):
        return self.__error

    @ERROR.setter
    def ERROR(self, value):
        self.__error = value

    @property
    def SUBTYPEBODY(self):
        return self.__subtypebody

    @SUBTYPEBODY.setter
    def SUBTYPEBODY(self, value):
        if not value:
            self.__subtypebody = "html"
        else:
            self.__subtypebody = value

    @property
    def CHARSET(self):
        return self.__charset

    @CHARSET.setter
    def CHARSET(self, value):
        if not value:
            self.__charset = "utf-8"
        else:
            self.__charset = value


if __name__ == "__main__":
    par = {"from": "BI@dasa.com.br",
           "to": ["almir.jacinto.ext@dasa.com.br"],
           "cc": [],
           "bcc": [],
           "subject": "Assunto do este de email",
           "body": "Corpo do teste de email",
           "host": "mail.dasa.com.br",
           "port": 25,
           "files": [f"C:\cloud\OneDrive\Projetos\DataEng\DATAx\DE-LIB\config\Log\LOG_EVENTOS_CORES_SQLITE_2025.json", "C:\cloud\OneDrive\Projetos\DataEng\DATAx\DE-LIB\config\Log\TESTE_PROCESSO_NUMERO_1.json" ],
           "subtype": "html",
           "charset": "utf-8",
           "zipfile": False
           }
    e = EMAIL()
    e.send_email(par)