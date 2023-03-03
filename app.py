from flask import Flask, redirect, render_template, request, url_for
import oracledb

user = 'SYSTEM'
password = 'root'
port = 1521
service_name = 'XE' # XE or XEPDB1 depending on your setup version
conn_string = "localhost:{port}/{service_name}".format(port=port, service_name=service_name)

# ASSET VIEW
asset_view = "SELECT A_ID, A_NAME, BRAND, COMPANY_ID,  A_MODEL, IS_AVAILABLE, IS_RETIRED, CREATED_DATE, UPDATED_DATE FROM ASSETMANAGEMENT.ASSET"
company_name_view  = "SELECT C_NAME FROM ASSETMANAGEMENT.COMPANY WHERE C_ID ="

# ASSIGNMENT VIEW
asset_history_view = "SELECT A_H_ID, ASSET_ID, EMPLOYEE_ID, REQUEST_ID, DATE_ASSIGNED FROM ASSETMANAGEMENT.ASSET_HISTORY"

# EMPLOYEE VIEW
employee_view = "SELECT EMPLOYEE_ID, FIRST_NAME, LAST_NAME, DOB, IS_PENDING, IS_APPROVED, JOB_ID, DEPT_ID FROM ASSETMANAGEMENT.EMPLOYEE"
employee_view_job = "SELECT TITLE FROM ASSETMANAGEMENT.JOB WHERE J_ID ="
employee_view_dept = "SELECT D_NAME FROM ASSETMANAGEMENT.DEPARTMENT WHERE D_ID ="

# REQUEST VIEW
request_view = "SELECT R_ID, EMPLOYEE_ID, ASSET_ID, IS_OPEN, IS_APPROVED, CREATED_DATE, UPDATED_DATE FROM ASSETMANAGEMENT.REQUEST"


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/assets',methods=['GET', 'POST'])
def assets():
    assets = []
    connection = oracledb.connect(user=user, password=password, dsn=conn_string)

    cur = connection.cursor()
    cur = cur.execute(asset_view)
    for row in cur:
        A_ID, A_NAME, BRAND, COMPANY_ID,  A_MODEL, IS_AVAILABLE, IS_RETIRED, CREATED_DATE, UPDATED_DATE = row

        cur2 = connection.cursor()
        COMPANY_NAME = cur2.execute(company_name_view + str(COMPANY_ID)).fetchone()[0]

        asset = {
            "AID": A_ID,
            "ANAME": A_NAME,
            "ABRAND": BRAND,
            "ACOMPANY": COMPANY_NAME,
            "AMODEL": A_MODEL,
            "IS_AVAILABLE": IS_AVAILABLE,
            "IS_RETIRED": IS_RETIRED,
            "CREATED": CREATED_DATE.strftime("%d-%b-%Y"),
            "UPDATED": UPDATED_DATE.strftime("%d-%b-%Y") if UPDATED_DATE is not None else "Not Updated"
        }
        assets.append(asset)

    cur.close()
    connection.close()

    if request.method == 'POST' and request.form['searchQuery']:
        searchQuery = request.form['searchQuery']
        assets = [a for a in assets if searchQuery.lower() in a['ANAME'].lower()]

    return render_template('assets.html', data=assets)

