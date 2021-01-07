#!/usr/bin/env python
# This program is designed to now give a voting user access to the terminal on the voting computer.

__author__ = '{Johannes Kistemaker}'
__email__ = '{johannes.kistemaker@hva.nl}'

import hashlib
import os

from cryptography.fernet import Fernet
from secure_delete import secure_delete

from Crypto.Random import random
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA


def key_create():
    # Create key for symmetric encryption
    key = Fernet.generate_key()
    return key


def hasher_pid(person):
    # Hasher for PersId
    h = hashlib.sha256()
    h.update(person.encode('utf-8'))
    hash_pid = h.hexdigest()
    return hash_pid


def file_encrypt(original):
    # Encrypt voting file having the username hash and vote
    f = Fernet(mykey)
    encrypted = f.encrypt(original)

    with open("vote.state", 'wb') as file:
        file.write(encrypted)


def file_decrypt(encrypted_file):
    # Decrypt voting file
    f = Fernet(mykey)

    with open(encrypted_file, 'rb') as file:
        encrypted = file.read()

    decrypted = f.decrypt(encrypted)
    return decrypted


def recount_file():
    # File used for recounts
    decrypted_vote_state = file_decrypt("vote.state").decode().replace("\n", ";")
    vote_list = decrypted_vote_state.split(";")
    anonymized_votes = vote_list[1::2]

    with open('recount.file', 'a+') as f:
        for anonymized_vote in anonymized_votes:
            f.write(anonymized_vote + "\n")
    f.close()


def check_temp_voter_file():
    # Checks if vote.state exists
    try:
        f = open("vote.state")
        f.close()
        return True
    except IOError:
        print("No election created yet. Type '?' for all options")
        return False


def random_num(pid):
    # Generate random int and store with hashed PersonId
    random_int = random.randint(1, 1000)
    # print(random_int)

    voted_code.append([pid, random_int])
    # print(voted_code)
    return random_int


def vote(voter, candidate):
    # Lets a validated user vote to temp file by hash from PersId
    with open('voters.csv') as csv_file_voters:
        csv_voters = csv_file_voters.read().split(";", 2)
        for row_voter_info in csv_voters:
            if voter in row_voter_info:
                # Hash persID number
                hash_pid = hasher_pid(voter)

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
                print("Vote casted!\nYour random int: " + str(random_num(hash_pid)))
                return

        print("You aren't eligible to vote, or have already voted")
        return


def create():
    # Create new election
    delete(arg="create")
    f = Fernet(mykey)
    encrypted = f.encrypt("hash_pid;canId\n".encode())

    with open("vote.state", 'wb') as file:
        file.write(encrypted)
    file.close()
    return


def results():
    # Publish results from election on CLI
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


def stats():
    # All print statements to file
    pass


def check(pers_id):
    # Check if user voted and secure code
    hash_pid = hasher_pid(pers_id)
    for items in voted_code:
        for item in items:
            if item == hash_pid:
                print(items[1])
                return
    print("No vote registered with your PersID")


def delete(arg):
    # Delete files securely
    if arg == "delete":
        try:
            # f = open("vote.state")
            # f.close()
            secure_delete.secure_random_seed_init()
            secure_delete.secure_delete("vote.state")
            secure_delete.secure_delete("recount.file")
        except IOError:
            print("Error in deleting files securely")

    elif arg == "delete recount":
        try:
            secure_delete.secure_random_seed_init()
            secure_delete.secure_delete("recount.file")
        except IOError:
            print("Error in deleting recount file securely")

    elif arg == "start":
        try:
            # f = open("vote.state")
            # f.close()
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


if __name__ == '__main__':
    try:
        # Create encryption key
        mykey = key_create()

        # Create 2d hash + random int
        voted_code = []

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
                        print('\tShow results') # Add check somewhere
                        print('Usage: stats')
                        print('\tShow statistics')
                        print('Usage: check')
                        print('\tCheck if your vote was casted using random int')
                        print('Usage: delete')
                        print('\tDelete all voting information securely')
                    elif "vote" in usr_input[0]:
                        if not ("-p" and "-c") in usr_input:
                            if check_temp_voter_file():
                                print("Error, try again with '-p' and '-c' info")
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

                                # Overwrite persId
                                persId = os.urandom(16)

                                # print(file_decrypt("vote.state").decode())

                    elif "create" in usr_input[0]:
                        # Start new election
                        create()
                    elif "results" in usr_input[0]:
                        if check_temp_voter_file():
                            # Only allow certain user to publish election results and close election afterwards
                            results()
                    elif "stats" in usr_input[0]:
                        # Diagnostic stats?
                        stats()
                    elif "check" in usr_input[0]:
                        if check_temp_voter_file():
                            # Check if voted and voted well
                            p = usr_input.index('-p')
                            persId = usr_input[(p + 1)]
                            check(persId)

                            # Overwrite persId
                            persId = os.urandom(16)
                    elif "delete" in usr_input[0]:
                        if "recount" in usr_input:
                            # Delete recount file
                            print("Recount file")
                            delete(arg="delete recount")
                        elif check_temp_voter_file():
                            # Delete all casted votes + recount file
                            print("Delete voter files")
                            delete(arg="delete")
                    else:
                        print("Type '?' for all possible arguments")

    except:
        try:
            # Store only anonymized file for counting
            recount_file()

            # Remove temp file with pii-data
            delete(arg="crash")
            print("Saved crash")

        except:
            print("Crashed exit")
            delete(arg="crash")
