#!/usr/bin/env python
# This program is designed to now give a voting user access to the terminal on the voting computer.

__author__ = '{Johannes Kistemaker}'
__email__ = '{johannes.kistemaker@hva.nl}'

import hashlib
import os

from cryptography.fernet import Fernet
from secure_delete import secure_delete


def key_create():
    key = Fernet.generate_key()
    return key


def file_encrypt(original):
    f = Fernet(mykey)
    encrypted = f.encrypt(original)

    with open("vote.state", 'wb') as file:
        file.write(encrypted)


def file_decrypt(encrypted_file):
    f = Fernet(mykey)

    with open(encrypted_file, 'rb') as file:
        encrypted = file.read()

    decrypted = f.decrypt(encrypted)
    return decrypted


def vote(voter, candidate):
    # Check if voter is in allowed voters list
    with open('voters.csv') as csv_file_voters:
        csv_voters = csv_file_voters.read().split(";", 2)
        for row_voter_info in csv_voters:
            if voter in row_voter_info:
                # Hash persID number
                h = hashlib.sha256()
                h.update(voter.encode('utf-8'))
                hash_pid = h.hexdigest()

                # Read temp file and check if voter already voted
                decrypted_vote_state = file_decrypt("vote.state").decode()
                print(decrypted_vote_state)
                csv_casted_votes = decrypted_vote_state.split(";", 1)
                for row_votes_info in csv_casted_votes:
                    if hash_pid in row_votes_info:
                        print("\nYou aren't eligible to vote or have already voted\n")
                        return

                # Add casted vote to temp file
                new_vote_state = decrypted_vote_state + str(hash_pid) + ";" + str(candidate) + "\n"
                file_encrypt(new_vote_state.encode())
                print("Vote casted! ")
                return

        print("You aren't eligible to vote, or have already voted")
        return


def create():

    f = Fernet(mykey)
    encrypted = f.encrypt("hash_pid;canId\n".encode())

    with open("vote.state", 'wb') as file:
        file.write(encrypted)
    file.close()

    return


def results():
    decrypted_vote_state = file_decrypt("vote.state").decode()
    print("EK: " + str(decrypted_vote_state.count("EK")))
    print("FS: " + str(decrypted_vote_state.count("FS")))
    print("TK: " + str(decrypted_vote_state.count("TK")))


def stats():
    pass


def delete():
    try:
        f = open("vote.state")
        f.close()
        secure_delete.secure_random_seed_init()
        secure_delete.secure_delete("vote.state")
    except IOError:
        print("Vote file does not exist, first run")


if __name__ == '__main__':
    # Permanently delete last election at run
    delete()
    try:
        # Create encryption key
        mykey = key_create()

        # Start new election
        create()
        # print(file_decrypt("vote.state").decode())

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
            elif "vote" in usr_input[0]:
                if not ("-p" and "-c") in usr_input:
                    print("Error, try again")
                else:
                    p = usr_input.index('-p')
                    c = usr_input.index('-c')
                    persId = usr_input[(p + 1)]
                    canId = usr_input[(c + 1)]
                    # print(persId)
                    # print(canId)

                    # Collect vote
                    vote(persId, canId)

                    # Overwrite persId and canId
                    persId = os.urandom(16)

                    print(file_decrypt("vote.state").decode())

            elif "create" in usr_input[0]:
                # Only allow certain user to create an election
                create()
            elif "results" in usr_input[0]:
                # Only allow certain user to publish election results and close election afterwards
                results()
            elif "stats" in usr_input[0]:
                # Diagnostic stats?
                stats()
            elif "delete" in usr_input[0]:
                # Delete all casted votes + diagnostics?
                print("delete")
                delete()

    except IndexError:
        print("Do better testing!")
        exit()
