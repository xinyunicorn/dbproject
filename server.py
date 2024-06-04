# virtualenv venv
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import current_app, g
import mysql.connector
from flask_mysqldb import MySQL
import hashlib
import secrets
import string

# a way of organizing into tables/data frames
import pandas as pd

app = Flask(__name__)
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'city_jail_new'

 
# mysql = MySQL(app)
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    db='city_jail_new'
)

myPublicdb = mysql.connector.connect(
    host='localhost',
    user='public',
    password='',
    db='city_jail_new'
)

cursor = mydb.cursor(buffered = True)

if mydb.is_connected():
    print('Connected to MySQL database')
else:
    print("Connection failed")

# TRACK CRIMINAL RECORD (STORED PROCEDURE)
@app.route("/track_criminal_record/<first_name>/<last_name>", methods=['POST'])
def get_criminal(first_name, last_name):
    try:
        records = []
        cursor = mydb.cursor(buffered=True)
        mydb.start_transaction()
        args = (first_name,last_name)
        print(args)
        cursor.callproc('track_criminal_record', args)
        for result in cursor.stored_results():
            for row in result.fetchall():
                # Append each row as a dictionary to records list
                record = {
                    'Violent Offender Status': row[0],
                    'Probation Status': row[1],
                    'Crime Classification': row[2],
                    'Sentence Type': row[3]
                }
                records.append(record)

        mydb.commit()
        # Return JSON response
        return jsonify(records)
    
    except Exception as e:
        print("Error executing track:", e)
        mydb.rollback()
        return jsonify({'error': str(e)}), 500

# GET ATTRIBUTES
@app.route("/get_attributes/<table>")
def get_attributes(table):
    # Fetch attributes corresponding to the selected table
    try:
        myPublicdb.start_transaction()
        cursor = myPublicdb.cursor(buffered = True)
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        columns = cursor.fetchall()
        attributes = [column[0] for column in columns]
        myPublicdb.commit()
        return jsonify(attributes)
    except Exception as e:
        print("Error fetching attributes:", e)
        myPublicdb.rollback()
        return []

# SEARCH (with condition)
@app.route("/search/<table>/<attribute>/<operator>/<content>")
def runSearch(table, attribute, operator, content):
    try:
        myPublicdb.start_transaction()
        cursor = myPublicdb.cursor(buffered = True)
        cursor.execute("USE city_jail_new")
        selectAllTableStr = f"SELECT * FROM {table} WHERE {attribute} {operator} '{content}'"
        cursor.execute(selectAllTableStr)
        df = cursor.fetchall()
        myPublicdb.commit()
        return jsonify(df)
    except Exception as e:
        print("Error executing search:", e)
        myPublicdb.rollback()
        return jsonify([])

# SEARCH (with condition, with sorting)
@app.route("/search/<table>/<attribute>/<operator>/<content>/<sort_attribute>/<order>")
def runSearchSort(table, attribute, operator, content, sort_attribute, order):
    try:
        myPublicdb.start_transaction()
        cursor = myPublicdb.cursor(buffered = True)
        cursor.execute("USE city_jail_new")
        selectAllTableStr = f"SELECT * FROM {table} WHERE {attribute} {operator} '{content}' ORDER BY {sort_attribute} {order}"
        cursor.execute(selectAllTableStr)
        df = cursor.fetchall()
        myPublicdb.commit()
        return jsonify(df)
    except Exception as e:
        print("Error executing search:", e)
        myPublicdb.rollback()
        return jsonify([])

# SEARCH (without condition)
@app.route("/search/<table>")
def runSearchAll(table):
    try:
        myPublicdb.start_transaction()
        cursor = myPublicdb.cursor(buffered = True)
        cursor.execute("USE city_jail_new")
        selectAllTableStr = f"SELECT * FROM {table}"
        cursor.execute(selectAllTableStr)
        df = cursor.fetchall()
        myPublicdb.commit()
        return jsonify(df)
    except Exception as e:
        print("Error executing search:", e)
        myPublicdb.rollback()
        return jsonify([])

# SEARCH (without condition, with sorting)
@app.route("/search/<table>/<sort_attribute>/<order>")
def runSearchAllSort(table, sort_attribute, order):
    try:
        myPublicdb.start_transaction()
        cursor = myPublicdb.cursor(buffered = True)
        cursor.execute("USE city_jail_new")
        selectAllTableStr = f"SELECT * FROM {table} ORDER BY  {sort_attribute} {order}"
        cursor.execute(selectAllTableStr)
        df = cursor.fetchall()
        myPublicdb.commit()
        return jsonify(df)
    except Exception as e:
        print("Error executing search:", e)
        myPublicdb.rollback()
        return jsonify([])

