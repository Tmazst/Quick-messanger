
from flask import Flask,render_template,url_for,redirect,request,flash,jsonify,session, send_from_directory
from flask_login import login_user, LoginManager,current_user,logout_user, login_required
from Forms import Register, Login,Contact_Form, Project_Form, Web_Design_Brief,Logo_Options,Poster_Options,Brochure_Options,Flyer_Options
from models import *
from flask_bcrypt import Bcrypt
import secrets
import os
from Forms import *
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
# from bs4 import BeautifulSoup as bs
from flask_colorpicker import colorpicker
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import FileStorage
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from itsdangerous import URLSafeSerializer
import pytz
from pywebpush import webpush, WebPushException
import json
from sqlalchemy import or_
import re
from QM_validators import PhoneValidator, PhoneNumberError
from hashlib import pbkdf2_hmac
import base64
import threading
from datetime import timedelta
from flask_wtf.csrf import CSRFProtect



#Did latest commit with the requirement file

#Change App
app = Flask(__name__)
app.config['SECRET_KEY'] = "45BFdfhfh-IKMwnfhdfcA7cR08RWECfzfhfdhfdfmYHFCeXFx97-P2_ZFxddfhfddfhdhdf5DDHtyoEP4yYCQ38aIVjI"
csrf = CSRFProtect(app)

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle':280}
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOADED"] = 'static/uploads'
app.config["ADVERTS_IMAGES"] = 'static/ad-images'
app.config["NEWS_IMAGES"] = 'static/comp-images'
app.config["VAPID_PRIVATE_KEY"] = "tACNLzOyTBgxLxmT7A9ZDhdhA-9y3l6DHMrLuMoBvYM"
app.config["VAPID_PUBLIC_KEY"] = "BF-IKMwncA7cR08RWECfzfmYHFCeXFx97-P2_ZFxd5DDHHryXyjBC6bzKa5oYkmN-DhjNYtyoEP4yYCQ38aIVjI"

# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://techtlnf_tmaz:!Tmazst41#@localhost/techtlnf_quick_m_db" 
# Local
if os.environ.get('EMAIL_INFO') == 'info@techxolutions.com':
    app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://root:tmazst41@localhost/quick_messanger' #"sqlite:///business_chat_db3.db"
else:#Online
    app.config[
    "SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://techtlnf_tmaz:!Tmazst41#@localhost/techtlnf_quick_m_db" 


VAPID_PRIVATE_KEY = app.config["VAPID_PRIVATE_KEY"]
VAPID_PUBLIC_KEY = app.config["VAPID_PUBLIC_KEY"] 
VAPID_CLAIMS = {
    "sub": "mailto:pro.dignitron@gmail.com"
}

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)

db.init_app(app)
CORS(app)  # Allow cross-origin requests

# export db after init 
DB_INIT = db

login_manager = LoginManager(app)
login_manager.login_view = "register"

# Encrypt Password
encrypt_password = Bcrypt(app)

@app.template_filter('liked_by_ip')
def liked_by_ip(likes, remote_ip):
    return any(like.ip == remote_ip for like in likes)

# Log in
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# @login_manager.unauthorized_handler
# def custom_unauthorized():
#     if request.accept_mimetypes.accept_json or request.is_json or request.path.startswith("/api"):
#         return jsonify({"error": "Unauthorized", "message": "Please log in"}), 401
#     flash("Please Register or Login to Access your Account", "warning")
#     return redirect(url_for("register"))

application = app

# email credentials 
if os.path.exists('client.json'):
    # Load secrets from JSON file
    with open('client.json') as f:
        creds = json.load(f)

def current_time_wlzone():
    # Get the current UTC time
    timestamp = datetime.now(pytz.utc)

    # Define the user's timezone
    user_timezone = 'Africa/Mbabane'  # Replace this with the user's timezon

    # Create a timezone object
    local_tz = pytz.timezone(user_timezone)

    # Convert UTC time to user's local tim
    local_time = timestamp.astimezone(local_tz)

    return local_time


