#Insert Customer methods here

import sqlite3
import math
import time

basket = None #a list containing tuples of (pid, sid, qty). sid is the store that the product came from

def customer_main(connection, cursor, cid):
    #A function that is called when a customer is logged in. Returns when the customer is logged out.
    global basket
    basket = list() # initialize empty basket
    
    logged_in = True
    while(logged_in):
        print("Current Basket: " + str(basket))
        print ("1. Search for products")
        print ("2. Place an order")
        print ("3. List orders")
        print ("Select an option or enter 'q' to log out.")
        choice = input()
        if choice == "q":
            logged_in = False
        elif choice == "1":
            search(connection, cursor, cid)
        elif choice == "2":
            place_order(connection, cursor, cid)
        elif choice == "3":
            list_order(connection, cursor, cid)
        else:
            print ("Invalid input. Try again.")
    
    return

def search(connection, cursor, cid):
    '''
    Search for products. The customer should be able to enter one or more keyword and the system should retrieve every product that match at least one of the keywords. 
    A product in a store matches a keyword if the keyword appears in the product name. Order the result based on the number of keyword matches with the product name 
    and the store name in a descending order (with the product that has the largest number of matches listed first). For each matching product, list the product id, 
    name, unit, the number of stores that carry it, the number of stores that have it in stock, the minimum price among the stores that carry it, the minimum price 
    among the stores that have the product in stock, and the number of orders within the past 7 days. If there are more than 5 matching products, only 5 would be 
    shown and the user would be given an option to see more but again 5 at a time. The user should be able to select a product and see more detail about the product 
    including the product id, name, unit, category and a listing of all stores that carry the product with their prices, quantities in stock and the number of orders 
    within the past 7 days. If a product is carried by more than one store, the result should be ordered as follows: (1) the stores that have the product in stock will 
    be listed before those that don't; (2) the stores in each case will be sorted based on the store price (from lowest to highest). The user should be able to select a 
    product from a store and add it to his/her basket. The default quantity should be set to 1, but the user should be able to change the quantity. The basket is deleted 
    after the customer logs out or places an order.
    '''
    
    print ("Enter keywords:")
    searchTerms = input().split()
    
    #Make a list for each term containing products that have the keyword in the product name
    #Store the list into a bigger list called listOfMatches
    listOfMatches = list()
    for term in searchTerms:
        query = "SELECT pid FROM products WHERE name LIKE '%"+term.strip()+"%';"
        cursor.execute(query)
        listOfMatches.append(cursor.fetchall())  
    
    #Count the products for each matching term
    productCount = dict()
    for termList in listOfMatches:
        for pid in termList:
            if(pid in productCount.keys()):
                productCount[pid] += 1
            else:
                productCount[pid] = 1
    
    #Order it based on products
    sortedProducts = sorted(productCount, key=lambda pid: productCount[pid], reverse=True)
    
    #Find the product's data for each product. List 5 at once.
    active = True
    pageNumber = 1
    while(active):
        indexNumber = 0
        print("Num\tPID\tName\tUnit\t# of s carries \t# of s in stock\tMin price\tMin price in stock\tOrders in past week")
        for i in range((pageNumber-1)*5,min((pageNumber*5)-1, len(sortedProducts))):
            
            indexNumber += 1
            
            #First query gets pid, name, unit, number of stores that carry it, and minimum price of stores that carry it,
            query = '''SELECT products.pid, products.name, products.unit, count(carries.sid), min(carries.uprice)
            FROM products left outer join carries using (pid)
            WHERE products.pid = :pid
            GROUP BY products.pid, products.name, products.unit;
            '''
            cursor.execute(query, {"pid": sortedProducts[i][0]})
            firstQuery = cursor.fetchone()
        
            #Second query gets number of stores that carry have it in stock, and minimum price of stores that have it in stock
            query = '''SELECT count(carries.sid), min(carries.uprice)
            FROM products left outer join carries using (pid)
            WHERE products.pid = :pid
            AND qty > 0
            GROUP BY products.pid;
            '''
            cursor.execute(query, {"pid": sortedProducts[i][0]})
            secondQuery = cursor.fetchone()
        
            #Third query gets number or orders for the product
            query = '''SELECT count(DISTINCT orders.oid)
            FROM orders, olines
            WHERE orders.oid = olines.oid
            AND olines.pid = :pid
            AND date(odate, '+7 day') >= date('now');
            '''
            cursor.execute(query, {"pid": sortedProducts[i][0]})
            thirdQuery = cursor.fetchone()
            
            print (str(indexNumber) + ".\t" + str(firstQuery[0]) + "\t" + str(firstQuery[1]) + "\t" + str(firstQuery[2]) + "\t" + str(firstQuery[3]) + "\t" + str(secondQuery[0]) + "\t" + str(firstQuery[4]) + "\t" + str(secondQuery[1]) + "\t" + str(thirdQuery[0]))
        
        print ("5. Previous Page 6. Next Page 7. Return to menu")
        
        #Choice branch
        undecided = True
        while undecided:
            try:
                numChoice = int(input())
                undecided = False
                if(numChoice > 0 and numChoice < 5): #Get detailed description of an item
                    if add_to_basket(connection, cursor, cid, sortedProducts[((pageNumber - 1)*5) + (numChoice - 1)][0]): #Show pid details and add to basket
                        print ("Product added!")
                    else:
                        print ("Cancelled")
                    
                elif(numChoice == 5): #Previous page
                    if(pageNumber > 1):
                        pageNumber -= 1
                elif(numChoice == 6): #Next page
                    if(pageNumber < int(math.ceil(len(sortedProducts)/5))):
                        pageNumber += 1
                elif(numChoice == 7): #Go back to menu
                    active = False
                else:
                    print ("Invalid input. Try again.")
                    undecided = True
            except ValueError:
                print ("Invalid input. Try again.")
                
    return
    
