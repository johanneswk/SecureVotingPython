# SecureVotingPython

###### _Work in progress_

This program lets voters defined in `voters.csv` vote on candidates defined in `candidates.csv`. 

To start an election the command `create` needs to be used. All the eligible voters can vote using the `vote` command.
If the results of the election can be obtained the command `results` needs to be used. 
The `recount.file` stores votes however, it needs to be cleared every new election by using the `delete` command.
This file should only be used in case the programme crashed or if a recount is requested 
and never used in different election.

## Required to run:
- Private key
- candidates.csv
- voters.csv

## Commands:
- `create`
  - Creates a new election round. Without this command there cannot be voted. This will delete the `vote.state` file,
    but will keep the anonymized `recount.file` file for recountings.
- `vote`
  - Allows an eligible voter to vote using the `-p` (voterID) and `-c` (candidateID) commands. 
    Results will be stored in encrypted `vote.state` file.
- `results`
  - Takes all the data from the encrypted `vote.state` and saves it as `results.txt`.
  - Sign the result info from inside `results.txt` to `signature.sign`.
  - Creates a file `recount.file`. This stores all the casted votes individually but without voterID info.
  - Deletes `vote.state`, but keeps `recount.file`
  
- `check`
  - Checks if the user has already voted and shows their random number (1-1000) to verify a stored vote.
  Use `-p` (voterID) to check for specific user.
- `delete`
  - Deletes both `vote.state` and `recount.file`. It is important to delete files after an election has closed, 
    otherwise the `recount.file` would become part of the newly created election.

## Example for voting:

`vote -p 923577756 -c FS`

## To do:
- Create / delete / results election by certain user
- Error stats (faulty logins, voted twice etc.)