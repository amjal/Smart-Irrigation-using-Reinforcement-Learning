import glob
from os import listdir
from os.path import isfile, join


class FileOperation:
    path = "./test_path"
    EPOCH_SIZE = 10
    POINTER_FILE = ""
    POINTER_EPOCH = 0
    FILES_COMPLETED = []
    FILE_IN_PROCESS = ""
    TEMP_FILES_ADDRESS = "temp1.cfg"
    END_OF_FILE = False

    def __init__(self, *args):
        if len(args) > 0:
            self.path = args[0]
            self.EPOCH_SIZE = args[1]
            self.POINTER_FILE = args[2]
            self.POINTER_EPOCH = args[3]
            self.FILES_COMPLETED = args[4]
            self.TEMP_FILES_ADDRESS = args[5]
        self.path_file_collector()
        self.currentFileInProcessName = ''
        self.logFile = open(self.TEMP_FILES_ADDRESS, 'a')

    def log_decorator(func):
        def wrapper(self, *args):
            # before starts
            self.logFile.writelines(
                ["File in process : " + str(self.FILE_IN_PROCESS) + " epoch point : " + str(self.POINTER_EPOCH) +
                 " Files completed : " + str(self.FILES_COMPLETED) + "\n"])
            # / before starts
            try:
                return func(self, args)
            except AssertionError as a:
                self.error_handler(1)
            except IndexError as i:
                self.error_handler(2)
            except TypeError as t:
                self.error_handler(3)
            except ValueError as v:
                self.error_handler(4)
            except NameError as n:
                self.error_handler(5)

            # after finished

        return wrapper

    @staticmethod
    def error_handler(error_number):

        def assertion_error():
            print('Assertion Exception Raised')
            exit(-1)

        def index_error():
            print('Index Exception Raised')
            exit(-1)

        def type_error():
            print('Caught TypeError Exception')
            exit(-1)

        def value_error():
            print('Caught ValueError Exception')
            exit(-1)

        def name_error():
            print('Caught ValueError Exception')
            exit(-1)

        switcher = {
            1: assertion_error,
            2: index_error,
            3: type_error,
            4: value_error,
            5: name_error
        }
        switcher.get(error_number)()

    fileSetForReading = False

    @log_decorator
    def read_line(self, *args):
        data = []
        if not self.fileSetForReading:
            self.start_new_file()
        for i in range(self.EPOCH_SIZE):
            current_data = self.currentFileInProcess.readline()
            if current_data != '':
                data.append(current_data)
            else:
                self.fileSetForReading = False
                self.start_new_file()
                break
        self.POINTER_EPOCH += 1
        return data

    @log_decorator
    def get_new_file(self, file):
        # Change current file in process
        self.FILE_IN_PROCESS = file
        self.POINTER_EPOCH = 0

    def path_file_collector(self):
        self.pathFiles = [f for f in glob.glob(self.path + "**/*.csv", recursive=True)]

    def start_new_file(self):
        self.FILES_COMPLETED.append(self.currentFileInProcessName)
        for file in self.pathFiles:
            if file not in self.FILES_COMPLETED:
                self.currentFileInProcess = open(file, "r")
                self.currentFileInProcessName = file
                self.fileSetForReading = True
                return 1
        self.logFile.writelines(
            ["File in process : " + str(self.FILE_IN_PROCESS) + " epoch point : " + str(self.POINTER_EPOCH) +
             " Files completed : " + str(self.FILES_COMPLETED) + "\n"])
        # exit(Exception("All path files finished"))
        self.END_OF_FILE = True

    def list_files(self):
        # read all files in path and return their names in only_files variable as a list
        try:
            only_files = [f for f in listdir(self.path) if isfile(join(self.path, f))]
            return only_files
        except NotADirectoryError:
            print('Error at FileOperation.list_files: Expected directory but a file was given')
            return []