# DELETE (with condition)
@app.route("/delete/<table>/<attribute>/<operator>/<content>", methods=["DELETE"])
def runDelete(table, attribute, operator, content):
    try:
        mydb.start_transaction()
        cursor = mydb.cursor(buffered = True)
        cursor.execute("USE city_jail_new")
        selectAllTableStr = f"DELETE FROM {table} WHERE {attribute} {operator} '{content}'"
        cursor.execute(selectAllTableStr)
        mydb.commit()  # Commit the transaction
        return jsonify({"message": "Deletion successful"})
    except Exception as e:
        print("Error executing delete:", e)
        mydb.rollback()
        return jsonify({"error": "Deletion failed"})

# DELETE (without condition)
@app.route("/delete/<table>", methods=["DELETE"])
def runDeleteAll(table):
    try:
        mydb.start_transaction()
        cursor = mydb.cursor(buffered = True)
        cursor.execute("USE city_jail_new")
        selectAllTableStr = f"DELETE FROM {table}"
        cursor.execute(selectAllTableStr)
        mydb.commit()  # Commit the transaction
        return jsonify({"message": "Deletion successful"})
    except Exception as e:
        print("Error executing delete:", e)
        mydb.rollback()
        return jsonify({"error": "Deletion failed"})

# CREATE NEW
@app.route("/create", methods=('GET', 'POST'))
def createNew():
    if request.method == 'POST':
        table = request.form['table']
        data = {}

        # Populate data dictionary with form fields
        for key in request.form:
            if key != 'table':
                data[key] = request.form[key]

        columns = ", ".join(data.keys())
        values = ", ".join([f"'{value}'" for value in data.values()])

        try:
            mydb.start_transaction()
            cursor = mydb.cursor(buffered = True)
            cursor.execute("USE city_jail_new")
            cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({values})")
            mydb.commit()
            return jsonify({"success": "Data inserted successfully."})
        except Exception as e: 
            print("Error executing create:", e)
            mydb.rollback()
            return jsonify({"error": "Creation failed. Please try again."}), 500
    
    return jsonify({"error": "Incomplete data input."}), 400
    
# UPDATE (with condition)
@app.route("/update/<table>/<old_attribute>/<old_input>/<new_attribute>/<new_input>", methods=('GET', 'POST'))
def runUpdate(table, old_attribute, old_input, new_attribute, new_input):
    if request.method == 'POST':
        try:
            mydb.start_transaction()
            cursor = mydb.cursor(buffered = True)
            cursor.execute("USE city_jail_new")
            print(f"UPDATE {table} SET {new_attribute}='{new_input}' WHERE {old_attribute} LIKE '{old_input}'" )
            # cursor.execute(str('UPDATE ') + table + str(' SET ') + str(new_attribute) + '='+str(new_input) + ' WHERE '+str(old_attribute) + ' like ' +  ''' + str(old_input))
            cursor.execute(f"UPDATE {table} SET {new_attribute} = {new_input} WHERE {old_attribute} = {old_input}")
            mydb.commit()
            return jsonify({"success": "Data updated successfully."})
        except Exception as e:
            print("Error executing update:", e)
            mydb.rollback()
            return jsonify({"error": "Update failed. Please try again."}), 500

    return jsonify({"error": "Incomplete data input."}), 400

# UPDATE (without condition)
@app.route("/update/<table>/<new_attribute>/<new_input>", methods=('GET', 'POST'))
def runUpdateAll(table, new_attribute, new_input):
    try:
        mydb.start_transaction()
        cursor = mydb.cursor(buffered = True)
        cursor.execute("USE city_jail_new")
        cursor.execute(f"UPDATE {table} SET {new_attribute}='{new_input}'")
        mydb.commit()
        return jsonify({"success": "Data updated successfully."})
    except Exception as e:
        print("Error executing update:", e)
        mydb.rollback()
        return jsonify({"error": "Update failed. Please try again."}), 500

# RENDER LANDING PAGE 
@app.route("/")
def no_session():
    return redirect(url_for("load_login"))

# RENDER ADMIN HOME 
@app.route("/home_admin/<session_id>")
def home_admin(session_id):
    current_sessions = []
    try:
        mydb.start_transaction()
        cursor = mydb.cursor(buffered = True)
        sqlSelectSessionIds = "SELECT * FROM session"
        cursor.execute(sqlSelectSessionIds)
        current_sessions = cursor.fetchall()
        mydb.commit()
        
    except Exception as e:
        mydb.rollback()
        print(e)

    for i in range(len(current_sessions)):
        admin = 0
        
        if(current_sessions[i][1] == session_id):
            try:
                mydb.start_transaction()
                cursor = mydb.cursor(buffered = True)
                sqlCheckAdminSession = "SELECT Admin FROM users WHERE id = "
                cursor.execute(sqlCheckAdminSession + str(int(current_sessions[i][0])))
                admin = cursor.fetchone()[0];   
                mydb.commit()
            except Exception as e:
                mydb.rollback()
                print(e)
            if(admin==1):
                return render_template("home_admin.html")
    else:
        return redirect(url_for("load_login"))


