# -*- coding: utf-8 -*-

""" MAIN ENTRY POINT FOR FLETX CLI
This module serves as the main entry point for the FletX CLI. It handles command-line
arguments, initializes the command registry, and executes the specified command.
"""

from fletx.cli import (
    FletXCLI
)

def main():
    """ 
    Main function to handle command-line arguments and execute commands.
    This function checks if any command is provided, retrieves the command class
    from the command registry, and executes the command with the provided arguments.
    If no command is provided, it lists all available commands.
    """

    cli = FletXCLI()
    cli.execute_from_command_line()

if __name__ == "__main__":
    main()
