import datetime as dt
from datetime import timedelta
from dateutil.relativedelta import relativedelta

class DATEUTILS:
    def __init__(self):
        ...

    # region Miscelanea
    @staticmethod
    def calcular_data(formula, variaveis, mascara):
        """Substitui variáveis na fórmula e calcula a nova data."""
        result = None
        try:
            # Convertendo a string para um objeto datetime
            data_base = dt.datetime.strptime(variaveis["data"], mascara)
            dias = int(variaveis["dias"])  # Convertendo dias para inteiro

            # Executando a fórmula
            nova_data = eval(formula, {}, {"data": data_base, "timedelta": timedelta, "dias": dias})
            result = nova_data.strftime(mascara)
        except Exception as error:
            result = f"Erro: {error}"
        finally:
            return result
    # endregion

    # region Data As Long
    @staticmethod
    def Date_to_DateAsLong(value):
        try:
            dataaslong = int(dt.datetime.timestamp(value) * 1e3)
            return dataaslong
        except Exception as error:
            msgerro = f"""Falha ao tentar transformar um DATA em um LONG: "{value}". {error}"""
            raise Exception(msgerro)

    @staticmethod
    def DateAsLong_to_Date(value):
        try:
            date = dt.datetime.fromtimestamp(value / 1e3)
            return date
        except Exception as error:
            msgerro = f"""Falha ao tentar transformar um LONG em uma data: "{value}". {error}"""
            raise Exception(msgerro)

    @staticmethod
    def TimeAsLong_to_Time(value: dt.timedelta):
        try:
            horas_total = round((value.days * 24) + int(value.seconds / 60 / 60), 2)
            minutos = round(((value.seconds / 60 / 60) - int((value.seconds / 60) / 60)) * 60, 2)
            seg = round(((minutos - int(minutos)) * 60), 2)
            hora = f"""{horas_total}:{int(minutos):02}:{int(round(seg)):02}"""
            return hora
        except Exception as error:
            msgerro = f"""Falha ao tentar converter um timedelta para um tempo (HH:mm:ss) "{value}". {error}"""
            raise Exception(msgerro)

    @staticmethod
    def Time_to_TimeAsLong(value):
        try:
            td = value.split(":")
            h = round(int(td[0]) * 60 * 60 * 1000)
            m = round(int(td[1]) * 60 * 1000)
            s = round(int(td[2]) * 1000)
            tempo = h + m + s
            return tempo
        except Exception as error:
            msgerro = f"""Falha ao tentar converter um horario em LONG "{value}". {error}"""
            raise Exception(msgerro)
    # endregion

    # region Dias Ano, Semestre, Mes, Quinzena
    @staticmethod
    def getPrimeiroDiaAno(data: dt.datetime) -> dt.datetime:
        result = dt.datetime(year=data.year, month=1, day=1, hour=0, minute=0, second=0)
        return result

    @staticmethod
    def getUltimoDiaAno(data: dt.datetime) -> dt.datetime:
        result = dt.datetime(year=data.year, month=12, day=31, hour=23, minute=59, second=59)
        return result

    @staticmethod
    def getPrimeiroDiaSemestre(data: dt.datetime) -> dt.datetime:
        if data.month >=7:
            month = 7
        else:
            month = 1
        result = dt.datetime(year=data.year, month=month, day=1, hour=0, minute=0, second=0)
        return result

    @staticmethod
    def getUltimoDiaSemestre(data: dt.datetime) -> dt.datetime:
        if data.month >= 7:
            month = 12
            day = 31
        else:
            month = 6
            day = 30
        result = dt.datetime(year=data.year, month=month, day=day, hour=23, minute=59, second=59)
        return result

    @staticmethod
    def getPrimeiroDiaMes(data: dt.datetime) -> dt.datetime:
        result = dt.datetime(year=data.year, month=data.month, day=1, hour=0, minute=0, second=0)
        return result

    @staticmethod
    def getUltimoDiaMes(data: dt.datetime) -> dt.datetime:
        # result = data + relativedelta(day=31)
        result = dt.datetime(year=data.year, month=data.month, day=(data + relativedelta(day=31)).day, hour=23,
                             minute=59, second=59)
        return result

    @staticmethod
    def getPrimeiroDiaQuinzena(data: dt.datetime) -> dt.datetime:
        if data.day > 15:
            day = 16
        else:
            day = 1
        result = dt.datetime(year=data.year, month=data.month, day=day, hour=0, minute=0, second=0)
        return result

    @staticmethod
    def getUltimoDiaQuinzena(data: dt.datetime) -> dt.datetime:
        if data.day > 15:
            day = data + relativedelta(day=31).day
        else:
            day = 15
        result = dt.datetime(year=data.year, month=data.month, day=day, hour=23, minute=59, second=59)
        return result

    @staticmethod
    def getPrimeiraHoraDia(data: dt.datetime) -> dt.datetime:
        result = dt.datetime(year=data.year, month=data.month, day=data.day, hour=0, minute=0, second=0)
        return result
    # endregion

    # region Horas, minutos, segundos, milisegundos
    @staticmethod
    def getUltimaHoraDia(data: dt.datetime) -> dt.datetime:
        result = dt.datetime(year=data.year, month=data.month, day=data.day, hour=23, minute=59, second=59)
        return result

    @staticmethod
    def getPrimeiroMinutoHora(data: dt.datetime) -> dt.datetime:
        result = dt.datetime(year=data.year, month=data.month, day=data.day, hour=data.hour, minute=0, second=0)
        return result

    @staticmethod
    def getUltimoMinutoHora(data: dt.datetime) -> dt.datetime:
        result = dt.datetime(year=data.year, month=data.month, day=data.day, hour=data.hour, minute=59, second=59)
        return result

    @staticmethod
    def getPrimeiroSegundoMinuto(data: dt.datetime) -> dt.datetime:
        result = dt.datetime(year=data.year, month=data.month, day=data.day, hour=data.hour, minute=data.minute, second=0)
        return result

    @staticmethod
    def getUltimoSegundoMinuto(data: dt.datetime) -> dt.datetime:
        result = dt.datetime(year=data.year, month=data.month, day=data.day, hour=data.hour, minute=data.minute, second=59)
        return result

    @staticmethod
    def getPrimeiroMilesimoSegundo(data: dt.datetime) -> dt.datetime:
        result = dt.datetime(year=data.year, month=data.month, day=data.day, hour=data.hour, minute=data.minute,
                             second=data.second, microsecond=0)
        return result

    @staticmethod
    def getUltimoMilesimoSegundo(data: dt.datetime) -> dt.datetime:
        result = dt.datetime(year=data.year, month=data.month, day=data.day, hour=data.hour, minute=data.minute,
                             second=data.second, microsecond=99999)
        return result
    # endregion

    # region DATA/HORA mascaras SQL | PYTHON
    @property
    def DATE_FORMAT_PYTHON(self):
        return "%Y-%m-%d"

    @property
    def DATETIME_FORMAT_PYTHON(self):
        return "%Y-%m-%d %H:%M:%S"

    @property
    def MILLISECONDS_FORMAT_PYTHON(self):
        return "%Y-%m-%d %H:%M:%S.%f"

    @property
    def TIME_FORMAT_PYTHON(self):
        return "%H:%M:%S:%f"

    @property
    def DATE_FORMAT_SQL(self):
        return "YYYY-MM-DD"

    @property
    def DATETIME_FORMAT_SQL(self):
        return "YYYY-MM-DD HH24:MI:SS"

    @property
    def MILLISECONDS_FORMAT_SQL(self):
        return "YYYY-MM-DD HH24:MI:SS.FF6"

    @property
    def TIME_FORMAT_SQL(self):
        return "HH24:MI:SS:FF6"

    @property
    def DATETIME_FILENAME(self):
        return "%Y%m%d%H%M%S"
    # endregion