# RENDER PUBLIC HOME 
@app.route("/home_public/<session_id>")
def home_public(session_id):
    current_sessions = []
    try:
        mydb.start_transaction()
        cursor = mydb.cursor(buffered = True)
        sqlSelectSessionIds = "SELECT * FROM session"
        cursor.execute(sqlSelectSessionIds)
        current_sessions = cursor.fetchall()
        mydb.commit()
        
    except Exception as e:
        mydb.rollback()
        print(e)

    for i in range(len(current_sessions)):
        admin = 0
        
        if(current_sessions[i][1] == session_id):
            try:
                mydb.start_transaction()
                cursor = mydb.cursor(buffered = True)
                sqlCheckAdminSession = "SELECT Admin FROM users WHERE id = "
                cursor.execute(sqlCheckAdminSession + str(int(current_sessions[i][0])))
                admin = cursor.fetchone()[0];   
                mydb.commit()
            except Exception as e:
                mydb.rollback()
                print(e)
            if(admin==0):
                return render_template("home_public.html")
            if(admin==1):
                return redirect("/home_admin/" + session_id)
    else:
        return redirect(url_for("load_login"))

# RENDER LOGIN
@app.route("/login")
def load_login():
    return render_template("login.html")
    
# PROCESS LOGIN 
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Get the values from the form
    username = request.form['uname']
    password = request.form['pwd']

    # Encrypt password
    password = hashlib.md5(password.encode())
    password = password.hexdigest()

    # Execute SQL query
    try:
        mydb.start_transaction()    
        cursor = mydb.cursor(buffered = True)
        sqlLoginCheck = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(sqlLoginCheck, (username, password))
        user = cursor.fetchone()
        userId = user[0]
        sqlAdminsCheck = "SELECT Admin FROM users WHERE username = %s AND password = %s"
        cursor.execute(sqlAdminsCheck, (username, password))
        Admin = cursor.fetchone()[0]
        session_id = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                for i in range(32))
        session_id = hashlib.md5(session_id.encode())
        session_id = session_id.hexdigest()
        sqlSessionIdGenerate = "INSERT INTO session VALUES (%s, %s)"
        cursor.execute(sqlSessionIdGenerate, (int(userId),session_id))
        AdminCheck = "SELECT Admin FROM users WHERE username = %s AND password = %s"
        cursor.execute(AdminCheck, (username, password))
        Admin = cursor.fetchone()[0]
        mydb.commit()   
    except Exception as e:
        mydb.rollback()
        print(e)
    # session_id = cursor.fetchone()
    if user:
        if Admin == 1:
            return redirect("/home_admin/" + session_id) #, session_id = session_id)
        else:
            return redirect("/home_public/" + session_id)
    else:
        return render_template("login.html", error="Incorrect username or password.")

# # REDIRECT LOGOUT 
# @app.route("/logout") 
# def logout_redirect():
#     return redirect("/logout/" + session_id)

# RENDER LOGOUT
@app.route("/logout/<session_id>")
def logout(session_id):
    try:
        mydb.start_transaction()        
        cursor = mydb.cursor(buffered = True)
        sqlDeleteSessionId = "DELETE FROM session WHERE session_id like " + str(session_id)
        cursor.execute(sqlDeleteSessionId)
        cursor.execute("SELECT * FROM session")
        mydb.commit()
    except Exception as e:
        mydb.rollback()
        print(e)
    print(cursor.fetchone())
    return redirect(url_for("load_login"))

# RENDER REGISTRATION
@app.route("/registration")
def load_registration():
    return render_template("registration.html")

# PROCESS REGISTRATION
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Get the values from the form
    firstname = request.form['fname']
    lastname = request.form['lname']
    username = request.form['uname']
    password = request.form['pwd']

    # Encrypt password
    password = hashlib.md5(password.encode())
    password = password.hexdigest()

    # Prepare and execute statement
    cursor = mydb.cursor(buffered = True)
    sql = "INSERT INTO users(firstname, lastname, username, password) VALUES (%s, %s, %s, %s)"
    try:
        mydb.start_transaction()
        cursor.execute(sql, (firstname, lastname, username, password))
        mydb.commit()
        return redirect(url_for("load_login"))

    except mysql.connector.Error as err:
        return render_template("registration.html", error=err.msg)

if __name__ == '__main__':
    app.run(debug=True)
