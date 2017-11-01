#Insert Customer methods here

import sqlite3
import math

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
    
    print "Enter keywords:"
    searchTerms = input().split()
    
    #Make a list for each term containing products that have the keyword in the product name
    #Store the list into a bigger list called listOfMatches
    listOfMatches = list()
    i = 0
    for term in searchTerms:
        cursor.execute("SELECT pid FROM products WHERE name LIKE '%:term%'",{"term": term})
        listOfMatches[i] = cursor.fetchall()
        i += 1
    
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
        print "Num\tPID\tName\tUnit\t# of stores that carry\t# of stores in stock\tMin price for stores\tMin price for stores with stock\tOrders in past week"
        for i in range((pageNumber-1)*5,min((pageNumber*5)-1, len(sortedProducts))):
            
            indexNumber += 1
            
            #First query gets pid, name, unit, number of stores that carry it, and minimum price of stores that carry it,
            query = '''SELECT products.pid, products.name, products.unit, count(carries.sid), min(carries.uprice)
            FROM products left outer join carries using (pid)
            WHERE products.pid = :pid
            GROUP BY products.pid, products.name, products.unit
            '''
            cursor.execute(query, {"pid": sortedProducts[i]})
            firstQuery = cursor.fetchone()
        
            #Second query gets number of stores that carry have it in stock, and minimum price of stores that have it in stock
            query = '''SELECT count(carries.sid), min(carries.uprice)
            FROM products left outer join carries using (pid)
            WHERE products.pid = :pid
            AND qty > 0
            GROUP BY products.pid
            '''
            cursor.execute(query, {"pid": sortedProducts[i]})
            secondQuery = cursor.fetchone()
        
            #Third query gets number or orders for the product
            query = '''SELECT count(DISTINCT orders.oid)
            FROM orders, olines
            WHERE orders.oid = olines.oid
            AND olines.pid = :pid
            AND date(odate, '+7 day') >= date('now')
            '''
            cursor.execute(query, {"pid": sortedProducts[i]})
            thirdQuery = cursor.fetchone()
            
            print str(indexNumber) + ".\t" + firstQuery[0] + "\t" + firstQuery[1] + "\t" + firstQuery[2] + "\t" + firstQuery[3] 
            + "\t" + secondQuery[0] + "\t" + firstQuery[4] + "\t" + secondQuery[1] + "\t" + thirdQuery[0]
        
        print "5. Previous Page 6. Next Page 7. Return to menu"
        
        #Choice branch
        undecided = True
        while undecided:
            try:
                numChoice = int(input())
                undecided = False
                if(numChoice > 0 and numChoice < 5): #Get detailed description of an item
                    show_product_details(connection, cursor, sortedProducts[((pageNumber - 1)*5) + (numChoice - 1)]) #Show pid details
                    undecided2 = True
                    while undecided2:
                        print "1. Add to basket 2. Return to previous screen"
                        try:
                            numChoice2 = int(input())
                            undecided2 = False
                            if(numChoice2 == 1): #Add to basket
                                #add to basket function here
                                placehodler = "help me REEEEEEEEEEEEEE" #TODO add to basket
                            elif(numChoice2 == 2): #Return to menu
                                pass
                            else:
                                print "Invalid input. Try again."
                                undecided2 = True
                        except ValueError:
                            print "Invalid input. Try again."
                elif(numChoice == 5): #Previous page
                    if(pageNumber > 1):
                        pageNumber -= 1
                elif(numChoice == 6): #Next page
                    if(pageNumber < int(math.ceil(len(sortedProducts)/5))):
                        pageNumber += 1
                elif(numChoice == 7): #Go back to menu
                    active = False
                else:
                    print "Invalid input. Try again."
                    undecided = True
            except ValueError:
                print "Invalid input. Try again."
                
    cursor.execute()
    return
    
#Helper function for search
def show_product_details(connection, cursor, pid):
    return

#Place_Order function
def place_order():
    # Create a basket (Array or Dictionary)
    # Ask the customer for item and qty to add into the basket, check the qty to ensure its enough
    # Before place the order, check again for qty
    # if qty is not met, ask if they want to change qty or delete
    # then placed the order with an unique oid
    return

#Create an Unique Order Number
def create_oid(connection, cursor):
    # Find last order number from table and add 1, if there are any preious number, create new one
    # Format: 5-digits, start with 10000
    
    rerurn
