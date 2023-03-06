from functools import wraps
from flask import Flask, flash, redirect, render_template, request, url_for, session
import oracledb

user = 'SYSTEM'
password = 'root'
port = 1521
service_name = 'XEPDB1' # XE or XEPDB1 depending on your setup version
conn_string = "localhost:{port}/{service_name}".format(port=port, service_name=service_name)

# ASSET VIEW
asset_view = "SELECT A_ID, A_NAME, BRAND, COMPANY_ID,  A_MODEL, IS_AVAILABLE, IS_RETIRED, CREATED_DATE, UPDATED_DATE FROM ASSETMANAGEMENT.ASSET"
company_name_view  = "SELECT C_NAME FROM ASSETMANAGEMENT.COMPANY WHERE C_ID ="

# ASSIGNMENT VIEW
asset_history_view = "SELECT A_H_ID, ASSET_ID, EMPLOYEE_ID, REQUEST_ID, DATE_ASSIGNED FROM ASSETMANAGEMENT.ASSET_HISTORY"

# EMPLOYEE VIEW
employee_view = "SELECT EMPLOYEE_ID, FIRST_NAME, LAST_NAME, DOB, IS_PENDING, IS_APPROVED, JOB_ID, DEPT_ID, LOGIN_ID FROM ASSETMANAGEMENT.EMPLOYEE"
employee_view_job = "SELECT TITLE FROM ASSETMANAGEMENT.JOB WHERE J_ID ="
employee_view_dept = "SELECT D_NAME FROM ASSETMANAGEMENT.DEPARTMENT WHERE D_ID ="

# REQUEST VIEW
request_view = "SELECT R_ID, EMPLOYEE_ID, ASSET_ID, IS_OPEN, IS_APPROVED, CREATED_DATE, UPDATED_DATE FROM ASSETMANAGEMENT.REQUEST"


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'uuid' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

def coordinator_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'uuid' in session:
            connection = oracledb.connect(user=user, password=password, dsn=conn_string)
            cur = connection.cursor()
            u = cur.execute("SELECT JOB_ID FROM ASSETMANAGEMENT.EMPLOYEE WHERE LOGIN_ID = " + str(session['uuid']) + "").fetchone()[0]
            if u == 1:
                return f(*args, **kwargs)
            else:
                flash('You are not a coordinator.')
                return redirect(url_for('home'))
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

def is_coordinator(uuid):
    connection = oracledb.connect(user=user, password=password, dsn=conn_string)
    cur = connection.cursor()
    xx = cur.execute("SELECT EMPLOYEE_ID FROM ASSETMANAGEMENT.COORDINATOR WHERE EMPLOYEE_ID = " + str(uuid))
    if xx is not None:
        return True
    else:
        return False

@app.route('/')
def home():
    u = session['uuid'] if 'uuid' in session else None
    
    if u is not None:
        connection = oracledb.connect(user=user, password=password, dsn=conn_string)
        cur = connection.cursor()
        u = cur.execute("SELECT FIRST_NAME FROM ASSETMANAGEMENT.EMPLOYEE WHERE LOGIN_ID = " + str(u) + "").fetchone()[0]

    
    return render_template('home.html', data=u)


@app.route('/assets',methods=['GET', 'POST'])
@login_required
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
@login_required
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
@coordinator_required
def employees():
    employees = []
    connection = oracledb.connect(user=user, password=password, dsn=conn_string)

    cur = connection.cursor()
    cur.execute(employee_view)

    for row in cur:
        EMPLOYEE_ID, FIRST_NAME, LAST_NAME, DOB, IS_PENDING, IS_APPROVED, JOB_ID, DEPT_ID, LOGIN_ID = row
        
        cur2 = connection.cursor()
        JOB_TITLE = cur2.execute(employee_view_job+str(JOB_ID)).fetchone()[0]
        DEPT_NAME = cur2.execute(employee_view_dept+str(DEPT_ID)).fetchone()[0]
        EMAIL = cur2.execute("SELECT EMAIL_ADDRESS FROM ASSETMANAGEMENT.LOGIN WHERE L_ID="+str(LOGIN_ID)).fetchone()[0]
        employee = {
            "EMPLOYEE_ID": EMPLOYEE_ID,
            "NAME": FIRST_NAME + " " + LAST_NAME,
            "DOB": DOB.strftime("%d-%b-%Y"),
            "IS_PENDING": IS_PENDING,
            "IS_APPROVED": IS_APPROVED,
            "JOB": JOB_TITLE,
            "DEPT": DEPT_NAME,
            "EMAIL":EMAIL
        }
        employees.append(employee)

    cur.close()
    connection.close()

    if request.method == 'POST' and request.form['searchQuery']:
        searchQuery = request.form['searchQuery']
        employees = [e for e in employees if searchQuery.lower() in e['NAME'].lower()]

    return render_template('employees.html', data=employees)


@app.route('/assignments', methods=['GET', 'POST'])
@login_required
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
@login_required
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
    print(session["uuid"])
    print(is_coordinator(session["uuid"]))
    return render_template('requests.html', data=requests, coordinator=is_coordinator(session["uuid"]))

@app.route('/requests/<rid>', methods=['GET'])
@login_required
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


