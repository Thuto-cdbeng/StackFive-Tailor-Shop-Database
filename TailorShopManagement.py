import mysql.connector
from mysql.connector import Error
from tabulate import tabulate  # Optional: formatted table printing


def create_db_connection(host_name, user_name, port_number, user_password, db_name):
    """Establishes connection to the MySQL Database."""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            port=port_number,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Successfully connected to the Tailoring Management Database.\n")
    except Error as e:
        print(f"Error connecting to database: '{e}'")
    return connection


def execute_query(connection, query, params=None):
    """Executes a SELECT query and prints tabular results."""
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        result = cursor.fetchall()
        field_names = [i[0] for i in cursor.description]
        
        if result:
            print(tabulate(result, headers=field_names, tablefmt="psql"))
        else:
            print("No records found.")
            
    except Error as e:
        print(f"Error executing query: '{e}'")
    finally:
        cursor.close()


# =====================================================================
# STAFF OPERATIONAL QUERIES (1.0 - 10.0)
# =====================================================================

def op_1_list_customers(conn):
    print("\n--- [1.0] Staff Portal: Customer Directory ---")
    query = "SELECT * FROM Customers;"
    execute_query(conn, query)

def op_2_services_by_category(conn):
    print("\n--- [2.0] Operations: Garment Services Volume Breakdown ---")
    query = """
    SELECT category, COUNT(service_id) AS total_services
    FROM GarmentServices
    GROUP BY category;
    """
    execute_query(conn, query)

def op_3_urgent_orders(conn):
    print("\n--- [3.0] Workshop Queue: Urgently Due Orders (<= 7 Days) ---")
    query = """
    SELECT o.order_id, c.first_name, c.last_name, DATEDIFF(o.due_date, CURDATE()) AS days_remaining
    FROM Orders o
    JOIN Customers c ON o.customer_id = c.customer_id
    WHERE DATEDIFF(o.due_date, CURDATE()) <= 7;
    """
    execute_query(conn, query)

def op_4_tailor_capacity(conn):
    print("\n--- [4.0] Staff Manager: Active Tailor Capacity Allocation ---")
    query = """
    SELECT t.first_name, t.last_name, COUNT(s.service_id) AS assigned_services
    FROM Tailors t
    LEFT JOIN GarmentServices s ON t.tailor_id = s.tailor_id
    GROUP BY t.tailor_id, t.first_name, t.last_name;
    """
    execute_query(conn, query)

def op_5_fitting_completion_rate(conn):
    print("\n--- [5.0] Fitting Specialist: Customer Fitting Completion Rate ---")
    query = """
    SELECT c.first_name, c.last_name,
           COUNT(f.fitting_id) AS total_fittings,
           ROUND((SUM(CASE WHEN f.status = 'Completed' THEN 1 ELSE 0 END) / NULLIF(COUNT(f.fitting_id), 0)) * 100, 2) AS completion_rate
    FROM Customers c
    JOIN Orders o ON c.customer_id = o.customer_id
    JOIN Fittings f ON o.order_id = f.order_id
    GROUP BY c.customer_id, c.first_name, c.last_name;
    """
    execute_query(conn, query)

def op_6_comprehensive_order_breakdown(conn):
    print("\n--- [6.0] Workshop: Master Operational Delivery Schedule ---")
    query = """
    SELECT o.order_id, CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
           s.service_name, CONCAT(t.first_name, ' ', t.last_name) AS lead_tailor, o.due_date
    FROM Orders o
    JOIN Customers c ON o.customer_id = c.customer_id
    JOIN GarmentServices s ON o.service_id = s.service_id
    JOIN Tailors t ON s.tailor_id = t.tailor_id;
    """
    execute_query(conn, query)