#Helper function for search
def add_to_basket(connection, cursor, cid, pid):
    #Shows detailed description of pid and the stores that it can be bought at. If prompted, the customer can choose to add the item to his basket and its quantity.
    global basket
    #First query gets product id, name, unit, and category
    query = '''SELECT pid, name, unit, cat
    FROM products
    WHERE pid = :pid;
    '''
    cursor.execute(query, {"pid": pid})
    firstQuery = cursor.fetchone()
    
    #Second query gets the stores that carry that product and does have stock
    query = '''SELECT stores.sid, stores.name, carries.uprice, carries.qty
    FROM stores, carries
    WHERE stores.sid = carries.sid
    AND carries.pid = :pid
    AND carries.qty > 0;
    '''
    cursor.execute(query, {"pid": pid})
    secondQuery = cursor.fetchall()    
    
    #Third query gets the stores that carry the product and does not have stock
    query = '''SELECT stores.sid, stores.name, carries.uprice, carries.qty
    FROM stores, carries
    WHERE stores.sid = carries.sid
    AND carries.pid = :pid
    AND carries.qty = 0;
    '''
    cursor.execute(query, {"pid": pid})
    thirdQuery = cursor.fetchall()     
    
    #Fourth query gets the orders that include this product within the last 7 days
    query = '''SELECT count(DISTINCT orders.oid)
    FROM orders, olines
    WHERE orders.oid = olines.oid
    AND olines.pid = :pid
    AND date(odate, '+7 day') >= date('now');
    '''
    cursor.execute(query, {"pid": pid})
    fourthQuery = cursor.fetchone()
    
    sorted(secondQuery, key=lambda store: store[2])
    sorted(thirdQuery, key=lambda store: store[2])
    sortedStores = secondQuery + thirdQuery
    
    #Print everything needed; pid, name, unit, cat, and orders first
    print ("Product Id: " + str(firstQuery[0]) + ", Name: " + str(firstQuery[1]) + ", Unit: " + str(firstQuery[2]) + ", Category: " + str(firstQuery[3]) + ", Orders in past week:" + str(fourthQuery[0]))
    #Print all the stores that carry this product, sorted, and indexed for future decision making.
    print ("Index\tSid\tName\tPrice\tQuantity")
    for i in range(len(sortedStores)):
        print (str(i) + ".\t" + str(sortedStores[i][0]) + "\t" + str(sortedStores[i][1]) + "\t" + str(sortedStores[i][2]) + "\t" + str(sortedStores[i][3]))
    active = True
    while(active):
        print ("Select a store by index to add the product to your basket. To go back, enter 'q'.")
        choice = input()
        if choice == 'q':
            active = False
        else:
            try:
                choice = int(choice)
                if choice >= 0 and choice < len(sortedStores):
                    quantity = int(input("Enter quantity: "))
                    if quantity <= int(sortedStores[choice][3]):
                        basket.append((pid, sortedStores[choice][0], quantity)) #Store (pid, sid, qty) in basket
                        return True                                          
                    else:
                        print ("Incorrect input. Try again.")
                else:
                    print ("Incorrect input. Try again.")
            except ValueError:
                print ("Incorrect input. Try again.")
    
    return False