#Create Asset
@app.route('/assets/create/', methods=['GET', 'POST'])
@login_required
def create_asset():
    if request.method == 'GET':
        return render_template('create_asset.html')
    
    if request.method == 'POST':
        connection = oracledb.connect(user=user, password=password, dsn=conn_string)

        #Check for empty fields
        if request.form['name'] == "" or request.form['brand'] == "" or request.form['company'] == "" or request.form['model'] == "":
            return render_template('create_asset.html', error="Please fill in all fields")
        #checkboxes are not included in request.form if they are not checked.
        if 'available' not in request.form:
            available = 0
        else:
            available = 1
        if 'retired' not in request.form:
            retired = 0
        else:
            retired = 1
        
        #check if company exists
        cur3 = connection.cursor()
        cur3.execute("SELECT C_ID FROM ASSETMANAGEMENT.COMPANY WHERE C_NAME = '" + request.form['company'] + "'")
        cur3 = cur3.fetchone()
        if cur3 == None:
            #company does not exist, create it
            cur5 = connection.cursor()
            cur5.execute(f"INSERT INTO ASSETMANAGEMENT.COMPANY VALUES (DEFAULT, '{request.form['company']}')")
            connection.commit()
            cur5.close()
            #set cid to the id of the company we just created
            cur4 = connection.cursor()
            cur4.execute("SELECT C_ID FROM ASSETMANAGEMENT.COMPANY WHERE C_NAME = '" + request.form['company'] + "'")
            cid = cur4.fetchone()[0]
        else:
            #company exists, set cid to the id of the company, happy path
            cid = cur3[0]
        
        cur2 = connection.cursor()
        cur2.execute(f"INSERT INTO ASSETMANAGEMENT.ASSET VALUES (DEFAULT, '{request.form['name']}', '{request.form['brand']}', '{cid}', '{request.form['model']}', {available}, {retired}, CURRENT_TIMESTAMP, NULL)")
        connection.commit()
        cur2.close()
        connection.close()
        return redirect(url_for('assets'))
    
# Create request
@app.route('/requests/create/', methods=['GET', 'POST'])
@login_required
def create_request():
    if request.method == 'GET':
        assets = []
        connection = oracledb.connect(user=user, password=password, dsn=conn_string)

        cur = connection.cursor()
        cur = cur.execute("SELECT A_ID, A_NAME, BRAND, COMPANY_ID,  A_MODEL, IS_AVAILABLE, IS_RETIRED, CREATED_DATE, UPDATED_DATE FROM ASSETMANAGEMENT.ASSET WHERE IS_AVAILABLE = 1 AND IS_RETIRED = 0")
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
        cur2 = connection.cursor()
        cur2.execute("SELECT FIRST_NAME, LAST_NAME FROM ASSETMANAGEMENT.EMPLOYEE WHERE EMPLOYEE_ID = " + str(session['uuid']))
        cur2 = cur2.fetchone()
        name = cur2[0] + " " + cur2[1]
        connection.close()
        return render_template('create_request.html', assets=assets, name=name)
    
    if request.method == 'POST':
        connection = oracledb.connect(user=user, password=password, dsn=conn_string)

        cur = connection.cursor()
        cur.execute(f"INSERT INTO ASSETMANAGEMENT.REQUEST VALUES (DEFAULT, {session['uuid']}, {request.form['request']}, 1, 0, CURRENT_TIMESTAMP, NULL)")
        connection.commit()
        cur.close()
        connection.close()
        return redirect(url_for('requests'))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        connection = oracledb.connect(user=user, password=password, dsn=conn_string)

        email = request.form['email']
        lpassword = request.form['password']
        cur = connection.cursor()
        cur.execute("SELECT L_ID FROM ASSETMANAGEMENT.LOGIN WHERE EMAIL_ADDRESS = '" + email + "' AND L_PASSWORD = '" + lpassword + "'")
        result = cur.fetchone()[0]
        uuid = cur.execute("SELECT EMPLOYEE_ID FROM ASSETMANAGEMENT.EMPLOYEE WHERE LOGIN_ID = " + str(result)).fetchone()[0]
        if result is None:
            return render_template('login.html', error="Invalid Credentials")
        else:
            session['uuid'] = result
            return redirect(url_for('home'))
    return render_template('login.html')

#Create Assignment
"""
Request becomes not open
Asset becomes not available
assignment logged in asset history
"""
@app.route('/assignment/approve/', methods=['POST'])
@login_required
@coordinator_required
def approve_request():
    if request.method == 'POST':
        connection = oracledb.connect(user=user, password=password, dsn=conn_string)
        cur = connection.cursor()
        cur.execute("SELECT * FROM ASSETMANAGEMENT.REQUEST WHERE R_ID = " + request.form['request'])
        cur = cur.fetchone()
        print(cur[0])
        employee_id = cur[1]
        asset_id = cur[2]
        cur = connection.cursor()
        cur.execute("UPDATE ASSETMANAGEMENT.ASSET SET IS_AVAILABLE = 0 WHERE A_ID = " + str(asset_id))
        connection.commit()
        cur.close()
        cur = connection.cursor()
        cur.execute("UPDATE ASSETMANAGEMENT.REQUEST SET IS_OPEN = 0 WHERE R_ID = " + str(request.form['request']))
        connection.commit()
        cur.close()
        cur = connection.cursor()
        cur.execute(f"INSERT INTO ASSETMANAGEMENT.ASSET_HISTORY VALUES (DEFAULT, {asset_id}, {employee_id}, {request.form['request']}, DEFAULT, NULL)")
        connection.commit()
        cur.close()
        connection.close()
        return redirect(url_for('requests'))

@app.route('/logout')
def logout():
    session.pop('uuid', None)
    flash('You were logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