ALLOWED_EXTENSIONS = {"txt", "xlxs",'docx', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

from PIL import Image

def compress_image(file_path, max_size_kb=150, quality=85):
    img = Image.open(file_path)
    img_format = img.format
    # Only compress if file is larger than max_size_kb
    if os.path.getsize(file_path) > max_size_kb * 1024:
        # For JPEG/WEBP, use quality; for PNG, use optimize
        if img_format in ['JPEG', 'JPG', 'WEBP']:
            img.save(file_path, format=img_format, quality=quality, optimize=True)
        elif img_format == 'PNG':
            img.save(file_path, format=img_format, optimize=True)
        print(f"Compressed: {file_path}")

def compress_folder(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                compress_image(os.path.join(root, file))


# Function to check if the file has an allowed extension
def allowed_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_news(file):

    return process_and_compress_upload(file, app.config["NEWS_IMAGES"])

def process_file(file):

    return process_and_compress_upload(file, app.config["UPLOADED"])

def process_ads(file):

    return process_and_compress_upload(file, app.config["ADVERTS_IMAGES"])

# Universal function to process and compress uploaded images
def process_and_compress_upload(file, save_folder, max_size_kb=150, quality=85):
    filename = secure_filename(file.filename)
    _img_name, _ext = os.path.splitext(filename)
    gen_random = secrets.token_hex(8)
    new_file_name = gen_random + _ext

    if file.filename == '':
        return 'No selected file'

    if file.filename:
        save_path = os.path.join(save_folder, new_file_name)
        file.save(save_path)
        # Only compress if it's an image
        try:
            from PIL import Image
            img = Image.open(save_path)
            img_format = img.format
            if os.path.getsize(save_path) > max_size_kb * 1024:
                if img_format in ['JPEG', 'JPG', 'WEBP']:
                    img.save(save_path, format=img_format, quality=quality, optimize=True)
                elif img_format == 'PNG':
                    img.save(save_path, format=img_format, optimize=True)
                print(f"Compressed: {save_path}")
        except Exception as e:
            print(f"Not an image or compression failed: {e}")
        print(f"File Upload Successful!!", "success")
        return new_file_name
    else:
        return f"Allowed are [.txt, .xls,.docx, .pdf, .png, .jpg, .jpeg, .gif] only"

def createall(db_):
    db_.create_all()

encry_pw = Bcrypt()

# @app.route("/username/<username>", methods=['POST','GET'])
def get_all_messages():
 
    usr = session.get("username", "")
    if usr:
        usr = serializer.loads(usr)

    print(" Ran First: ", usr)
    message_list = None
    if usr:
    # Only get messages where key == current user
        message_list = Messages.query.filter(Messages.key == usr).order_by(Messages.date.desc()).all()
        #..I am getting all the latest messages with my key
        if not message_list:
            print("No Messages Found")
            return []
        print("Step 1: ", message_list)
        latest_messages = {}
        for msg in message_list:
            # The other user is always the one who is not the current user
            #..all the keys listed in message_list are my username
            #..other; should always be the person i am receiving the msg from or sending to so that i can decrypt and display them on the UI(message buttons)
            #..these msg with my key are encrypted with my pkey
            other = msg.receiver if msg.sender == usr else msg.sender
            #Here I am checking if the other(the person i am chatting with) user is not in the latest messages (add if not present)
            #..or present but, the date of the current message is greater than the one in latest_messages
            if other not in latest_messages or msg.date > latest_messages[other].date:
            #...if yes, then I add the message to the latest_messages dictionary
                latest_messages[other] = msg
        print("Step 2: ", latest_messages)
        return list(latest_messages.values())

    else:
        return []

all_msgs = None

ser = Serializer(app.config['SECRET_KEY']) 

@app.context_processor
def inject_ser():

    companies = company_info.query.all()
    messages = get_all_messages()
    current = None
    company = None
    usr_obj = None

    check_user_ndb = session.get("username", "")
    if check_user_ndb:
        check_user_ndb = serializer.loads(check_user_ndb)

    chk_user = chat_user.query.filter_by(username=check_user_ndb).first()#confirm user in db
    if chk_user:
        print("inject_ser==Currently in Session: ",check_user_ndb )
        current = chk_user.username 
        company = company_info.query.filter_by(usr_fKey=chk_user.id).first()
        print("inject_ser==Company To Dict Object: ", company)
        usr_obj = User.query.filter_by(cht_usr_fKey=chk_user.id).first()
        login_user(usr_obj)
        # print("inject_ser==Company Resolved: ")
    else:
        session['c_user'] = ""
        print("inject_ser==Username not Found, company object not resolved: ",session.get('username'))

    return dict(current=current,messages=messages, company=company,usr_obj =usr_obj,ser=ser,companies=companies,usrn = chat_user )

@app.route("/username/<username>/<id>", methods=['POST','GET'])
def username(username,id):
    print("username== Ran Late; User", username)
    # if not current_user.is_authenticated:
    if username:
        session['c_user'] = username
        print("username==user updated in session")
        db_username = chat_user.query.filter_by(username=username).first()
        if db_username:
            usr = User.query.filter_by(cht_usr_fKey=db_username.id).first()
            if usr:
                login_user(usr)
                print("username==Login a success")
            else:
                print("username==Failed login user not found")
            session['_no'] = db_username.id 
            print("username==Current User: ",db_username)
        else:
            print("username==User Not Found in DB: ", username)
            print("username==User Resolved from JS: ", username)
            return jsonify({"User":"User Not in DB"}),200
    else:
        session['c_user'] = ""
        session['_no'] = ""


    return jsonify({"User":"Success"}),200

import africastalking

# Initialize Africa's Talking
AT_USERNAME = "thabo"  # Replace with your Africa's Talking username
AT_API_KEY = "atsk_8f084216094ad2630840078202328804584781195f017493341390e99016c0f6bf96f6c8"    # Replace with your Africa's Talking API key

africastalking.initialize(AT_USERNAME, AT_API_KEY)
sms = africastalking.SMS

def send_sms_via_africastalking(phone, message,):
    try:
        response = sms.send(message, [phone])  # Replace with your sender ID
        print("SMS sent:", response)
        return {"status": "success", "response": response}
    except Exception as e:
        print("SMS sending failed:", e)
        return {"status": "error", "error": str(e)}

@app.route('/send_sms') #, methods=['POST']
def send_af_sms():
    print("Phone Number to Validate:xxx ")
    # data = request.get_json()sender="20404" 
    all_companies = company_info.query.all()
    # if not phone or not message:
    #     return jsonify({'status': 'error', 'msg': 'Phone and message required'}), 400
    results = []
    sent_numbers = set()
    for company in all_companies:
        if company and company.company_contacts:
            print("Company: ", company, "Company Contacts: ", company.company_contacts)
            company_name = company.company_name
            if len(company_name) > 17:
                company_name = company_name[:17] + "..."
            phone = company.company_contacts
            phone_validator = PhoneValidator
            try:
                val_phone = phone_validator(phone).validate()
                # Only send if this number hasn't been sent to yet
                if val_phone in sent_numbers:
                    continue
                sent_numbers.add(val_phone)
                message = f"Welcome to Quick Messanger {company_name}! Grow your market presence, improve B2B/B2C communication & build networks. Visit: https://qm.techxolutions.com"
                result = send_sms_via_africastalking(val_phone, message)
                results.append({"company": company_name, "status": "success", "response": result})
            except PhoneNumberError as e:
                flash(f"Invalid phone number: {e}", "danger")
                results.append({"company": company_name, "status": "error", "error": str(e)})
                continue
    return jsonify(results)


@app.route('/sms_marketing_form') #, methods=['POST']
def sms_marketing():
    print("Phone Number to Validate:xxx ")
    # data = request.get_json()sender="20404" 
    all_companies = company_info.query.all()
    form = SMSMarketingForm()
    # if not phone or not message:
    #     return jsonify({'status': 'error', 'msg': 'Phone and message required'}), 400
    results = []
    sent_numbers = set()
    for company in all_companies:
        if company and company.company_contacts:
            print("Company: ", company, "Company Contacts: ", company.company_contacts)
            company_name = company.company_name
            if len(company_name) > 17:
                company_name = company_name[:17] + "..."
            phone = company.company_contacts
            phone_validator = PhoneValidator
            try:
                val_phone = phone_validator(phone).validate()
                # Only send if this number hasn't been sent to yet
                if val_phone in sent_numbers:
                    continue
                sent_numbers.add(val_phone)
                message = f"Welcome to Quick Messanger {company_name}! Grow your market presence, improve B2B/B2C communication & build networks. Visit: https://qm.techxolutions.com"
                result = send_sms_via_africastalking(val_phone, message)
                results.append({"company": company_name, "status": "success", "response": result})
            except PhoneNumberError as e:
                flash(f"Invalid phone number: {e}", "danger")
                results.append({"company": company_name, "status": "error", "error": str(e)})
                continue
    return jsonify(results)


@app.route('/send_to_one') #, methods=['POST']
def send_af_one():

    results = []

    company = company_info.query.filter_by(company_name="Tech Xolutions").first()

    if company and company.company_contacts:
        print("Company: ", company, "Company Contacts: ", company.company_contacts)
        company_name = company.company_name
        if len(company_name) > 17:
            company_name = company_name[:17] + "..."
        phone = company.company_contacts
        phone_validator = PhoneValidator
        try:
            val_phone = phone_validator(phone).validate()
            # Only send if this number hasn't been sent to yet
            
            message = f"Welcome to Quick Messanger {company_name}! Grow your market presence, improve B2B/B2C communication & build networks. Visit: https://qm.techxolutions.com"
            result = send_sms_via_africastalking(val_phone, message)
            results.append({"company": company_name, "status": "success", "response": result})
        except PhoneNumberError as e:
            flash(f"Invalid phone number: {e}", "danger")
            results.append({"company": company_name, "status": "error", "error": str(e)})
            
    return jsonify(results)


@app.route('/follow_company', methods=['POST', 'GET'])
def follow_company():

    # flask db migrate -m "Add description column to CompanyInfo"
    data = request.get_json()
    cid = data.get('cid')
    # cid = ser.loads(company_id)['cid']
    print("Follow Company==Company ID: ", cid)
    if not cid:
        return jsonify({'status': 'error', 'msg': 'Company name required'}), 400

    # Check if the company exists
    company = company_info.query.get(cid)
    print("Follow Company==Company Object: ", company)
    if not company:
        return jsonify({'status': 'error', 'msg': 'Company not found'}), 404
    
    # Check if the user is already following the company
    if current_user.is_authenticated:
        existing_follower = Followers.query.filter_by(user_id=current_user.id, company_id=cid).first()
        if existing_follower:
            return jsonify({'status': 'success', 'msg': f'You are already following {company.company_name}'}), 200
    
    existing_follower = Followers.query.filter_by(ip_address=request.remote_addr, company_id=cid).first()
    if existing_follower:
        return jsonify({'status': 'success', 'msg': f'You are already following {company.company_name}'}), 200

    followers = Followers(ip_address=request.remote_addr,company_id=cid) #ip_address=request.remote_addr,

    # Add the user to the company's followers
    if current_user.is_authenticated:
        followers.user_id = current_user.id
        
    db.session.add(followers)
    db.session.commit()
    return jsonify({'status': 'success', 'msg': f'You are now following {company.company_name}'}), 200

# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# # Google Sheets setup (do this once at the top of your file)
# SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# CREDS = ServiceAccountCredentials.from_json_keyfile_name('appenda-d102d5f024d6.json', SCOPE)
# gc = gspread.authorize(CREDS)
# SHEET = gc.open('qm_jsons').sheet1  # Replace with your sheet name

# @app.route('/queue_sms', methods=['POST'])
# def queue_sms():
#     data = request.get_json()
#     phone = data.get('phone')
#     message = data.get('message')
#     if not phone or not message:
#         return jsonify({'status': 'error', 'msg': 'Phone and message required'}), 400

#     # Add new row: phone, message, status, timestamp
#     SHEET.append_row([phone, message, 'pending', datetime.now().isoformat()])
#     return jsonify({'status': 'success', 'msg': 'SMS job queued'})

serializer = URLSafeSerializer(app.config['SECRET_KEY'])



@app.route("/", methods=['POST','GET'])
def home():

    # Example usage:
    # compress_folder(app.config["NEWS_IMAGES"])
    # compress_folder(app.config["ADVERTS_IMAGES"])
    # compress_folder(app.config["UPLOADED"])

    msd_del = Messages.query.get(81)

    if msd_del:
        db.session.delete(msd_del)
        db.session.commit()

    with app.app_context():
        db.create_all()
        db.session.commit()
        
    print("Hoping for a call")
    visitor_ip = request.remote_addr

    chk_if_reg = Visitors.query.filter_by(ip=visitor_ip).first()

    if current_user and current_user.is_authenticated:
        company = company_info.query.filter_by(usr_id=current_user.id).first()
        if company and company.company_name:
            if company.image == "logo-avator.png" or not company.email:
                flash("Please Finish Company Registration","warning")
                print("Company Name: ",)
                return redirect(url_for("company_account"))

    if chk_if_reg:
        print("Hoping for a redirect")
        chk_if_reg.last_visit = current_time_wlzone()
        chk_if_reg.n_visits += 1
        db.session.commit()
        return redirect(url_for("business_community"))
    else:
        visit_obj = Visitors(
            ip = visitor_ip,
            n_visits = 1,
            timestamp = current_time_wlzone(),
            first_visit = current_time_wlzone(),
        )

        db.session.add(visit_obj)
        db.session.commit()

        return redirect(url_for("business_community"))

    # Get all company logos (excluding empty or default ones)
    all_logos = [c.image for c in company_info.query.all() if c.image and c.image != "default.jpg"]

    # all_messages = get_all_messages()
    # latest_entry = Messages.query.filter_by(sender=user.id).order_by(Messages.date.desc()).first()
    # return redirect(url_for('home'))
    qm_bs_obj = company_info.query.filter_by(company_name="Quick Messanger").first()
    latest_req=None
    if latest_req:
        latest_req = company_info.query.order_by(company_info.id.asc()).all()[1]
    messages = get_all_messages()
    print("Home==Companies Showcasing: ", qm_bs_obj, latest_req)
    del_al_msgs = Messages.query.all()
    for msg in del_al_msgs:
        if msg.sender == "none" or msg.receiver == "none":
            db.session.delete(msg)
            db.session.commit()
            print("Home==Deleted Messages: ", msg)

    return render_template("index.html", qm_bs_obj=qm_bs_obj,latest_req=latest_req,all_logos=all_logos)

# Key saved in DB, file encrypted and saved in cloud or server
@app.route('/save_recovery_data', methods=['POST'])
def save_recovery_data1():
    data = request.get_json()
    username = data.get('username')
    encrypted_json = data.get('encrypted_json')
    
    cuser = chat_user.query.filter_by(username=username).first()
    if not cuser:
        return jsonify({'status': 'error', 'msg': 'User not found'}), 404
    
    user = User.query.get(cuser.id)

    if not user:
        return jsonify({'status': 'error', 'msg': 'User not found'}), 404

    # Save encrypted JSON to cloud or server (example: local file, S3, or Google Drive)
    # For demo, save to a file named after the user

    with open(f'working_files/{username}_working_file.json', 'w') as f:
        json.dump(encrypted_json, f)
    # SHEET.append_row([username, json.dumps(encrypted_json)])

    update_urecov_status = recovery_check_v2.query.filter_by(username=username).first()
    update_urecov_status.status = True
    db.session.commit()

    print("Recovery Data Saved: ", username, encrypted_json)
    flash("Recovery Data Saved Successfully", "success")

    return jsonify({'status': 'success'}),201

@app.route('/log-notification-permission', methods=['POST'])
def log_notification_permission():
    data = request.get_json()
    print("Client permission:", data.get('permission'), "; Client Address: ",request.remote_addr)
    return jsonify({'status': 'success'})

# Get salt from db and derive key using password 
@app.route('/get_key', methods=['POST'])
def save_recovery_data():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'status': 'error', 'msg': 'Username and password required'}), 400
    if not data.get('username') or not data.get('password'):
        return jsonify({'status': 'error', 'msg': 'Username and password cannot be empty'}), 400
    
    print("Data Received: ", data)

    username = data.get('username')
    password = data.get('password')

    cuser = chat_user.query.filter_by(username=username).first()
    if not cuser:
        return jsonify({'status': 'error', 'msg': 'User not found'}), 404
    
    user = User.query.get(cuser.id)

    if user and encry_pw.check_password_hash(user.password, password):
        def derive_key_from_password(password, salt):
            
            # salt should be random and stored alongside the encrypted data
            key = pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
            return base64.urlsafe_b64encode(key)
        
        # Fetch salt as base64 string from DB
        print("Check User ID == save_recovery_data: ", user.id)
        salt_obj = UserKey.query.filter_by(user_id=user.id).first()
        print("Check Salt Object in UserKey == save_recovery_data: ", salt_obj)
        salt = base64.b64decode(salt_obj.salt) if salt_obj else None


        print("Salt Retrieved: ", salt)
        print("Check Password First == save_recovery_data: ", password)
        # salt_b64 = base64.b64encode(salt).decode('utf-8')
        key_ = derive_key_from_password(password, salt)

        # if not UserKey.query.filter_by(user_id=user.id).first():
        #     # If no key exists, create a new one
        #     salt = os.urandom(16)
        #     new_key = UserKey(user_id=user.id, salt=salt_b64)
        #     db.session.add(new_key)
        #     db.session.commit()

        if not key_:
            return jsonify({'status': 'error', 'msg': 'Key not found'}), 404

        return jsonify({'key': key_.decode('utf-8')}), 200
    else:
        return jsonify({'status': 'error', 'msg': 'Invalid username or password'}), 401


def get_encrypted_json_from_sheet(username):
    records = SHEET.get_all_records()
    for row in records:
        if row['username'] == username:
            return json.loads(row['encrypted_json'])
    return None

