#!/usr/bin/env python
# This program is designed to now give a voting user access to the terminal on the voting computer.

__author__ = '{Johannes Kistemaker}'
__email__ = '{johannes.kistemaker@hva.nl}'


import io
import csv


from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

gDbg = False
gSigner = "signer@cs-hva.nl"


def sign(data, signer=gSigner, sfx='.prv'):
    if isinstance(data, io.StringIO):
        data = data.read()
    if not isinstance(data, bytes):
        data = bytes(data, encoding='utf-8')

    sign = b''
    # Calculate the signature of the data using a prv_key, sha256, pkcs1 en rsa-2048
    # Student Work {{
    with io.open(signer+'.prv', "rb") as fp:
        prv_key = serialization.load_pem_private_key(fp.read(), password=None)
    sign = prv_key.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    # Student Work {{

    return ':'.join(['#sign', 'sha256-PKCS1-rsa2048', signer, sign.hex()])


def verify(data, signature, signer=gSigner, sfx='.pub'):
    if isinstance(data, io.StringIO):
        data = data.read()
    if not isinstance(data, bytes):
        data = bytes(data, encoding='utf-8')
    flds = signature.split(':')
    if flds[1] != 'sha256-PKCS1-rsa2048' and flds[2] != signer:
        print('Error: Unknown signature:', signature)
        return None
    sign = bytes.fromhex(flds[3])

    res = False
    # Validate the signature of the data using a prvKey, sha256, pkcs1 en rsa-2048
    # Student Work {{
    with io.open(signer+'.pub', "rb") as fp:
        pub_key = serialization.load_pem_public_key(fp.read())
    try:
        sign = bytes.fromhex(flds[3])
        pub_key.verify(
            sign,
            data,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        res = True
    except Exception as e:
        print('Exception', e)
        res = False
    # Student Work }}

    return res


def load_file(fname, use_sign=True, signer=gSigner):
    """ Load file check signature """
    data = io.open(fname, 'r', encoding='UTF-8').read()
    n = data.find('#sign')
    if n > 0:
        sign = data[n:].strip()
        data = data[0:n]
        if use_sign:
            res = verify(data, sign, signer, sfx='.pub')
            if not res: return None
    return io.StringIO(data)


def save_file(fname, data, use_sign=True, signer=gSigner):
    """ Save file check signature """
    if isinstance(data, io.StringIO):
        data = data.read()
    n = data.find('#sign')
    if n > 0:
        data = data[0:n]
    if use_sign:
        data += sign(data, signer) + '\n'
    io.open(fname, 'w', encoding='UTF-8').write(data)
    return


def load_voters(fname):
    try:
        voters = {s['studNr']: s for s in csv.DictReader(load_file(fname), delimiter=';')}
        return voters
    except Exception as e:
        return {}


def load_candidates(fname):
    try:
        candidates = {s['mdwId']: s for s in csv.DictReader(load_file(fname), delimiter=';')}
        return candidates
    except Exception as e:
        return {}


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
    try:
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
