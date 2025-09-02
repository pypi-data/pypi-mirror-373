def main():
    print("Hello from beetle-logging!")


if __name__ == "__main__":
    main()
import logging
import os
import datetime

os.system("")

### Default Levels
rootDefLevel = logging.DEBUG    # lowest level to output globally, generally stays at DEBUG
streamDefLevel = logging.INFO  # Terminal logging level
fileDefLevel = logging.INFO  # File logging level

#####################
#                   #
# general functions #
#                   #
#####################

def getDateTime():
    dt = datetime.datetime
    timeNow = dt.now(tz=None)
    return str(dt.strftime(timeNow, "%b-%d-%Y_%I-%M-%S%p"))

######################
#                    #
# console formatting #
#                    #
######################

class colors:
    pink = '\033[95m'
    blue = '\033[94m'
    cyan = '\033[96m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    reset = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'

#################
#               #
# logger config #
#               #
#################
class beetle:
    def __init__(self, appname, fileLogging=True):
        # logger init
        self.logger = logging.getLogger(appname)
        self.logger.setLevel(rootDefLevel)

        # stream handler with custom colors
        self._stream_handler = logging.StreamHandler()
        self._stream_handler.setLevel(streamDefLevel)
        class _streamFormatter(logging.Formatter):
            """Logging Formatter to add colors and count warning / errors"""

            msgformat1 = '%(asctime)s | '
            msgformat2 = ' | %(name)s | %(message)s'

            FORMATS = {
                logging.DEBUG: msgformat1 + colors.blue + 'DEBUG' + colors.reset + msgformat2,
                logging.INFO: msgformat1 + 'INFO' + msgformat2,
                logging.WARNING: msgformat1 + colors.yellow + 'WARNING' + colors.reset + msgformat2,
                logging.ERROR: msgformat1 + colors.red + 'ERROR' + colors.reset + msgformat2,
                logging.CRITICAL: msgformat1 + colors.red + colors.underline + 'CRITICAL' + colors.reset + msgformat2
            }

            def format(self, record):
                log_fmt = self.FORMATS.get(record.levelno)
                formatter = logging.Formatter(log_fmt)
                return formatter.format(record)
        self._stream_handler.setFormatter(_streamFormatter())
        self.logger.addHandler(self._stream_handler)

        if fileLogging:
            # check if "logs" directory exists in the folder, create it if not
            if not (os.path.isdir('logs')):
                os.mkdir('logs')

            # file handler
            self._file_handler = logging.FileHandler('logs/' + getDateTime() + '.txt') 
            fileFormat = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
            self._file_handler.setFormatter(fileFormat)
            self._file_handler.setLevel(fileDefLevel)
            self.logger.addHandler(self._file_handler)

        self.logger.debug(f"Beetle logger initialized with name \"{appname}\"")

    def setStreamLevel(self, level):
        """
        Sets logging level on the stream handler
        @param level, (logging.LEVEL) Desired level
        """
        self._stream_handler.setLevel(level)

    def setFileLevel(self, level):
        """
        Sets logging level on the file handler
        @param level, (logging.LEVEL) Desired level
        """
        self._file_handler.setLevel(level)

if __name__ == "__main__":
    bt = beetle("app")
    bt.logger.critical("Congrats, you ran beetle and it worked. Now go actually use it somewhere!")