@app.route('/get_recovery_data', methods=['POST'])
def get_recovery_data():
    data = request.get_json()
    username = data.get('username')
    print("Username Received: ", username)
    cuser = chat_user.query.filter_by(username=username).first()
    if not cuser:
        return jsonify({'status': 'error', 'msg': 'User not found'}), 404
    
    user = User.query.get(cuser.id)

    if not user:
        return jsonify({'status': 'error', 'msg': 'User not found'}), 404

    # From Google sheets 
    # encrypted_json = get_encrypted_json_from_sheet(username)
    try:
        with open(f'working_files/{username}_working_file.json', 'r') as f:
            encrypted_json = json.load(f)
    except FileNotFoundError:
        return jsonify({'status': 'error', 'msg': 'Your keys not found, Please create new keys'}), 404

    if not encrypted_json:
        return jsonify({'status': 'error', 'msg': 'Your keys not found, Please create new keys'}), 404
    
    return jsonify({
        'status': 'success',
        'encrypted_json': encrypted_json,
    })


# In-memory storage for keys and messages
users = {}  # {username: public_key}
messages = {}  # {username: [encrypted_messages]}

# @app.route('/send_sms', methods=['POST'])
# def send_sms():
#     data = request.get_json()
#     phone = data.get('phone')
#     message = data.get('message')
#     result = send_sms_via_huawei(phone, message)
#     return {"result": result}

@app.route("/recovery_status_reg", methods=['POST','GET'])
def recovery_register():

    data = request.get_json()
    usrname = data.get("username")
    chat_user_ = chat_user.query.filter_by(username=usrname).first()
    user_ = User.query.filter_by(cht_usr_fKey=chat_user_.id).first()
    
    if request.method == "POST":
        if(user_):
            save_rec_status = recovery_check(
                cht_usr_id = usrname,
                username = chat_user_.username,
                name = user_.name,
                timestamp = current_time_wlzone()
            )

            db.session.add(save_rec_status)
            db.session.commit()

    return jsonify({"res":"success"}),201

@app.route("/recovery_status_check", methods=['POST','GET'])
def recovery_check_func():

    data = request.get_json()
    usrname = data.get("username")

    chat_user_ = chat_user.query.filter_by(username=usrname).first()
    user_ = User.query.filter_by(cht_usr_fKey=chat_user_.id).first()

    if request.method == "POST" and user_ :
        rec_status = recovery_check.query.filter_by(username=usrname).first()

        if rec_status:
            return jsonify({"res":rec_status.status}),200
        else:
            save_rec_status = recovery_check(
                cht_usr_id = usrname,
                username = chat_user_.username,
                name = user_.name,
                timestamp = current_time_wlzone()
            )

            db.session.add(save_rec_status)
            db.session.commit()

        if not current_user.is_authenticated:
            login_user(user_)
            print("Recovery, User is loged In")

    return jsonify({"res":"checking status"}),200

@app.route("/recovery_status_update", methods=['POST','GET'])
def recovery_update():

    data = request.get_json()
    usrname = data.get("username")

    chat_user_ = chat_user.query.filter_by(username=usrname).first()
    user_ = User.query.filter_by(cht_usr_fKey=chat_user_.id).first()

    if request.method == "POST":
        if(user_):
            rec_status = recovery_check.query.filter_by(username = usrname).first()
           
            rec_status.reg_timestamp = current_time_wlzone()
            rec_status.status = "True"

            db.session.commit()

    return jsonify({"res":"success"}),201

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')

@app.route('/manifest.js')
def manifest():
    return send_from_directory('static', 'manifest.js')

def send_chat_message(message_form,receiver_,recipientMsg_):
    users = chat_user.query.all()
    user_name = chat_user.query.get(current_user.cht_usr_fKey)
    print("DEBUG: ", current_user.id)
    company = company_info.query.filter_by(usr_id=current_user.id).first()

    curr_user = User.query.filter_by(cht_usr_fKey=current_user.id).first()
    subject = message_form.get("subject")
    message = message_form.get("reply-message")
    print("Debug Reply MEssage: ", message)	
    # Receiver's Details'
    receiver =receiver_
    recipientMsg = recipientMsg_
    
    rec_email = message_form.get("recipient_email")

    if request.method=="POST":
        msg = Messages(
            sender = user_name.username,
            receiver = receiver,
            subject = subject,
            message = recipientMsg,
            date = current_time_wlzone(), #timestamp
            key = receiver,
            company_info_name = company.company_name
        )

        db.session.add(msg)
        
        # assign my username to key so  i will be able to open the msg with my pKey 
        msg2 = Messages(
            sender = user_name.username,
            receiver = receiver,
            subject = subject,
            message =  message,
            date = current_time_wlzone(), #timestamp
            key = user_name.username,
            company_info_name = company.company_name
        )

        db.session.add(msg2)
        db.session.commit()
        flash("Message Sent!!","success")
        print("Messages Sent!!")


@app.route("/user_inbox", methods=['POST','GET'])
@login_required
def user_inbox():
    return render_template("user_messages.html")

@app.route("/reply_unit", methods=['POST','GET'])
@login_required
def reply_unit():

    if request.method == "POST":
        curr_user = None
        users = chat_user.query.all()
        cht_id = session.get("_no")

        company = company_info.query.get(cht_id)

        if cht_id:
            curr_user = User.query.filter_by(cht_usr_fKey=cht_id).first()
        else:
            print("Current User not Found in compose: ",cht_id)

        print("Users: ", users)

        message_form = request.form
        receiver_ = message_form.get("recipient_username")
        recipientMsg_ =  message_form.get("rec_encrypted-msg")
        if current_user.is_authenticated:
            send_msg =send_chat_message(message_form,receiver_,recipientMsg_)
            return redirect(url_for('reply_unit'))
        
    return render_template("messege_reply_unit.html")


@app.route('/message_blueprint', methods=['GET', 'POST'])
@login_required
def message_blueprint():

    curr_user = None
    users = chat_user.query.all()
    cht_id = session.get("_no")

    company = company_info.query.get(cht_id)

    if cht_id:
        curr_user = User.query.filter_by(cht_usr_fKey=cht_id).first()
    else:
        print("Current User not Found in compose: ",cht_id)

    print("Users: ", users)

    message_form = request.form
    receiver_ = message_form.get("recipient_username")
    recipientMsg_ =  message_form.get("rec_encrypted-msg")

    if request.method == "POST":
            send_msg =send_chat_message(message_form,receiver_,recipientMsg_)
            return redirect(url_for('get_messages', key=receiver_))

    return render_template("message_blueprint.html", users=users,usr=curr_user,company=company)

@app.route("/vpid", methods=['POST','GET'])
def public_key():
    key = app.config["VAPID_PUBLIC_KEY"]
    return jsonify({'vpkey':key})

subscriptions = []

@app.route('/subscribe', methods=['POST'])
def subscribe():
    print('Q-MESSANGER PSUH NOTIFICATION SUBSCRIPTION - user subscribing...')
    # Save subscription info to your DB
    subscription_info = request.get_json()
    # Save subscription_info for the user
    subscriptions.append({
        "endpoint": subscription_info.get("endpoint"),
        "keys": {
            "p256dh": subscription_info["keys"]["p256dh"],
            "auth": subscription_info["keys"]["auth"]
        }
    })

    sub = NotificationsAccess.query.filter_by(ip=request.remote_addr).first()
    if sub:
        sub.endpoint = subscription_info.get("endpoint")
        sub.p256dh = subscription_info["keys"]["p256dh"]
        sub.auth = subscription_info["keys"]["auth"]
        sub.ip = request.remote_addr
        sub.usr_id = current_user.id if current_user.is_authenticated else None
        sub.timestamp = current_time_wlzone()

        db.session.commit()
        print("Updated Notification Subscription for ", request.remote_addr)

        return jsonify({"success": True}), 201 
     

    save_details = NotificationsAccess(
        endpoint = subscription_info.get("endpoint"),
        p256dh = subscription_info["keys"]["p256dh"],
        auth = subscription_info["keys"]["auth"],
        ip = request.remote_addr,
        usr_id = current_user.id if current_user.is_authenticated else None,
        timestamp = current_time_wlzone()
    )

    db.session.add(save_details)
    db.session.commit()
    print("new Notification Subscription for ", request.remote_addr)
    flash("✔Success!","success")

    return jsonify({"success": True}), 201


# @app.route('/send_push', methods=['POST'])
# def send_push():
#     # Get subscription info from your DB
#     subscription_info = request.get_json().get('subscription')
#     message = request.get_json().get('message', 'You have a new message!')
#     try:
#         webpush(
#             subscription_info,
#             data=json.dumps({
#                 "title": "New Message",
#                 "body": message,
#                 "url": "/get_messages"
#             }),
#             vapid_private_key=VAPID_PRIVATE_KEY,
#             vapid_claims=VAPID_CLAIMS
#         )
#         return jsonify({"success": True}), 200
#     except WebPushException as ex:
#         print("Web push failed: {}", repr(ex))
#         return jsonify({"success": False, "error": str(ex)}), 500

# @app.route('/check_user', methods=['POST'])
# def check_user():
#     data = request.get_json()
#     if not data or 'username' not in data:
#         return jsonify({'exists': False}), 200

#     username = data['username']
#     print("Check User: ", username)

#     # Check if the user exists in the database
#     user = chat_user.query.filter_by(username=username).first()
#     name_obj = User.query.filter_by(cht_usr_fKey=user.id).first() if user else None
#     if user:
#         return jsonify({'exists': True, 'user': name_obj.name}), 200
#     else:
#         return jsonify({'exists': False}), 200
           

@login_required
@app.route('/upload_image', methods=['POST',"GET"])
def uplaod_image():
    
    if request.method =="POST":
        
        data = request.form.to_dict()
        usern = data.get("username")

        # print("Proccessing Image Upload: ",data)
    # Check if the request contains a file
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image'] 
        print("Proccessing Image Upload: ",file,)

        if not data:
            return jsonify({'Error':'No Image Data'}),400
        
        cht_usr = chat_user.query.filter_by(username=usern).first()

        if not cht_usr:
            return jsonify({'Error':'No Image Data'}),400
        
        comp=company_info.query.filter_by(usr_fKey=cht_usr.id).first()

        comp.image = process_file(file)
        db.session.commit()
        print("Image Upload Successfull: ",comp.image)

        return jsonify({'Success':'Image Upload Successfull'}),200

