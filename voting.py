#!/usr/bin/env python
# This program is designed to now give a voting user access to the terminal on the voting computer.

__author__ = '{Johannes Kistemaker}'
__email__ = '{johannes.kistemaker@hva.nl}'


import io
import csv


from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding


def vote():
    pass


def create():
    pass


def results():
    pass


def stats():
    pass


def delete():
    pass


if __name__ == '__main__':
    # Permanently delete last election at run
    delete()
    try:
        # Start new election
        create()

        print("Welcome to this electronic voting program!")
        while True:
            print("Type '?' for all possible arguments")
            usr_input = input("> ").split()

            if "?" in usr_input[0]:
                print('Usage: create')
                print('\tInitialize vote system')
                print('Usage: vote -p <persId> -c <candId>')
                print('\tCast vote')
                print('Usage: results')
                print('\tShow results')
                print('Usage: stats')
                print('\tShow statistics')
                print('Usage: delete')
                print('\tDelete all information (securily)')
            if "vote" in usr_input[0]:
                if not ("-p" and "-c") in usr_input:
                    print("Error, try again")
                else:
                    p = usr_input.index('-p')
                    c = usr_input.index('-c')
                    persId = usr_input[(p + 1)]
                    canId = usr_input[(c + 1)]
                    print(persId)
                    print(canId)
                    vote()
            if "create":
                # Only allow certain user to create an election
                create()
            if "results":
                # Only allow certain user to publish election results and close election afterwards
                results()
            if "stats":
                # Diagnostic stats?
                stats()
            if "delete":
                # Delete all casted votes + diagnostics
                delete()

    except IndexError:
        print("Do better testing!")
        exit()