def op_7_service_match_matrix(conn):
    print("\n--- [7.0] Front Desk: Automated Service Action Guidelines ---")
    query = """
    SELECT c.first_name, c.last_name, s.service_name,
           CASE 
               WHEN s.category = 'Bespoke' THEN 'Full Fitting Required'
               WHEN s.category = 'Alteration' THEN 'Standard Adjustment'
               ELSE 'Quick Repair'
           END AS service_action
    FROM Customers c
    CROSS JOIN GarmentServices s;
    """
    execute_query(conn, query)

def op_8_tailor_workload_hours(conn):
    print("\n--- [8.0] Staff Manager: Tailor Workload & Projected Hours ---")
    query = """
   SELECT t.first_name, t.last_name, 
       GROUP_CONCAT(s.service_name SEPARATOR ', ') AS services,
       SUM(s.est_hours) AS total_projected_hours
FROM Tailors t
JOIN GarmentServices s ON t.tailor_id = s.tailor_id
GROUP BY t.tailor_id, t.first_name, t.last_name;
    """
    execute_query(conn, query)

def op_9_revenue_projection(conn):
    print("\n--- [9.0] Management: Revenue Projections by Service Category ---")
    query = """
    SELECT s.category, COUNT(o.order_id) AS orders_placed,
           SUM(s.base_price) AS gross_revenue_projection,
           AVG(s.base_price) AS average_order_value
    FROM GarmentServices s
    JOIN Orders o ON s.service_id = o.service_id
    GROUP BY s.category;
    """
    execute_query(conn, query)

def op_10_inactive_customers(conn):
    print("\n--- [10.0] Marketing: Re-engagement List (Inactive Clients) ---")
    query = """
    SELECT c.customer_id, c.first_name, c.last_name, c.email
    FROM Customers c
    WHERE NOT EXISTS (
        SELECT 1 FROM Orders o WHERE o.customer_id = c.customer_id
    );
    """
    execute_query(conn, query)


# =====================================================================
# CLI NAVIGATION MENU
# =====================================================================

def display_menu():
    print("\n" + "="*55)
    print("      TAILORING SHOP STAFF MANAGEMENT PORTAL")
    print("="*55)
    print(" 1. View Customer Directory")
    print(" 2. View Service Category Breakdown")
    print(" 3. View Urgent Orders Queue (<= 7 Days)")
    print(" 4. View Tailor Capacity Allocation")
    print(" 5. View Customer Fitting Completion Rates")
    print(" 6. View Master Operational Delivery Schedule")
    print(" 7. View Service Action Matrix")
    print(" 8. View Tailor Workload & Projected Hours")
    print(" 9. View Revenue Projections by Category")
    print("10. View Inactive Customers (Outreach)")
    print(" 0. Exit System")
    print("="*55)


def main():
    # Database Configuration (Update credentials as needed)
    DB_HOST = "172.21.12.21"
    DB_USER = "4371942"
    DB_PORT = 21942
    DB_PASS = "!St4371942"
    DB_NAME = "TailorShop_DB"

    conn = create_db_connection(DB_HOST, DB_USER, DB_PORT, DB_PASS, DB_NAME)

    if conn is None:
        print("Failed to initialize database session. Exiting...")
        return

    while True:
        display_menu()
        choice = input("Select an option (0-10): ").strip()

        if choice == '1':
            op_1_list_customers(conn)
        elif choice == '2':
            op_2_services_by_category(conn)
        elif choice == '3':
            op_3_urgent_orders(conn)
        elif choice == '4':
            op_4_tailor_capacity(conn)
        elif choice == '5':
            op_5_fitting_completion_rate(conn)
        elif choice == '6':
            op_6_comprehensive_order_breakdown(conn)
        elif choice == '7':
            op_7_service_match_matrix(conn)
        elif choice == '8':
            op_8_tailor_workload_hours(conn)
        elif choice == '9':
            op_9_revenue_projection(conn)
        elif choice == '10':
            op_10_inactive_customers(conn)
        elif choice == '0':
            print("\nClosing connection... Exiting Staff Management Portal.")
            conn.close()
            break
        else:
            print("Invalid input. Please enter a number from 0 to 10.")


if __name__ == "__main__":
    main()