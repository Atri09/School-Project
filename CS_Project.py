"""
Cyber Crime Management System
Class 12 Computer Science Project

A menu-driven program using MySQL for managing cybercrime cases and officers.
"""

import mysql.connector
from datetime import date
import csv
import matplotlib.pyplot as plt


# Database Configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "kali"
DB_NAME = "cyber_crime_db"


# Global connection variable
conn = None
cursor = None


# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def connect_database():
    """Connects to MySQL and creates database if needed"""
    
    global conn, cursor
    
    try:
        # Connect without database first
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.commit()
        cursor.close()
        conn.close()
        
        # Reconnect with database
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        print("✅ Connected to MySQL successfully!")
        create_tables()
        
    except mysql.connector.Error as e:
        print(f"❌ Database connection failed: {e}")
        exit()


def create_tables():
    """Creates necessary tables"""

    # Officers Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS officers (
            officer_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(20) NOT NULL,
            designation VARCHAR(20),
            contact VARCHAR(15)
        )
    """)
    
    # Crimes Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crimes (
            case_id INT AUTO_INCREMENT PRIMARY KEY,
            case_name VARCHAR(50) NOT NULL,
            crime_type VARCHAR(30),
            date_reported DATE,
            status VARCHAR(50),
            victim_name VARCHAR(50),
            assigned_officer_id INT DEFAULT NULL,
            FOREIGN KEY (assigned_officer_id) REFERENCES officers(officer_id) ON DELETE SET NULL
        )
    """)
    
    # Criminal Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS convicted_criminals (
            criminal_id INT AUTO_INCREMENT PRIMARY KEY,
            case_id INT NOT NULL,
            criminal_name VARCHAR(50) NOT NULL,
            date_caught DATE,
            location_caught VARCHAR(50),
            punishment_details TEXT,
            FOREIGN KEY (case_id) REFERENCES crimes(case_id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    print("✅ Tables created successfully!")


def close_connection():
    """Closes database connection"""
    if conn:
        conn.close()
        print("Database connection closed.")


# ============================================================================
# CRIME MANAGEMENT FUNCTIONS
# ============================================================================

def add_crime():
    """Add a new crime case"""
    print("\n" + "="*50)
    print("ADD NEW CRIME CASE")
    print("="*50)
    
    case_name = input("Enter Case Name: ")
    
    print("\nCrime Types: Phishing, Hacking, Cyberbullying, Identity Theft, Fraud")
    crime_type = input("Enter Crime Type: ")
    
    date_reported = input("Enter Date (YYYY-MM-DD): ")
    
    print("\nStatus: Pending, Under Investigation, Solved, Closed")
    status = input("Enter Status: ")
    
    victim_name = input("Enter Victim Name: ")
    
    # Insert into database
    query = """INSERT INTO crimes (case_name, crime_type, date_reported, status, victim_name)
               VALUES (%s, %s, %s, %s, %s)"""
    
    values = (case_name, crime_type, date_reported, status, victim_name)
    
    try:
        cursor.execute(query, values)
        conn.commit()
        print("\n✅ Crime case added successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")


def view_crimes():
    """View all crime cases, including assigned officer"""
    print("\n" + "="*50)
    print("ALL CRIME CASES")
    print("="*50)
    
    # Use LEFT JOIN to link crimes with officers. 
    # LEFT JOIN ensures crimes without an assigned officer are still shown (Officer Name will be NULL).
    query = """
    SELECT 
        c.case_id, c.case_name, c.crime_type, c.date_reported, c.status, o.name 
    FROM crimes c
    LEFT JOIN officers o ON c.assigned_officer_id = o.officer_id
    """
    
    cursor.execute(query)
    records = cursor.fetchall()
    
    if not records:
        print("No records found!")
        return
    
    # NOTE: The columns displayed here must match the SELECT query above
    print(f"\n{'ID':<5} {'Case Name':<20} {'Type':<15} {'Status':<15} {'Officer Assigned':<25}")
    print("-" * 85)
    
    for record in records:
        # officer_name is the 6th element (index 5) in the returned tuple
        case_id, case_name, crime_type, date_rep, status, officer_name = record
        
        # Handle cases where no officer is assigned
        officer_display = officer_name if officer_name else "N/A"
        
        print(f"{case_id:<5} {case_name:<20} {crime_type:<15} {status:<15} {officer_display:<25}")


def search_crime():
    """Search crimes by case name"""
    print("\n" + "="*50)
    print("SEARCH CRIME CASES")
    print("="*50)
    
    search_term = input("Enter case name to search: ")
    
    query = "SELECT case_id, case_name, crime_type, date_reported, status, victim_name FROM crimes WHERE case_name LIKE %s"
    cursor.execute(query, (f"%{search_term}%",))
    records = cursor.fetchall()
    
    if not records:
        print("No matching records found!")
        return
    
    print(f"\n{'ID':<5} {'Case Name':<25} {'Type':<20} {'Status':<20}")
    print("-" * 75)
    
    for record in records:
        case_id, case_name, crime_type, date_rep, status, victim = record
        print(f"{case_id:<5} {case_name:<25} {crime_type:<20} {status:<20}")


def update_crime_status():
    """Update status of a crime case"""
    print("\n" + "="*50)
    print("UPDATE CRIME STATUS")
    print("="*50)
    view_crimes()
    
    case_id = int(input("\nEnter Case ID to update: "))
    
    # Check if case exists
    cursor.execute("SELECT case_name FROM crimes WHERE case_id = %s", (case_id,))
    result = cursor.fetchone()
    
    if not result:
        print("❌ Case ID not found!")
        return
    
    print(f"Current Case: {result[0]}")
    print("\nStatus Options: Pending, Under Investigation, Solved, Closed")
    new_status = input("Enter new status: ")
    
    query = "UPDATE crimes SET status = %s WHERE case_id = %s"
    cursor.execute(query, (new_status, case_id))
    conn.commit()
    
    print("✅ Status updated successfully!")


def delete_crime():
    """Delete a crime case"""
    print("\n" + "="*50)
    print("DELETE CRIME CASE")
    print("="*50)
    view_crimes()
    
    case_id = int(input("\nEnter Case ID to delete: "))
    
    # Check if exists
    cursor.execute("SELECT case_name FROM crimes WHERE case_id = %s", (case_id,))
    result = cursor.fetchone()
    
    if not result:
        print("❌ Case ID not found!")
        return
    
    confirm = input(f"Delete case '{result[0]}'? (yes/no): ")
    
    if confirm.lower() == 'yes':
        cursor.execute("DELETE FROM crimes WHERE case_id = %s", (case_id,))
        conn.commit()
        print("✅ Case deleted successfully!")
    else:
        print("Deletion cancelled.")
#MADE BY SHUBHAM ATRI
def assign_officer():
    """Assigns an officer to a crime case"""
    print("\n" + "="*50)
    print("ASSIGN OFFICER TO CRIME CASE")
    print("="*50)
    
    try:
        view_crimes()
        case_id = int(input("\nEnter Case ID to assign officer: "))
    except ValueError:
        print("❌ Invalid input for Case ID. Must be a number.")
        return

    # Check if case exists
    cursor.execute("SELECT case_name FROM crimes WHERE case_id = %s", (case_id,))
    case_result = cursor.fetchone()
    if not case_result:
        print("❌ Case ID not found!")
        return
    
    print(f"Current Case: {case_result[0]}")
    
    # Show available officers
    view_officers()
    
    try:
        officer_id = int(input("\nEnter Officer ID to assign: "))
    except ValueError:
        print("❌ Invalid input for Officer ID. Must be a number.")
        return

    # Check if officer exists
    cursor.execute("SELECT name FROM officers WHERE officer_id = %s", (officer_id,))
    officer_result = cursor.fetchone()
    if not officer_result:
        print("❌ Officer ID not found!")
        return

    # Update the crimes table
    query = "UPDATE crimes SET assigned_officer_id = %s WHERE case_id = %s"
    try:
        cursor.execute(query, (officer_id, case_id))
        conn.commit()
        print(f"\n✅ Officer '{officer_result[0]}' successfully assigned to Case ID {case_id}!")
    except Exception as e:
        print(f"❌ Error assigning officer: {e}")


# ============================================================================
# OFFICER MANAGEMENT FUNCTIONS
# ============================================================================

def add_officer():
    """Add a new officer"""
    print("\n" + "="*50)
    print("ADD NEW OFFICER")
    print("="*50)
    
    name = input("Enter Officer Name: ")
    designation = input("Enter Designation (Inspector, Sub-Inspector, Constable): ")
    contact = input("Enter Contact Number: ")
    
    query = "INSERT INTO officers (name, designation, contact) VALUES (%s, %s, %s)"
    values = (name, designation, contact)
    
    try:
        cursor.execute(query, values)
        conn.commit()
        print("\n✅ Officer added successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")


def view_officers():
    """View all officers"""
    print("\n" + "="*50)
    print("ALL OFFICERS")
    print("="*50)
    
    cursor.execute("SELECT * FROM officers")
    records = cursor.fetchall()
    
    if not records:
        print("No records found!")
        return
    
    print(f"\n{'ID':<5} {'Name':<30} {'Designation':<20} {'Contact':<15}")
    print("-" * 75)
    
    for record in records:
        officer_id, name, designation, contact = record
        print(f"{officer_id:<5} {name:<30} {designation:<20} {contact:<15}")



# ============================================================================
# CRIMINAL/ACCUSED MANAGEMENT FUNCTIONS
# ============================================================================

def record_criminal():#Made By SHUBHAM ATRI
    """Records details of the criminal/accused caught for a case"""
    print("\n" + "="*50)
    print("RECORD ACCUSED/CONVICTED CRIMINAL")
    print("="*50)
    
    # Get Case ID and validate
    try:
        # Show all crimes so user can pick the correct case
        view_crimes() 
        case_id = int(input("\nEnter Case ID to record the criminal: "))
    except ValueError:
        print("❌ Invalid input. Case ID must be a number.")
        return

    cursor.execute("SELECT case_name FROM crimes WHERE case_id = %s", (case_id,))
    case_result = cursor.fetchone()
    if not case_result:
        print(f"❌ Case ID {case_id} not found!")
        return

    print(f"\n✅ Recording criminal for Case: {case_result[0]}")
    
    # Get Criminal Details
    criminal_name = input("Enter Criminal/Accused Name: ")
    date_caught = input("Enter Date Caught (YYYY-MM-DD): ")
    location_caught = input("Enter Location Caught: ")
    punishment_details = input("Enter Punishment Details (or 'Pending'): ")
    
    # Insert into database
    query = """INSERT INTO convicted_criminals 
               (case_id, criminal_name, date_caught, location_caught, punishment_details)
               VALUES (%s, %s, %s, %s, %s)"""
    
    values = (case_id, criminal_name, date_caught, location_caught, punishment_details)
    
    try:
        cursor.execute(query, values)
        conn.commit()
        print(f"\n✅ Criminal '{criminal_name}' recorded successfully for Case ID {case_id}!")
        
        # Optional: Automatically update the case status if a criminal is recorded
        confirm_update = input("Do you want to update the crime status to 'Solved'? (yes/no): ")
        if confirm_update.lower() == 'yes':
            update_query = "UPDATE crimes SET status = 'Solved' WHERE case_id = %s"
            cursor.execute(update_query, (case_id,))
            conn.commit()
            print("✅ Crime status updated to 'Solved'.")
            
    except Exception as e:
        print(f"❌ Error recording criminal: {e}")


def view_criminals_by_case():
    """View all recorded criminals/accused associated with a specific crime case"""
    print("\n" + "="*50)
    print("VIEW CRIMINALS/ACCUSED BY CASE")
    print("="*50)
    
    try:
        view_crimes()
        case_id = int(input("\nEnter Case ID to view recorded criminals: "))
    except ValueError:
        print("❌ Invalid input. Case ID must be a number.")
        return
        
    cursor.execute("SELECT case_name FROM crimes WHERE case_id = %s", (case_id,))
    case_result = cursor.fetchone()
    
    if not case_result:
        print(f"❌ Case ID {case_id} not found!")
        return

    print(f"\n--- Recorded Criminals for Case: {case_result[0]} (ID: {case_id}) ---")

    query = """SELECT criminal_id, criminal_name, date_caught, location_caught, punishment_details 
               FROM convicted_criminals WHERE case_id = %s"""
    
    cursor.execute(query, (case_id,))
    records = cursor.fetchall()

    if not records:
        print("No criminals/accused recorded for this case.")
        return
    
    print(f"\n{'ID':<5} {'Name':<25} {'Date Caught':<15} {'Location':<15} {'Punishment':<35}")
    print("-" * 100)
    
    for record in records:
        criminal_id, name, date_caught, location, punishment = record
        # Truncate punishment details for cleaner output
        punishment_display = punishment if len(punishment) < 35 else punishment[:32] + '...'
        print(f"{criminal_id:<5} {name:<25} {str(date_caught):<15} {location:<15} {punishment_display:<35}")


# ============================================================================
# REPORT FUNCTIONS
# ============================================================================

def generate_report():
    """Generate summary report"""#Made by SHUBHAM ATRI
    print("\n" + "="*50)
    print("CRIME STATISTICS REPORT")
    print("="*50)
    
    # Total crimes
    cursor.execute("SELECT COUNT(*) FROM crimes")
    total = cursor.fetchone()[0]
    
    # Status-wise count
    cursor.execute("SELECT status, COUNT(*) FROM crimes GROUP BY status")
    status_data = cursor.fetchall()
    
    print(f"\nTotal Crime Cases: {total}")
    print("\nStatus-wise Breakdown:")
    print("-" * 40)
    
    for status, count in status_data:
        percentage = (count / total * 100) if total > 0 else 0
        print(f"{status:<25}: {count:>3} ({percentage:.1f}%)")
    
    # Crime type distribution
    print("\nCrime Type Distribution:")
    print("-" * 40)
    cursor.execute("SELECT crime_type, COUNT(*) FROM crimes GROUP BY crime_type")
    type_data = cursor.fetchall()
    
    for crime_type, count in type_data:
        percentage = (count / total * 100) if total > 0 else 0
        print(f"{crime_type:<25}: {count:>3} ({percentage:.1f}%)")

def visualize_data():
    """Show graphical crime statistics"""
    print("\n" + "="*50)
    print("📊 VISUAL CRIME ANALYSIS")
    print("="*50)

    # --- Crime Type Distribution ---
    cursor.execute("SELECT crime_type, COUNT(*) FROM crimes GROUP BY crime_type")
    type_data = cursor.fetchall()

    if not type_data:
        print("No data available for visualization.")
        return

    types = [row[0] for row in type_data]
    counts = [row[1] for row in type_data]

    plt.figure(figsize=(7, 4))
    plt.bar(types, counts)
    plt.title("Crime Type Distribution")
    plt.xlabel("Crime Type")
    plt.ylabel("Number of Cases")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()

    # --- Status Distribution ---
    cursor.execute("SELECT status, COUNT(*) FROM crimes GROUP BY status")
    status_data = cursor.fetchall()

    statuses = [row[0] for row in status_data]
    status_counts = [row[1] for row in status_data]

    plt.figure(figsize=(6, 4))
    plt.pie(status_counts, labels=statuses, autopct="%1.1f%%", startangle=90)
    plt.title("Case Status Breakdown")
    plt.axis("equal")
    plt.show()



def export_data():
    """Gives a CSV file to export data"""
    print("\n" + "="*50)
    print("EXPORTING DATA")
    print("="*50)
    
    while True:
        print("\nSpecify Which Data to be exported")
        print("1. Crime Data")
        print("2. Officers Data")
        print("0. Back to Main Menu")
        
        try:
            ch = input("Enter Your Choice (1, 2 or 0): ")
            if ch == '0':
                break
            
            choice = int(ch)
            
            if choice == 1:
                print("Exporting Crime data to crime_data.csv...")
                f_name = 'crime_data.csv'
                cursor.execute("SELECT * FROM crimes")
                headers = [i[0] for i in cursor.description]
                records = cursor.fetchall()
                
                with open(f_name, 'w', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    #Made by SHUBHAM ATRI
                    csv_writer.writerow(headers)
                    
                    csv_writer.writerows(records)
                
                print(f"✅ Successfully exported {len(records)} crime records to {f_name}!")
                return # Exit the loop
            
            elif choice == 2:
                print("Exporting Officer data to officer_data.csv...")
                f_name = 'officer_data.csv'
                cursor.execute("SELECT * FROM officers")
                headers = [i[0] for i in cursor.description]
                records = cursor.fetchall()

                with open(f_name, 'w', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    
                    csv_writer.writerow(headers)
                    
                    csv_writer.writerows(records)
                
                print(f"✅ Successfully exported {len(records)} officer records to {f_name}!")
                return # Exit the loop

            else:
                print("❌ Invalid choice.")

        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except Exception as e:
            print(f"❌ An error occurred during export: {e}")
                
    
    
    


# ============================================================================
# MAIN MENU
# ============================================================================

def display_menu():
    """Display main menu"""
    print("\n" + "="*50)
    print("CYBER CRIME MANAGEMENT SYSTEM")
    print("="*50)
    print("\n---- CRIME MANAGEMENT ----")
    print("1. Add New Crime Case")
    print("2. View All Crimes")
    print("3. Search Crime")
    print("4. Update Crime Status")
    print("5. Assign Officer to Case")
    print("6. Delete Crime Case")
    
    print("\n---- OFFICER MANAGEMENT ----")
    print("7. Add New Officer")
    print("8. View All Officers")

    print("\n---- CRIMINAL/Accused MANGEMENT ----")
    print("9. Record Criminal/Accused Details")
    print("10. View Recorded Criminals by Case")
    
    print("\n---- REPORTS ----")
    print("11. Generate Statistics Report")
    print("12. Export Data")
    print("13. Visualize Crime Data")

    print("\n0. Exit")
    print("="*50)


def main():
    """Main program"""
    print("\n🚀 Starting Cyber Crime Management System...")
    connect_database()
    
    while True:
        display_menu()
        choice = input("\nEnter your choice: ")
        
        if choice == '1':
            add_crime()
            
        elif choice == '2':
            view_crimes()
            
        elif choice == '3':
            search_crime()
            
        elif choice == '4':
            update_crime_status()

        elif choice == "5":
            assign_officer()
             
        elif choice == '6':
            delete_crime()
            
        elif choice == '7':
            add_officer()#MADE BY SHUBHAM ATRI
            
        elif choice == '8':
            view_officers()

        elif choice == '9':
            record_criminal()
            
        elif choice == '10':
            view_criminals_by_case()
            
        elif choice == '11':
            generate_report()
            
        elif choice == '12':
            export_data()

        elif choice == '13':
            visualize_data()
            
        elif choice == '0':
            close_connection()
            return
            
            
            print("\n👋 Thank you for using the system!")
            break
        else:
            print("❌ Invalid choice! Please try again.")
        
        input("\nPress Enter to continue...")


try:
    main()
except KeyboardInterrupt:
    print("\nApplication interrupted. Closing connection.")
finally:
    close_connection()