@csrf.exempt
@app.route('/compose', methods=['POST',"GET"])
@login_required
def compose():
    curr_user = None
    users=None
    chat_with = None
    chat_with_company = None

    if request.method == "GET":
        comp_id = request.args.get('id')
        if comp_id:
            cid = ser.loads(comp_id).get('data')
            print("Compose==Company ID: ", cid)
            chat_with_company = company_info.query.get(cid)
            if not chat_with_company:
                print("Compose==No Company Found with ID: ", cid)
                return redirect(url_for('compose'))
            chat_with = chat_user.query.get(chat_with_company.usr_fKey)
                
    message_form = MessagesForm()
    
    if current_user.is_authenticated:
        users = chat_user.query.all()
        user_name = chat_user.query.get(current_user.cht_usr_fKey)
        print("DEBUG: ", current_user.id)
        company = company_info.query.filter_by(usr_id=current_user.id).first()

        curr_user = User.query.filter_by(cht_usr_fKey=current_user.id).first()

        receiver = request.form.get("recipient")
        recipientMsg = request.form.get("rec-msg-ownpkey-enryptd")
        print("Debug Recipient Encrypted Message: ", recipientMsg)

        if request.method=="POST":
            msg = Messages(
                sender = user_name.username,
                receiver = receiver,
                subject = message_form.subject.data,
                message = recipientMsg,
                date = current_time_wlzone(), #timestamp
                key = receiver,
                company_info_name = company.company_name
            )

            db.session.add(msg)
            
            # assign my username to key so  i will be able to open the msg with my pKey 
            msg2 = Messages(
                sender = user_name.username,
                receiver = receiver,
                subject = message_form.subject.data,
                message = message_form.message.data,
                date = current_time_wlzone(), #timestamp
                key = user_name.username,
                company_info_name = company.company_name
            )

            db.session.add(msg2)
            db.session.commit() #TEMPORAL
            flash("Message Sent!!","success")
            print("Messages Sent!!")
            # After saving the message
            recipient_user = chat_user.query.filter_by(username=receiver).first()
            if not recipient_user:
                return jsonify({'Error':"Invalid Request"})
            user = User.query.filter_by(cht_usr_fKey=recipient_user.id).first()
            if not user:
                return jsonify({'Error':"Invalid Request"})

            recipient_sub = NotificationsAccess.query.filter_by(usr_id=user.id).order_by(NotificationsAccess.timestamp.desc()).first()

            if not recipient_sub:
                print("User Not Susbribed, ", request.remote_addr)
                return redirect(url_for('home'))
            
            # for sub in recipient_subs:
            recipient_sub_info = {
                "endpoint": recipient_sub .endpoint,
                "keys": {
                    "p256dh": recipient_sub .p256dh,
                    "auth": recipient_sub .auth
                }
            }
            try:
                print(f"New message from {curr_user.name}")
                print(f"New message to @webpush {curr_user.name}")

                webpush(
                    recipient_sub_info,
                    data=json.dumps({
                        "title": "New Message",
                        "body": f"New message from {curr_user.name}",
                        "url": "/get_messages?key=" + user_name.username,
                        "url_reply": "/reply_unit",
                        "username": user_name.username
                    }),
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims=VAPID_CLAIMS,
                    ttl=200
                )
                print("Web Push Activated!")
            except WebPushException as ex:
                print("Web push failed: {}", repr(ex))
                print(recipient_sub_info)
            # print("Notification Sent!")
            return redirect(url_for('compose'))

        print("Users: ", users)
    else:
        if request.method=="POST":
            receiver = request.form.get("recipient")
            recipientMsg = request.form.get("rec-msg-ownpkey-enryptd")
            chat_user_ = chat_user.query.filter_by(username=receiver).first()
            print("Receiver: ",receiver, " ,Msg: ",  recipientMsg)
            if chat_user_:
                company = company_info.query.filter_by(usr_fKey=chat_user_.id).first()
                if not company:
                    print("No Company Found for User: ", chat_user_.username)
                    flash("No Company Found for User", "warning")
                    return redirect(url_for('compose'))
                
                msg = Messages(
                    sender = message_form.name.data,
                    receiver = receiver,
                    subject = message_form.subject.data,
                    message = recipientMsg,
                    date = current_time_wlzone(), #timestamp
                    key = receiver,
                    company_info_name = company.company_name
                )
                db.session.add(msg)
                db.session.commit()

                print("No User Authenticated, Redirecting to Login")
                flash("Please Login to Compose Messages", "warning")
                receiver = request.form.get("recipient")
                recipientMsg = request.form.get("rec-msg-ownpkey-enryptd")
                return redirect(url_for('home'))

    return render_template("compose.html", users=users,usr=curr_user,form=message_form, chat_with = chat_with,chat_with_company=chat_with_company )

@csrf.exempt
@app.route('/campaign_route', methods=['POST',"GET"])
# @login_required
def campaign_route():
    view = None

    requested_list_view = request.args.get("req_view")
    if requested_list_view:
        view = requested_list_view
    # Convert list of dicts to list of objects
    company_dicts = [c.to_dict() for c in company_info.query.all()]
    company_objs = [CompanyObj(**d) for d in company_dicts]

    for comp in company_objs:
        # for prop in comp:
        print("DEBUG Companies: ", comp.company_name)

    companies = company_info.query.all()
    categories = {comp.category for comp in companies}

    return render_template("campaign_route.html",companies=company_objs,categories=categories,view=view)

@csrf.exempt
@app.route('/compose_mobile', methods=['POST',"GET"])
# @login_required
def compose_mobile():
    curr_user = None
    users=None
    chat_with = None
    chat_with_company = None

    if request.method == "GET":
        comp_id = request.args.get('id')
        if comp_id:
            cid = ser.loads(comp_id).get('data')
            print("Compose==Company ID: ", cid)
            chat_with_company = company_info.query.get(cid)
            if not chat_with_company:
                print("Compose==No Company Found with ID: ", cid)
                return redirect(url_for('compose'))
            chat_with = chat_user.query.get(chat_with_company.usr_fKey)
                
    message_form = MessagesForm()

    if request.method=="POST":
        receiver = request.form.get("recipient")
        recipientMsg = request.form.get("rec-msg-ownpkey-enryptd")
        chat_user_ = chat_user.query.filter_by(username=receiver).first()
        print("Receiver: ",receiver, " ,Msg: ",  recipientMsg)
        if chat_user_:
            company = company_info.query.filter_by(usr_fKey=chat_user_.id).first()
            if not company:
                print("No Company Found for User: ", chat_user_.username)
                flash("No Company Found for User", "warning")
                return redirect(url_for('compose'))
            
            msg = Messages(
                sender = message_form.name.data,
                phone = message_form.phone.data,
                cust_email = message_form.cust_email.data,
                receiver = receiver,
                subject = message_form.subject.data,
                message = recipientMsg,
                date = current_time_wlzone(), #timestamp
                key = receiver,
                company_info_name = company.company_name
            )
            db.session.add(msg)
            db.session.commit()

            print("Message sent successfully")
            flash("Message sent successfully", "warning")
            # receiver = request.form.get("recipient")
            # recipientMsg = request.form.get("rec-msg-ownpkey-enryptd")
            return redirect(url_for('home'))

    return render_template("compose_in_mobile.html", users=users,usr=curr_user,form=message_form, chat_with = chat_with,chat_with_company=chat_with_company )

def app_notification(recipient_sub,curr_user,msg,title="Q-Messanger",url="/"):
    pushed_num = 0
    failed_num = 0
    pushed_ip_list = []
    failed_ip_list = []

    recipient_sub_info = {
            "endpoint": recipient_sub .endpoint,
            "keys": {
                "p256dh": recipient_sub .p256dh,
                "auth": recipient_sub .auth
            }
        }
    
    try:
        print(f"Updates from! {curr_user}")
        webpush(
            recipient_sub_info,
            data=json.dumps({
                "title": title,
                "body": msg,
                "url": url if url else "https://qm.techxolutions.com",
                "username": curr_user
            }),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS,
            ttl=200
        )
        pushed_num += 1
        pushed_ip_list.append(recipient_sub_info.ip)
        print("Web Push Activated, Update!")

    except WebPushException as ex:
        if 'unsubscribed or expired' in str(ex):
            # Remove subscription from DB
            db.session.delete(recipient_sub)
            db.session.commit()
            print(f"Removed expired subscription uid: {recipient_sub.usr_id}")
        else:
            print("Web push failed, update: {}", repr(ex))
        failed_num += 1
        failed_ip_list.append(recipient_sub_info.ip)

    print("Q-MESSANGER NOTIFICATIONS - Successfully pushed notifications: ",pushed_num)
    print("Q-MESSANGER NOTIFICATIONS - Failed notifications: ",failed_num)

    with open("Push Notifications Report.txt", "rw") as file:
        pass

# Adverts Code 
# {% for row in adverts|batch(3, '') %}
#     <div class="masonry-row gen-flex">
#         {% for ad in row %}
#             <div class="column gen-flex-col">
#                 {% if ad.image %}
#                     <img src="{{ ad.image }}" alt="Ad Image">
#                 {% endif %}
#                 {% if ad.video %}
#                     <iframe src="{{ ad.video }}" allowfullscreen></iframe>
#                 {% endif %}
#             </div>
#         {% endfor %}
#     </div>
# {% endfor %}

@app.route('/auto_recovery_checker', methods=['POST',"GET"])
def auto_recovery_checker():

    data = request.get_json()
    if not data:
        return jsonify({"Error":"No User Submitted"}),400

    print("Auto Recovery Check Data: ", data)
    get_rec_status = recovery_check_v2.query.filter_by(username=data["username"]).first()
    # print("Auto Recovery Check Data: ", data)

    return jsonify({"status":'auto_recovery_checker'})

@app.route('/install')
def install_app():
    return render_template('download_app.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/get_email', methods=['POST',"GET"])
# @login_required
def get_email():
    data = request.get_json()
    if not data:
        return jsonify({"Error":"No User Submitted"}),400
    
    usr = chat_user.query.filter_by(username=data["username"]).first()
    user = User.query.filter_by(cht_usr_fKey=usr.id).first()
    print("Pkey: ",usr.pkey)

    return jsonify({"email":user.email,'rec_pKey':usr.pkey}),200

@app.route('/legacy_recovery', methods=['GET'])
def legacy_recovery():
    # This route is for legacy recovery, it will be used to recover old users
    # who have not registered their keys or recovery data.
    # It will redirect to the recovery page.

    return render_template("legacy_recovery.html")

# Login using indexedDB's Username'
@app.route('/login', methods=['GET'])
def login(id=None):
    print("Check Id: ",id)
    if request.method == "GET":
        req_username = request.args.get('id')
        username = chat_user.query.filter_by(username=req_username).first()

        if not username:
            print("No Username In DB with Identified by: ",req_username)
            return redirect(url_for('register'))
        
        user = User.query.filter_by(cht_usr_fKey=username.id).first()

        # data = request.get_json()
        if user:
            login_user(user)
            flash(f"Welcome, {user.name}","success")
            signed_username = serializer.dumps(username.username)
            session['username'] = signed_username
            session.permanent = True
            session['pubKey']=username.pkey
            return redirect(url_for('home'))
        else:
            print("User Not Found")
            return redirect(url_for('register'))
                # return redirect(url_for("home"))

    return jsonify({"message":"User Logged in"}),200

# Login using indexedDB's Username'
@app.route('/manual_login', methods=['GET',"POST"])
def manual_login(id=None):
    form = Login()
    print("Check Id: ",id)

    if request.method == "POST":
        
        user_login = User.query.filter_by(email=form.email.data).first()
        

        if user_login and encry_pw.check_password_hash(user_login.password, form.password.data):
            login_user(user_login)
            username = chat_user.query.get(user_login.cht_usr_fKey)

            flash(f"Welcome, {user_login.name}","success")
            signed_username = serializer.dumps(username.username)
            session['username'] =  signed_username
            session.permanent = True
            session['pubKey']=username.pkey
            return redirect(url_for('home'))
        else:
            flash("Wrong credentials please re-check email or password",'error')
            return redirect(url_for('manual_login'))
            # return redirect(url_for("home"))

    return render_template("manual_login.html",form=form)

