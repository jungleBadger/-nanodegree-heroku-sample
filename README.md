# App developed to meet Udacity Nanodegree requirements.

- Log analysis system using postgres within a Linux environment

### TECHNOLOGIES:
- Python3
- Vagrant
- VirtualBox
- Postgres

### Setup
1. Install Vagrant And VirtualBox (provided by udacity)
2. Clone this repository

### To Run

Launch Vagrant VM by running `vagrant up`, you can the log in with `vagrant ssh`

To load the data, use the command `psql -d news -f newsdata.sql` (provided by udacity). It will load all database schema

The database includes three tables:
- Authors table
- Articles table
- Log table

To execute the program, run `python3 db.py` from the command line or from your preferred IDE.