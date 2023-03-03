import datetime
from flask import Flask, request, render_template
import oracledb
# Replace with your actual Oracle database credentials
user = 'SYSTEM'
password = 'root'
port = 1521
service_name = 'XE'
conn_string = "localhost:{port}/{service_name}".format(
    port=port, service_name=service_name)
app = Flask(__name__)
data = []
id = []

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/assets',methods=['GET'])
def update():
    assets = []
    connection = oracledb.connect(
        user=user, password=password, dsn=conn_string)
    cur = connection.cursor()
    cur.execute('SELECT A_ID, A_NAME, A_MODEL, IS_AVAILABLE, IS_RETIRED, CREATED_DATE FROM ASSETMANAGEMENT.ASSET')
    for row in cur:
        assets.append({"AID": row[0], "ANAME": row[1],
                    "AMODEL": row[2], "IS_AVAILABLE": row[3], "IS_RETIRED": row[4], "CREATED_DATE": row[5].strftime("%d-%b-%Y")})
    # Close the cursor and connection
    cur.close()
    connection.close()
    # Pass the data to the template to display in the HTML table
    return render_template('assets.html', data=assets)
    #return render_template('about.html')





if __name__ == '__main__':
    app.run(debug=True)