@app.route('/assets/edit/<aid>', methods=['GET', "POST"])
def edit_asset(aid):
    connection = oracledb.connect(user=user, password=password, dsn=conn_string)
    cur = connection.cursor()

    A_ID, A_NAME, BRAND, COMPANY_ID,  A_MODEL, IS_AVAILABLE, IS_RETIRED, CREATED_DATE, UPDATED_DATE = cur.execute(asset_view + " WHERE A_ID = " + aid).fetchone()
    COMPANY_NAME = cur.execute(company_name_view + str(COMPANY_ID)).fetchone()[0]

    asset = {
        "AID": A_ID, 
        "ANAME": A_NAME,
        "ABRAND": BRAND,
        "ACOMPANY": COMPANY_NAME,
        "AMODEL": A_MODEL, 
        "IS_AVAILABLE": IS_AVAILABLE, 
        "IS_RETIRED": IS_RETIRED, 
        "CREATED": CREATED_DATE.strftime("%d-%b-%Y"), 
        "UPDATED": UPDATED_DATE.strftime("%d-%b-%Y") if UPDATED_DATE is not None else "Not Updated" 
    }
    
    if request.method == 'POST':
        available = 1 if request.form.get('available') == 'on' else 0
        retired = 1 if request.form.get('retired') == 'on' else 0

        model = request.form['model'] if request.form['model'] != "" else A_MODEL
        brand = request.form['brand'] if request.form['brand'] != "" else BRAND
        name = request.form['name'] if request.form['name'] != "" else A_NAME

        cur.execute(f"UPDATE ASSETMANAGEMENT.ASSET SET IS_AVAILABLE = {available}, IS_RETIRED = {retired}, A_MODEL = '{model}', BRAND = '{brand}', A_NAME = '{name}' WHERE A_ID = " + aid + "")
        connection.commit()

        cur.close()
        connection.close()        
        return redirect(url_for('assets'))
    
    connection.close()
    return render_template('edit_asset.html', asset=asset)

@app.route('/employees',methods=['GET', 'POST'])
def employees():
    employees = []
    connection = oracledb.connect(user=user, password=password, dsn=conn_string)

    cur = connection.cursor()
    cur.execute(employee_view)

    for row in cur:
        EMPLOYEE_ID, FIRST_NAME, LAST_NAME, DOB, IS_PENDING, IS_APPROVED, JOB_ID, DEPT_ID = row
        
        cur2 = connection.cursor()
        JOB_TITLE = cur2.execute(employee_view_job+str(JOB_ID)).fetchone()[0]
        DEPT_NAME = cur2.execute(employee_view_dept+str(DEPT_ID)).fetchone()[0]

        employee = {
            "EMPLOYEE_ID": EMPLOYEE_ID,
            "NAME": FIRST_NAME + " " + LAST_NAME,
            "DOB": DOB.strftime("%d-%b-%Y"),
            "IS_PENDING": IS_PENDING,
            "IS_APPROVED": IS_APPROVED,
            "JOB": JOB_TITLE,
            "DEPT": DEPT_NAME
        }
        employees.append(employee)

    cur.close()
    connection.close()

    if request.method == 'POST' and request.form['searchQuery']:
        searchQuery = request.form['searchQuery']
        employees = [e for e in employees if searchQuery.lower() in e['NAME'].lower()]

    return render_template('employees.html', data=employees)


@app.route('/assignments', methods=['GET', 'POST'])
def assignments():
    assignments = []
    connection = oracledb.connect(user=user, password=password, dsn=conn_string)

    cur = connection.cursor()
    cur.execute(asset_history_view)

    for row in cur:
        A_H_ID, ASSET_ID, EMPLOYEE_ID, REQUEST_ID, DATE_ASSIGNED = row
        
        cur2 = connection.cursor()
        EMPLOYEE_NAME = cur2.execute("SELECT FIRST_NAME, LAST_NAME FROM ASSETMANAGEMENT.EMPLOYEE WHERE EMPLOYEE_ID = " + str(EMPLOYEE_ID)).fetchone()
        EMPLOYEE_NAME = EMPLOYEE_NAME[0] + " " + EMPLOYEE_NAME[1]
        ASSET_NAME =  cur2.execute("SELECT A_NAME FROM ASSETMANAGEMENT.ASSET WHERE A_ID = " + str(ASSET_ID)).fetchone()[0]

        asset = {
            "A_H_ID": A_H_ID,
            "ASSET_NAME": ASSET_NAME,
            "EMPLOYEE_NAME": EMPLOYEE_NAME,
            "REQUEST_ID": REQUEST_ID,
            "DATE_ASSIGNED": DATE_ASSIGNED.strftime("%d-%b-%Y")
        }
        assignments.append(asset)

    cur.close()
    connection.close()

    if request.method == 'POST' and request.form['searchQuery']:
        searchQuery = request.form['searchQuery']
        assignments = [a for a in assignments if searchQuery.lower() in (a["ASSET_NAME"] + " " + a["EMPLOYEE_NAME"]).lower()]

    return render_template('assignments.html', data=assignments)

