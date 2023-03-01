#!/usr/bin/env python3
from flask import Flask, redirect, render_template, request, url_for
import oracledb


app = Flask(__name__)
user = "SYSTEM"
password = "root"
dsn = "localhost:1521/XE"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        employeeID = request.args.get("employeeID")
        dob = request.args.get("dob")

        print(employeeID)
        print(dob)

        return render_template('index.html')
     
    else:
        # connection = oracledb.connect(user=user, password=password, dsn=dsn)
        # cur = connection.cursor()
        # cur.execute("SELECT FIRST_NAME FROM HR.EMPLOYEES WHERE EMPLOYEE_ID = 101")
        # x = cur.fetchone()
        # cur.close()
        # connection.close()

        return render_template('index.html')


if __name__=="__main__":
    app.run(host='127.0.0.1',port=4455,debug=True) 