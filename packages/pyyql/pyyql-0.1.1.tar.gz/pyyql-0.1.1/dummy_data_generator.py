import csv
import random
from datetime import datetime, timedelta
import uuid

def generate_department_data():
    """Generate department.csv with 20 departments"""
    departments = [
        "Engineering", "Sales", "Marketing", "Human Resources", "Finance", 
        "Operations", "Customer Support", "Product Management", "Data Science", "Legal",
        "Business Development", "Quality Assurance", "Research & Development", "IT Support", "Procurement",
        "Facilities", "Training & Development", "Compliance", "Strategy", "Analytics"
    ]
    
    department_data = []
    for i, dept_name in enumerate(departments, 1):
        department_data.append({
            'department_id': f"DEPT{i:03d}",
            'department_name': dept_name,
            'status': random.choice([1, 1, 1, 1, 0])  # 80% active, 20% inactive
        })
    
    return department_data

def generate_manager_data():
    """Generate manager.csv with 30 managers"""
    manager_names = [
        "Alice Johnson", "Bob Smith", "Carol Williams", "David Brown", "Emma Davis",
        "Frank Miller", "Grace Wilson", "Henry Moore", "Ivy Taylor", "Jack Anderson",
        "Kate Thomas", "Liam Jackson", "Maya White", "Noah Harris", "Olivia Martin",
        "Paul Thompson", "Quinn Garcia", "Rachel Martinez", "Sam Robinson", "Tina Clark",
        "Uma Rodriguez", "Victor Lewis", "Wendy Lee", "Xavier Walker", "Yara Hall",
        "Zoe Allen", "Aaron Young", "Betty King", "Carl Wright", "Diana Lopez"
    ]
    
    # Get department IDs for assignment
    dept_ids = [f"DEPT{i:03d}" for i in range(1, 21)]
    
    manager_data = []
    for i, name in enumerate(manager_names, 1):
        manager_data.append({
            'manager_id': f"MGR{i:03d}",
            'manager_name': name,
            'manager_start_year': random.randint(2015, 2024),
            'department_id': random.choice(dept_ids)
        })
    
    return manager_data

def generate_employee_data():
    """Generate employee.csv with 100 employees"""
    
    # Employee names pool
    first_names = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
        "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
        "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa",
        "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna",
        "Steven", "Carol", "Paul", "Ruth", "Andrew", "Sharon", "Joshua", "Michelle",
        "Kenneth", "Laura", "Kevin", "Sarah", "Brian", "Kimberly", "George", "Deborah",
        "Edward", "Dorothy", "Ronald", "Lisa", "Timothy", "Nancy", "Jason", "Karen",
        "Jeffrey", "Betty", "Ryan", "Helen", "Jacob", "Sandra", "Gary", "Donna",
        "Nicholas", "Carol", "Eric", "Ruth", "Jonathan", "Sharon", "Stephen", "Michelle",
        "Larry", "Laura", "Justin", "Sarah", "Scott", "Kimberly", "Brandon", "Deborah",
        "Benjamin", "Dorothy", "Samuel", "Lisa", "Gregory", "Nancy", "Alexander", "Karen",
        "Patrick", "Betty", "Frank", "Helen", "Raymond", "Sandra", "Jack", "Donna",
        "Dennis", "Carol", "Jerry", "Ruth", "Tyler", "Sharon", "Aaron", "Michelle"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
        "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
        "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
        "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
        "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker"
    ]
    
    # Get manager IDs for assignment
    manager_ids = [f"MGR{i:03d}" for i in range(1, 31)]
    
    # Employment statuses
    statuses = ["active", "active", "active", "active", "on_leave", "terminated"]
    
    employee_data = []
    for i in range(1, 101):  # 100 employees
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        
        employee_data.append({
            'emp_id': i,
            'emp_name': full_name,
            'emp_joining_year': random.randint(2018, 2024),
            'manager_id': random.choice(manager_ids + [None, None])  # Some employees without managers
        })
    
    return employee_data

def write_csv_files():
    """Generate and write all CSV files"""
    
    # Generate data
    departments = generate_department_data()
    managers = generate_manager_data()
    employees = generate_employee_data()
    
    # Write department.csv
    with open('department.csv', 'w', newline='', encoding='utf-8') as f:
        if departments:
            writer = csv.DictWriter(f, fieldnames=departments[0].keys())
            writer.writeheader()
            writer.writerows(departments)
    
    # Write manager.csv
    with open('manager.csv', 'w', newline='', encoding='utf-8') as f:
        if managers:
            writer = csv.DictWriter(f, fieldnames=managers[0].keys())
            writer.writeheader()
            writer.writerows(managers)
    
    # Write employee.csv
    with open('employee.csv', 'w', newline='', encoding='utf-8') as f:
        if employees:
            writer = csv.DictWriter(f, fieldnames=employees[0].keys())
            writer.writeheader()
            writer.writerows(employees)
    
    print("CSV files generated successfully!")
    print(f"- department.csv: {len(departments)} records")
    print(f"- manager.csv: {len(managers)} records") 
    print(f"- employee.csv: {len(employees)} records")
    
    # Print sample data for verification
    print("\nSample Department Data:")
    for dept in departments[:3]:
        print(f"  {dept}")
    
    print("\nSample Manager Data:")
    for mgr in managers[:3]:
        print(f"  {mgr}")
        
    print("\nSample Employee Data:")
    for emp in employees[:3]:
        print(f"  {emp}")

if __name__ == "__main__":
    # Set random seed for reproducible data
    random.seed(42)
    
    # Generate CSV files
    write_csv_files()
    
    # Show data relationships
    print("\n" + "="*50)
    print("DATA RELATIONSHIPS:")
    print("="*50)
    print("employee.manager_id -> manager.manager_id")
    print("manager.department_id -> department.department_id")
    print("\nThis creates a proper hierarchy: Employee -> Manager -> Department")