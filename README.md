# database-project-p3

This branch contains login, logout, register + authentication, view public info and init.py of all the cases when not logged in

Here is how to set up the server (I use mac so it might be a little different)

Things to download: 
- python Flask 
- virtual environment
https://phoenixnap.com/kb/install-flask (I followed this link)

Step-by-step setup:
1. Make a directory for the project
2. Create a folder inside that directory with all the html files
3. Start phpMyAdmin
4. Set up virtual environment. Name of my virtual environment is venv so
5. On your terminal, do the following: 
  - cd to the directory of the project
  - . <name of your virtual env>/bin/activate
  Mine is 'env' so I would type . venv/bin/activate
  - export FLASK_APP=init.py
  - flask run
6. Run the http link on your browser 
