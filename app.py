import datetime
from flask import Flask, render_template, request
import oracledb

user = 'SYSTEM'
password = 'root'
port = 1521
service_name = 'XE'
conn_string = "localhost:{port}/{service_name}".format(port=port, service_name=service_name)

employee_view = "SELECT EMPLOYEE_ID, FIRST_NAME, LAST_NAME, DOB, IS_PENDING, IS_APPROVED, JOB_ID, DEPT_ID FROM ASSETMANAGEMENT.EMPLOYEE"
employee_view_job = "SELECT TITLE FROM ASSETMANAGEMENT.JOB WHERE J_ID ="
employee_view_dept = "SELECT D_NAME FROM ASSETMANAGEMENT.DEPARTMENT WHERE D_ID ="

asset_view = "SELECT A_ID, A_NAME, BRAND, COMPANY_ID,  A_MODEL, IS_AVAILABLE, IS_RETIRED, CREATED_DATE, UPDATED_DATE FROM ASSETMANAGEMENT.ASSET"

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/assets',methods=['GET', 'POST'])
def assets():
    assets = []
    connection = oracledb.connect(user=user, password=password, dsn=conn_string)
    cur = connection.cursor()
    cur.execute(asset_view)
    for row in cur:
        company = ""
        cur2 = connection.cursor()
        cur2.execute("SELECT C_NAME FROM ASSETMANAGEMENT.COMPANY WHERE C_ID = " + str(row[3]))
        for row2 in cur2:
            company = row2[0]
        cur2.close()

        updated = row[8]
        if updated is None:
            updated = "Not Updated"
        else:
            updated = updated.strftime("%d-%b-%Y")
        assets.append({"AID": row[0], "ANAME": row[1],
                    "ABRAND": row[2], "ACOMPANY":company, "AMODEL": row[4], "IS_AVAILABLE": row[5], "IS_RETIRED": row[6], "CREATED": row[7].strftime("%d-%b-%Y"), "UPDATED": updated })
    cur.close()
    connection.close()

    if request.method == 'POST':
        searchQuery = request.form['searchQuery']
        assets = [a for a in assets if searchQuery in a['ANAME']]
    return render_template('assets.html', data=assets)

@app.route('/employees',methods=['GET', 'POST'])
def employees():
    emp = []
    connection = oracledb.connect(user=user, password=password, dsn=conn_string)
    cur = connection.cursor()
    cur.execute(employee_view)

    # Subqueries for job and dept
    for row in cur:
        job = ""
        dept = ""

        cur2 = connection.cursor()
        cur2.execute(employee_view_job+str(row[6]))
        for row2 in cur2:
            job = row2[0]
        cur2.close()

        cur3 = connection.cursor()
        cur3.execute(employee_view_dept+str(row[7]))
        for row3 in cur3:
            dept = row3[0]
        cur3.close()

        emp.append({"EMPLOYEE_ID": row[0], "NAME": row[1] + " " + row[2], "DOB": row[3].strftime("%d-%b-%Y"), "IS_PENDING": row[4], "IS_APPROVED": row[5], "JOB": job, "DEPT": dept})

    cur.close()
    connection.close()
    if request.method == 'POST':
        searchQuery = request.form['searchQuery']
        emp = [e for e in emp if searchQuery in e['NAME']]
    return render_template('employees.html', data=emp)




if __name__ == '__main__':
    app.run(debug=True)
