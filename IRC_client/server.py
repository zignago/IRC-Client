#!/usr/bin/env python3

# Gian Zignago
# CMP_SC 4850
# March 18, 2022
# Server program for Project v2

import socket
import pickle
from User import User
import csv

PORT = 17832
HOST = '127.0.0.1'

def checkFunction(connection, data):

    data = data.decode('utf-8') # decode data
    command = data.split() # split string into parts

    if command[0] == "logout": # logout
        updateUserState(command[1], True) # verify user is currently logged in
        result = getUserState(command[1])

        if result: # user is currently logged in
            updateUserState(command[1], False) # change user logged in state to False
            print(command[1] + " logout") # message signifying that the given user has logged out
            connection.send(bytes(command[1] + " left",'utf-8'))

        else: # user is not currently logged in
            err = "Denied. Please login first"

    elif command[0] == "who":
        result = who()
        print(result)
        connection.send(bytes(result,'utf-8'))

    elif command[0] == "login": # login as a registered user
        result = login(connection, command[1], command[2]) # verify login credentials

        if result: # valid login credentials
            updateUserState(command[1], True)
            logged = getUser(command[1]) # get user object
            logged = pickle.dumps(logged) # put user object in pickle
            header = bytes("login",'utf-8') # header string signifying login success
            connection.send(header + logged) # send header and pickle to client

        else: # invalid login credentials
            connection.send(bytes("Denied. Username or password incorrect",'utf-8'))

    elif command[0] == "newuser": # register new user
        result = checkUserExists(command[1]) # check if user already exists

        if result: # user does not exist
            newUser(connection,command[1], command[2]) # register new user using given information

        else: # user already exists
            err = "Denied. User account already exists."
            connection.send(bytes(err,'utf-8'))

    elif command[0] == "send": # send message as a logged in user
        command = data.split(" ", 2) # split command into form (send, uname, msg, content)
        message = command[1] + ": " + command[2]
        print(message)
        connection.send(bytes(message,'utf-8'))

    elif command[0] == "retry": # no user is logged in
        connection.send(bytes("retrying",'utf-8'))


def checkUserExists(user):
    for name in users: # iterate through users arr to see if user exists
        username = name.username
        if username == user:
            return False # user exists
    return True # user does not exits


# Handle a user's login attempt
def login(connection,user,password):

    file = open("users.txt", "r") # open the users.txt file

    reader = csv.reader(file, delimiter=',') # access all users in file via csv decoding

    for row in reader: # for each line in users.txt

        # cleanse username in file to compare
        uname = row[0] # get username entry
        uname = uname[1:] # remove opening parenthesis

        if uname == user: # compare user input with username on record in file

            # cleanse password in file to compare
            passw = row[1] # access password for given user
            passw = passw[:-1] # remove closing parenthesis
            passw = passw[1:] # remove leading space

            if passw == password: #compare user input password with pass in file
                print(uname, "login.")
                return True # login attempt successful

    file.close() # close users.txt file
    return False # login attempt unsuccessful  


# Add a tuple containing a new user+password into users.txt
def newUser(connection,username,passw):

    file = open("users.txt", "a") # open the users.txt file

    entry = "\n(" + username + ", " + passw + ")" # generate tuple in form (uname, pass)
    users.append(User(username, False)) # register new entry to User list

    file.write(entry) # append entry tuple to the bottom of the file
    file.close() # close file

    success = "New user account created. Please login." # user creation successful
    print("New user account created.") # notify new user has been created successfully

    connection.send(bytes(success,'utf-8'))


# Get state of user
def getUserState(user):
    for name in users:
        username = name.username
        if username == user:
            return name.logStatus


# Change state of user
def updateUserState(user, state):
    for name in users:
        username = name.username
        if username == user:
            name.logStatus = state


# Get user object
def getUser(user):
    for name in users:
        username = name.username
        if username == user:
            return name


# Create user object list
def usersInit():
    users = []

    file = open("users.txt", "r") # open users.txt file
    reader = csv.reader(file, delimiter=',') #use csv decoding

    for row in reader: # for registered user in users.txt
        username = row[0]
        username = username[1:] # remove opening parenthesis
        users.append(User(username,False)) # create new users with the usernames in the file

    file.close() # close users.txt file
    return users


# returns list of all currently logged in users
def who():
    logStr = ''
    for name in users:
        print(name.username)
        print(getUserState(name.username))
        if getUserState(name.username):
            logStr += name.username
            print(name)
    return logStr


if __name__ == "__main__":

    print("My chat room server. Version Two.\n")

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.bind((HOST, PORT))
            s.listen()
            connection, addr = s.accept()

            with connection:
                data = connection.recv(1024)
                users = usersInit() # initiale list of registered users
                checkFunction(connection,data) # filter data from client to relevant funtion, if existant
                connection.sendall(data) # send data buffer to client