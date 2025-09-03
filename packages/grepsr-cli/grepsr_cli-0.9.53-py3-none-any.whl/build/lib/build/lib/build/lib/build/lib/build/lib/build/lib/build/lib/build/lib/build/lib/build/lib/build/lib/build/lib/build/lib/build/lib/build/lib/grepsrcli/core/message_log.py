class Log:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def info(message):
        print(f'{Log.OKGREEN}INFO: {message}{Log.ENDC}')

    @staticmethod
    def error(message):
        print(f'{Log.BOLD}{Log.FAIL}ERR: {message}{Log.ENDC}')

    @staticmethod
    def standout(message):
        print(f'{Log.HEADER}{message}{Log.ENDC}')

    @staticmethod
    def success(message):
        print(f'{Log.OKGREEN}SUCCESS: {message}{Log.ENDC}')

    @staticmethod
    def warn(message):
        print(f'{Log.WARNING}WARNING: {message}{Log.ENDC}')

    @staticmethod
    def heading(message):
        print(f'{Log.OKBLUE}{message}{Log.ENDC}')