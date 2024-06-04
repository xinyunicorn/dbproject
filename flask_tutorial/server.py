#risky - anything install in global env - will affect global env - can reinstall python - try and look macup - mac setup python venv

# virtualenv venv
from flask import Flask, render_template, request
from flask import current_app, g
import mysql.connector
#render_template for file - will be html files
from flask_mysqldb import MySQL

# a way of organizing into tables/data frames
import pandas as pd

app = Flask(__name__)
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'
 
# mysql = MySQL(app)
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)
cursor = mydb.cursor()
@app.route("/statement")

def runstatement():
    
    #activating the sql db - cursor is how u navigate it - execute, fetch, commit
    cursor.execute("SHOW DATABASES")
    # cursor.execute("show tables;")
    # results = cursor.fetchall() #fetches all info from a select statement
    # mysql.connection.commit()
    df = cursor.fetchall()
    # if (cursor.description):
    #     column_names = [desc[0] for desc in cursor.description]
    #     df = pd.DataFrame(results, columns=column_names)
    # cursor.close() #avoid data leak
    return df

# function right under route is related to that route - must be unique!

@app.route("/")

# displays on a local host - auto restart server

def hello_world():
    return "Hello World"
#     # this would give the html template
#     # file must be named "templates" with an "s"
#     # return render_template("index.html")
#     # can do all the crud oeprations
#     # can be any sql statement
#     df = runstatement("SELECT * FROM hotel;")
#     hotelnames = []
#     # what does i, j represent?
#     for i, j in df.iterrows():
#         #print(i, j)
#         #print(j["hotelname"])
#         #i is the index, j is the column - not distinct unless in distinct
#         hotelnames.append(j["hotelname"])
#     #return "hello"
#     return render_template("index.html", hotelnames=hotelnames)

# only 1 function per route? yes

#API call types
# get - when open url, if u hv a form inside and submit - that's a post- info in body - is what u put into the form
# post - a get that has a body - the body has a dictionary of info to send to app - security - info from backend
#update
#delete
#put

@app.route("/bye",methods=['GET','POST'])
# @app.route("/bye")
# # displays the url then /bye will give Bye World
# #either separate route or condition
def bye_world():
    # # request?
    # if(request.method == "GET"):
    # # what do you pass in?
    #     infox = request.form.get("sdfa")
    # #key value in dict, so pass in dict key, then the info will give u the value

    return "Bye World"

@app.route("/name/<name>")

def hello_name(name):
    # return "Hello " + name
    # return render_template("profile.html", name=name)
    canaccess = True
    if (canaccess):
        return render_template("profile.html", thename=name)
    else:
        return "No Access"

if __name__ == '__main__':
    app.run(debug=True)


