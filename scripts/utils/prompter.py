from typing import List

class Prompter():

    class bcolors:
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
    def print_red(message : str) ->  None:
        print(f"{Prompter.bcolors.FAIL}{message}: {Prompter.bcolors.ENDC}")

    @staticmethod
    def prompt_for_input(prompt: str) -> str:
        while True:
            res = input(f"{Prompter.bcolors.OKCYAN}{prompt}: {Prompter.bcolors.ENDC}")
            if len(res) > 0:
                return res

    @staticmethod
    def check_if_response_is_y(res : str) -> bool:
        if res == "y" or res == "yes":
            return True
        return False

    @staticmethod
    def check_if_response_is_n(res : str) -> bool:
        if res == "n" or res == "no":
            return True
        return False

    @staticmethod
    def check_if_response_is_y_n(res : str) -> bool:
        res = res.strip()
        res = res.lower()
        if Prompter.check_if_response_is_y(res) or Prompter.check_if_response_is_n(res):
            return True
        return False

    @staticmethod
    def wait_for_y_n_response(response : str) -> str:
        while not Prompter.check_if_response_is_y_n(response):
            response = Prompter.prompt_for_input("Please respond \"y\" or \"n\"")
        return response

    @staticmethod
    def prompt_for_input_from_options(prompt: str, formatted_options: List, values: List):
        print(f"{Prompter.bcolors.OKCYAN}{prompt}{Prompter.bcolors.ENDC}")
        for i in range(len(formatted_options)):
            print(f"\t{str(i)}: {formatted_options[i]}")

        while True:
            selection = input("Selection: ")
            try:
                selNum = int(selection)
                if selNum in range(len(formatted_options)):
                    return values[selNum]
                else:
                    Prompter.print_red("Please select a valid option")
            except ValueError as e:
                Prompter.print_red("Please input a number")