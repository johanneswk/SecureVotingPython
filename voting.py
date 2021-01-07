#!/usr/bin/env python
# This program is designed to now give a voting user access to the terminal on the voting computer.

__author__ = '{Johannes Kistemaker}'
__email__ = '{johannes.kistemaker@hva.nl}'

import hashlib
import os

from cryptography.fernet import Fernet
from secure_delete import secure_delete

from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA


# from Crypto import Random


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
                # print(decrypted_vote_state)
                csv_casted_votes = decrypted_vote_state.split(";", 1)
                for row_votes_info in csv_casted_votes:
                    if hash_pid in row_votes_info:
                        print("You aren't eligible to vote or have already voted")
                        return

                # Add casted vote to temp file
                new_vote_state = decrypted_vote_state + str(hash_pid) + ";" + str(candidate) + "\n"
                file_encrypt(new_vote_state.encode())
                print("Vote casted! ")
                return

        print("You aren't eligible to vote, or have already voted")
        return


def create():
    delete(arg="create")
    f = Fernet(mykey)
    encrypted = f.encrypt("hash_pid;canId\n".encode())

    with open("vote.state", 'wb') as file:
        file.write(encrypted)
    file.close()
    return


def results():
    # Publish results on CLI
    decrypted_vote_state = file_decrypt("vote.state").decode().replace("\n", ";")

    votes_emeri = decrypted_vote_state.count("EK")
    votes_frans = decrypted_vote_state.count("FS")
    votes_tim = decrypted_vote_state.count("TK")
    print("EK: " + str(votes_emeri) + "\nFS: " + str(votes_frans) + "\nTK: " + str(votes_tim))

    # Publish results in result.csv
    result = ("EK: " + str(votes_emeri) + "\nFS: " + str(votes_frans) + "\nTK: " + str(votes_tim)).encode()

    with open('signer@cs-hva.nl.prv', 'r') as f:
        key = RSA.importKey(f.read())
    f.close()

    # with open('signer@cs-hva.nl.pub', 'r') as g:
    #     pubkey = RSA.importKey(g.read())
    # g.close()

    h = SHA256.new(result)
    signer = PKCS115_SigScheme(key)
    signature = signer.sign(h)

    with open("signature.sign", 'wb') as h:
        h.write(signature)
    h.close()

    with open("results.txt", 'w') as i:
        i.write(result.decode())
    i.close()

    # create recountable file
    recount_file()

    # delete temp voter file after results
    delete(arg="results")


def recount_file():
    decrypted_vote_state = file_decrypt("vote.state").decode().replace("\n", ";")
    vote_list = decrypted_vote_state.split(";")
    anonymized_votes = vote_list[1::2]

    with open('recount.file', 'a+') as f:
        for anonymized_vote in anonymized_votes:
            print(anonymized_vote)
            f.write(anonymized_vote + "\n")
    f.close()


def stats():
    pass


def delete(arg):
    if arg == "delete":
        try:
            f = open("vote.state")
            f.close()
            secure_delete.secure_random_seed_init()
            secure_delete.secure_delete("vote.state")
            secure_delete.secure_delete("recount.file")
        except IOError:
            print("Error in deleting files securely")

    elif arg == "start":
        try:
            f = open("vote.state")
            f.close()
            secure_delete.secure_random_seed_init()
            secure_delete.secure_delete("vote.state")
        except IOError:
            print("First run, creating election...")

    elif arg == "crash" or arg == "results":
        try:
            # f = open("vote.state")
            # f.close()
            secure_delete.secure_random_seed_init()
            secure_delete.secure_delete("vote.state")
        except IOError:
            print("Error in deleting files at crash")


def check_temp_voter_file():
    try:
        f = open("vote.state")
        f.close()
        return True
    except IOError:
        print("No election created yet. Type '?' for all options")
        return False


if __name__ == '__main__':
    try:
        # Create encryption key
        mykey = key_create()

        # print(file_decrypt("vote.state").decode())

        print("Welcome to this electronic voting program!")
        print("Type '?' for all possible arguments")
        while True:
            # Check user input
            try:
                usr_input = input("> ").split()
            finally:
                if not usr_input:
                    print("Type '?' for all possible arguments")
                else:
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
                            if check_temp_voter_file():
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

                                # print(file_decrypt("vote.state").decode())

                    elif "create" in usr_input[0]:
                        # Start new election
                        create()
                    elif "results" in usr_input[0]:
                        # Only allow certain user to publish election results and close election afterwards
                        results()
                    elif "stats" in usr_input[0]:
                        # Diagnostic stats?
                        stats()
                    elif "delete" in usr_input[0]:
                        # Delete all casted votes + recount file?
                        print("delete")
                        delete(arg="delete")
                    else:
                        print("Type '?' for all possible arguments")


    except:
        print("Do better testing!")

        try:
            # Store only anonymized file for counting
            recount_file()

            # Remove temp file with pii-data
            # delete(arg="crash")
            print("Saved crash")
            # Exit program
            # exit()
        except:
            print("Crashed exit")
            delete(arg="crash")