#Place_Order function
def place_order(connection, cursor, cid):
    global basket
    # Ask the customer for item and qty to add into the basket, check the qty to ensure its enough
    
    # query to get for qty
    
    store_carries = list()
    for k in range(len(basket)):
        cursor.execute('SELECT qty FROM carries c WHERE c.pid = :pid AND c.sid = :sid ;', {"pid": basket[k][0], "sid": basket[k][1]})
        store_carries.append(cursor.fetchone()) 
    
    # Before place the order, check again for qty
    # if qty is not met, ask if they want to change qty or delete
    firstTime = True
    print(basket)
    print(store_carries)
    for i in basket:
        for j in store_carries:
            print("I'm doing the thing" + str(i) + str(j))
            if i[2] > j[0]:
                delete = input('Do you want to change the qty[c] or delete[d]: ')
                if delete == 'd':
                    basket.remove[i]
                elif delete == 'c':
                    change = input('What is your new qty: ')
                    i[2] = change
                    
            
            oid = create_oid(connection, cursor)
            odate = time.strftime("%Y-%m-%d %H:%M:%S")
            address_query = cursor.execute('SELECT c.address FROM customers c WHERE c.cid = cid', {"cid": cid})
            data = (oid, cid, odate, address_query)
            sid = i[1]
            pid = i[0]
            qty = i[2]
	    info = {"sid":sid, "pid":pid}
            cursor.execute('SELECT carries.uprice FROM carries WHERE sid = :sid AND pid = :pid;', info)
	    uprice = cursor.fetchone()
            oline_data = (oid, sid, pid, qty, uprice) 
            if (firstTime):
                firstTime = False
                cursor.execute('INSERT INTO order VALUES (?,?,?,?);', data)
            cursor.execute('INSERT INTO olines VALUES (?,?,?,?,?);', oline_data)
                
    # if query_qty is not <= qty prompt the delete
    # then placed the order with an unique oid
    # use def creat_oid()
    print ("Order created!")
	
    connection.commit()
    return

#Create an Unique Order Number
def create_oid(connection, cursor):
    # Find last order number from table and add 1, if there are any preious number, create new one
    # Format: 5-digits, start with 10000
    
    cursor.execute("SELECT max(oid) FROM orders;")
    oid = (cursor.fetchall()) + 1
    if oid == 1:
        oid = 10001
    return oid


