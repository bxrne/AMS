import datetime
from flask import Flask, render_template
import oracledb

user = 'SYSTEM'
password = 'root'
port = 1521
service_name = 'XE'
conn_string = "localhost:{port}/{service_name}".format(port=port, service_name=service_name)

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/assets',methods=['GET'])
def assets():
    assets = []
    connection = oracledb.connect(user=user, password=password, dsn=conn_string)
    cur = connection.cursor()
    cur.execute('SELECT A_ID, A_NAME, A_MODEL, IS_AVAILABLE, IS_RETIRED, CREATED_DATE FROM ASSETMANAGEMENT.ASSET')
    for row in cur:
        assets.append({"AID": row[0], "ANAME": row[1],
                    "AMODEL": row[2], "IS_AVAILABLE": row[3], "IS_RETIRED": row[4], "CREATED_DATE": row[5].strftime("%d-%b-%Y")})
    cur.close()
    connection.close()
    return render_template('assets.html', data=assets)

@app.route('/employees',methods=['GET'])
def employees():
    emp = []
    connection = oracledb.connect(user=user, password=password, dsn=conn_string)
    cur = connection.cursor()
    cur.execute("SELECT EMPLOYEE_ID, FIRST_NAME, LAST_NAME, DOB, IS_PENDING, IS_APPROVED, JOB_ID, DEPT_ID FROM ASSETMANAGEMENT.EMPLOYEE")
    for row in cur:
        id = row[0]
        fname = row[1]
        lname = row[2]
        dob = row[3].strftime("%d-%b-%Y")
        is_pending = row[4]
        is_approved = row[5]
        job_id = row[6]
        dept_id = row[7]
        job = ""
        dept = ""

        cur2 = connection.cursor()
        cur2.execute("SELECT TITLE FROM ASSETMANAGEMENT.JOB WHERE J_ID ="+str(job_id)+"")
        for row2 in cur2:
            job = row2[0]
        cur2.close()

        cur3 = connection.cursor()
        cur3.execute("SELECT D_NAME FROM ASSETMANAGEMENT.DEPARTMENT WHERE D_ID ="+str(dept_id)+"")
        for row3 in cur3:
            dept = row3[0]
        cur3.close()

        emp.append({"EMPLOYEE_ID": id, "FIRST_NAME": fname,
                    "LAST_NAME": lname, "DOB": dob, "IS_PENDING": is_pending, "IS_APPROVED": is_approved, "JOB": job, "DEPT": dept})

    cur.close()
    connection.close()
    return render_template('employees.html', data=emp)




if __name__ == '__main__':
    app.run(debug=True)
