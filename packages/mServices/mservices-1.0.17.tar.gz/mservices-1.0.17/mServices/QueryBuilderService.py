from django.db import connection
import json
from datetime import datetime

class QueryBuilderService:
    def __init__(self, table):
        self.table = table
        self.select_columns = '*'
        self.conditions = []
        self.or_conditions = []
        self.joins = []
        self.order_by = ''
        self.limit = None
        self.offset = None
        self.group_by = ''

    def select(self, *columns, aggregate_mode=False):
        """
        Select specific columns for the query.
        If aggregate_mode is True, wrap each column in MAX() unless it's a constant/grouping field.
        """
        if not columns:
            self.select_columns = '*'
            return self

        formatted_columns = []
        for col in columns:
            if aggregate_mode and ' as ' in col.lower():
                left, alias = col.rsplit(' as ', 1)
                formatted_columns.append(f"MAX({left.strip()}) as {alias.strip()}")
            elif aggregate_mode and '.' in col:
                # No alias but column is dotted (like table.column)
                alias = col.split('.')[-1]
                formatted_columns.append(f"MAX({col.strip()}) as {alias}")
            else:
                formatted_columns.append(col)

        self.select_columns = ', '.join(formatted_columns)
        return self

    
    def leftJoin(self, join_expression, on_column1, on_column2):
        """Perform a LEFT JOIN where join_expression can be 'table_name' or 'table_name AS alias'."""
        self.joins.append(f"LEFT JOIN {join_expression} ON {on_column1} = {on_column2}")
        return self
    
    def where(self, column, value, operator="="):
        """Apply a WHERE condition."""
        self.conditions.append((f"{column} {operator} %s", [value]))
        return self
    
    def where_group(self, callback):
        """Encapsulates multiple OR conditions inside parentheses."""
        # Start the group
        group_conditions = []
        
        # Apply conditions inside the group using the callback
        callback(group_conditions)  # This should add conditions
        
        # Close the group
        self.conditions.append(("(" + " OR ".join([cond[0] for cond in group_conditions]) + ")", [val for cond in group_conditions for val in cond[1]]))
        return self

    def orWhere(self, column, value, operator="="):
        """Apply an OR WHERE condition."""
        self.or_conditions.append((f"{column} {operator} %s", [value]))
        return self

    def whereIn(self, column, values):
        """Filter results where column value is in a list."""
        placeholders = ', '.join(['%s'] * len(values))
        self.conditions.append((f"{column} IN ({placeholders})", values))
        return self

    def whereNotIn(self, column, values):
        """Filter results where column value is not in a list."""
        placeholders = ', '.join(['%s'] * len(values))
        self.conditions.append((f"{column} NOT IN ({placeholders})", values))
        return self
    
    def whereBetween(self, column, start, end):
        """Filter results where column value is between two values."""
        self.conditions.append((f"{column} BETWEEN %s AND %s", [start, end]))
        return self
    
    def whereLike(self, columns, search_string):
        """Apply a LIKE condition for multiple columns (search functionality)."""
        like_conditions = [f"{col} LIKE %s" for col in columns]
        self.conditions.append((f"({' OR '.join(like_conditions)})", [f"%{search_string}%"] * len(columns)))
        return self
    
    def whereNull(self, column):
        """Filter records where a column is NULL."""
        self.conditions.append((f"{column} IS NULL", []))
        return self

    def whereNotNull(self, column):
        """Filter records where a column is NOT NULL."""
        self.conditions.append((f"{column} IS NOT NULL", []))
        return self

    def count(self):
        """Get the count of records."""
        return self.aggregate("COUNT(*)")

    def max(self, column):
        """Get the max value of a column."""
        return self.aggregate(f"MAX({column})")

    def min(self, column):
        """Get the min value of a column."""
        return self.aggregate(f"MIN({column})")

    def avg(self, column):
        """Get the average value of a column."""
        return self.aggregate(f"AVG({column})")

    def aggregate(self, agg_function):
        """Helper method to execute an aggregate function."""
        # Set select_columns to the desired aggregate function
        self.select_columns = agg_function
        query, values = self.build_query()  # No need to pass select_column, it's now part of the instance
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            return cursor.fetchone()[0]
        
    def pluck(self, column):
        """Get a list of values for a single column."""
        query, values = self.build_query(select_column=column)
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            return [row[0] for row in cursor.fetchall()]
        
    def orderBy(self, column, direction="asc"):
        """Apply ORDER BY sorting."""
        self.order_by = f"ORDER BY {column} {direction.upper()}"
        return self

    def get(self):
        """Retrieve multiple records."""
        query, values = self.build_query()
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    def first(self):
        """Retrieve the first matching record."""
        self.limit = 1  # Set limit to 1 to fetch only one record
        query, values = self.build_query()  # Build the query
        print(f"Executing query: {query}")
        
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
        return None  # Return None if no record is found
    
    def groupBy(self, *columns):
        """Apply GROUP BY clause with one or more columns."""
        self.group_by = ', '.join(columns)
        return self

    
    def apply_conditions(self, filter_json, allowed_filters, search_string, search_columns):
        """Apply conditions based on filter_json."""
        if filter_json:
            try:
                filter_dict = json.loads(filter_json)  # Convert to dictionary
                for column, cond in filter_dict.items():
                    if column in allowed_filters:
                        # Skip if the column already has a condition
                        if not any(existing_cond[0].startswith(f"{column} ") for existing_cond in self.conditions):
                            try:
                                condition = self._apply_filter_condition(column, cond)
                                if condition:
                                    self.conditions.append(condition)
                            except Exception as e:
                                print(f"Error applying condition for column '{column}': {e}")
            except json.JSONDecodeError as e:
                print(f"Error parsing filter_json: {e}")

        # If search string is provided, add search conditions to specific columns
        if search_string and search_columns:
            # Create a group for OR conditions
            self.where_group(lambda group_conditions: [
                group_conditions.append((f"{col} LIKE %s", [f"%{search_string}%"])) for col in search_columns
            ])

        return self
    
    def _apply_filter_condition(self, column, cond):
        """Helper method to construct conditions from the filter."""
        operator = cond["o"]
        value = cond["v"]
        if operator == "LIKE":
            return f"{column} LIKE %s", [f"%{value}%"]
        elif operator == "=":
            return f"{column} = %s", [value]
        # Add more operators as needed
        return None

    # def paginate(self, page, limit, allowed_sorting_columns, sort_by, sort_dir):
    def paginate(self, page, limit, allowed_sorting_columns, sort_by, sort_dir):
        """Apply pagination and sorting to the query and return structured pagination data."""
        
        if sort_by and sort_dir:
            sort_dir = sort_dir.lower() if sort_dir.lower() in ["asc", "desc"] else "asc"
            self.order_by = f"ORDER BY {sort_by} {sort_dir}"

        offset = (page - 1) * limit
        self.limit = limit
        self.offset = offset

        # Get total record count with filtering and grouping
        count_query, count_values = self.build_query(count_mode=True)
        with connection.cursor() as cursor:
            cursor.execute(count_query, count_values)
            total = cursor.fetchone()[0] if cursor.rowcount > 0 else 0

        # Get actual paginated data
        query, values = self.build_query()
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        last_page = (total // limit) + (1 if total % limit > 0 else 0)

        return {
            "total_records": total,
            "per_page": limit,
            "current_page": page,
            "last_page": last_page,
            "data": data
        }
    
    def build_query(self, count_mode=False):
        values = []

        if count_mode:
            if self.group_by:
                # Build subquery count
                inner = f"SELECT {self.select_columns.replace('DISTINCT ', '')} FROM {self.table}"
                if self.joins: inner += " " + " ".join(self.joins)
                if self.conditions:
                    conds = [c[0] for c in self.conditions]
                    values += [v for c in self.conditions for v in c[1]]
                    inner += " WHERE " + " AND ".join(conds)
                inner += f" GROUP BY {self.group_by}"
                query = f"SELECT COUNT(*) FROM ({inner}) AS t"
            else:
                # simple count
                query = f"SELECT COUNT(*) FROM {self.table}"
                if self.joins: query += " " + " ".join(self.joins)
                if self.conditions:
                    conds = [c[0] for c in self.conditions]
                    values += [v for c in self.conditions for v in c[1]]
                    query += " WHERE " + " AND ".join(conds)
        else:
            query = f"SELECT {self.select_columns} FROM {self.table}"
            if self.joins: query += " " + " ".join(self.joins)
            if self.conditions:
                conds = [c[0] for c in self.conditions]
                values += [v for c in self.conditions for v in c[1]]
                query += " WHERE " + " AND ".join(conds)
            if self.group_by: query += f" GROUP BY {self.group_by}"
            if self.order_by: query += f" {self.order_by}"
            if self.limit is not None:
                query += f" LIMIT {self.limit}"
                if self.offset is not None: query += f" OFFSET {self.offset}"

        return query, values
        
    def execute(self, query, values):
        """Execute the built query and return results."""
        print(f"Executing query: {query}")
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return results
    

    def insert(self, data):
        """Insert data into the table dynamically and return the inserted data."""
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        table_columns = self.get_table_columns()
        filtered_data = {key: value for key, value in data.items() if key in table_columns}
        
        if not filtered_data:
            raise ValueError("No valid columns provided for insert")
        
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        if "created_at" in table_columns:
            filtered_data.setdefault("created_at", now)
        if "updated_at" in table_columns:
            filtered_data.setdefault("updated_at", now)
        
        columns = ', '.join(filtered_data.keys())
        placeholders = ', '.join(['%s'] * len(filtered_data))
        values = list(filtered_data.values())
        
        query = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"
        
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            cursor.execute("SELECT LAST_INSERT_ID()")
            last_id = cursor.fetchone()[0]
        
        filtered_data["id"] = last_id
        return filtered_data
        
    def insertGetId(self, data):
        """Insert data and return the last inserted ID."""
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        values = list(data.values())
        
        query = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"
        
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            cursor.execute("SELECT LAST_INSERT_ID()")
            last_id = cursor.fetchone()[0]
        return last_id
    
    def update(self, data):
        """Update records dynamically based on conditions and valid columns."""
        if not data:
            raise ValueError("No data provided for update")
        
        # Filter data based on the table's columns
        table_columns = self.get_table_columns()
        filtered_data = {key: value for key, value in data.items() if key in table_columns}
        
        if not filtered_data:
            raise ValueError("No valid columns provided for update")
        
        # Automatically set 'updated_at' if the column exists
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        if "updated_at" in table_columns:
            filtered_data["updated_at"] = now
        
        # Prepare the SET clause for the update query
        set_clause = ', '.join([f"{key} = %s" for key in filtered_data.keys()])
        values = list(filtered_data.values())
        
        # Ensure there are conditions for the update
        if not self.conditions:
            raise ValueError("Update must have at least one condition")
        
        # Prepare the WHERE clause for the update query
        condition_strings = [cond[0] for cond in self.conditions]
        condition_values = [val for cond in self.conditions for val in cond[1]]
        
        # Construct the full query
        query = f"UPDATE {self.table} SET {set_clause} WHERE " + " AND ".join(condition_strings)
        values.extend(condition_values)
        
        # Execute the update query
        with connection.cursor() as cursor:
            cursor.execute(query, values)
        
        return filtered_data  # Return the updated data

    def delete(self):
        """Delete records based on conditions."""
        if not self.conditions:
            raise ValueError("Delete must have at least one condition")
        
        condition_strings = [cond[0] for cond in self.conditions]
        condition_values = [val for cond in self.conditions for val in cond[1]]
        
        query = f"DELETE FROM {self.table} WHERE " + " AND ".join(condition_strings)
        
        with connection.cursor() as cursor:
            cursor.execute(query, condition_values)
        
        return True
    
    def get_table_columns(self):
        """Retrieve the column names for the current table."""
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW COLUMNS FROM {self.table}")
            return [row[0] for row in cursor.fetchall()]