@app.route('/register_new_keys', methods=['POST','GET'])
@login_required
def register_new_keys():
    data = request.get_json()
    if not data:
        return jsonify({"message":"No User Submitted"}),400
    
    username_ss = session.get("username", "")
    if username_ss:
        username_ss = serializer.loads(username_ss)

    if not username_ss == data.get('username'):
        return jsonify({"message":"Username Mismatch"}), 401
    
    if request.method == 'POST':
        
        if not username:
            flash("You must be logged in to register new keys","warning")
            return jsonify({"message":"User not logged in"}), 401

        usr = chat_user.query.filter_by(username=username_ss).first()
        if not usr:
            flash("User not found, please register first","warning")
            return redirect(url_for('register'))

        # Update the user's public key
        usr.pkey = data['newPkey']
        db.session.commit()
        
        flash("Public Key Updated Successfully","success")

        return jsonify({"success": True, "message": "Key update successful"}), 201
    
@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    session.pop('pubKey', None)
    
    logout_user()
    
    return redirect(url_for('home'))

@csrf.exempt
@app.route('/api/is_logged_in')
def is_logged_in():
    return jsonify({'logged_in': current_user.is_authenticated})

def notify_all_subscribers_async(curr_user, msg, title="Q-Messanger", url="/"):
    def notify():
        with app.app_context():
            all_subs = NotificationsAccess.query.all()
            for sub in all_subs:
                try:
                    print(f"Sending Notification to {curr_user} Message{msg}")
                    app_notification(sub, curr_user, msg, title, url)
                except Exception as e:
                    print(f"Notification failed for {sub.id}: {e}")
    threading.Thread(target=notify).start()

#Reporting Error
@app.route('/log_sw_unregistration', methods=['POST'])
def log_sw_unregistration():
    data = request.get_json()
    if not data:
        return jsonify({"message":"No User Submitted"}),400
    
    print("Service Worker Unregistered due error cause in fetch a page URL", current_time_wlzone(), ", IP: ", request.remote_addr)

    return jsonify({"success": True, "message": "Unregistration logged successfully"}), 201

@csrf.exempt
@app.route('/register', methods=['POST','GET'])
def register():
    # data = request.json
    
    usr_ssn = session.get("username", "")
    if usr_ssn:
        usr_ssn = serializer.loads(usr_ssn)
    usrnm = chat_user.query.filter_by(username=usr_ssn).first()

    if usrnm:
        return redirect(url_for('home'))

    if request.method == 'POST':
        form = request.form
        print("USER DATA",form)
        # Check If Username Exists 
        if chat_user.query.filter_by(username=form['username']).all():
            flash("Username already exists, please use a different Username","warning")
            return redirect(url_for('register'))
        
        # Check If Email Exists 
        if User.query.filter_by(email=form['email']).all():
            flash("❌ Email already exists, please use a different Email","warning")
            return redirect(url_for('register'))
        
        # Register Chat User 
        reg_usr_db = chat_user(
            username=form['username'],
            pkey=form['pKey']
        )

        db.session.add(reg_usr_db)
        
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("❌ Username already exists, please use a different Email","warning")
            return redirect(url_for('register'))

        get_user = chat_user.query.filter_by(username=form['username']).first()

        print("register==DEBUG USERNAME IN DB: ",get_user )

        # IF Chat user 
        # if get_user:

        #     # Generate and Save User Salt 
        #     salt = os.urandom(16) # Generate a random salt
        #     salt_b64 = base64.b64encode(salt).decode('utf-8')

        #     # save salt 
        #     #Note: Its chat_user.id not user.id
        #     salt_obj = UserKey(
        #         user_id = get_user.id,
        #         salt = salt_b64
        #     )

        #     print("register==DEBUG SALT: ",salt_obj)
        #     db.session.add(salt_obj)
        #     db.session.commit()

        # Register User and Company info 
        if get_user:
            hashd_pwd = encrypt_password.generate_password_hash(form['password']).decode('utf-8')
            user_details = User(
                name = form['name'],
                cht_usr_fKey = get_user.id,
                password = hashd_pwd,
                confirm_password = hashd_pwd,
                email = form['email'],
                image = "default.jpg",
            )
            db.session.add(user_details)
            db.session.commit()

            # Generate and Save User Salt 
            salt = os.urandom(16) # Generate a random salt
            salt_b64 = base64.b64encode(salt).decode('utf-8')

            # save salt 
            #Note: Its chat_user.id not user.id
            salt_obj = UserKey(
                user_id = user_details.id,
                salt = salt_b64
            )

            print("register==DEBUG SALT: ",salt_obj)
            db.session.add(salt_obj)
            db.session.commit()

            signed_username = serializer.dumps(get_user.username)
            session['username'] = signed_username
            session.permanent = True
            session['pubKey']=get_user.pkey

            user = User.query.filter_by(cht_usr_fKey=get_user.id).first()

            company_details = company_info(
                company_name = form['company_name'],
                usr_fKey = get_user.id,
                usr_id = user.id,
                image = "logo-avator.png",
                country = form['country']
            )
                
            db.session.add(company_details)

            db.session.add(user_details)

            uid = get_user.id
            print("UID: ", uid)
            id_ser = ser.dumps({"form": uid})
            print("UID_SER: ", id_ser)

            # data_json = {
            #             'id': id_ser,
            #             'username': get_user.username
            #         }
            
            try:
                db.session.commit()

                if company_details.id:
                    # Create Recovery Entry for this User
                    create_recovery_entry = recovery_check_v2(
                        cht_usr_id = get_user.id,
                        comp_id = company_details.id,
                        username = get_user.username,
                        timestamp = current_time_wlzone()
                    )
                    db.session.add(create_recovery_entry)
                    db.session.commit()
                    print("Registration - Recovery Entry Created")

                print("register==Registration Successful")
                flash("✔ Registration Successful","success")
                # After successful registration and db.session.commit()

                # session['username'] = get_user.username
                # session['pubKey']=get_user.pkey
                # session.permanent = True  # Make the session permanent 
                return redirect(url_for('home'))
            except IntegrityError:
                db.session.rollback()  # Rollback the session to clear the pending state
                print("register==User Registration Evoked because of Integrity Error: ", get_user.username)
                db.session.commit()
        else:
            flash("❌ User Registration Failed, Please try again","warning")
            print("register==User Registration Failed, Please try again")
            return redirect(url_for('register'))
        
        print("Registration Successful")

        print("USER DATA: ",reg_usr_db)
        # Save the public key to the database or any persistent storage

    return render_template('register.html')

@csrf.exempt
@app.route('/fetch_user_data', methods=['POST'])
def fetch_user_data():
    data = request.get_json()
    if request.method =="POST":
        if data:
            user_data = chat_user.query.filter_by(username=data['usernm']).first()
            if user_data:
                user = User.query.filter_by(cht_usr_fKey=user_data.id).first()
                print("fetch_user_data==User found: ",user)
                company__info = company_info.query.filter_by(usr_fKey=user_data.id).first()
                print("fetch_user_data==company found: ",company__info)
                if not user:
                    print("fetch_user_data==User Not found")
                    return jsonify({"Error":"fetch_user_data==User Not found"})
                
                user_information = user.to_dict()

                if not company__info:
                    print("fetch_user_data==Company Not found")
                    return jsonify({"Error":"fetch_user_data==Company Not found"})
                
                comp_information = company__info.to_dict()

                all_info = {**user_information, **comp_information}
                print("fetch_user_data==All_Info: ",all_info)

                return jsonify({"info":all_info}), 200
        else:
            print("fetch_user_data==No Data Received")

    return 

@app.route("/mobile", methods=["POST", "GET"])
def mobile():

    return render_template("mobile_menu.html")

# ------------------------------user DATA------------------------------- #
@app.route("/user_account", methods=["POST", "GET"])
@login_required
def user_account_form():
    print("Login In User: ", session.get('username'))

    user_account_form = Register(obj=User)

    db.create_all()

    id = current_user.id
    usr_acc = User.query.get(id)
    # usr_acc = User.query.filter_by(cht_usr_fKey=id).first()

    if request.method == "POST":

        if isinstance(user_account_form.image.data, FileStorage):
            print("Check Image Update: ", user_account_form.image.data)
            pfl_pic = process_file(user_account_form.image.data)
            usr_acc.image = pfl_pic

        usr_acc.name = user_account_form.name.data
        usr_acc.email = user_account_form.email.data
        usr_acc.contacts = user_account_form.contacts.data
        usr_acc.position = user_account_form.position.data
        # usr_acc.fb_link = user_account_form.facebook_link.data

        db.session.commit()
        print("Account Update Successful")

    # from myproject.models import user
    return render_template("user_account.html", form=user_account_form,usr_acc=usr_acc)

# ------------------------------COMPANIES DATA------------------------------- #
@csrf.exempt
@app.route("/company_account", methods=["POST", "GET"])
@login_required
def company_account():

    company_contacts = None

    db.create_all()
    id = current_user.id
    cmp_usr = company_info.query.filter_by(usr_id=id).first()
    cmp_obj = company_info.query.filter_by(usr_id=id).first().to_dict()
    company_update = Company_Register_Form(obj=cmp_usr)

    if not cmp_usr:
        print("company_account==No Company Found for User ID: ", id)
        return jsonify({"error": "No Company Found, Please Register"}), 404
    
    if cmp_usr.company_contacts: 
        company_contacts = cmp_usr.company_contacts

    if request.method == "POST":

        if len(company_update.company_email.data) <= 6:
            flash("Please Enter a Valid Email Adress", "warning")
            return redirect(url_for("company_account"))

        if isinstance(company_update.company_logo.data, FileStorage):
            print("Check company_logo Update: ", company_update.company_logo.data)
            pfl_pic = process_file(company_update.company_logo.data)
            cmp_usr.image = pfl_pic

        category_value = company_update.category.data
        if category_value == "Other":
            category_value = company_update.category_other.data
        
        cmp_usr.category = category_value
        cmp_usr.name = company_update.company_name.data
        cmp_usr.email = company_update.company_email.data
        cmp_usr.company_contacts = company_update.company_contacts.data
        cmp_usr.tagline = company_update.tagline.data
        cmp_usr.website = company_update.website_link.data
        cmp_usr.fb_link = company_update.facebook_link.data
        cmp_usr.other2 = company_update.abbreviation.data
        cmp_usr.company_address = company_update.company_address.data
        cmp_usr.twitter_link = company_update.twitter_link.data
        # cmp_usr.instagram_link = company_update.instagram_link.data
        cmp_usr.youtube = company_update.youtube_link.data
        cmp_usr.payment_options = request.form.get('payment_options')

        try:
            db.session.commit()
            flash("Account updated!", "success")
            # Send SMS to the company if company_contacts is empty
            if not company_contacts and cmp_usr.company_contacts:
                company_name = cmp_usr.company_name
                if len(company_name) > 17:
                    company_name = company_name[:17] + "..."
                phone = cmp_usr.company_contacts
                phone_validator = PhoneValidator
                print("Phone Number to Validate: ", phone)
                try:
                    val_phone = phone_validator(phone).validate()
                    message = f"Welcome to Quick Messanger {company_name}! Grow your market presence, improve B2B/B2C communication & build networks. Visit: https://qm.techxolutions.com"
                    # print("Phone Number to Validate2: ", val_phone)
                    result = send_sms_via_africastalking(val_phone, message)
                    print(f"company: {company_name}, status: success, response: {result}")
                    
                except PhoneNumberError as e:
                    print(f"company: {company_name}, No: {phone}; Invalid phone number: {e}", "danger")

                # Notify All users about new company registration 
                tagline = cmp_usr.tagline
                if tagline and len(tagline) > 80:
                    tagline = tagline[:77] + "..."
                notify_all_subscribers_async(
                    curr_user=current_user.name,
                    msg=f"{tagline}. Discover {cmp_usr.company_name} on Quick Messenger Today!",
                    title=cmp_usr.company_name + " is now on Quick Messenger!",
                    url="/business_community"
                )
                print(f"{cmp_usr.company_name} sending Notification to all subscribers")
            else:
                print(f"company_account== Company Contacts Provided {cmp_usr.company_name}, SMS not sent")
            
            # Send email confirmation
            if cmp_usr.email:
                print(f"company_account== Preparing to send email to {cmp_usr.company_name}")
                reg_confirmation(cmp_usr.email, cmp_usr.company_name)
                    
            return redirect(url_for('home'))
        
        except IntegrityError as e:
            db.session.rollback()
            flash("Email address must be unique and not empty.", "danger")
            # Optionally, log the error or handle further

        # return redirect(url_for('company_account'))

    # from myproject.models import user
    return render_template("company_account.html", company_update=company_update,cmp_usr=cmp_usr,cmp_obj=cmp_obj)

