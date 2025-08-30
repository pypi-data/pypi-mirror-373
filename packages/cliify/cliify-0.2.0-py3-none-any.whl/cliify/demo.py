
from cliify import command, commandParser
from cliify.ui.prompt_toolkit import SplitConsole
from cliify.ui.prompt_toolkit import Console
import logging 
from termcolor import colored

logger = logging.getLogger('MyCli')

@commandParser
class myClass:
    def __init__(self):
        self.value = 0
        self.type = None


    @command(when=lambda self: self.type == 'dog')
    def bark(self):
        """
                Bark like a dog
        """
        print(colored("Woof!", 'green'))


    #Add completions to arguments in the command decorator
    @command(completions={'type': ['dog', 'cat', 'bird']}) 
    def setType(self, type: str):
        """
                Set the type of the object

                args:
                    type: The type to set
        """
        print(colored(f"Set Type to {type}", 'blue'))
        self.type = type

    #Support for lambda functions in completions
    @command(completions={'value': lambda self: [str(i) for i in range(10)]})
    def setValue(self, value: int):
        """
                Set the value of the object

                args:
                    value: The value to set

        """
        logger.info(f"Set value to {value}")
        self.value = value

    #adding $file to your completions will include file path completions
    @command(completions={'file': ['$file']})
    def open(self, file: str):
        """
                Open a file
                
                args:
                    file: The file to open
        """

        logger.info(f"Opening {file}")

    @command(completions={'test': ['$commands']})
    def test(self, test: str):
        """
                Test command

                args:
                    test: The test to run
        """
        print(colored(f"Test {test}", 'blue'))

    @command(completions={'cmd': ['$commands','!help','!cmd']})
    def help(self, cmd: str):
        """
                Show help for a command

                args:
                    help: The command to show help for
        """
        out = self.getHelp(cmd)
        print(colored(out, 'yellow'))



def main():
    obj = myClass()
    console = SplitConsole(obj, "My CLI", "history.txt")
    logger.warning("This is a warning message")
    console.start()

if __name__ == "__main__":
    main()
