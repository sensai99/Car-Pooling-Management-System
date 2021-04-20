from authy.api import AuthyApiClient
from flask import Flask, render_template, redirect, session, url_for, request, Response
from flask_mysqldb import MySQL
import MySQLdb

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = '12345'

api = AuthyApiClient(app.config['AUTHY_API_KEY'])

app.config['MYSQL_HOST'] = "127.0.0.1"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "softeng@123"
app.config['MYSQL_DB'] = "login_info"


db = MySQL(app)


# for default page
@app.route('/')
def home():
    session['flag_signup'] = 1
    return render_template("Page_Basic.html")

# for login page
@app.route('/login', methods = ['GET', 'POST'])
def login():

    msg = ''
    if request.method == 'POST':

        if 'mobilenumber' in request.form and 'password' in request.form:

            mobilenumber = int(request.form['mobilenumber'])
            password = request.form['password']

            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM logininfo_t WHERE mobilenumber=%s AND password=%s', (mobilenumber, password))
            info = cursor.fetchone()

            # if the entered mobilenumber and password pair is present in the DB...
            if info:

                session['mobilenumber'] = info['mobilenumber']
                session['username'] = info['username']

                msg = 'Logged in successfully!'
                # return render_template('Page_Account.html', msg = msg)
                return redirect(url_for('dashboard'))
            
            # if the entered details are wrong
            else:
                msg = 'Incorrect mobilenumber / password!'
            
    return render_template('login.html', msg = msg)


# for logout page
@app.route('/logout')
def logout():
    session.pop('mobilenumber', None)
    session.pop('username', None)
    session.pop('chattines', None)
    session.pop('smoking', None)
    session.pop('pets', None)
    session.pop('music', None)
    return redirect(url_for('home'))


# for signup page - related to mobile number registration
@app.route('/signupNum', methods=['POST', 'GET']) 
def signupNum():

    if request.method == 'POST':

        mobilenumber = request.form['mobilenumber']
        session['mobilenumber'] = mobilenumber
        session['flag_signup'] = 1

        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM logininfo_t WHERE mobilenumber=%s',([mobilenumber]))
        info = cursor.fetchall()
        
        if info:
            return render_template('signup_mobNum.html',exists='yes')
        
        else:
            api.phones.verification_start(mobilenumber, country_code = '+91', via = 'sms')
            return redirect(url_for('verify'))

    return render_template('signup_mobNum.html')


# for signup page - related to verifying the mobilenumber
@app.route('/verify', methods = ['POST', 'GET'])
def verify():

    if request.method == 'POST':

        otp = request.form['otp']
        mobilenumber = session['mobilenumber']

        verification = api.phones.verification_check(mobilenumber, '+91', otp)

        if verification.ok():

            if session['flag_signup'] == 1:
                # return Response('<h1>verification successful!</h1>')
                return redirect(url_for('signupDetails'))
            else:
                # redirect to update password page
                return redirect(url_for('update_password'))

        else:
            return Response('<h1>Verification unsuccessful!</h1>')

    
    return render_template('signup_verifyNum.html')


# for sign page - related to user details
@app.route('/signupDetails', methods = ['POST', 'GET'])
def signupDetails():

    if request.method == 'POST':

        session['username'] = username = request.form['username']
        session['dob'] = dob = str(request.form['dob'])

        # check how to make this secure
        session['password'] = password = request.form['password']

        # retrieving the mobilenumber and dob of the current user
        mobilenumber = session['mobilenumber']

        print('mobilenumber', mobilenumber)

        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO `login_info`.`logininfo_t`(`mobilenumber`, `password`, `username`, `dob`)VALUES(%s, %s, %s, %s)', (mobilenumber, password, username, dob))
        db.connection.commit()
        # cursor.execute('SELECT * FROM logininfo_t WHERE mobilenumber=%s AND password=%s', (mobilenumber, password))

        return redirect(url_for('dashboard'))

    return render_template('signup_details.html')


# for Default user account page - Page_Account.html
@app.route('/dashboard')
def dashboard():
    return render_template('Page_Account.html')