@app.route('/public_key/<usrname>', methods=['GET'])
def get_public_key(usrname):
    try:
        usr = chat_user.query.filter_by(username=usrname).first()
        print("get_public_key==USERNAME From DB: ", usr.username)
        if not usr:
            return jsonify({'error': 'User not found'}), 404
        print("get_public_key==PUBLIC KEY RESOLVED: ", usr.pkey)
        return jsonify({'publicKey': usr.pkey})
    except Exception as e:
        print("get_public_key==Error fetching public key:", str(e))
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    print("Is this Running??")
    data = request.get_json()

    if not data['to']:
        return jsonify({'status': 'Not sent'}),200
    
    # cht_usr = chat_user.query.get(username=data['to']).first()
    # if not cht_usr:
    #     return jsonify({'status': 'message_sent'}),200

    cht_id = chat_user.query.get(current_user.cht_usr_fKey)

    msgs = Messages.query.filter_by(receiver=data['to']).all()
    for msg in msgs:
        print("Welcome Sent Check: ",msg.subject)
        if msg.subject == "Welcome to Quick Messanger!":
            print("Welcome Sent")
            return ""
        
    qm = company_info.query.filter_by(company_name="Quick Messanger").first()
    
    comp = company_info.query.filter_by(usr_fKey=cht_id.id).first()
    if not comp:
        print("send_message==Company Object not found, for user: ",current_user.id)
        return jsonify({'status': 'Company Object not found'}),400
    if qm:
        qm_cht_usr = chat_user.query.get(qm.usr_fKey)
        message = Messages(
            sender=qm_cht_usr.username,
            receiver=data['to'],
            sender_id = qm_cht_usr.id,
            subject = data['subject'],
            message=data['message'],
            key=data['to'], #They used my pkey to encrypt
            company_info_id = comp.id,
            company_info_name = comp.company_name
        )
        db.session.add(message)
        db.session.commit()

    # print("Messages: ", messages)
    return jsonify({'status': 'message_sent'}),200

@app.route("/delete_news/<int:news_id>", methods=["POST", "GET"])
@login_required
def delete_news(news_id):
    news = News.query.get_or_404(news_id)

    try:
        # Delete image files associated with this news post
        for img in news.images_id:
            if img.image:
                image_path = os.path.join("static", "comp-images", secure_filename(img.image))
                if os.path.exists(image_path):
                    os.remove(image_path)
            if img.main:
                main_image_path = os.path.join("static", "comp-images", secure_filename(img.main))
                if os.path.exists(main_image_path):
                    os.remove(main_image_path)

        # Delete the news object (and all images via cascade)
        db.session.delete(news)
        db.session.commit()
        flash("News and associated images deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting news: {str(e)}", "danger")

    return redirect(url_for("news"))

@app.route('/sendme_message', methods=['POST'])
@login_required
def sendme_message():
    print(" DEBUG senme_message")
    data = request.get_json()
    from_who = data.get('sender')
    print("SEND MESSAGE: ", data)
    if not data or "sender" not in data or 'to' not in data or 'message' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    # get cht_user_id 
    cht_id = chat_user.query.get(current_user.cht_usr_fKey).id
    
    comp = company_info.query.filter_by(usr_fKey=cht_id).first()
    if not comp:
        print("send_message==Company Object not found, for user: ",current_user.id)
        return jsonify({'status': 'Company Object not found'}),400
    
    #When I load messages I get messages with key my username only so that I be able to decrypt
    #with my keys. When they send to me they already used my pkey
    
    message = Messages(
        sender=from_who,
        sender_id = current_user.id,
        subject = data['subject'],
        receiver=data['to'],
        message=data['message'],
        key=from_who, #Me, encrypted with my pkey
        company_info_id = comp.id,
        company_info_name = comp.company_name
    )

    db.session.add(message)
    db.session.commit()

    print("sendme_message==Messages: ", messages)
    return jsonify({'status': 'message_sent'}),200

@app.route('/advert_form', methods=['POST',"GET"])
@login_required
def adverts_form():

    form = AdvertForm()
    form_req = request.form.get('pinned-story')

    comp_news = News.query.filter_by(usr_id=current_user.id).all()
    company = current_user.company_id[0]

    if request.method == "POST":
        advert = Advert(
            usr_id = current_user.id,
            comp_id = current_user.company_id[0].id,
            advert_title = form.advert_title.data,
            pinned_1 = form_req
        )

        if form.advert_image.data:
            advert_img = process_ads(form.advert_image.data)
            advert.advert_image = advert_img

        db.session.add(advert)
        db.session.commit()
        flash("Advert Uploaded Successfully","success")
        msg = company.company_name +"  just dropped a brand-new advert — check it out and don’t miss your chance to be part of something exciting!"
        title="Q-Messanger Adverts"
        url = "/adverts"

        try:
            recipient_sub = NotificationsAccess.query.filter_by(usr_id=current_user.id).order_by(NotificationsAccess.timestamp.desc()).first()
            app_notification(recipient_sub,current_user.name,msg,title,url=url)
            print("Q-MESSANGER: NOTIFICATIONS LOGS - Pushed advert notification from: ",company.company_name)
        except:
            print("Advert Notification Push Error")

    return render_template("advert_form.html",form=form,comp_news=comp_news)

@app.route("/adverts")
def adverts():
    remote_ip = request.remote_addr
    adverts = Advert.query.all()
    companies = {c.id: c for c in company_info.query.all()}
    num_columns = 3
    columns = [[] for _ in range(num_columns)]
    for idx, ad in enumerate(adverts):
        print("idx % num_columns: ",idx % num_columns)
        columns[idx % num_columns].append(ad)
    # print("All Cols: ",columns)
    return render_template("adverts.html",columns=columns,companies=companies,adverts=adverts,remote_ip=remote_ip)



@csrf.exempt
@app.route('/like_ad', methods=['POST'])
def like_ad():
    already_liked = None
    data = request.get_json()
    ad_id = data.get('ad_id')
    action = data.get('action')
    name = data.get('name')
    contacts = data.get('contacts')
    ad = Advert.query.get(ad_id)
    if not ad:
        return jsonify({'success': False, 'message': 'Ad not found.'}), 404

    # Check if user already liked this ad
    if current_user.is_authenticated:
        already_liked = Likes.query.filter_by(user_id=current_user.id, ad_id=ad_id).first()
    else:
        already_liked = Likes.query.filter_by(ip=request.remote_addr, ad_id=ad_id).first()
    
    if already_liked:
        print("Already Liked: ", already_liked)
        return jsonify({'success': False, 'message': 'You already liked this ad.', 'likes': len(ad.likes) or 0})

    # Add like
    
    like = Likes(ad_id=ad_id)
    if current_user.is_authenticated:
        like.user_id = current_user.id
        like.action = action
    else:
        like.ip = request.remote_addr
        like.action = action
        like.name = name
        like.contacts = contacts
        print("Like Action 2: ", like.action,name,contacts)
    db.session.add(like)
    db.session.commit()
    db.session.refresh(ad) 
    print("Like Action 3: ", like.action,name,contacts)

    return jsonify({'success': True, 'likes': len(ad.likes)})


@app.route("/company_stories")
@app.route("/news")
def news():
    news = News.query.all()
    all_news_imgs = NewsImages.query.all()
    companies_n_news = [company.to_dict() for company in company_info.query.all()]

    return render_template("news.html",news=news,all_news_imgs=all_news_imgs,companies_n_news=companies_n_news)

@csrf.exempt
@app.route("/news_pinned")
@login_required
def news_pinned():
    news_id = request.args.get("nid")
    print("News ID: ", news_id)
    news = News.query.filter_by(id=news_id).first()
    news_imgs = NewsImages.query.filter_by(news_id=news_id).all()
    company = company_info.query.filter_by(usr_id=current_user.id).first().to_dict()

    return render_template("news_pinned.html",story=news,news_imgs=news_imgs,company=company)

@app.route('/update_news_views/<int:news_id>', methods=['GET'])
def news_views(news_id):
   
    user_id = None
    if current_user.is_authenticated:
        user_id  = current_user.id

    # Increment the view count
    view = Views(
        news_id=news_id,
        user_id=user_id,
        ip=request.remote_addr,  # Get the user's IP address
        view_date=current_time_wlzone()
    )

    # Check if the view already exists for this user and news item
    existing_view = Views.query.filter_by(news_id=news_id, user_id=user_id, ip=request.remote_addr).first()

    if not existing_view:
        db.session.add(view)
        db.session.commit()
        print("News View Count Incremented for News ID: ", news_id)
        return jsonify({'status': 'view_count_incremented'}), 200

    return jsonify({'status': 'previously'}), 200

@app.route('/news_form', methods=['POST',"GET"])
@login_required 
def news_form():

    form = StoryForm()
    
    if request.method == "POST":
        hashtags = ''
        for tag in form.hashtags.data:
            hashtags += " #"+tag
       
        news_obj = News(
            usr_id = current_user.id,
            comp_id = current_user.company_id[0].id,
            story_title = form.story_title.data,
            story=form.story.data,
            timestamp=current_time_wlzone(),
            other = hashtags
        )
        # db.session.rollback()
        db.session.add(news_obj)
        db.session.commit()
        # After committing, news_obj.id will be automatically set by SQLAlchemy
        story = News.query.get(news_obj.id)

        if form.images.data:
            for image_file in form.images.data:
                image= process_news(image_file)
                news_images_obj = NewsImages(
                    image = image,
                    news_id = story.id
                    # caption = news_images_obj.caption.data,
                    # main = news_images_obj.main.data
                )
                print("##News Image: ",news_images_obj.image )
                db.session.add(news_images_obj)

            db.session.commit()
            flash("Post successful","success")

    return render_template("news_updates_form.html",form=form)

