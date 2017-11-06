#Insert Agent methods here
import numpy.random as rnd
import datetime

def agent_main(connection, cursor, aid):
    #A function that is called when an agent is logged in. Returns when the agent is logged out.
    
    logged_in = True
    while(logged_in):
        print ("1. Set up a delivery")
        print ("2. Update a delivery")
        print ("3. Add to stock")
        print ("Select an option or enter 'q' to log out.")
        choice = input()
        if choice == "q":
            logged_in = False
        elif choice == "1":
            setup(connection, cursor)
        elif choice == "2":
            pass #Insert update a delivery function here
        elif choice == "3":
            pass #Insert add to stock function here
        else:
            print ("Invalid input. Try again.")
    
    return

def setup(connection, cursor):
    #Algorithm: Show a list of orders. If an agent choose a order, ask them for the pickUpTime. After choosing an order, the agent is allowed to choose another order to input 'q' to finalize the delivery.
    #Generate a unique trackingNo
    # Find last order number from table and add 1, if there are any preious number, create new one
    # Format: 5-digits, start with 10000
    
    cursor.execute("SELECT max(trackingno) FROM deliveries;")
    trackingno = cursor.fetchone()[0] + 1
    if trackingno == 1:
        trackingno = 10001
    
    #List orders - orders that aren't already in a delivery
    query = '''SELECT oid
    FROM orders
    '''
    cursor.execute(query)
    orderList = cursor.fetchall()
    if len(orderList) == 0:
        print ("No orders to setup. Returning to main menu.")
        return
    
    print ("Index\tOrder Id\tCustomer\tOrder date\tAddress")
    #For each order in orderList, print its details and give it an index
    for i in range(len(orderList)):
        query = '''SELECT oid, cid, odate, address
        FROM orders
        WHERE oid = :oid
        '''
        cursor.execute(query, {"oid": orderList[i][0]})
        result = cursor.fetchone()
        print (str(i) + ".\t" + str(result[0]) + "\t" + str(result[1]) + "\t" + str(result[2]) + "\t" + str(result[3]) )   
    
    #Pick a order
    active = True
    while active:
        print ("Select an order using index to add to the delivery. Input 'q' to finish setup for this delivery.")
        choice = input()
        if choice == 'q':
            active = False
        else:
            try:
                choice = int(choice)
                if choice >= 0 and choice < len(orderList):
                    #Change pick up time (or not)
                    if(input("Set up pickup time? (Enter 'y' for yes)") == 'y'):
                        pickUpTime = input("Enter pick-up time: (e.g. year-month-day hour:minute:second)")
                        #Taken from https://stackoverflow.com/questions/12672629/python-how-to-convert-string-into-datetime
                        pickUpTime = datetime.datetime.strptime(pickUpTime, "%Y-%m-%d %H:%M:%S")
                        query = '''INSERT INTO deliveries VALUES (:trackingno, :oid, :pickUpTime, null);'''
                        cursor.execute(query, {"trackingno": trackingno, "oid": orderList[choice][0], "pickUpTime": pickUpTime})
                    else:
                        #Insert without pickup time
                        query = '''INSERT INTO deliveries VALUES (:trackingno, :oid, null, null);'''
                        cursor.execute(query, {"trackingno": trackingno, "oid": orderList[choice][0]})
                    connection.commit()
                    print ("Order added to delivery!")
            except ValueError:
                print ("Invalid input. Try again.")
    return

def update(connection, cursor):
    #get a tracking number
    trackingNo = None
    try:
        trackingNo = int(input("Enter tracking number: "))
        query = '''SELECT * FROM deliveries WHERE trackingNo = :trackingNo
        '''
        cursor.execute(query, {"trackingNo": trackingNo})
    except ValueError:
        print ("Invalid Input. Returning to menu.")
        return
    
    #show pickup time
    delivery = cursor.fetchone()
    print ("Current pick up time: " + str(delivery[2]))
    print ("Current drop off time: " + str(delivery[3]))
    
    #allow agent to change pickup /drop off time or remove order
    active = True
    while(active):
        active = False
        decision = input("Enter '1' or")
    return

def add_to_stock(connection,cursor):
    #unfinished
    return