def list_order(connection, cursor, cid):
    ''' 
    List orders. The customer should be able to see all his/her orders; 
    the listing should include for each order, the order id, order date, the number of products ordered and the total price; 
    the orders should be listed in a sorted order with more recent orders listed first. 
    If there are more than 5 orders, only 5 would be shown and the user would be given an option to see more but again 5 at a time. 
    The user should be able to select an order and see more detail of the order including delivery information such as tracking number, 
    pick up and drop off times, the address to be delivered, and a listing of the products in the order, 
    which will include for each product the store id, the store name, the product id, the product name, quantity, unit and unit price.
    '''
    # Listing Orders - Order by Most recent (Descending order in oid)
    
    query = '''SELECT oid
    FROM orders
    WHERE cid = :cid
    ORDER BY oid DESC;
    '''
    cursor.execute(query, {"cid": cid})
    # orderList will contain all the oid with the same 
    orderList = cursor.fetchall()
    
    # No order is placed by the customer
    if len(orderList) == 0:
        print ("There is no order placed. Returning to main menu.")
        return
    
    # List the orders, 5 at a time
    # Format: Order Id, Order Date, Number of product ordered, Total Price
    
    active = True
    pageNumber = 1
    while(active):
        indexNumber = 0
        print ("Index\tOrder ID\tOrder Date\tNumber of Product\tTotal Price")
        for i in range((pageNumber-1)*5,min((pageNumber*5)-1, len(orderList))):
            indexNumber += 1
            
            # First query gets the Order Number and Order date
            query = '''SELECT oid, odate
            FROM orders
            WHERE oid = :oid;
            '''
            cursor.execute(query, {"oid": orderList[i][0]})
            firstQuery = cursor.fetchone()
            
            # Second query gets the Number of Product and Total Price
            query = '''SELECT sum(qty), sum(qty * uprice)
            FROM olines
            WHERE oid = :oid;
            '''
            cursor.execute(query, {"oid": orderList[i][0]})
            secondQuery = cursor.fetchone()
            
            print (str(indexNumber) + ".\t" + str(firstQuery[0]) + "\t\t" + str(firstQuery[1]) + "\t" + str(secondQuery[0]) + "\t\t\t" + str(secondQuery[1]))
        
        # Display options based on page number
        # pageStat: Indicate page based on following condition
        if pageNumber == 1 and ((len(orderList)//5) <= 1):
            print ("7. Return to Menu")
            pageStat = 4
        elif pageNumber == 1:
            print ("6. Next Page 7. Return to Menu")
            pageStat = 1
        elif pageNumber == len(orderList)//5:
            print ("5. Previous Page 7. Return to Menu")
            pageStat = 3
        else:
            print ("5. Previous Page 6. Next Page 7. Return to menu")
            pageStat = 2
        
        # Chioce Branch
        undecided = True
        while undecided:
            try:
                numChoice = int(input())
                undecided = False
                if(numChoice > 0 and numChoice < 5): #Get detailed description of an order
                    list_detail(connection, cursor, cid, orderList[((pageNumber - 1)*5) + (numChoice - 1)][0])
                
                elif(numChoice == 5 and pageStat != 1 and pageStat != 4): # Previous page
                    pageNumber -= 1
                elif(numChoice == 6 and pageStat != 3 and pageStat != 4): # Next page
                    pageNumber += 1
                elif(numChoice == 7): # Go back to menu
                    active = False
                else:
                    print ("Invalid input. Try again.")
                    undecided = True
            except ValueError:
                print ("Invalid input. Try again.")
                                    
    return
    
    # Helper function for Listing
def list_detail(connection, cursor, cid, oid):
        # Displays Delivery Infromation: Tracking Number, Pick Up Time, and Drop Off Time
        # Also, A list of products in the Order, with its: Store ID, Product ID, Quantity, Unit, and Unit Price
        
        # Delivery Information
        query = '''SELECT trackingno, pickUpTime, dropOffTime
        FROM deliveries
        WHERE oid = :oid;
        '''
        cursor.execute(query, {"oid": oid})
        deliQuery = cursor.fetchone()
        
        print ("Order Number\tTracking Number\tPick Up Time\t Drop Off Time")
        print (str(oid) + "\t\t" + str(deliQuery[0]) + "\t" + str(deliQuery[1]) + "\t" + str(deliQuery[2]))
        
        # Product Information
        print ("Product\tStore ID\tProduct ID\t Quantity\tUnit\tUnit Price")
        
        # Count the Number of Product in the Order
        cursor.execute('SELECT count(pid) FROM olines WHERE oid = :oid', {"oid": oid})
        count = cursor.fetchone()
        
        
        # Fetch the products into a List
        cursor.execute('SELECT pid FROM olines WHERE oid = :oid', {"oid": oid})
        prodList = cursor.fetchall()
        
        # Create a list with all the pid in the order
        i = 0
        for i in range(int(count[0])):
            query = '''SELECT products.name, olines.sid, olines.pid, olines.qty, products.unit, olines.uprice
            FROM products, olines
            WHERE products.pid = :pid AND products.pid = olines.pid;
            '''
            cursor.execute(query, {"pid": prodList[i][0]})
            prodQuery = cursor.fetchone()
            
            print (str(prodQuery[0]) + "\t" + str(prodQuery[1]) + "\t"+ str(prodQuery[2]) + "\t" + str(prodQuery[3]) + "\t" + str(prodQuery[4]) + "\t"+ str(prodQuery[5]))
            
            i += 1   
        
        return