@app.route('/push_notif_form', methods=['POST',"GET"])
@login_required 
def push_notif_form():
    form = QMUpdatesForm()
    if request.method =="POST":
        notify = qm_updates(
            title = form.title.data,
            content = form.content.data,
            start_date = form.start_date.data,
            end_date = form.end_date.data,
            url = form.url.data,
            timestamp = current_time_wlzone()
        )

        if form.days.data:
            notify.days = form.days.data

        db.session.add(notify)
        db.session.commit()

        title = form.title.data
        content = form.content.data
        url = form.url.data

        recipient_subs = NotificationsAccess.query.all()
        for recipient_sub in recipient_subs:
            app_notification(recipient_sub,current_user.name,content,title=title,url=url)

    return render_template("marketing_updates_form.html",form=form)

class CompanyObj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

@app.route('/business_community', methods=['POST',"GET"])
def business_community():
    view = None

    requested_list_view = request.args.get("req_view")
    if requested_list_view:
        view = requested_list_view
    # Convert list of dicts to list of objects
    company_dicts = [c.to_dict() for c in company_info.query.all()]
    company_objs = [CompanyObj(**d) for d in company_dicts]

    for comp in company_objs:
        # for prop in comp:
        print("DEBUG Companies: ", comp.company_name)

    companies = company_info.query.all()
    categories = {comp.category for comp in companies}

    return render_template("business_community.html",companies=company_objs,categories=categories,view=view)

@app.route('/email_prospects_form', methods=['POST',"GET"])
def email_prospects():
    form = EmailProspectsForm()
    email = form.email.data
    name = form.name.data
    company = form.company.data

    if request.method == "POST":
        email_prospective_companies(email,name,company)
        # app_notification(recipient_sub,current_user.name,content,title=title,url=url)

    return render_template("email_prospects_form.html",form=form)

@app.route('/business_profile', methods=['POST',"GET"])
def business_profile():
    # print("business_profile Request: ")
    data = request.get_json()
    follow_status = False
    # print("ID Request: ", data)
    if data:
        de_ser = ser.loads(data["cid"])
        id_ = de_ser.get('cid')
        # print("ID Request: ", id_)
        company_profile = company_info.query.get(id_).to_dict()
    
        follow_status = Followers.query.filter_by(ip_address=request.remote_addr,company_id=id_).first()
        if follow_status:
            follow_status = True

    return jsonify({"company":company_profile, "follow_status": follow_status}), 200

@app.route('/digital_marketing', methods=['POST',"GET"])
def digital_marketing():

    return render_template("digital_marketing.html")

@app.route('/get_messages', methods=['GET'])
@login_required
def get_messages():
    
    # user_messages = []
    if request.method == 'GET':

        other_usrname = request.args.get('key')
        sender_phone=request.args.get('phone')
        other_user_obj = chat_user.query.filter_by(username=other_usrname).first()
        my_usrname = chat_user.query.get(current_user.cht_usr_fKey)
        if not other_usrname:
            print("**get_messages==No Username Found")
            return jsonify({'error': 'No username provided'}), 400
        
        print("Get Messages ==Username: ", other_usrname)
        print("Get Messages ==MY_Username: ", my_usrname.username)

        # Fetch all messages between the two users
        all_chat_messages = Messages.query.filter(
            or_(
                (Messages.sender == my_usrname.username) & (Messages.receiver == other_usrname),
                (Messages.sender == other_usrname) & (Messages.receiver == my_usrname.username)
            )
        ).order_by(Messages.date.asc()).all()

        if len(all_chat_messages) == 0:
            all_chat_messages = Messages.query.filter_by(phone=sender_phone).order_by(Messages.date.asc()).all()
        

        if not all_chat_messages:
            return jsonify({'error': 'No messages found'}), 200
        print("All Chat Messages", all_chat_messages)

        messages_wcurrent_ukey = [msg for msg in all_chat_messages if msg.key == my_usrname.username]
        #..I am getting all the latest messages with my key
        print("All Messages with my key", messages_wcurrent_ukey)

        if not messages_wcurrent_ukey:
            print("No Messages Found")
            return []
        
        other_usr_company = company_info.query.filter_by(usr_fKey=other_user_obj.id).first()
        print("Comp Found? ", other_usr_company)
        other_usr_company_dict = other_usr_company.to_dict()

        my_company_info = company_info.query.filter_by(usr_fKey=my_usrname.id).first()
        my_company_dict = my_company_info.to_dict()

        if not other_usr_company:
            print("No Company Found")
            return jsonify({'error': 'You Have No Company Registered in The System'}), 400

        # Convert messages to dictionary format

        # messages_list = [msg.to_dict() for msg in messages_wcurrent_ukey]
        # return jsonify({'messages': messages_list}), 200

        return render_template("message_blueprint.html", chat_messages=messages_wcurrent_ukey, chat_user = chat_user, other_usrname =other_usrname,
                               other_usr_company_info=other_usr_company_dict, my_company_info=my_company_dict)

@app.route('/update_field_user', methods=['POST','GET'])
@login_required
def update_user():

    usr_id = current_user.id
    fields = ["name","image","email","position","contacts"]

    if usr_id:
        user = User.query.get(usr_id)

        data = request.get_json()

        if data["field"] == "name":
            print("Updating :", data["value"])
            user.name = data["value"] 
        elif data["field"] == "email":
            print("Updating :", data["value"])
            user.email = data["value"] 
        elif data["field"] == "position":
            print("Updating :", data["value"])
            user.position = data["value"]
            print("Updating :", data["value"])
        elif data["field"] == "contacts":
            print("Updating :", data["value"])
            user.contacts = data["value"] 
        db.session.commit()

        flash("Update Successful","success")
        return jsonify({"Message":"Field Update Successful"})
    else:
        print("User Details Not saved!")

@app.route('/update_field', methods=['POST','GET'])
@login_required
def update_company():

    usr_id = current_user.id
    fields = ["name","image","email","position","contacts"]
    data = request.get_json()

    if usr_id and data:
        company = company_info.query.filter_by(usr_fKey=usr_id).first()

        if data["field"] == "postal_address":
            print("Updating :", data["value"])
            company.postal_address = data["value"] 
        elif data["field"] == "company_contacts":
            print("Updating :", data["value"])
            company.company_contacts = data["value"] 
        elif data["field"] == "website":
            print("Updating :", data["value"])
            company.website = data["value"]
        elif data["field"] == "tagline":
            print("Updating :", data["value"])
            company.tagline = data["value"] 
        elif data["field"] == "company_address":
            print("Updating :", data["value"])
            company.company_address = data["value"] 
        elif data["field"] == "facebook_link":
            print("Updating :", data["value"])
            company.facebook_link = data["value"]
        elif data["field"] == "instagram_link":
            print("Updating :", data["value"])
            company.instagram_link = data["value"]
        elif data["field"] == "twitter_link":
            print("Updating :", data["value"])
            company.twitter_link = data["value"]
        elif data["field"] == "company_email":
            print("Updating :", data["value"])
            company.company_email = data["value"]
        elif data["field"] == "whatsapp":
            print("Updating :", data["value"])
            company.whatsapp = data["value"]

        db.session.commit() 
        
        # flash("Update Successful","success")
        return jsonify({"Message":"Field Update Successful"})
        

    return render_template("message_blueprint.html")

@app.route('/download/job-advert')
def download_job_advert():
    print("Downolading Advert: ",request.remote_addr)
    return send_from_directory(
        directory='static/business-images',
        path='Q-Messanger_Job_advert_Marketing_Intern.pdf',
        as_attachment=True,
        mimetype='application/pdf'
    )

def email_prospective_companies(email,name, company_name):
    """Send registration confirmation email."""
    if not email:
        print("reg_confirmation==No Email Provided")
        return jsonify({"error": "Email not sent, No email provided"}), 400

    def send_veri_mail():

        app.config["MAIL_SERVER"] = "smtp.googlemail.com"
        app.config["MAIL_PORT"] = 587
        app.config["MAIL_USE_TLS"] = True
        # Creditentials saved in environmental variables
        em = app.config["MAIL_USERNAME"] = creds.get('email')  # os.getenv("MAIL")
        app.config["MAIL_PASSWORD"] = creds.get('gpass') #os.getenv("PWD")
        app.config["MAIL_DEFAULT_SENDER"] = "noreply@gmail.com"

        mail = Mail(app)


        msg = Message(subject="Quick Messanger - Eswatini", sender="no-reply@gmail.com", recipients=[email])

        msg.html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Invitation to Register on Quick Messanger!</title>
