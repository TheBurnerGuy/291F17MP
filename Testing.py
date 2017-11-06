import sqlite3
import time
import hashlib
import sys

connection = None
cursor = None

def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA forteign_keys=ON; ')
    connection.commit()
    return

def define_tables():
    global connection, cursor

    tableQuery ='''drop table if exists deliveries;
drop table if exists olines;
drop table if exists orders;
drop table if exists customers;
drop table if exists carries;
drop table if exists products;
drop table if exists categories;
drop table if exists stores;
drop table if exists agents;

create table agents (
  aid           text,
  name          text,
  pwd       	text,
  primary key (aid));
create table stores (
  sid		int,
  name		text,
  phone		text,
  address	text,
  primary key (sid));
create table categories (
  cat           char(3),
  name          text,
  primary key (cat));
create table products (
  pid		char(6),
  name		text,
  unit		text,
  cat		char(3),
  primary key (pid),
  foreign key (cat) references categories);
create table carries (
  sid		int,
  pid		char(6),
  qty		int,
  uprice	real,
  primary key (sid,pid),	
  foreign key (sid) references stores,
  foreign key (pid) references products);
create table customers (
  cid		text,
  name		text,
  address	text,
  pwd		text,
  primary key (cid));
create table orders (
  oid		int,
  cid		text,
  odate		date,
  address	text,
  primary key (oid),
  foreign key (cid) references customers);
create table olines (
  oid		int,
  sid		int,
  pid		char(6),
  qty		int,
  uprice	real,
  primary key (oid,sid,pid),
  foreign key (oid) references orders,
  foreign key (sid) references stores,
  foreign key (pid) references products);
create table deliveries (
  trackingNo	int,
  oid		int,
  pickUpTime	date,
  dropOffTime	date,
  primary key (trackingNo,oid),
  foreign key (oid) references orders);
    '''

    cursor.executescript(tableQuery)
    connection.commit()

    return

def insert_data():
    global connection, cursor
    
    #Follow guidelines at https://eclass.srv.ualberta.ca/pluginfile.php/3632951/mod_page/content/24/prj-tables.sql    
    
    insert_agents = '''
                        INSERT INTO agents(aid, name, pwd) VALUES
                            ('1', 'Henry', 'water'),
                            ('2', 'Jordan', 'jodan'),
                            ('3', 'Calvin', 'kelvin');
                     '''

    insert_stores =  '''
                        INSERT INTO stores(sid, name, phone, address) VALUES
                                (1, 'Walmart', '7809119111', 'New York'),
                                (2, 'Superstore', '7808118111', 'Old York'),
                                (3, 'EB Games', '7807117111', 'Newfoundland'),
                                (4, 'Shoppers Drug Mart', '7806116111', 'Oldfoundland'),
                                (5, 'Sobeys', '7805115111', 'New Town'),
                                (6, 'Sears', '7804114111', 'Old Town');
                       '''
                       
    insert_categories =  '''
                        INSERT INTO categories(cat, name) VALUES
                                ("mea", "Meat and seafood"),
                                ("fav", "Fruit and vegetables"),
                                ("frz", "Frozen"),
                                ("gam", "Games"),
                                ("toy", "Toys"),
                                ("mis", "Miscellaneous");
                       '''
                       
    insert_products =  '''
                        INSERT INTO products(pid, name, unit, cat) VALUES
                                ("p1", "Chicken Breast", "kg", "mea"),
                                ("p2", "Chicken Leg", "kg", "mea"),
                                ("p3", "Beef", "kg", "mea"),
                                ("p4", "Pork", "kg", "mea"),
                                ("p5", "Orange", "kg", "fav"),
                                ("p6", "Apple", "kg", "fav"),
                                ("p7", "Banana", "kg", "fav"),
                                ("p8", "Dark Souls 1", "kg", "gam"),
                                ("p9", "Dark Souls 2", "kg", "gam"),
                                ("p10", "Demon Souls", "kg", "gam"),
                                ("p11", "Minecraft Pickaxe", "kg", "toy"),
                                ("p12", "Chicken Thigh", "kg", "mea");
                       '''
                       
    insert_carries =  '''
                        INSERT INTO carries(sid, pid, qty, uprice) VALUES
                                (1, "p1", 10, 5.99),
                                (1, "p2", 10, 4.99),
                                (1, "p12", 10, 7.99),
                                (2, "p1", 0, 4.99),
                                (2, "p2", 10, 5.99),
                                (2, "p12", 10, 6.99),
                                (5, "p1", 5, 5.99),
                                (5, "p2", 0, 4.50),
                                (5, "p12", 0, 7.50);
                       '''
                       
    insert_customers =  '''
                        INSERT INTO customers(cid, name, address, pwd) VALUES
                                ('101', 'Henry', 'Somewhere', 'water'),
                                ('102', 'Calvin', 'Somewhere', 'jodan'),
                                ('103', 'Jordan', 'Somewhere', 'kelvin');
                       '''
                       
    insert_orders =  '''
                        INSERT INTO orders(oid, cid, odate, address) VALUES
                                (10000, '101', datetime('now'), 'Somewhere'),
                                (10001, '101', datetime('now'), 'Somewhere'),
                                (10002, '102', datetime('now', '-14 days'), 'Somewhere');
                       '''
                       
    insert_olines =  '''
                        INSERT INTO students(student_id, name) VALUES
                                (1509106, 'Saeed'),
                                (1409106, 'Alex'),
                                (1609106, 'Mike');
                       '''
                       
    insert_deliveries =  '''
                        INSERT INTO student(student_id, name) VALUES
                                (1509106, 'Saeed'),
                                (1409106, 'Alex'),
                                (1609106, 'Mike');
                       '''

    cursor.execute(insert_agents)
    cursor.execute(insert_stores)
    cursor.execute(insert_categories)
    cursor.execute(insert_products)
    cursor.execute(insert_carries)
    cursor.execute(insert_customers)
    cursor.execute(insert_orders)
    
    #Insert other cursor.execute statements when finished
    
    connection.commit()
    return

