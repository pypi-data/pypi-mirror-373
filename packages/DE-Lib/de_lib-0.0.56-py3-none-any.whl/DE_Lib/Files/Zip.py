import zipfile
from zipfile import ZipFile
import shutil
import os


class ZIP:
    def __init__(self):
        self.__read = ("r")
        self.__write = "w"
        self.__append = "a"
        self.__moving = "MOVING"
        self.__delete = "DELETE"
        self.__nothing = "NOTHING"
        self.__modo = None

    # ---------------------------------
    def ZipFiles(self):
        msg, result = None, True
        try:
            ...
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result


    # ---------------------------------
    def zip(self, files:list, zipfile: str, modo:str="w", action:str="NOTHING", moving:str=""):
        msg, result = None, True
        try:
            # modo
            with ZipFile(zipfile, modo) as zfh:
            #zfh = ZipFile(file=zipfile, mode="w")
                for file in files:
                    zfh.write(filename=file)

                    # action
                    if action == self.NOTHING:
                        pass
                    elif action == self.DELETE:
                        for file in files:
                            os.remove(file)
                    elif action == self.MOVING:
                        if os.path.isdir(moving):
                            shutil.move(file, moving)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    # ---------------------------------
    def unzip(self, zipfile:str, outputfolder:str):
        msg, result = None, True
        try:
            zfh = ZipFile(zipfile, self.READ)
            zfh.extractall(outputfolder)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result


    @property
    def NOTHING(self):
        return self.__nothing

    @NOTHING.setter
    def NOTHING(self, value):
        self.__nothing = value


    @property
    def DELETE(self):
        return self.__delete

    @DELETE.setter
    def DELETE(self, value):
        self.__delete = value

    @property
    def MOVING(self):
        return self.__moving

    @MOVING.setter
    def MOVING(self, value):
        self.__moving = value


    @property
    def APPEND(self):
        return self.__append

    @APPEND.setter
    def APPEND(self, value):
        self.__append = value


    @property
    def WRITE(self):
        return self.__write

    @WRITE.setter
    def WRITE(self, value):
        self.__write = value


    @property
    def READ(self):
        return self.__read

    @READ.setter
    def READ(self, value):
        self.__read = value


