#!/usr/bin/env python3

# Gian Zignago
# CMP_SC 4850
# March 18, 2022
# Client program for Project v2

import socket
import pickle
from User import User

PORT = 17832
HOST = '127.0.0.1'

print("My chat room client. Version Two.\n")

userLogged = User("init",False)

while True:

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.connect((HOST, PORT))

        command = input()

        commandArr = command.split() # split input by spaces

        if commandArr[0] == "logout": # logout user

            if len(commandArr) == 1: # verifies correct command usage

                if userLogged and userLogged.logStatus == True: # verify that user is currently logged in
                    msg = commandArr[0] + " " + userLogged.username
                    s.send(bytes(msg,'utf-8'))

                    response = s.recv(1024)
                    response = response.decode('utf-8')

                    print(response) # display logout message
                    s.close # close socket connection

                    break

                else: # user is not currently logged in
                    print("Denied. Please login first.")
                    command = "retry"
                    s.send(bytes(command,'utf-8'))
                    response = s.recv(1024)
                    response = response.decode('utf-8')

            else: # incorrect command usage
                print("Command usage: logout")
                command = "retry"
                s.send(bytes(command,'utf-8'))
                response = s.recv(1024)
                response = response.decode('utf-8')

        elif commandArr[0] == "login": # login user

            if len(commandArr) == 3: # verifies correct command usage

                s.send(bytes(command,'utf-8')) # send login command to server
                response = s.recv(1024) # receive data from server
                result = response[:5]
                result = result.decode('utf-8') # decode header bytes

                if result == "login": # header matches
                    userObj = response[5:]
                    userLogged = pickle.loads(userObj) # de-pickle user
                    print("login confirmed")

                else: # header does not match
                    print(response.decode('utf-8')) # error response
                
            else: # incorrect command usage
                print("Command usage: login [user] [pass]")
                s.send(bytes("retry",'utf-8'))
                response = s.recv(1024)
                response = response.decode('utf-8')

        elif commandArr[0] == "newuser": # register new user

            if len(commandArr) == 3: # verifies correct command usage

                if len(commandArr[1]) < 3 or len(commandArr[1]) > 32: # invalid UserID length
                    print("UserID length must be between 3 and 32 characters.")
                    command = "retry"
                    s.send(bytes(command,'utf-8'))
                    response = s.recv(1024)
                    response = response.decode('utf-8')

                if len(commandArr[2]) < 4 or len(commandArr[2]) > 8: # invalid password length
                    print("Password length must be between 4 and 8 characters.")
                    command = "retry"
                    s.send(bytes(command,'utf-8'))
                    response = s.recv(1024)
                    response = response.decode('utf-8')

                s.send(bytes(command,'utf-8'))
                response = s.recv(1024)
                response = response.decode('utf-8')
                print(response)

            else:
                print("Command usage: newuser [username] [password]")
                command = "retry"
                s.send(bytes(command,'utf-8'))
                response = s.recv(1024)
                response = response.decode('utf-8')

        elif commandArr[0] == "send": # send message as a logged in user

            if userLogged and userLogged.logStatus: # verify that user is currently logged in

                if commandArr[1] == "all" or commandArr[1] == userLogged.username: # send all & send UserID
                    message = command.split(" ", 2) # isolate message to send
                
                else:
                    message = command.split(" ", 1) # isolate message to send

                if len(message) == 2 and message[0] == "send": # verifies correct command usage

                    if len(message[1]) > 256 or len(message[1]) == '': # invalid length mmessage
                        print("Message size must be between 1 and 256 characters.")
                        command = "retry"
                        s.send(bytes(command,'utf-8'))
                        response = s.recv(1024)
                        response = response.decode('utf-8')

                    message.insert(1,userLogged.username) # add username to message for server
                    send = "" # send variable holds the string to be sent

                    for i in message:
                        send += i + " " # append sections to send message

                    s.send(bytes(send,'utf-8'))
                    response = s.recv(1024)
                    response = response.decode('utf-8')

                    print(response)

                else: # incorrect command usage
                    print("Command usage: send [message]")
                    command = "retry"
                    s.send(bytes(command,'utf-8'))
                    response = s.recv(1024)
                    response = response.decode('utf-8')

            else: # user is not logged in
                print("Action requires user to be logged in.")
                command = "retry"
                s.send(bytes(command,'utf-8'))
                response = s.recv(1024)
                response = response.decode('utf-8')


        elif commandArr[0] == "who":
            if len(commandArr) == 1:
                s.send(bytes(command,'utf-8'))
                response = s.recv(1024)
                response = response.decode('utf-8')

                print(response)
                
            else: # user has input text after command
                print("Command usage: who")
                command = "retry"
                s.send(bytes(command,'utf-8'))
                response = s.recv(1024)
                response = response.decode('utf-8')

        else: # the user has entered an invalid command

            print("Unknown command. Try one of the following inputs:")

            if userLogged.logStatus: # if the user is already logged in
                print(" - send [message]\n - send all [message]\n - send [UserID] [message]\n - who\n - logout")

            elif not userLogged.logStatus: # if the user is not logged in
                print(" - login [username] [password]\n - newuser [username] [password]")

            command = "retry"
            s.send(bytes(command,'utf-8'))
            response = s.recv(1024)
            response = response.decode('utf-8')