# for offer a ride page
@app.route('/offer-ride', methods=['POST', 'GET'])
def offer_ride():
    
    if request.method == 'POST':
        
        source = request.form['source']
        destination = request.form['destination']
        
        if source and destination:
            return redirect(url_for('post_route'))
    
    return render_template('OfferaRide.html')


# for find a ride page
@app.route('/find-ride')
def find_ride():
    return render_template('FindaRide.html')


@app.route('/post-route', methods=['POST', 'GET'])
def post_route():
    # select = request.form('passengers_select')
    # fare = request.form('farepkm')
    # print(select, fare)
    
    # # if select and fare:
    #     return redirect(url_for('dashboard'))

        
    return render_template('PostRoute.html')



# for forgot password page
@app.route('/forgot-password', methods = ['POST', 'GET'])
def forgot_password():

    if request.method == 'POST':

        mobilenumber = session['mobilenumber'] = request.form['mobilenumber']

        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM logininfo_t WHERE mobilenumber=%s', [mobilenumber])
        info = cursor.fetchone()

        print('im in')
        # if the entered mobilenumber exists in the database
        if info:

            print('im in - 1')

            # send the verification code
            api.phones.verification_start(mobilenumber, country_code = '+91', via = 'sms')

            # flag to pass to the verify function
            session['flag_signup'] = 0

            print(session['flag_signup'])

            return redirect(url_for('verify'))

        # if the entered mobilenumber doesn't exist in the database
        else:
            return Response('<h1> Wrong Mobilenumber </h1>')

    return render_template('forgotpass.html')


# for update password page
@app.route('/update-password', methods=['POST', 'GET'])
def update_password():

    if request.method == 'POST':

        password = request.form['password']

        mobilenumber = session['mobilenumber']

        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE `logininfo_t` SET `password` = %s WHERE `mobilenumber` = %s', (password, mobilenumber))
        db.connection.commit()

        return redirect(url_for('login'))

    return render_template('updatepass.html')


# for profile page
@app.route('/profile', methods=['POST', 'GET'])
def profile():

    mobilenumber = session['mobilenumber']
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM logininfo_t WHERE mobilenumber=%s', [mobilenumber])
    info = cursor.fetchone()

    # if entry found
    if info:

        preferences = info['preferences']

        if preferences[0] == 'Y':
            session['chattines'] = 'yes'
        elif preferences[0] == 'N':
            session['chattines'] = 'no'
        else:
            session['chattines'] = 'N/A'

        if preferences[1] == 'Y':
            session['smoking'] = 'yes'
        elif preferences[1] == 'N':
            session['smoking'] = 'no'
        else:
            session['smoking'] = 'N/A'

        if preferences[2] == 'Y':
            session['pets'] = 'yes'
        elif preferences[2] == 'N':
            session['pets'] = 'no'
        else:
            session['pets'] = 'N/A'

        if preferences[3] == 'Y':
            session['music'] = 'yes'
        elif preferences[3] == 'N':
            session['music'] = 'no'
        else:
            session['music'] = 'N/A'
        


    return render_template('profile.html')

# for travel preferences page
@app.route('/travel-preferences', methods=['POST', 'GET'])
def travel_preferences():

    if request.method == 'POST':

        session['chattines'] = chattines = request.form['chattines']
        session['smoking'] = smoking = request.form['smoking']
        session['pets'] = pets = request.form['pets']
        session['music'] = music = request.form['music']
        

        preferences = ''
        if chattines == 'yes':
            preferences += 'Y'
        elif chattines == 'no':
            preferences += 'N'
        else:
            preferences += 'X'

        if smoking == 'yes':
            preferences = 'Y'
        elif smoking == 'no':
            preferences += 'N'
        else:
            preferences += 'X'

        if pets == 'yes':
            preferences += 'Y'
        elif pets == 'no':
            preferences += 'N'
        else:
            preferences += 'X'

        if music == 'yes':
            preferences += 'X'
        elif music == 'no':
            preferences += 'N'
        else:
            preferences += 'X'


        mobilenumber = session['mobilenumber']

        # update these preferences to the database
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE `logininfo_t` SET `preferences` = %s WHERE `mobilenumber` = %s', (preferences, mobilenumber))
        db.connection.commit()


        return redirect(url_for('profile'))

    return render_template('travelpreferences.html')


if __name__ == '__main__':
    app.run(debug = True)