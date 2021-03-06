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
            update(connection, cursor)
        elif choice == "3":
            add_to_stock(connection, cursor)
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
                        pickUpTime = input("Enter pick-up time (e.g. year-month-day hour:minute:second): ")
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
    delivery = cursor.fetchall()
    
    undecided = True
    while(undecided):
        print("Index:\tOrder Id\tPick up time\tDrop off time")
        for i in range(len(delivery)):
            print (str(i) +"\t"+ str(delivery[i][1])+ "\t" + str(delivery[i][2]) +"\t"+ str(delivery[i][3]))      
            
        print("Select an order by index or enter 'q' to return to menu")
        try:
            choice = input()
            if(choice == 'q'):
                undecided = False
            elif int(choice) >= 0 and int(choice) < len(delivery):
                #allow agent to change pickup /drop off time or remove order
                oid = delivery[int(choice)][1]
                active = True
                while(active):
                    print("1. Change pick up time")
                    print("2. Change drop off time")
                    print("3. Remove from delivery")
                    decision = input("Select a choice or enter 'q' to go back to order list: ")
                    if decision == "1": #change pickup time
                        changeTime = input("Enter pick-up time (e.g. year-month-day hour:minute:second): ")
                        changeTime = datetime.datetime.strptime(changeTime, "%Y-%m-%d %H:%M:%S")
                        query = '''UPDATE deliveries SET pickUpTime = :changeTime WHERE trackingNo = :trackingNo AND oid = :oid
                        '''
                        cursor.execute(query, {"changeTime": changeTime, "trackingNo": trackingNo, "oid":oid})
                        delivery[int(choice)][2] = changeTime
                        print("Succesfully changed pick up time!")
                    elif decision == "2": #change dropoff time
                        changeTime = input("Enter pick-up time (e.g. year-month-day hour:minute:second): ")
                        changeTime = datetime.datetime.strptime(changeTime, "%Y-%m-%d %H:%M:%S")
                        query = '''UPDATE deliveries SET dropOffTime = :changeTime WHERE trackingNo = :trackingNo AND oid = :oid
                        '''
                        cursor.execute(query, {"changeTime": changeTime, "trackingNo": trackingNo, "oid":oid})
                        delivery[int(choice)][3] = changeTime
                        print("Succesfully changed drop off time!")
                    elif decision == "3": # delete
                        query = '''DELETE FROM deliveries WHERE trackingNo = :trackingNo AND oid = :oid
                        '''
                        cursor.execute(query, {"trackingNo": trackingNo, "oid":oid})
                        connection.commit()
                        delivery.pop(int(choice))
                        print("Succesfully deleted!")
                        active = False
                    elif decision == "q":
                        active = False
                    else:
                        print("Invalid input. Try again.")                
            else:
                print("Incorrect input. Try again.")
        except ValueError:
            print("Incorrect input. Try again.")
    
    connection.commit()
            
    return

def add_to_stock(connection, cursor):
    # An agent should be able to select a product and a store (by giving the product id and the store id) and give the number of products to be added to the stock. The agent should have the option to change the unit price.
    
    pid = None
    sid = None
    
    try:
        pid = str(input("Enter the Product ID: "))
        sid = int(input("Enter the Store ID: "))
        info = {"pid":pid, "sid":sid}
        query = '''SELECT * FROM carries WHERE pid = :pid AND sid = :sid;
        '''
        cursor.execute(query, info)
        
    except:
        print ("Invalid Input. Returning to menu.")
        return
    
    # Display current info
    add = cursor.fetchone()
    print("Current quantity is: " + str(add[2]))
    print("Current unit price is: " + str(add[3]))
    
    active = True
    while(active):
        active = False
        
        # Update quantity
        try:
            qty = int(input("Enter new quantity: "))
            info = {"qty":qty, "pid":pid, "sid":sid}
  
            query = '''UPDATE carries
            SET qty = :qty
            WHERE pid = :pid AND sid = :sid;
            '''
            cursor.execute(query, info)
            print("Quantity Updated")
            
            # Option for update unit price
            
            decision = input("Would you like to change the unit price? (Y/N) ")
            
            if (decision == "Y"):
                uprice = float(input("Enter new unit price: "))
                info = {"uprice":uprice, "pid":pid, "sid":sid}
                query = '''UPDATE carries
                SET uprice = :uprice
                WHERE pid = :pid AND sid = :sid;
                '''
                cursor.execute(query, info)
                print("Unit price Updated")
            else:
                return
            
        except:
            print ("Invalid Input. Returning to menu.")
            return            
    
    return