</head>
<body style="margin:0; padding:0; background:#f7f7f9; font-family:'Segoe UI', Arial, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f7f7f9; min-height:100vh;max-width: 700px;margin:0 auto">
        <tr>
            <td align="center">
                <table width="100%" cellpadding="0" cellspacing="0" style="background:#fff; border-radius:16px; box-shadow:0 4px 24px rgba(0,0,0,0.07); margin:40px 0; max-width:480px;"></table>
                    <tr>
                        <td align="center" style="padding:32px 0 16px 0;">
                            <img src="https://qm.techxolutions.com/static/images/logo-icon-white.png"  alt="Quick Messenger Logo" style="height:80px; border-radius:12px; background:#EF4036; padding:8px;">
                            <h3 style="color:#222; margin:0 0 12px 0; letter-spacing:1px;">✉Invitation to Register on Quick Messenger!</h3>
                        </td>
                    </tr>

                    <tr>
                        <td align="left" style="padding:0 32px;">
                            <p style="color:#EF4036; font-size:1.1em; margin:0 0 24px 0; font-weight:600;"><span style="color:#222;"></span></p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:0 32px;">
                            
                            <div class="main_cont" style="background:#f1f1f1; border-radius:10px; padding:18px 20px; margin-bottom:24px;">
                                <p style="color:#EF4036; font-size:1.1em; margin:0 0 24px 0; font-weight:600;"><span style="color:#222;">Good day {name},</span></p>

                                <p style="color:#353535; font-size:1em; margin:0 0 24px 0; font-weight:400;">I'm reaching out to introduce <b>Quick Messenger</b> — a fast-growing digital platform built to help businesses in Eswatini and beyond <b>increase brand awareness, 
                                    reach new audiences, and form valuable trading partnerships,</b> both locally and internationally.
                                </p> 
                                <a href="https://qm.techxolutions.com/business_community" target="_blank" style="display:inline-block; background:#EF4036; color:#fff; text-decoration:none; font-weight:500; padding:5px 15px; border-radius:15px; font-size:1em; margin-bottom:24px; box-shadow:0 2px 8px #ef403633;">Explore Platform</a>
                                <div style="background:#f1f1f1; border-radius:10px; padding:18px 20px; margin-bottom:24px;">
                                    <h2 style="color:#EF4036; font-size:1.1em; margin:0 0 10px 0;">Why Quick Messenger?</h2>
                                    <ul style="color:#444; font-size:1em; padding-left:18px; margin:0;">
                                        <li>📢 <b>Advertise & Promote</b> your products both on the platform and through digital
                                        channels (Interactive Adverts, SMS, push notifications, email).
                                        </li>
                                        <li>🌐 <b>Through our Business Community,</b> showcase your profile and product offerings across Eswatini and internationally –
                                        boosting brand awareness.
                                        </li>
                                        <li>🚀 <b>Instant Messaging</b> with your clients and partners</li>
                                        <li>📌 <b>Brand Awareness</b> & products campaigns</li>
                                        <li>🔒 <b>Secure & Private</b> communications</li>
                                        <li>📱 <b>Mobile & Desktop</b>, Application - easy to install</li>
                                        <li>📊 <b>Analytics</b> to track your engagement</li>
                                    </ul>
                                </div>
                                <p style="margin:0 0 8px 0;font-weight: 500;color:#353535">Please Follow the link below to explore pricing:</p>
                                <a href="https://qm.techxolutions.com/pricing" target="_blank" style="display:inline-block; background:#EF4036; color:#fff; text-decoration:none; font-weight:500; padding:5px 15px; border-radius:15px; font-size:1em; margin-bottom:24px; box-shadow:0 2px 8px #ef403633;">Pricing</a>
                                
                                <div style="background:#f1f1f1; border-radius:10px; padding:18px 20px; margin-bottom:24px;">
                                    <h2 style="color:#EF4036; font-size:1.1em; margin:0 0 10px 0;">Unlock the full power of our digital marketing Features?</h2>
                                    <ul style="color:#444; font-size:1em; padding-left:18px; margin:0;">
                                        <li>📲 <b>Interactive Advertising:</b> We Boost engagement with smart, clickable call-to-action (CTA) links that drive traffic to your offers, services — directly from your post or message.
                                        </li>
                                        <li>✉ <b>SMS Marketing:</b> We help you reach your customers instantly with Bulk SMS Campaigns — ideal 
                                            for promotions, reminders, and announcements. Reliable, fast, and mobile-first.
                                        </li>
                                        <li>🚀 <b>Push Note Marketing:</b> Send real-time push notifications straight to users’ devices or browsers. 
                                            A powerful way to keep your audience updated and engaged — even when they’re not on your site.</li>
                                        <li>📧 <b>Branded Email Marketing: </b> We take the hassle out of email design — you provide the content, we handle the branding. 
                                            Your emails will always reflect your business identity professionally.</li>
                                        <li>📌 <b>Advert Pinning Helper: </b> Give your ads more depth! Our Advert Pinning Helper lets you attach useful links to your 
                                            messages — whether it's your product website, image galleries, reviews, or external platforms.</li>
                                        <li>📊 <b>CRM System</b> – Gain valuable insights about your audience to make informed decisions and significantly reduce your marketing costs in the near future.</li></ul>
                                </div>

                                <p style="margin:0 0 8px 0;font-weight: 500;color:#353535">Join the Business Community for Free:</p>
                                <a href="https://qm.techxolutions.com/register" target="_blank" style="display:inline-block; background:#3671ef; color:#fff; text-decoration:none; font-weight:500; padding:5px 15px; border-radius:15px; font-size:1em; margin-bottom:24px; box-shadow:0 2px 8px #ef403633;">Sign Up</a>
                                <p style="margin:0 0 8px 0;color:#353535">🤝🏼We would love to have {company_name} on board.</p>
                                <div style="background:#f1f1f1; border-radius:10px; padding:18px 20px; margin-bottom:24px;">
                                    <ul style="color:#444; font-size:1em; padding-left:18px; margin:0;list-style-type: none;margin-left:-26px">
                                        <li>Warm Regards, </li>
                                        <li><b>Thabo Maziya, </b> Founder & CEO</li>
                                        <li> <i>CEO - Quick Messanger</i> </li>
                                        <li>✉ <a href="mailto:thabo@techxolutions.com" style="text-decoration: none;color:#2977c0"> thabo@techxolutions.com</a>  </li>
                                        <li>📞 <a href="tel://+26876412255" style="text-decoration: none;color:#2977c0"> (+268) 7641 2255</a></li>
                                        <li>🌐 <a href="https://qm.techxolutions.com" style="text-decoration: none;color:#2977c0"> techxolutions.com</a></li>
                                        <div>
                                            <span></span>
                                            <span> </span>
                                            <span> </span>
                                        </div>
                                    </ul>
                                </div>
                            </div>

                        </td>
                    </tr>
                 
                    <tr>
                        <td align="center" style="padding:0 32px 32px 32px; color:#888; font-size:0.95em; text-align:center;">
                            <p style="margin:0 0 8px 0;">Need help? Our support team is here for you: <a href="mailto:thabo@techxolutions.com" style="color:#EF4036; text-decoration:none;">info@techxolutions.com</a></p>
                            <p style="margin:0;">Welcome aboard,<br><b>The Quick Messenger Team</b></p>
                        </td>
                    </tr>
                </table>
                <p style="color:#bbb; font-size:0.9em; margin-top:16px;">&copy; 2025 Quick Messenger. All rights reserved.</p>
            </td>
        </tr>
    </table>
</body>
</html>
"""
        try:
            mail.send(msg)
            flash(f'Email Sent Successffully', 'success')
            print(f"reg_confirmation==Email sent to {email} for company {company_name}")
            return "Email Sent"
        except Exception as e:
            # flash(f'Email not sent here', 'error')
            print(f"reg_confirmation==Error sending email: {str(e)}")
            return "The mail was not sent"

    # try:
    send_veri_mail() 

def reg_confirmation(email, company_name):
    """Send registration confirmation email."""
    if not email:
        print("reg_confirmation==No Email Provided")
        return jsonify({"error": "Email not sent, No email provided"}), 400

    def send_veri_mail():

        app.config["MAIL_SERVER"] = "smtp.googlemail.com"
        app.config["MAIL_PORT"] = 587
        app.config["MAIL_USE_TLS"] = True
        # Creditentials saved in environmental variables
        em = app.config["MAIL_USERNAME"] = creds.get('email')  # os.getenv("MAIL")
        app.config["MAIL_PASSWORD"] = creds.get('gpass') #os.getenv("PWD")
        app.config["MAIL_DEFAULT_SENDER"] = "noreply@gmail.com"

        mail = Mail(app)


        msg = Message(subject="Registration Confirmation", sender="no-reply@gmail.com", recipients=[email])

        msg.html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Welcome to Quick Messenger!</title>
</head>
<body style="margin:0; padding:0; background:#f7f7f9; font-family:'Segoe UI', Arial, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f7f7f9; min-height:100vh;">
        <tr>
            <td align="center">
                    <table width="100%" cellpadding="0" cellspacing="0" style="background:#fff; border-radius:16px; box-shadow:0 4px 24px rgba(0,0,0,0.07); margin:40px 0; max-width:480px;"></table>
                    <tr>
                        <td align="center" style="padding:32px 0 16px 0;">
                            <img src="https://qm.techxolutions.com/static/images/logo-icon-white.png" alt="Quick Messenger Logo" style="height:60px; border-radius:12px; background:#EF4036; padding:8px;">
                        </td>
                    </tr>
                    <tr>
                        <td align="center" style="padding:0 32px;">
                            <h1 style="color:#222; font-size:2em; margin:0 0 12px 0; letter-spacing:1px;">Welcome to Quick Messenger!</h1>
                            <p style="color:#EF4036; font-size:1.1em; margin:0 0 24px 0; font-weight:600;">We're excited to have <span style="color:#222;">{company_name}</span> join our business community.</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:0 32px;">
                            <div style="background:#f1f1f1; border-radius:10px; padding:18px 20px; margin-bottom:24px;">
                                <h2 style="color:#EF4036; font-size:1.1em; margin:0 0 10px 0;">Why Quick Messenger?</h2>
                                <ul style="color:#444; font-size:1em; padding-left:18px; margin:0;">
                                    <li>🚀 <b>Instant Messaging</b> with your clients and partners</li>
                                    <li>📢 <b>Advertise & Promote</b> your products & services</li>
                                    <li>📌 <b>Brand Awareness</b> & products campaigns</li>
                                    <li>🔒 <b>Secure & Private</b> communications</li>
                                    <li>📱 <b>Mobile & Desktop</b> Application - easy to install</li>
                                    <li>🌐 <b>Business Community</b> networking</li>
                                    <li>📊 <b>Analytics</b> to track your engagement</li>
                                </ul>
                                <div style="margin-top:18px; background:#fff7e6; border-left:4px solid #EF4036; padding:12px 16px; border-radius:8px; color:#EF4036; font-size:1.05em;">
                                    <b>
                                        At Quick Messenger, we are committed to becoming the region’s leading digital marketing platform—empowering your business with advanced CRM (Customer Relationship Management) and CMS (Content Management System) tools. Our mission is to help you connect, engage, and grow like never before.
                                    </b>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td align="center" style="padding:0 32px;">
                            <a href="https://qm.techxolutions.com/business_community" style="display:inline-block; background:#EF4036; color:#fff; text-decoration:none; font-weight:600; padding:14px 36px; border-radius:8px; font-size:1.1em; margin-bottom:24px; box-shadow:0 2px 8px #ef403633;">Explore</a>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:0 32px 32px 32px; color:#888; font-size:0.95em; text-align:center;">
                            <p style="margin:0 0 8px 0;">Need help? Our support team is here for you: <a href="mailto:thabo@techxolutions.com" style="color:#EF4036; text-decoration:none;">info@techxolutions.com</a></p>
                            <p style="margin:0;">Welcome aboard,<br><b>The Quick Messenger Team</b></p>
                        </td>
                    </tr>
                </table>
                <p style="color:#bbb; font-size:0.9em; margin-top:16px;">&copy; 2025 Quick Messenger. All rights reserved.</p>
            </td>
        </tr>
    </table>
</body>
</html>
"""


        try:
            mail.send(msg)
            flash(f'We have sent you an email to confirm your registration', 'success')
            print(f"reg_confirmation==Email sent to {email} for company {company_name}")
            return "Email Sent"
        except Exception as e:
            # flash(f'Email not sent here', 'error')
            print(f"reg_confirmation==Error sending email: {str(e)}")
            return "The mail was not sent"

    # try:
    send_veri_mail() 
    # except:

@app.route('/get_reviews', methods=['POST'])
def get_reviews():
    data = request.get_json()
    company_id = data.get('company_id')
    reviews = Review.query.filter_by(company_id=company_id).all()
    return jsonify({
        "reviews": [
            {
                "rating": r.rating,
                "comment": r.comment,
                "customer_name": r.customer_name
            } for r in reviews
        ]
    })

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    with app.app_context():
        db.create_all()
        db.session.commit()

    app.run(debug=True, port=5001)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
