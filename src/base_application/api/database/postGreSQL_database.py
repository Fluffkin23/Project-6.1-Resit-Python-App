import psycopg2
import re

# Establishing the connection
conn = psycopg2.connect(
    database="Quintor", user='postgres', password='password', host='localhost', port='5432'
)


def table_create():
    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    # Creating table as per requirement
    sql_create_association_table = """ CREATE TABLE IF NOT EXISTS Association (
                accountID VARCHAR(35) NOT NULL PRIMARY KEY ,
                name VARCHAR(50) NOT NULL,
                password VARCHAR(256) NOT NULL
            ); """
    # Create Association table
    cursor.execute(sql_create_association_table)

    sql_create_file_table = """ CREATE TABLE IF NOT EXISTS File (
                referenceNumber VARCHAR(16) NOT NULL PRIMARY KEY ,
                statementNumber VARCHAR NOT NULL,
                sequenceDetail VARCHAR NOT NULL,
                availableBalance REAL NOT NULL,
                forwardAvBalance REAL NOT NULL,
                accountID VARCHAR(35) NOT NULL,
                FOREIGN KEY (accountID) REFERENCES Association (AccountID)
            ); """
    # Create File table
    cursor.execute(sql_create_file_table)

    sql_create_category_table = """ CREATE TABLE IF NOT EXISTS Category (
                    categoryID SERIAL PRIMARY KEY,
                    name VARCHAR(32)
                    ); """
    # Create category table
    cursor.execute(sql_create_category_table)

    sql_create_member_table = """ CREATE TABLE IF NOT EXISTS Member (
                        memberID SERIAL PRIMARY KEY,
                        name VARCHAR(32) NOT NULL,
                        email VARCHAR(254) NOT NULL
                        ); """
    # Create Member table
    cursor.execute(sql_create_member_table)

    sql_create_transaction_table = """ CREATE TABLE IF NOT EXISTS Transactions (
                   transactionID SERIAL PRIMARY KEY,
                   referenceNumber VARCHAR(16),
                   transactionDetail VARCHAR ,
                   description VARCHAR(128),
                   amount DOUBLE PRECISION NOT NULL,
                   currency VARCHAR(3) NOT NULL,
                   transaction_date VARCHAR(10),
                   categoryID INTEGER,
                   memberID INTEGER,
                   typeTransaction VARCHAR,
                   FOREIGN KEY (referenceNumber) REFERENCES File (referenceNumber),
                   FOREIGN KEY (categoryID) REFERENCES Category (categoryID),
                   FOREIGN KEY (memberID) REFERENCES Member (memberID)
                   ); """
    # Create transaction table
    cursor.execute(sql_create_transaction_table)
    print("Tables created successfully........")
    conn.commit()
    # Closing the connection
    if conn:
        conn.close()
        print("PostgreSQL connection is closed")
    else:
        print("Error! cannot create the database connection.")


table_create()
