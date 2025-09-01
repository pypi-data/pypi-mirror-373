from DE_Lib.Utils import Colors

colors = Colors.COLORS()


class LEVEL:
    def __init__(self):
        self.__log__level__ = {"code":None, "name": None, "color": None}
        self.__logEvent = {}

    # region Level
    @property
    def NOTSET(self):
        self.__log__level__["code"] = 0
        self.__log__level__["name"] = "NOTSET"
        self.__log__level__["color"] = colors.green_light_fore
        return self.__log__level__

    @property
    def WARNING(self):
        self.__log__level__["code"] = 10
        self.__log__level__["name"] = "WARNING"
        self.__log__level__["color"] = colors.yellow_light_fore
        return self.__log__level__

    @property
    def DEBUG(self):
        self.__log__level__["code"] = 20
        self.__log__level__["name"] = "DEBUG"
        self.__log__level__["color"] = colors.green_light_fore
        return self.__log__level__

    @property
    def ERROR(self):
        self.__log__level__["code"] = 30
        self.__log__level__["name"] = "ERROR"
        self.__log__level__["color"] = colors.red_light_fore
        return self.__log__level__

    @property
    def INFO(self):
        self.__log__level__["code"] = 40
        self.__log__level__["name"] = "INFO"
        self.__log__level__["color"] = colors.gray_light_fore
        return self.__log__level__

    @property
    def CRITICAL(self):
        self.__log__level__["code"] = 50
        self.__log__level__["name"] = "CRITICAL"
        self.__log__level__["color"] = colors.red_fore + colors.white_back
        return self.__log__level__

    @property
    def DESTAQUE(self):
        self.__log__level__["code"] = 60
        self.__log__level__["name"] = "DESTAQUE"
        self.__log__level__["color"] = colors.cyan_fore
        return self.__log__level__

    @property
    def ENFASE(self):
        self.__log__level__["code"] = 70
        self.__log__level__["name"] = "ENFASE"
        self.__log__level__["color"] = colors.white_fore + colors.bold + colors.underline
        return self.__log__level__

    @property
    def LOG_LEVEL(self):
        result = {"code": self.__log__level__["code"],
                  "name": self.__log__level__["name"],
                  "color": self.__log__level__["color"]
                  }
        self.__logEvent[result["name"]] = {"code":result["code"], "color": result["color"]}
        return result
    # endregion

