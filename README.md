SMART INVENTORY MANAGEMENT SYSTEM
Python Tkinter + MySQL

REQUIREMENTS
1. Windows with Python installed.
2. MySQL Server installed and running.
3. Install connector:
   python -m pip install mysql-connector-python

SETUP

1. Open database.py.
2. Replace YOUR_MYSQL_PASSWORD with your MySQL root password.
   Example: "password": "MyActualPassword"
3. Save database.py.
4. Run from the project folder:
   python main.py

DATABASE
The application creates the smart_inventory database and required tables automatically.
inventory.sql is also supplied if you want to inspect/run the SQL manually.
Do not run inventory.sql against a different database without checking its USE statement.

DEFAULT LOGIN
Username: admin
Password: admin123

IMPORTANT SECURITY NOTE
Change the default password before using the application for real inventory.
This is a learning/demo project. SHA-256 password hashing is used for demonstration;
for a production application, use a password-hashing algorithm such as Argon2 or bcrypt.
