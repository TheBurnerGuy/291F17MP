#Temporary Login File

import sqlite3
import time
import hashlib
import Customer
import Agent

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

    course_query=   '''
                        CREATE TABLE course (
                                    course_id INTEGER,
                                    title TEXT,
                                    seats_available INTEGER,
                                    PRIMARY KEY (course_id)
                                    );
                    '''

    student_query=  '''
                        CREATE TABLE student (
                                    student_id INTEGER,
                                    name TEXT,
                                    PRIMARY KEY (student_id)
                                    );
                    '''

    enroll_query= '''
                    CREATE TABLE enroll (
                                student_id INTEGER,
                                course_id INTEGER,
                                enroll_date DATE,
                                grade TEXT,
                                PRIMARY KEY (student_id, course_id),
                                FOREIGN KEY(student_id) REFERENCES student(student_id),
                                FOREIGN KEY(course_id) REFERENCES course(course_id)
                                );
                '''

    cursor.execute(course_query)
    cursor.execute(student_query)
    cursor.execute(enroll_query)
    connection.commit()

    return

def insert_data():
    global connection, cursor

    insert_courses = '''
                        INSERT INTO course(course_id, title, seats_available) VALUES
                            (1, 'CMPUT 291', 200),
                            (2, 'CMPUT 391', 100),
                            (3, 'CMPUT 101', 300);
                     '''

    insert_students =  '''
                        INSERT INTO student(student_id, name) VALUES
                                (1509106, 'Saeed'),
                                (1409106, 'Alex'),
                                (1609106, 'Mike');
                       '''

    cursor.execute(insert_courses)
    cursor.execute(insert_students)
    connection.commit()
    return

def main():
    global connection, cursor

    path="./register.db"
    connect(path)
    connection.create_function('GPA', 1, GPA)

    define_tables()
    insert_data()
    


    connection.commit()
    connection.close()
    return

if __name__ == "__main__":
    main()
