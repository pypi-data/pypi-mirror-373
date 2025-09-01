# TODO ugly azure extension

from davidkhala.azure.cli.ext import COMMAND_LOADER_CLS as AbstractLoader


def say_hello(_):
    print(_)
    print("Hello from your custom Azure CLI extension!")


class COMMAND_LOADER_CLS(AbstractLoader):
    def load_command_table(self, args):
        self.set_command('hello world', say_hello)

        return self.command_table
