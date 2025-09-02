from lukhed_basic_utils import classCommon
from typing import Optional
from mysql.connector.connection import MySQLConnection
import mysql.connector
import atexit
import json
import psycopg2
import atexit
from psycopg2 import sql

class SqlHelper(classCommon.LukhedAuth):
    def __init__(self, datbase_project, datbase_name, key_management='github', auth_type='basic', 
                 auth_dict=None):
        """
        Initializes the SqlHelper class for managing SQL database connections and operations.

        Parameters
        ----------
        datbase_project : str
            Name of the project or repository where the database is hosted. This class will use this to manage 
            the authentication data going forward. Setup the authentication data for a project one time and then you 
            can re-use it for all future connections to the database by utilizing the database project name.
        datbase_name : str
            Name of the database to connect to. All queries and operations will be performed on this database. You 
            can change the database later by using the `change_database` method.
        key_management : str, optional
            Options for storing your authentication data. 'local' to store your auth on your local hardware. 
            'github' to store your on in a private github repository (you will need a github account and github token).
            , by default 'github'
        auth_type : str, optional
            For this class, only 'basic' is currently available, which is authentication by 'host', 'user', and 
            'password', by default 'basic'
        auth_dict : dict, optional
            By default, this class will walk you through providing your authentication data to be stored according 
            to your preference via command prompts. You can also provide the necessary dictionarty via this 
            parameter to skip the setup., by default None
        """
        
        # Creates the files needed for re-use either locally or on Github
        super().__init__(datbase_project, key_management=key_management)

        self.auth_type = auth_type
        self._auth_dict = auth_dict

        self.database_project = datbase_project
        self.database_name = datbase_name

        if self._auth_data is None:
            self._auth_setup()

        self.db_connection = None                       # type: Optional[MySQLConnection]
        self.cursor = None
        atexit.register(self.close_connection)

    ###################
    # Auth and Connection
    
    def _auth_setup(self):
        """
        Set up authentication for the SQL database.

        Parameters
        ----------
        None
        """
        if self.auth_type == 'basic':
            if self._auth_dict is None:
                # Walk the user through the basic auth setup
                input("Basic auth requires the following information: 'host', 'user', 'password'. "
                    "Press enter to start inputting these values.")
                host = input("Enter host (e.g. 123.241.123.12): ")
                user = input("Enter user: ")
                password = input("Enter password: ")

                self._auth_data = {
                    "host": host,
                    "user": user,
                    "password": password
                }
            
            # Write auth data to user specified storage
            self.kM.force_update_key_data(self._auth_data)
            print("Basic auth data has been set up successfully.")

        else:
            raise ValueError(f"Unsupported auth_type: {self.auth_type}")
        
    def _check_connect_db(self):
        if self.db_connection is None:
            self.connect()
        elif self.db_connection.is_connected():
            pass
        else:
            self.connect()
        
    def connect(self):
        self.db_connection = mysql.connector.connect(
            host=self._auth_data['host'],
            user=self._auth_data['user'],
            password=self._auth_data['password'],
            database=self.database_name
        )
        self.cursor = self.db_connection.cursor()

    def test_connection(self):
        self._check_connect_db()
        if self.db_connection.is_connected():
            print("Connected to the database " + self.database_name)
        else:
            print("Failed to connect to the database")

    def close_connection(self):
        if self.db_connection and self.db_connection.is_connected():
            self.db_connection.close()
            print("Connection was closed to " + self.database_name)

    def change_database(self, database_name):
        self.close_connection()
        self.database_name = database_name
        print("New database is: " + self.database_name)

    def update_auth_data(self, force_new_auth_dict=None):
        if force_new_auth_dict is not None:
            self._auth_dict = force_new_auth_dict
        self._auth_setup()


    ##################
    # Table Management
    def get_all_tables(self):
        self._check_connect_db()
        query = "SHOW TABLES;"
        self.cursor.execute(query)
        tables = [table[0] for table in self.cursor.fetchall()]
        return tables
    
    def create_table(self, table_name, *column_tuples, include_id=False, charset='utf8mb4'):
        """
        Create a new table with the specified name and columns.

        Parameters
        ----------
        table_name : str
            Name of the table to be created
        column_tuples : tuple or list of tuples
            Contains column name and data type. Example: ('column1', 'INT'), ('column2', 'VARCHAR(255)')
        include_id : bool, optional
            Whether to include an incrementing ID column
        charset : str, optional
            Character set for the table (default is 'utf8mb4')
        """
        self._check_connect_db()

        if isinstance(column_tuples[0][0], (tuple, list)):
            column_tuples = column_tuples[0]

        if include_id:
            id_column = ('id', 'INT AUTO_INCREMENT PRIMARY KEY')
            column_tuples = [id_column] + list(column_tuples)

        columns_str = ', '.join([f'{col_name} {col_type}' for col_name, col_type in column_tuples])
        query = f"CREATE TABLE {table_name} ({columns_str}) CHARACTER SET {charset};"

        self.cursor.execute(query)
        self.db_connection.commit()

    def delete_table(self, table_name, has_foreign_key=False):
        """
        Delete a table from the database.

        Parameters
        ----------
        table_name : str
            Name of the table to be deleted
        has_foreign_key : bool
            Whether the table has foreign key constraints
        """
        self._check_connect_db()

        if has_foreign_key:
            # Drop foreign key constraints
            foreign_keys = self.get_foreign_keys(table_name)
            for foreign_key in foreign_keys:
                foreign_key_name = foreign_key['constraint_name']
                query = f"ALTER TABLE {table_name} DROP FOREIGN KEY {foreign_key_name};"
                self.cursor.execute(query)
                self.db_connection.commit()

        # Drop the table
        query = f"DROP TABLE {table_name};"
        self.cursor.execute(query)
        self.db_connection.commit()

    def table_exists(self, table_name):
        """
        Check if a table exists in the database.

        Parameters
        ----------
        table_name : str
            Name of the table

        Returns
        -------
        bool
            True if the table exists, False otherwise
        """
        self._check_connect_db()

        query = f"SHOW TABLES LIKE '{table_name}';"
        self.cursor.execute(query)
        result = self.cursor.fetchone()

        return result is not None
    
    def rename_table(self, old_table_name, new_table_name):
        """
        Rename a table.

        Parameters
        ----------
        old_table_name : str
            Current name of the table
        new_table_name : str
            New name for the table
        """
        self._check_connect_db()

        query = f"ALTER TABLE {old_table_name} RENAME TO {new_table_name};"
        self.cursor.execute(query)
        self.db_connection.commit()

    def reset_table(self, table_name, reset_auto_increment=True):
        """
        This function erases the table and also resets the auto_increment if the bool is set to do so

        Parameters
        ----------
        table_name : str
            Table name you want to erase from the currently connected db
        reset_auto_increment : bool, optional
            If TRUE, resets auto increment of id also
        """
        self._check_connect_db()

        # Delete all rows from the table
        delete_query = f"DELETE FROM {table_name}"
        self.cursor.execute(delete_query)
        self.db_connection.commit()

        # Reset the auto-increment value for the ID column
        if reset_auto_increment:
            reset_auto_increment_query = f"ALTER TABLE {table_name} AUTO_INCREMENT = 1"
            self.cursor.execute(reset_auto_increment_query)
            self.db_connection.commit()

    def remove_rows_from_table(self, table_name, rows=1, order_column="id"):
        """
        This function removes a row for the named table by default. It will remove more rows if you specify. This
        function works by ordering the table by the order_column, by default "id". If you have an id column that is
        named different then you have to specify that. For example order_column="match_id".

        Parameters
        ----------
        table_name : str
            Name of the table
        rows : int, optional
            Number of rows to remove (default is 1)
        order_column : str, optional
            Column by which to order the table for row removal (default is "id")
        """
        self._check_connect_db()
        delete_query = f"DELETE FROM {table_name} ORDER BY {order_column} DESC LIMIT {rows}"
        self.cursor.execute(delete_query)
        self.db_connection.commit()


    ########################
    # Table Data Management: Data Checks and Queries
    def display_table_in_console(self, table_name, max_rows=20, min_column_width=15):
        """
        Display a formatted table in the console with proper alignment and borders.

        Parameters
        ----------
        table_name : str
            Name of the table to display
        max_rows : int, optional
            Maximum number of rows to display (default is 20)
        min_column_width : int, optional
            Minimum width for each column (default is 15)

        Returns
        -------
        None
        """
        self._check_connect_db()
        select_query = f"SELECT * FROM {table_name}"
        self.cursor.execute(select_query)

        # Get columns and data
        columns = [column[0] for column in self.cursor.description]
        data = self.cursor.fetchmany(max_rows) if max_rows else self.cursor.fetchall()

        # Calculate column widths
        col_widths = []
        for i, col in enumerate(columns):
            # Get max width of column content including header
            content_width = max(
                max(len(str(row[i])) for row in data) if data else 0,
                len(col)
            )
            col_widths.append(max(content_width + 2, min_column_width))

        # Create separator line
        separator = '+' + '+'.join('-' * width for width in col_widths) + '+'

        # Print table header
        print(f"\nTable: {table_name}")
        print(separator)
        print('|' + '|'.join(
            f"{col:^{width}}" for col, width in zip(columns, col_widths)
        ) + '|')
        print(separator)

        # Print data rows
        for row in data:
            print('|' + '|'.join(
                f"{str(cell):^{width}}" for cell, width in zip(row, col_widths)
            ) + '|')

        print(separator)
        if max_rows and len(data) == max_rows:
            print(f"Note: Showing first {max_rows} rows only.")
    
    def get_table_as_list(self, table_name, max_rows=None):
        self._check_connect_db()
        select_query = f"SELECT * FROM {table_name}"
        self.cursor.execute(select_query)

        columns = [column[0] for column in self.cursor.description]
        data = self.cursor.fetchmany(max_rows) if max_rows else self.cursor.fetchall()

        result = [columns]

        for row in data:
            result.append(list(row))

        return result
    
    def get_last_x_entries(self, table_name, x):
        """
        This function assumes a column has an "id" column to order by.

        Parameters
        ----------
        table_name : str
            Name of the table
        x : int
            Number of last entries to retrieve
        """
        self._check_connect_db()
        select_query = f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT {x}"
        self.cursor.execute(select_query)

        columns = [column[0] for column in self.cursor.description]
        data = self.cursor.fetchall()

        result = [columns]

        for row in data:
            result.append(list(row))

        return result
    
    def query_table_by_columns(self, table_name, *condition_tuples):
        """
        Query the table by specified columns and conditions.

        Parameters
        ----------
        table_name : str
            Name of the table to query
        condition_tuples : tuple(s) or list of tuples
            Conditions for the query, specified as tuples of column-value pairs

        Returns
        -------
        list
            A list of rows matching the query conditions
        """
        self._check_connect_db()

        if isinstance(condition_tuples[0][0], (tuple, list)):
            conditions_list = [
                " AND ".join([f"{column} = %s" for column, _ in tuple]) for tuple in condition_tuples
            ]
            values = [value for tuple in condition_tuples for _, value in tuple]
        else:
            conditions_list = [
                " AND ".join([f"{column} = %s" for column, _ in condition_tuples])
            ]
            values = [value for _, value in condition_tuples]

        conditions_sql = " OR ".join(conditions_list)
        query = f"SELECT * FROM {table_name} WHERE {conditions_sql};"

        self.cursor.execute(query, values)
        rows = self.cursor.fetchall()
        rows_as_lists = [list(row) for row in rows]

        return rows_as_lists
    
    def query_by_month_day(self, table_name, date_column, date_string):
        """
        Query records where the date matches the month and day.

        Parameters
        ----------
        table_name : str
            Name of the table to query
        date_column : str
            The column name with date
        date_string : str
            Target date in the provided format

        Returns
        -------
        list
            A list of rows matching the query conditions
        """
        self._check_connect_db()

        query = f"""
                SELECT *
                FROM {table_name}
                WHERE MONTH({date_column}) = MONTH(%s)
                  AND DAY({date_column}) = DAY(%s);
            """

        self.cursor.execute(query, (date_string, date_string))
        rows = self.cursor.fetchall()
        rows_as_lists = [list(row) for row in rows]

        return rows_as_lists
    
    def get_columns_with_null_values(self, table_name, *lookup_condition_tuples):
        """
        Get columns with null values in the specified table and conditions.

        Parameters
        ----------
        table_name : str
            Name of the table to query
        lookup_condition_tuples : tuple(s) or list of tuples
            Conditions to find the row

        Returns
        -------
        list of str
            Column names with null values in the row
        """

        self._check_connect_db()

        if isinstance(lookup_condition_tuples[0][0], (tuple, list)):
            lookup_conditions = [
                f"{column} = %s" for column, _ in lookup_condition_tuples[0]
            ]
            values = [value for _, value in lookup_condition_tuples[0]]
        else:
            lookup_conditions = [f"{column} = %s" for column, _ in lookup_condition_tuples]
            values = [value for _, value in lookup_condition_tuples]

        lookup_conditions_sql = " AND ".join(lookup_conditions)
        query = f"SELECT * FROM {table_name} WHERE {lookup_conditions_sql} LIMIT 1;"

        self.cursor.execute(query, values)
        row = self.cursor.fetchone()

        if row is not None:
            columns_with_null_values = [col_name for col_name, value in row.items() if value is None]
            return columns_with_null_values
        else:
            return []
        
    def is_value_null(self, table_name, to_check_column, *lookup_condition_tuples):
        """
        Check if a value is null in the specified table and conditions.

        Parameters
        ----------
        table_name : str
            Name of the table to check
        to_check_column : str
            The column whose value you want to check
        lookup_condition_tuples : tuple(s) or list of tuples
            Conditions to find the row

        Returns
        -------
        bool
            True if NULL, False if not
        """

        result = self.get_single_value_from_table(table_name, to_check_column, *lookup_condition_tuples)

        if result is None:
            return True  # The value is null
        else:
            return False
    
    def check_if_data_exists(self, table_name, columns, values):
        """
        Checks if the specified data exists in the table.

        Parameters
        ----------
        table_name : str
            Name of the table to check
        columns : list
            List of columns to check
        values : list
            List of values corresponding to the columns to check

        Returns
        -------
        bool
            True if data exists, False if not
        """

        self._check_connect_db()
        query = f"SELECT COUNT(*) FROM {table_name} WHERE {' AND '.join([f'{col} = %s' for col in columns])}"

        self.cursor.execute(query, values)
        count = self.cursor.fetchone()[0]

        return count > 0
    
    def check_if_value_exists_in_column(self, table_name, column, value_to_check):
        """
        Check if a value exists in the specified column of the table.

        Parameters
        ----------
        table_name : str
            Name of the table to check
        column : str
            The column to check for the value
        value_to_check : str, int, float, etc.
            The value to check in the specified column

        Returns
        -------
        bool
            True if the value exists, False if not
        """
        self._check_connect_db()

        query = f"SELECT COUNT(*) FROM {table_name} WHERE {column} = %s"
        self.cursor.execute(query, (value_to_check,))
        count = self.cursor.fetchone()[0]

        return count > 0
    
    #######################
    # Table Data Management: Inserts and Updates
    def insert_data(self, table_name, columns, values, check_for_unique=False):
        """

        Parameters
        ----------
        table_name : str
            The name of the table you want to insert data into
        columns : list
            The columns you want to insert data in (order matters)
        values : list
            The values corresponding to the columns you want to add (order matters)
        check_for_unique : bool, optional
            If set True, it will first check if the data you are trying to add
            already exists in the table to prevent duplicate entries

        Returns
        -------
        bool
            True if data was added, False if not
        """

        add_data = True
        if check_for_unique:
            add_data = not self.check_if_data_exists(table_name, columns, values)

        if add_data:
            self._check_connect_db()
            placeholders = ', '.join(['%s'] * len(values))
            column_names = ', '.join(columns)
            query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

            self.cursor.execute(query, values)
            self.db_connection.commit()
            return True
        else:
            print("Data already exists in the table matching the information you are trying to add.")
            return False
        
    def insert_data_as_table(self, table_name, table_columns, table_rows_list_of_list):
        """
        Insert data into a table.

        Parameters
        ----------
        table_name : str
            Name of the table
        table_columns : list of str
            Column names
        table_rows_list_of_list : list of lists
            Each inner list contains values for a row
        """
        self._check_connect_db()

        # Construct the SQL query for insertion
        placeholders = ", ".join(["%s"] * len(table_columns))
        columns_str = ", ".join(table_columns)
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders});"

        try:
            # Execute the query for multiple rows
            for row_values in table_rows_list_of_list:
                self.cursor.execute(query, row_values)
            self.db_connection.commit()

        except Exception as e:
            self.db_connection.rollback()
            print(f"An error occurred: {e}")

    def update_single_value_in_table(self, table_name, column_to_update, new_value, *lookup_condition_tuples):
        """
        Update a single value in the specified table.

        Parameters
        ----------
        table_name : str
            Table in which you want to update a value
        column_to_update : str
            The column you want to update
        new_value : 
            The new value to update
        lookup_condition_tuples : tuple(s) or list of tuples
            Conditions to find the row

        Returns
        -------
        None
        """

        self._check_connect_db()

        if isinstance(lookup_condition_tuples[0][0], (tuple, list)):
            lookup_conditions = [
                f"{column} = %s" for column, _ in lookup_condition_tuples[0]
            ]
            values = [value for _, value in lookup_condition_tuples[0]]
        else:
            lookup_conditions = [f"{column} = %s" for column, _ in lookup_condition_tuples]
            values = [value for _, value in lookup_condition_tuples]

        lookup_conditions_sql = " AND ".join(lookup_conditions)
        query = f"UPDATE {table_name} SET {column_to_update} = %s WHERE {lookup_conditions_sql};"

        values = [new_value] + values
        self.cursor.execute(query, values)
        self.db_connection.commit()

    def update_multiple_values_in_table(self, table_name, columns_to_update_list, values_to_update_list,
                                        *lookup_condition_tuples):
        """
        Update multiple values in the specified table.

        Parameters
        ----------
        table_name : str
            Table in which you want to update values
        columns_to_update_list : list of str
            The columns you want to update
        values_to_update_list : list
            The new values to update
        lookup_condition_tuples : tuple(s) or list of tuples
            Conditions to find the row

        Returns
        -------
        None
        """

        self._check_connect_db()

        if isinstance(lookup_condition_tuples[0][0], (tuple, list)):
            lookup_conditions = [
                f"{column} = %s" for column, _ in lookup_condition_tuples[0]
            ]
            values = [value for _, value in lookup_condition_tuples[0]]
        else:
            lookup_conditions = [f"{column} = %s" for column, _ in lookup_condition_tuples]
            values = [value for _, value in lookup_condition_tuples]

        lookup_conditions_sql = " AND ".join(lookup_conditions)

        columns_values_to_update = ", ".join(
            [f"{col} = %s" for col in columns_to_update_list]
        )

        query = f"UPDATE {table_name} SET {columns_values_to_update} WHERE {lookup_conditions_sql};"

        values = values_to_update_list + values
        self.cursor.execute(query, values)
        self.db_connection.commit()
        
    
    #######################
    # Table Data Management: Columns
    def get_columns_in_table(self, table_name):
        """
        Get the list of column names in the specified table.

        Parameters
        ----------
        table_name : str
            Name of the table

        Returns
        -------
        list of str
            Column names
        """
        self._check_connect_db()

        query = f"SHOW COLUMNS FROM {table_name};"
        self.cursor.execute(query)
        columns = [column[0] for column in self.cursor.fetchall()]

        return columns
    
    def add_column_to_table(self, table_name, column_name, column_type, after_column=None):
        """
        Add a column to the specified table.

        Parameters
        ----------
        table_name : str
            Name of the table
        column_name : str
            Name of the column to be added
        column_type : str
            Data type of the column to be added
        after_column : str, optional
            Name of the existing column after which the new column should be placed

        Returns
        -------
        None
        """
        self._check_connect_db()
        alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        if after_column is not None:
            alter_query += f" AFTER {after_column}"
        self.cursor.execute(alter_query)
        self.db_connection.commit()

    def rename_column(self, table_name, old_column_name, new_column_name):
        """
        Rename a column in a table.

        Parameters
        ----------
        table_name : str
            Name of the table
        old_column_name : str
            Name of the column to be renamed
        new_column_name : str
            New name for the column

        Returns
        -------
        None
        """
        self._check_connect_db()

        query = f"ALTER TABLE {table_name} CHANGE {old_column_name} {new_column_name};"
        self.cursor.execute(query)
        self.db_connection.commit()

    def change_column_type(self, table_name, column_name, new_type):
        """
        Change the data type of a column.

        Parameters
        ----------
        table_name : str
            Name of the table
        column_name : str
            Name of the column
        new_type : str
            New data type for the column

        Returns
        -------
        None
        """
        self._check_connect_db()

        query = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} {new_type};"
        self.cursor.execute(query)
        self.db_connection.commit()

    def change_column_charset(self, table_name, column_name, new_charset, new_collation):
        """
        Change the character set and collation of a column.

        Parameters
        ----------
        table_name : str
            Name of the table
        column_name : str
            Name of the column
        new_charset : str
            New character set for the column
        new_collation : str
            New collation for the column

        Returns
        -------
        None
        """
        self._check_connect_db()

        query = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} VARCHAR(500) CHARACTER SET " \
                f"{new_charset} COLLATE {new_collation};"
        self.cursor.execute(query)
        self.db_connection.commit()

    def delete_column(self, table_name, column_name):
        """
        Delete a column from a table.

        Parameters
        ----------
        table_name : str
            Name of the table
        column_name : str
            Name of the column to be deleted

        Returns
        -------
        None
        """
        self._check_connect_db()

        query = f"ALTER TABLE {table_name} DROP COLUMN {column_name};"
        self.cursor.execute(query)
        self.db_connection.commit()

    def get_column_data_as_list(self, table_name, column_name):
        """
        Retrieve data from a column as a list.

        Parameters
        ----------
        table_name : str
            Name of the table
        column_name : str
            Name of the column

        Returns
        -------
        list
            Data in the column as a list
        """
        self._check_connect_db()

        query = f"SELECT {column_name} FROM {table_name}"
        self.cursor.execute(query)
        column_data = [row[0] for row in self.cursor.fetchall()]

        return column_data
    
    def initialize_values_in_column_to_provided_value(self, table, column_name, value):
        """
        This function initializes all values in a column to a provided value.

        Parameters
        ----------
        table : str
            The name of the table in which you want to initialize the column values.
        column_name : str
            The name of the column you want to initialize.
        value : str, int, float, etc.
            The value to which you want to set all entries in the specified column.
        """
        self._check_connect_db()
        query = f"UPDATE {table} SET {column_name} = {value}"
        self.cursor.execute(query)
    
    def append_value_to_column(self, table_name, column_to_append, value_to_append, *lookup_condition_tuples):
        """
        This function is used to append a value to a JSON array stored in a column.

        Key Points:
            The column must be of type JSON in MySQL
            The function uses JSON_ARRAY_APPEND MySQL function
            Multiple lookup conditions can be used to find the correct row
            The value is always appended to the end of the existing array

        This is particularly useful when you need to maintain a history or list of values without creating separate 
        rows in the database.

        Parameters
        ----------
        table_name : str
            Table where the update should occur
        column_to_append : str
            The column whose list you want to append to
        value_to_append : str
            Value to append to the list in the specified column
        lookup_condition_tuples : tuple(s) or list of tuples
            Conditions to find the row

        Returns
        -------
        None
        """

        self._check_connect_db()

        if isinstance(lookup_condition_tuples[0][0], (tuple, list)):
            lookup_conditions = [
                f"{column} = %s" for column, _ in lookup_condition_tuples[0]
            ]
            values = [value for _, value in lookup_condition_tuples[0]]
        else:
            lookup_conditions = [f"{column} = %s" for column, _ in lookup_condition_tuples]
            values = [value for _, value in lookup_condition_tuples]

        lookup_conditions_sql = " AND ".join(lookup_conditions)
        query = f"UPDATE {table_name} SET {column_to_append} = JSON_ARRAY_APPEND({column_to_append}, '$', %s) " \
                f"WHERE {lookup_conditions_sql};"

        values = [value_to_append] + values
        self.cursor.execute(query, values)
        self.db_connection.commit()

    def append_values_to_columns(self, table_name, columns_to_append_to, values_to_append, *lookup_condition_tuples):
        """
        Append values to multiple columns in the specified table.

        Parameters
        ----------
        table_name : str
            Table where the update should occur
        columns_to_append_to : list of str
            Columns whose lists you want to append to
        values_to_append : list of str
            Values to append to the lists in the specified columns
        lookup_condition_tuples : tuple(s) or list of tuples
            Conditions to find the row

        Returns
        -------
        None
        """
        self._check_connect_db()

        if isinstance(lookup_condition_tuples[0][0], (tuple, list)):
            lookup_conditions = [
                f"{column} = %s" for column, _ in lookup_condition_tuples[0]
            ]
            values = [value for _, value in lookup_condition_tuples[0]]
        else:
            lookup_conditions = [f"{column} = %s" for column, _ in lookup_condition_tuples]
            values = [value for _, value in lookup_condition_tuples]

        lookup_conditions_sql = " AND ".join(lookup_conditions)
        query_parts = []

        for column_to_append, value_to_append in zip(columns_to_append_to, values_to_append):
            query_part = f"{column_to_append} = JSON_ARRAY_APPEND({column_to_append}, '$', %s)"
            query_parts.append(query_part)

            values.append(value_to_append)

        query = f"UPDATE {table_name} SET {', '.join(query_parts)} WHERE {lookup_conditions_sql};"

        self.cursor.execute(query, values)
        self.db_connection.commit()
    
    def append_values_to_columns_concat(self, table_name, columns_to_append_to, values_to_append,
                                        *lookup_condition_tuples):
        """
        Append values to multiple columns in the specified table using string concatenation.

        Parameters
        ----------
        table_name : str
            Table where the update should occur
        columns_to_append_to : list of str
            Columns whose values you want to append to
        values_to_append : list of str
            Values to append to the columns
        lookup_condition_tuples : tuple(s) or list of tuples
            Conditions to find the row

        Returns
        -------
        None
        """
        self._check_connect_db()

        if isinstance(lookup_condition_tuples[0][0], (tuple, list)):
            lookup_conditions = [f"{column} = %s" for column, _ in lookup_condition_tuples[0]]
            values = [value for _, value in lookup_condition_tuples[0]]
        else:
            lookup_conditions = [f"{column} = %s" for column, _ in lookup_condition_tuples]
            values = [value for _, value in lookup_condition_tuples]

        lookup_conditions_sql = " AND ".join(lookup_conditions)

        for column, value in zip(columns_to_append_to, values_to_append):
            query = f"UPDATE {table_name} SET {column} = CONCAT({column}, ', {json.dumps(value)}') WHERE {lookup_conditions_sql};"
            self.cursor.execute(query, values)
            self.db_connection.commit()
    
    #######################
    # Table Data Management: Rows
    def get_total_rows(self, table_name):
        """
        Get the total number of rows in the specified table.

        Parameters
        ----------
        table_name : str
            Name of the table

        Returns
        -------
        int
            Total number of rows in the table
        """
        try:
            self._check_connect_db()
            # Constructing the SQL query
            query = f"SELECT COUNT(*) FROM {table_name};"

            # Executing the query
            self.cursor.execute(query)
            total_rows = self.cursor.fetchone()[0]
            return total_rows
        except Exception as e:
            raise e
        
    def delete_first_rows(self, table_name, x):
        """
        Delete the first x rows from the specified table.

        Parameters
        ----------
        table_name : str
            Name of the table
        x : int
            Number of rows to delete
        """
        try:
            self._check_connect_db()

            # Constructing the SQL query
            query = f"DELETE FROM {table_name} LIMIT {x};"

            # Executing the query
            self.cursor.execute(query)
            self.db_connection.commit()
        except Exception as e:
            self.db_connection.rollback()
            raise e
    
    def get_single_value_from_table(self, table_name, column_to_retrieve, *lookup_condition_tuples):
        """
        Retrieve a single value from the specified table.

        Parameters
        ----------
        table_name : str
            Table from which you want to retrieve a value
        column_to_retrieve : str
            The column you want to retrieve
        lookup_condition_tuples : tuple(s) or list of tuples
            Conditions to find the row

        Returns
        -------
        The value of the specified column in the matching row, or None if not found
        """
        self._check_connect_db()

        if isinstance(lookup_condition_tuples[0][0], (tuple, list)):
            lookup_conditions = [
                f"{column} = %s" for column, _ in lookup_condition_tuples[0]
            ]
            values = [value for _, value in lookup_condition_tuples[0]]
        else:
            lookup_conditions = [f"{column} = %s" for column, _ in lookup_condition_tuples]
            values = [value for _, value in lookup_condition_tuples]

        lookup_conditions_sql = " AND ".join(lookup_conditions)
        query = f"SELECT {column_to_retrieve} FROM {table_name} WHERE {lookup_conditions_sql} LIMIT 1;"

        self.cursor.execute(query, values)
        result = self.cursor.fetchone()

        if result is None:
            return result
        else:
            if len(result) == 1:
                return result[0]
            else:
                return result
    
    def bulk_update_rows(self, table_name, columns_to_update, rows_to_update):
        """
        Perform a bulk update of rows in the specified table.

        Parameters
        ----------
        table_name : str
            Name of the table
        columns_to_update : list of str
            Columns to be updated
        rows_to_update : list of lists
            Each inner list contains values for the corresponding columns

        Returns
        -------
        None
        """
        self._check_connect_db()

        values = []

        update_query = f"UPDATE {table_name} AS target\nJOIN (VALUES\n"

        for row in rows_to_update:
            placeholders = ', '.join(['%s'] * len(row))
            update_query += f"    ({placeholders}),\n"
            values.extend(row)

        update_query = update_query.rstrip(',\n') + "\n) AS source (" + ', '.join(columns_to_update) + ")\n"
        update_query += f"ON " + ' AND '.join([f"target.{col} = source.{col}" for col in columns_to_update]) + "\n"
        update_query += f"SET\n"
        update_query += ', '.join([f"target.{col} = source.{col}" for col in columns_to_update]) + ";"

        self.cursor.execute(update_query, values)
        self.db_connection.commit()

    
    ###################
    # General Query Execution
    def execute_query(self, query, params=None):
        """
        Execute a SQL query with optional parameters.

        Parameters
        ----------
        query : str
            The SQL query to be executed
        params : tuple or list, optional
            Parameters to be passed to the query

        Returns
        -------
        cursor
            For SELECT queries, returns cursor for fetching results
        None
            For other queries
        """
        self._check_connect_db()
        if params is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, params)

        # For SELECT queries, return cursor for fetching results
        if query.strip().upper().startswith('SELECT'):
            return self.cursor
        
        # For other queries (UPDATE, INSERT, etc), commit and return None
        self.db_connection.commit()
        return None


    ###################
    # Datbase Key Management
    def get_foreign_keys(self, table_name):
        """
        Get a list of foreign key constraints for a given table.

        Parameters
        ----------
        table_name : str
            Name of the table

        Returns
        -------
        list of dicts
            Each dict containing information about a foreign key constraint
        """
        self._check_connect_db()

        query = f"SELECT constraint_name FROM information_schema.key_column_usage " \
                f"WHERE referenced_table_name = '{table_name}'; "
        self.cursor.execute(query)
        foreign_keys = [{'constraint_name': foreign_key[0]} for foreign_key in self.cursor.fetchall()]

        return foreign_keys
    
    def add_foreign_key(self, table_name, foreign_key_name, column_name, referenced_table, referenced_column):
        """
        Add a foreign key constraint to a table.

        Parameters
        ----------
        table_name : str
            Name of the table
        foreign_key_name : str
            Name for the foreign key constraint
        column_name : str
            Name of the column to become a foreign key
        referenced_table : str
            Name of the table containing the referenced column
        referenced_column : str
            Name of the referenced column

        Returns
        -------
        None
        """
        self._check_connect_db()

        alter_query = (
            f"ALTER TABLE {table_name} "
            f"ADD CONSTRAINT {foreign_key_name} "
            f"FOREIGN KEY ({column_name}) "
            f"REFERENCES {referenced_table}({referenced_column})"
        )

        self.cursor.execute(alter_query)
        self.db_connection.commit()

