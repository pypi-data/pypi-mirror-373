import sys


class PythonVersion:
    """ Get system python installed running version details """

    @staticmethod
    def get_info():
        """ Get the whole information regarding the python version """
        return sys.version_info

    @staticmethod
    def get_major():
        """ Get the python version major value """
        return PythonVersion.get_info().major

    @staticmethod
    def get_minor():
        """ Get the python version minor value """
        return PythonVersion.get_info().minor

    @staticmethod
    def get_micro():
        """ Get the python version micro value """
        return PythonVersion.get_info().micro

    @staticmethod
    def get_releaselevel():
        """ Get the python version releaselevel value """
        return PythonVersion.get_info().releaselevel

    @staticmethod
    def get_serial():
        """ Get the python version serial value """
        return PythonVersion.get_info().serial
