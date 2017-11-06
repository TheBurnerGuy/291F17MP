#Temporary Login File

import sqlite3
import sys
import time
import hashlib
import Customer
import Agent
import getpass

connection = None
cursor = None
lid = None #Login ID - general case between customer and agent

def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return

def customer_login():
    #sets lid to cid upon successful login
    #returns true or false based on success or failure of logging in
    global connection, cursor, lid
    
    print "Enter your customer id:"
    cid = input()
    print "Enter your password:"
    pwd = getpass.getpass()
    
    cursor.execute("SELECT * FROM customers WHERE cid = :cid AND pwd = :pwd;",{"cid": cid, "pwd": pwd})
    if(len(cursor.fetchall()) == 1):
        print "Login successful!"
        lid = cid
        return True
    else:
        print "Login failed."
        return False
    
def agent_login():
    #sets lid to aid upon successful login
    #returns true or false based on success or failure of logging in
    global connection, cursor, lid
    
    print "Enter your agent id:"
    aid = input()
    print "Enter your password:"
    pwd = getpass.getpass()
    
    cursor.execute("SELECT * FROM agents WHERE aid = :aid AND pwd = :pwd;",{"aid": aid, "pwd": pwd})
    if(len(cursor.fetchall()) == 1):
        print "Login successful!"
        lid = aid
        return True
    else:
        print "Login failed. Invalid id or password."
        return False

def customer_register():
    #Implementation of registering customer into database
    global connection, cursor, lid
    
    print "Enter your name:"
    name = input()
    print "Enter your address:"
    address = input()
    
    while(True):
        print "Enter an unique customer id:"
        cid = input()
        cursor.execute("SELECT * FROM customers WHERE cid = :cid;",{"cid": cid})
        if(len(cursor.fetchall()) == 0):
            break
        else:
            print("{0} is not a unique customer id.".format(cid))
    
    print "Enter a password:"
    pwd = getpass.getpass()
    
    cursor.execute("INSERT INTO customers VALUES (:cid, :name, :address, :pwd);", {"cid": cid, "name": name, "address": address, "pwd": pwd})
    connection.commit()
    print "Registration successful!"
    
    lid = cid
    
    return

def customer():
    #Implementation of customer class
    global lid
    Customer.customer_main(connection, cursor, lid)
    return
    
def agent():
    #Insert implementation of agent
    global lid
    Agent.agent_main(connection, cursor, lid)
    return

def main(path):
    global connection, cursor, lid

    connect(path) #path = ./register.db
    #connection.create_function('GPA', 1, GPA)

    #tables should be defined already in register.db
    #data should be inserted already in register.db
    
    #Login implementation
    active = True
    while(active):
        try:
            print "1. Customer Login\n2. Agent Login\n3. Customer Register\n4. Exit"
            answer = int(input())
            if(answer == 1):
                if(customer_login()):
                    customer()
            elif(answer == 2):
                if(agent_login()):
                    agent()
            elif(answer == 3):
                customer_register()
                customer()
            elif(answer == 4):
                active = False
            else:
                print "Invalid input. Try again."
        except ValueError:
            #Taken from https://stackoverflow.com/questions/8075877/converting-string-to-int-using-try-except-in-python
            print 'Invalid input. Try again.'

    connection.commit()
    connection.close()
    return

if __name__ == "__main__":
    if len(sys.argv) > 1: # Database name is given
        path = str(sys.argv[1]) # Use second argument
    else:
        path = "./register.db"
    main(path)