class PostgresSqlHelper(classCommon.LukhedAuth):
    def __init__(self, datbase_project, datbase_name, key_management='github', auth_type='basic',
                 auth_dict=None):
        """
        Initializes the PostgresSqlHelper class for managing PostgreSQL database connections and operations.

        This class mirrors the structure and behavior of the original MySQL-based SqlHelper but is adapted for use with 
        PostgreSQL databases such as those hosted on Supabase. It provides support for table management, data insertion, 
        querying, and connection handling using psycopg2.

        Parameters
        ----------
        datbase_project : str
            Name of the project or repository where the database is hosted. This class will use this to manage 
            the authentication data going forward. Setup the authentication data for a project one time and then you 
            can re-use it for all future connections to the database by utilizing the database project name.
        datbase_name : str
            Name of the PostgreSQL database to connect to. All queries and operations will be performed on this database. 
            You can change the database later by using the `change_database` method.
        key_management : str, optional
            Options for storing your authentication data. 'local' to store your auth on your local hardware. 
            'github' to store it in a private GitHub repository (you will need a GitHub account and GitHub token),
            by default 'github'
        auth_type : str, optional
            Currently supports 'basic' auth, which is authentication by 'host', 'user', and 'password', by default 'basic'
        auth_dict : dict, optional
            By default, this class will walk you through providing your authentication data to be stored according 
            to your preference via command prompts. You can also provide the necessary dictionary via this 
            parameter to skip the setup., by default None
        """

        super().__init__(datbase_project, key_management=key_management)

        self.auth_type = auth_type
        self._auth_dict = auth_dict

        self.database_project = datbase_project
        self.database_name = datbase_name

        if self._auth_data is None:
            self._auth_setup()

        self.db_connection = None
        self.cursor = None
        atexit.register(self.close_connection)

    
    ###################
    # Auth and Connection
    def _auth_setup(self):
        if self.auth_type == 'basic':
            if self._auth_dict is None:
                input("Basic auth requires the following information: 'host', 'user', 'password', and 'port' "
                    "Press enter to start inputting these values.")
                host = input("Enter host (e.g. db.xxxxxx.supabase.co): ")
                user = input("Enter user: ")
                password = input("Enter password: ")
                port = input("Enter port: ")

                self._auth_data = {
                    "host": host,
                    "user": user,
                    "password": password,
                    "port": port
                }

            self.kM.force_update_key_data(self._auth_data)
            print("Basic auth data has been set up successfully.")
        else:
            raise ValueError(f"Unsupported auth_type: {self.auth_type}")

    def _check_connect_db(self):
        if self.db_connection is None:
            self.connect()

    def connect(self):
        self.db_connection = psycopg2.connect(
            host=self._auth_data['host'],
            user=self._auth_data['user'],
            password=self._auth_data['password'],
            dbname=self.database_name,
            port=self._auth_data['port']
        )
        self.cursor = self.db_connection.cursor()

    def test_connection(self):
        self._check_connect_db()
        print(f"Connected to the database {self.database_name}")

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.db_connection:
            self.db_connection.close()
            print(f"Connection was closed to {self.database_name}")

    def change_database(self, database_name):
        self.close_connection()
        self.database_name = database_name
        print("New database is: " + self.database_name)

    def update_auth_data(self, force_new_auth_dict=None):
        if force_new_auth_dict is not None:
            self._auth_dict = force_new_auth_dict
        self._auth_setup()

    
    ##################
    # Table Management
    def get_all_tables(self):
        self._check_connect_db()
        query = """
            SELECT tablename
            FROM pg_catalog.pg_tables
            WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';
        """
        self.cursor.execute(query)
        tables = [table[0] for table in self.cursor.fetchall()]
        return tables

    def create_table(self, table_name, *column_tuples, include_id=False):
        self._check_connect_db()

        if isinstance(column_tuples[0][0], (tuple, list)):
            column_tuples = column_tuples[0]

        if include_id:
            id_column = ('id', 'SERIAL PRIMARY KEY')
            column_tuples = [id_column] + list(column_tuples)

        columns_str = ', '.join([f'{col_name} {col_type}' for col_name, col_type in column_tuples])
        query = sql.SQL("CREATE TABLE {} ({})").format(
            sql.Identifier(table_name),
            sql.SQL(columns_str)
        )

        self.cursor.execute(query)
        self.db_connection.commit()

    def delete_table(self, table_name):
        self._check_connect_db()
        query = sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(sql.Identifier(table_name))
        self.cursor.execute(query)
        self.db_connection.commit()

    def table_exists(self, table_name):
        self._check_connect_db()
        query = """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = %s
            );
        """
        self.cursor.execute(query, (table_name,))
        return self.cursor.fetchone()[0]

    def rename_table(self, old_table_name, new_table_name):
        self._check_connect_db()
        query = sql.SQL("ALTER TABLE {} RENAME TO {}").format(
            sql.Identifier(old_table_name),
            sql.Identifier(new_table_name)
        )
        self.cursor.execute(query)
        self.db_connection.commit()

    def reset_table(self, table_name, reset_auto_increment=True):
        """
        This function deletes all rows from a table and optionally resets the auto-increment (SERIAL) sequence.

        Parameters
        ----------
        table_name : str
            Table name you want to erase from the currently connected db
        reset_auto_increment : bool, optional
            If TRUE, resets auto increment of id also (assumes column is named 'id')
        """
        self._check_connect_db()

        # Delete all rows from the table
        query = sql.SQL("DELETE FROM {}").format(sql.Identifier(table_name))
        self.cursor.execute(query)
        self.db_connection.commit()

        # Reset auto-increment sequence if requested
        if reset_auto_increment:
            sequence_name = f"{table_name}_id_seq"
            reset_query = sql.SQL("ALTER SEQUENCE {} RESTART WITH 1").format(sql.Identifier(sequence_name))
            self.cursor.execute(reset_query)
            self.db_connection.commit()

    def remove_rows_from_table(self, table_name, rows=1, order_column="id"):
        """
        Removes a number of rows from a table by ordering with a specified column.

        Parameters
        ----------
        table_name : str
            Name of the table
        rows : int, optional
            Number of rows to remove (default is 1)
        order_column : str, optional
            Column by which to order the table for row removal (default is "id")
        """
        self._check_connect_db()

        query = sql.SQL(
            "DELETE FROM {} WHERE ctid IN (SELECT ctid FROM {} ORDER BY {} DESC LIMIT %s)"
        ).format(
            sql.Identifier(table_name),
            sql.Identifier(table_name),
            sql.Identifier(order_column)
        )
        self.cursor.execute(query, (rows,))
        self.db_connection.commit()


    ########################
    # Table Data Management: Data Checks and Queries
    def display_table_in_console(self, table_name, max_rows=20, min_column_width=15):
        """
        Display a formatted table in the console with proper alignment and borders.

        Parameters
        ----------
        table_name : str
            Name of the table to display
        max_rows : int, optional
            Maximum number of rows to display (default is 20)
        min_column_width : int, optional
            Minimum width for each column (default is 15)

        Returns
        -------
        None
        """
        self._check_connect_db()
        select_query = f'SELECT * FROM "{table_name}"'
        self.cursor.execute(select_query)

        columns = [desc[0] for desc in self.cursor.description]
        data = self.cursor.fetchmany(max_rows) if max_rows else self.cursor.fetchall()

        col_widths = []
        for i, col in enumerate(columns):
            content_width = max(
                max(len(str(row[i])) for row in data) if data else 0,
                len(col)
            )
            col_widths.append(max(content_width + 2, min_column_width))

        separator = '+' + '+'.join('-' * width for width in col_widths) + '+'

        print(f"\nTable: {table_name}")
        print(separator)
        print('|' + '|'.join(
            f"{col:^{width}}" for col, width in zip(columns, col_widths)
        ) + '|')
        print(separator)

        for row in data:
            print('|' + '|'.join(
                f"{str(cell):^{width}}" for cell, width in zip(row, col_widths)
            ) + '|')

        print(separator)
        if max_rows and len(data) == max_rows:
            print(f"Note: Showing first {max_rows} rows only.")

    def get_table_as_list(self, table_name, max_rows=None):
        self._check_connect_db()
        select_query = f'SELECT * FROM "{table_name}"'
        self.cursor.execute(select_query)

        columns = [desc[0] for desc in self.cursor.description]
        data = self.cursor.fetchmany(max_rows) if max_rows else self.cursor.fetchall()

        return [columns] + [list(row) for row in data]

    def get_last_x_entries(self, table_name, x):
        """
        This function assumes the table has an 'id' column to order by.

        Parameters
        ----------
        table_name : str
            Name of the table
        x : int
            Number of last entries to retrieve

        Returns
        -------
        list
            List of rows including column headers
        """
        self._check_connect_db()
        select_query = f'SELECT * FROM "{table_name}" ORDER BY id DESC LIMIT %s'
        self.cursor.execute(select_query, (x,))

        columns = [desc[0] for desc in self.cursor.description]
        data = self.cursor.fetchall()
        return [columns] + [list(row) for row in data]

    def query_table_by_columns(self, table_name, *condition_tuples):
        """
        Query the table by specified columns and conditions.

        Parameters
        ----------
        table_name : str
            Name of the table to query
        condition_tuples : tuple(s) or list of tuples
            Conditions for the query, specified as tuples of column-value pairs

        Returns
        -------
        list
            A list of rows matching the query conditions
        """
        self._check_connect_db()

        if isinstance(condition_tuples[0][0], (tuple, list)):
            conditions_list = [
                " AND ".join([f"{col} = %s" for col, _ in group]) for group in condition_tuples
            ]
            values = [val for group in condition_tuples for _, val in group]
        else:
            conditions_list = [" AND ".join([f"{col} = %s" for col, _ in condition_tuples])]
            values = [val for _, val in condition_tuples]

        conditions_sql = " OR ".join(conditions_list)
        query = f'SELECT * FROM "{table_name}" WHERE {conditions_sql};'

        self.cursor.execute(query, values)
        return [list(row) for row in self.cursor.fetchall()]

    def query_by_month_day(self, table_name, date_column, date_string):
        """
        Query records where the date matches the month and day.

        Parameters
        ----------
        table_name : str
            Name of the table to query
        date_column : str
            The column name with date
        date_string : str
            Target date (e.g., '2024-01-15')

        Returns
        -------
        list
            A list of rows matching the query conditions
        """
        self._check_connect_db()

        query = f'''
            SELECT *
            FROM "{table_name}"
            WHERE EXTRACT(MONTH FROM {date_column}) = EXTRACT(MONTH FROM %s::date)
            AND EXTRACT(DAY FROM {date_column}) = EXTRACT(DAY FROM %s::date)
        '''
        self.cursor.execute(query, (date_string, date_string))
        return [list(row) for row in self.cursor.fetchall()]

    def get_columns_with_null_values(self, table_name, *lookup_condition_tuples):
        """
        Get columns with null values in the specified row.

        Parameters
        ----------
        table_name : str
            Name of the table
        lookup_condition_tuples : tuple(s) or list of tuples
            Conditions to identify the row

        Returns
        -------
        list of str
            Column names with NULL values in the row
        """
        self._check_connect_db()

        if isinstance(lookup_condition_tuples[0][0], (tuple, list)):
            conditions = [f"{col} = %s" for col, _ in lookup_condition_tuples[0]]
            values = [val for _, val in lookup_condition_tuples[0]]
        else:
            conditions = [f"{col} = %s" for col, _ in lookup_condition_tuples]
            values = [val for _, val in lookup_condition_tuples]

        query = f'SELECT * FROM "{table_name}" WHERE {" AND ".join(conditions)} LIMIT 1'
        self.cursor.execute(query, values)
        row = self.cursor.fetchone()

        if row is None:
            return []

        columns = [desc[0] for desc in self.cursor.description]
        return [col for col, val in zip(columns, row) if val is None]

    def is_value_null(self, table_name, to_check_column, *lookup_condition_tuples):
        """
        Check if a value is NULL in the specified table and column.

        Parameters
        ----------
        table_name : str
            Table to check
        to_check_column : str
            Column to evaluate
        lookup_condition_tuples : tuple(s) or list of tuples
            Conditions to identify the row

        Returns
        -------
        bool
            True if NULL, False otherwise
        """
        result = self.get_single_value_from_table(table_name, to_check_column, *lookup_condition_tuples)
        return result is None

    def check_if_data_exists(self, table_name, columns, values):
        """
        Check if a specific row exists based on multiple column values.

        Parameters
        ----------
        table_name : str
            Table name
        columns : list of str
            Columns to match
        values : list
            Values to match against columns

        Returns
        -------
        bool
            True if a match exists, False otherwise
        """
        self._check_connect_db()

        conditions = ' AND '.join([f"{col} = %s" for col in columns])
        query = f'SELECT COUNT(*) FROM "{table_name}" WHERE {conditions}'
        self.cursor.execute(query, values)
        return self.cursor.fetchone()[0] > 0

    def check_if_value_exists_in_column(self, table_name, column, value_to_check):
        """
        Check if a value exists in a specific column of a table.

        Parameters
        ----------
        table_name : str
            Table to search
        column : str
            Column name
        value_to_check : any
            Value to search for

        Returns
        -------
        bool
            True if the value exists, False otherwise
        """
        self._check_connect_db()

        query = f'SELECT COUNT(*) FROM "{table_name}" WHERE {column} = %s'
        self.cursor.execute(query, (value_to_check,))
        return self.cursor.fetchone()[0] > 0

    #######################
    # Table Data Management: Inserts and Updates
    def insert_data(self, table_name, columns, values, check_for_unique=False):
        """
        Inserts a row into a PostgreSQL table. Optionally checks for uniqueness.

        Parameters
        ----------
        table_name : str
        columns : list of str
        values : list
        check_for_unique : bool

        Returns
        -------
        bool
        """
        add_data = True
        if check_for_unique:
            add_data = not self.check_if_data_exists(table_name, columns, values)

        if add_data:
            self._check_connect_db()
            query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, columns)),
                sql.SQL(', ').join(sql.Placeholder() * len(values))
            )
            self.cursor.execute(query, values)
            self.db_connection.commit()
            return True
        else:
            print("Data already exists in the table matching the information you are trying to add.")
            return False

    def insert_data_as_table(self, table_name, table_columns, table_rows_list_of_list):
        """
        Insert multiple rows into a PostgreSQL table.

        Parameters
        ----------
        table_name : str
        table_columns : list of str
        table_rows_list_of_list : list of list
        """
        self._check_connect_db()

        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(map(sql.Identifier, table_columns)),
            sql.SQL(', ').join(sql.Placeholder() * len(table_columns))
        )

        try:
            for row_values in table_rows_list_of_list:
                self.cursor.execute(query, row_values)
            self.db_connection.commit()
        except Exception as e:
            self.db_connection.rollback()
            print(f"An error occurred: {e}")

    def update_single_value_in_table(self, table_name, column_to_update, new_value, *lookup_condition_tuples):
        """
        Update a single column's value in a specific row.

        Parameters
        ----------
        table_name : str
        column_to_update : str
        new_value : any
        lookup_condition_tuples : tuple(s)
        """
        self._check_connect_db()

        if isinstance(lookup_condition_tuples[0][0], (tuple, list)):
            conditions = [f"{col} = %s" for col, _ in lookup_condition_tuples[0]]
            values = [val for _, val in lookup_condition_tuples[0]]
        else:
            conditions = [f"{col} = %s" for col, _ in lookup_condition_tuples]
            values = [val for _, val in lookup_condition_tuples]

        where_clause = " AND ".join(conditions)
        query = sql.SQL("UPDATE {} SET {} = %s WHERE " + where_clause).format(
            sql.Identifier(table_name),
            sql.Identifier(column_to_update)
        )
        self.cursor.execute(query, [new_value] + values)
        self.db_connection.commit()

    def update_multiple_values_in_table(self, table_name, columns_to_update_list, values_to_update_list, *lookup_condition_tuples):
        """
        Update multiple columns in a single row using WHERE conditions.

        Parameters
        ----------
        table_name : str
        columns_to_update_list : list of str
        values_to_update_list : list
        lookup_condition_tuples : tuple(s)
        """
        self._check_connect_db()

        if isinstance(lookup_condition_tuples[0][0], (tuple, list)):
            conditions = [f"{col} = %s" for col, _ in lookup_condition_tuples[0]]
            values = [val for _, val in lookup_condition_tuples[0]]
        else:
            conditions = [f"{col} = %s" for col, _ in lookup_condition_tuples]
            values = [val for _, val in lookup_condition_tuples]

        set_clause = ', '.join([f"{col} = %s" for col in columns_to_update_list])
        where_clause = " AND ".join(conditions)

        query = sql.SQL(f"UPDATE {{}} SET {set_clause} WHERE {where_clause}").format(
            sql.Identifier(table_name)
        )
        self.cursor.execute(query, values_to_update_list + values)
        self.db_connection.commit()


    #######################
    # Table Data Management: Columns
    def get_columns_in_table(self, table_name):
        """
        Get the list of column names in the specified PostgreSQL table.

        Parameters
        ----------
        table_name : str

        Returns
        -------
        list of str
            Column names
        """
        self._check_connect_db()
        query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s;
        """
        self.cursor.execute(query, (table_name,))
        return [row[0] for row in self.cursor.fetchall()]
    
    def add_column_to_table(self, table_name, column_name, column_type, after_column=None):
        """
        Add a column to the specified PostgreSQL table.

        Parameters
        ----------
        table_name : str
        column_name : str
        column_type : str
        after_column : str, optional (ignored in PostgreSQL)
        """
        self._check_connect_db()

        query = sql.SQL("ALTER TABLE {} ADD COLUMN {} {}").format(
            sql.Identifier(table_name),
            sql.Identifier(column_name),
            sql.SQL(column_type)
        )
        self.cursor.execute(query)
        self.db_connection.commit()

    def rename_column(self, table_name, old_column_name, new_column_name):
        """
        Rename a column in a PostgreSQL table.

        Parameters
        ----------
        table_name : str
        old_column_name : str
        new_column_name : str
        """
        self._check_connect_db()
        query = sql.SQL("ALTER TABLE {} RENAME COLUMN {} TO {}").format(
            sql.Identifier(table_name),
            sql.Identifier(old_column_name),
            sql.Identifier(new_column_name)
        )
        self.cursor.execute(query)
        self.db_connection.commit()

    def change_column_type(self, table_name, column_name, new_type):
        """
        Change the data type of a column in PostgreSQL.

        Parameters
        ----------
        table_name : str
        column_name : str
        new_type : str
        """
        self._check_connect_db()
        query = sql.SQL("ALTER TABLE {} ALTER COLUMN {} TYPE {}").format(
            sql.Identifier(table_name),
            sql.Identifier(column_name),
            sql.SQL(new_type)
        )
        self.cursor.execute(query)
        self.db_connection.commit()

    def change_column_charset(self, table_name, column_name, new_charset, new_collation):
        """
        Change the collation of a column in PostgreSQL (character sets are cluster-level).

        Parameters
        ----------
        table_name : str
        column_name : str
        new_charset : str (ignored – PostgreSQL uses UTF-8)
        new_collation : str (PostgreSQL collation name)
        """
        self._check_connect_db()
        query = sql.SQL("ALTER TABLE {} ALTER COLUMN {} SET COLLATION {}").format(
            sql.Identifier(table_name),
            sql.Identifier(column_name),
            sql.Identifier(new_collation)
        )
        self.cursor.execute(query)
        self.db_connection.commit()

    def delete_column(self, table_name, column_name):
        """
        Delete a column from a PostgreSQL table.
        """
        self._check_connect_db()
        query = sql.SQL("ALTER TABLE {} DROP COLUMN {}").format(
            sql.Identifier(table_name),
            sql.Identifier(column_name)
        )
        self.cursor.execute(query)
        self.db_connection.commit()

    def get_column_data_as_list(self, table_name, column_name):
        """
        Retrieve data from a column as a list.
        """
        self._check_connect_db()
        query = sql.SQL("SELECT {} FROM {}").format(
            sql.Identifier(column_name),
            sql.Identifier(table_name)
        )
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def initialize_values_in_column_to_provided_value(self, table, column_name, value):
        """
        Initialize all values in a column to the provided value.
        """
        self._check_connect_db()
        query = sql.SQL("UPDATE {} SET {} = %s").format(
            sql.Identifier(table),
            sql.Identifier(column_name)
        )
        self.cursor.execute(query, (value,))
        self.db_connection.commit()

    def append_value_to_column(self, table_name, column_to_append, value_to_append, *lookup_condition_tuples):
        """
        Append a value to a JSONB array in a PostgreSQL column.
        """
        self._check_connect_db()

        if isinstance(lookup_condition_tuples[0][0], (tuple, list)):
            conditions = [f"{col} = %s" for col, _ in lookup_condition_tuples[0]]
            values = [val for _, val in lookup_condition_tuples[0]]
        else:
            conditions = [f"{col} = %s" for col, _ in lookup_condition_tuples]
            values = [val for _, val in lookup_condition_tuples]

        condition_sql = " AND ".join(conditions)
        query = f"""
            UPDATE {table_name}
            SET {column_to_append} = COALESCE({column_to_append}, '[]'::jsonb) || to_jsonb(%s::jsonb)
            WHERE {condition_sql}
        """
        self.cursor.execute(query, [json.dumps(value_to_append)] + values)
        self.db_connection.commit()

    def append_values_to_columns(self, table_name, columns_to_append_to, values_to_append, *lookup_condition_tuples):
        """
        Append values to multiple JSONB columns in PostgreSQL.
        """
        self._check_connect_db()

        if isinstance(lookup_condition_tuples[0][0], (tuple, list)):
            conditions = [f"{col} = %s" for col, _ in lookup_condition_tuples[0]]
            values = [val for _, val in lookup_condition_tuples[0]]
        else:
            conditions = [f"{col} = %s" for col, _ in lookup_condition_tuples]
            values = [val for _, val in lookup_condition_tuples]

        condition_sql = " AND ".join(conditions)
        update_parts = []
        value_placeholders = []

        for col, val in zip(columns_to_append_to, values_to_append):
            update_parts.append(
                f"{col} = COALESCE({col}, '[]'::jsonb) || to_jsonb(%s::jsonb)"
            )
            value_placeholders.append(json.dumps(val))

        query = f"""
            UPDATE {table_name}
            SET {', '.join(update_parts)}
            WHERE {condition_sql}
        """
        self.cursor.execute(query, value_placeholders + values)
        self.db_connection.commit()

    def append_values_to_columns_concat(self, table_name, columns_to_append_to, values_to_append, *lookup_condition_tuples):
        """
        Append values to multiple columns using string concatenation.
        """
        self._check_connect_db()

        if isinstance(lookup_condition_tuples[0][0], (tuple, list)):
            conditions = [f"{col} = %s" for col, _ in lookup_condition_tuples[0]]
            values = [val for _, val in lookup_condition_tuples[0]]
        else:
            conditions = [f"{col} = %s" for col, _ in lookup_condition_tuples]
            values = [val for _, val in lookup_condition_tuples]

        condition_sql = " AND ".join(conditions)

        for col, val in zip(columns_to_append_to, values_to_append):
            query = f"""
                UPDATE {table_name}
                SET {col} = COALESCE({col}, '') || ', {json.dumps(val)}'
                WHERE {condition_sql}
            """
            self.cursor.execute(query, values)
            self.db_connection.commit()

    #######################
    # Table Data Management: Rows
    def get_total_rows(self, table_name):
        """
        Get the total number of rows in the specified table.
        """
        self._check_connect_db()
        query = sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name))
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]

    def delete_first_rows(self, table_name, x):
        """
        Delete the first x rows from the specified table.
        NOTE: Requires a primary key or ordering column for deterministic behavior.
        """
        self._check_connect_db()
        # Replace 'id' with your table's primary key if needed
        query = sql.SQL("""
            DELETE FROM {table}
            WHERE ctid IN (
                SELECT ctid FROM {table}
                ORDER BY ctid
                LIMIT %s
            )
        """).format(table=sql.Identifier(table_name))
        self.cursor.execute(query, (x,))
        self.db_connection.commit()

    def get_single_value_from_table(self, table_name, column_to_retrieve, *lookup_condition_tuples):
        """
        Retrieve a single value from the specified table.
        """
        self._check_connect_db()

        if isinstance(lookup_condition_tuples[0][0], (tuple, list)):
            conditions = [f"{col} = %s" for col, _ in lookup_condition_tuples[0]]
            values = [val for _, val in lookup_condition_tuples[0]]
        else:
            conditions = [f"{col} = %s" for col, _ in lookup_condition_tuples]
            values = [val for _, val in lookup_condition_tuples]

        condition_sql = " AND ".join(conditions)
        query = sql.SQL("SELECT {} FROM {} WHERE {} LIMIT 1").format(
            sql.Identifier(column_to_retrieve),
            sql.Identifier(table_name),
            sql.SQL(condition_sql)
        )

        self.cursor.execute(query, values)
        result = self.cursor.fetchone()

        return result[0] if result and len(result) == 1 else result

    def bulk_update_rows(self, table_name, columns_to_update, rows_to_update):
        """
        Perform a bulk update of rows in the specified table.
        This method assumes the first column in columns_to_update is the unique key.
        """
        self._check_connect_db()

        key_column = columns_to_update[0]
        set_columns = columns_to_update[1:]

        cases = {col: [] for col in set_columns}
        ids = []

        for row in rows_to_update:
            row_dict = dict(zip(columns_to_update, row))
            key = row_dict[key_column]
            ids.append(key)
            for col in set_columns:
                cases[col].append((key, row_dict[col]))

        set_clauses = []
        values = []

        for col, case_list in cases.items():
            case_sql = f"{col} = CASE {key_column} " + \
                ' '.join([f"WHEN %s THEN %s" for _ in case_list]) + " ELSE {col} END"
            set_clauses.append(case_sql)
            for pair in case_list:
                values.extend(pair)

        query = f"""
            UPDATE {table_name}
            SET {', '.join(set_clauses)}
            WHERE {key_column} IN ({', '.join(['%s'] * len(ids))});
        """
        values.extend(ids)
        self.cursor.execute(query, values)
        self.db_connection.commit()


    ###################
    # General Query Execution
    def execute_query(self, query, params=None):
        """
        Execute a SQL query with optional parameters.

        Parameters
        ----------
        query : str
            The SQL query to be executed
        params : tuple or list, optional
            Parameters to be passed to the query

        Returns
        -------
        cursor
            For SELECT queries, returns cursor for fetching results
        None
            For other queries
        """
        self._check_connect_db()
        
        if params is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, params)

        if query.strip().upper().startswith('SELECT'):
            return self.cursor

        self.db_connection.commit()
        return None