@app.route('/requests', methods=['GET', 'POST'])
def requests():
    requests = []
    connection = oracledb.connect(user=user, password=password, dsn=conn_string)

    cur = connection.cursor()
    cur.execute(request_view)

    for row in cur:
        R_ID, EMPLOYEE_ID, ASSET_ID, IS_OPEN, IS_APPROVED, CREATED_DATE, UPDATED_DATE = row

        cur2 = connection.cursor()  
        EMPLOYEE_NAME = cur2.execute("SELECT FIRST_NAME, LAST_NAME FROM ASSETMANAGEMENT.EMPLOYEE WHERE EMPLOYEE_ID = " + str(EMPLOYEE_ID)).fetchone() 
        EMPLOYEE_NAME = EMPLOYEE_NAME[0] + " " + EMPLOYEE_NAME[1]

        ASSET_NAME =  cur2.execute("SELECT A_NAME FROM ASSETMANAGEMENT.ASSET WHERE A_ID = " + str(ASSET_ID)).fetchone()[0]

        _request = {
            "R_ID": R_ID,
            "ASSET_NAME": ASSET_NAME,
            "EMPLOYEE_NAME": EMPLOYEE_NAME,
            "IS_OPEN": IS_OPEN,
            "IS_APPROVED": IS_APPROVED,
            "CREATED_DATE": CREATED_DATE.strftime("%d-%b-%Y"),
            "UPDATED_DATE": UPDATED_DATE.strftime("%d-%b-%Y") if UPDATED_DATE is not None else "Not Updated"
        }
        requests.append(_request)

    cur.close()
    connection.close()
    
    if request.method == 'POST' and request.form['searchQuery']:
        searchQuery = request.form['searchQuery']
        requests = [r for r in requests if searchQuery.lower() in (r["ASSET_NAME"] + " " + r["EMPLOYEE_NAME"]).lower()]
    
    return render_template('requests.html', data=requests)


@app.route('/requests/<rid>', methods=['GET'])
def view_request(rid):
    connection = oracledb.connect(user=user, password=password, dsn=conn_string)
    
    cur = connection.cursor()
    R_ID, ASSET_ID, EMPLOYEE_ID, IS_OPEN, IS_APPROVED, CREATED_DATE, UPDATED_DATE = cur.execute("SELECT R_ID, ASSET_ID, EMPLOYEE_ID, IS_OPEN, IS_APPROVED, CREATED_DATE, UPDATED_DATE FROM ASSETMANAGEMENT.REQUEST WHERE R_ID = " + rid).fetchone()
    
    ASSET_NAME = cur.execute("SELECT A_NAME FROM ASSETMANAGEMENT.ASSET WHERE A_ID = " + str(ASSET_ID)).fetchone()[0]

    EMPLOYEE_NAME = cur.execute("SELECT FIRST_NAME, LAST_NAME FROM ASSETMANAGEMENT.EMPLOYEE WHERE EMPLOYEE_ID = " + str(EMPLOYEE_ID)).fetchone()
    EMPLOYEE_NAME = EMPLOYEE_NAME[0] + " " + EMPLOYEE_NAME[1]

    connection.close()

    data = {
        "R_ID": R_ID,
        "ASSET_NAME": ASSET_NAME,
        "EMPLOYEE_NAME": EMPLOYEE_NAME,
        "IS_OPEN": IS_OPEN,
        "IS_APPROVED": IS_APPROVED,
        "CREATED_DATE": CREATED_DATE.strftime("%d-%b-%Y"),
        "UPDATED_DATE": UPDATED_DATE.strftime("%d-%b-%Y") if UPDATED_DATE is not None else "Not Updated"
    }

    return render_template('request.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