# def enroll_assign_grades():
#     global connection, cursor
# 
#     cursor.execute('SELECT * FROM course;')
#     all_courses = cursor.fetchall()
# 
#     cursor.execute('SELECT * FROM student;')
#     all_students = cursor.fetchall()
# 
#     Grades = ['A', 'A', 'C', 'B', 'C', 'B', 'F', 'C', 'A']
#     i=0
# 
#     for every_course in all_courses:
#         for every_student in all_students:
#             enroll(every_student[0], every_course[0])
# 
#             data = (Grades[i], every_student[0], every_course[0])
#             cursor.execute('UPDATE enroll SET grade=? where student_id=? and course_id=?;', data)
#             i += 1
# 
#     return
# 
# def enroll(student_id, course_id):
#     global connection, cursor
# 
#     current_date = time.strftime("%Y-%m-%d %H:%M:%S")
# 
#     crs_id = (course_id,)
#     cursor.execute('SELECT seats_available FROM course WHERE course_id=?;', crs_id)
#     seats_available = cursor.fetchone()
# 
#     if seats_available > 0:
#         data = (student_id, course_id, current_date)
#         cursor.execute('INSERT INTO enroll (student_id, course_id, enroll_date) VALUES (?,?,?);', data) 
#         cursor.execute('UPDATE course SET seats_available = seats_available - 1 where course_id=?;', crs_id)
#     
#     connection.commit()
#     return
# 
# def drop(student_id, course_id):
#     global connection, cursor
#     
#     ### YOUR PART ###
#     # Drop the course for the student and update the seats_avialable column
# 
#     connection.commit()
#     return
# 
# def GPA(grade):
#     global connection, cursor
# 
#     ### YOUR PART ###
#     # Map the grade to a numerical value
# 
#     return 0

def main(path):
    global connection, cursor
    
    print "Creating a database at: " + path
    connect(path)

    define_tables()
    insert_data()

    connection.commit()
    connection.close()
    print "Done"
    return

if __name__ == "__main__":
    if len(sys.argv) > 1: # Database name is given
        path = str(sys.argv[1]) # Use second argument
    else:
        path = "./register.db"
    main(path)
