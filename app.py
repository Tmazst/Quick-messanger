
from flask import Flask,render_template,url_for,redirect,request,flash,jsonify,session
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
from sqlalchemy import or_
from werkzeug.datastructures import FileStorage
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
import pytz


#Did latest commit with the requirement file

#Change App
app = Flask(__name__)
app.config['SECRET_KEY'] = "sdsd1245jfe832j2rj_32j"

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle':280}
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOADED"] = 'static/uploads'
app.config["ADVERTS_IMAGES"] = 'static/ad-images'

# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://techtlnf_tmaz:!Tmazst41#@localhost/techtlnf_quick_m_db" 
# Local
if os.environ.get('EMAIL_INFO') == 'info@techxolutions.com':
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///business_chat_db.db"
else:#Online
    app.config[
    "SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://techtlnf_tmaz:!Tmazst41#@localhost/techtlnf_quick_m_db" 


db.init_app(app)
CORS(app)  # Allow cross-origin requests

login_manager = LoginManager(app)

# Encrypt Password
encrypt_password = Bcrypt(app)

# Log in
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

application = app

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

# Function to check if the file has an allowed extension
def allowed_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_file(file):

        filename = secure_filename(file.filename)

        _img_name, _ext = os.path.splitext(filename)
        gen_random = secrets.token_hex(8)
        new_file_name = gen_random + _ext

        if file.filename == '':
            return 'No selected file'

        if file.filename:
            file_saved = file.save(os.path.join(app.config["UPLOADED"],new_file_name))
            print(f"File Upload Successful!!", "success")
            return new_file_name

        else:
            return f"Allowed are [.txt, .xls,.docx, .pdf, .png, .jpg, .jpeg, .gif] only"


def process_ads(file):

        filename = secure_filename(file.filename)

        _img_name, _ext = os.path.splitext(filename)
        gen_random = secrets.token_hex(8)
        new_file_name = gen_random + _ext

        if file.filename == '':
            return 'No selected file'

        if file.filename:
            file_saved = file.save(os.path.join(app.config["ADVERTS_IMAGES"],new_file_name))
            print(f"File Upload Successful!!", "success")
            return new_file_name

        else:
            return f"Allowed are [.txt, .xls,.docx, .pdf, .png, .jpg, .jpeg, .gif] only"

def createall(db_):
    db_.create_all()

encry_pw = Bcrypt()

# @app.route("/username/<username>", methods=['POST','GET'])
def get_all_messages():
    usr = session.get("username")
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
    check_user_ndb = session.get('username') #Username stored in session
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


@app.route("/", methods=['POST','GET'])
def home():


    # all_messages = get_all_messages()
    # latest_entry = Messages.query.filter_by(sender=user.id).order_by(Messages.date.desc()).first()
    # return redirect(url_for('home'))
    qm_bs_obj = company_info.query.filter_by(company_name="Quick Messanger").first()
    latest_req = company_info.query.order_by(company_info.id.asc()).all()[1]
    messages = get_all_messages()
    print("Home==Companies Showcasing: ", qm_bs_obj, latest_req)
    del_al_msgs = Messages.query.all()
    for msg in del_al_msgs:
        if msg.sender == "none" or msg.receiver == "none":
            db.session.delete(msg)
            db.session.commit()
            print("Home==Deleted Messages: ", msg)

    # all_msgs = Messages.query.all()
    # for msg in all_msgs:
    #     # if msg.sender == "none" or msg.receiver == "none":
    #         db.session.delete(msg)
    #         db.session.commit()
    #         print("Home==Deleted Messages: ", msg)

    # if current_user.is_authenticated:
    #     company = company_info.query.filter_by(usr_id=current_user.id).first()
    #     if not company.category or company.company_contacts or company.company_address:
    #         return redirect(url_for("company_account"))

    return render_template("index.html", qm_bs_obj=qm_bs_obj,latest_req=latest_req )

# In-memory storage for keys and messages
users = {}  # {username: public_key}
messages = {}  # {username: [encrypted_messages]}


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


@app.route('/compose', methods=['POST',"GET"])
# @login_required
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
            db.session.commit()
            flash("Message Sent!!","success")
            print("Messages Sent!!")
            return redirect(url_for('compose'))

        print("Users: ", users)

    return render_template("compose.html", users=users,usr=curr_user,form=message_form, chat_with = chat_with,chat_with_company=chat_with_company )

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
            session['username'] = username.username
            session['pubKey']=username.pkey
            return redirect(url_for('home'))
        else:
            print("User Not Found")
            return redirect(url_for('register'))
                # return redirect(url_for("home"))

    return jsonify({"message":"User Logged in"}),200

@app.route('/register', methods=['POST','GET'])
def register():
    # data = request.json
    
    usr_ssn = session.get('username')
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

            user = User.query.filter_by(cht_usr_fKey=get_user.id).first()

            company_details = company_info(
                company_name = form['company_name'],
                usr_fKey = get_user.id,
                usr_id=user.id,
                image = "logo-avator.png",
                country = form['country']
            )
                
            db.session.add(company_details)

            db.session.add(user_details)

            uid = get_user.id
            print("UID: ", uid)
            id_ser = ser.dumps({"form": uid})
            print("UID_SER: ", id_ser)

            data_json = {
                        'id': id_ser,
                        'username': get_user.username
                    }
            
            try:
                db.session.commit()
                print("register==Registration Successful")
                flash("✔ Registration Successful","success")
                # session['username'] = get_user.username
                # session['pubKey']=get_user.pkey
                # session.permanent = True  # Make the session permanent 
                return redirect(url_for('home'))
            except IntegrityError:
                db.session.rollback()  # Rollback the session to clear the pending state
                print("register==User Registration Evoked because of Integrity Error: ", get_user.username)
                db.session.commit()

        print("Registration Successful")

        print("USER DATA: ",reg_usr_db)
        # Save the public key to the database or any persistent storage

    return render_template('register.html')

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

# ------------------------------COMPANIES DATA------------------------------- #
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
@app.route("/company_account", methods=["POST", "GET"])
@login_required
def company_account():

    db.create_all()
    id = current_user.id
    cmp_usr = company_info.query.filter_by(usr_id=id).first()
    company_update = Company_Register_Form(obj=cmp_usr)

    if not cmp_usr:
        print("company_account==No Company Found for User ID: ", id)
        return jsonify({"error": "No Company Found, Please Register"}), 404

    if request.method == "POST":

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
        cmp_usr.company_address = company_update.company_address.data
        cmp_usr.twitter_link = company_update.twitter_link.data
        # cmp_usr.instagram_link = company_update.instagram_link.data
        cmp_usr.youtube = company_update.youtube_link.data
        cmp_usr.payment_options = request.form.get('payment_options')

        db.session.commit()

    # from myproject.models import user
    return render_template("company_account.html", company_update=company_update,cmp_usr=cmp_usr)

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
    data = request.get_json()

    if data['to'] == "Select User":
        return ""

    cht_id = chat_user.query.get(current_user.cht_usr_fKey)
    
    comp = company_info.query.filter_by(usr_fKey=cht_id.id).first()
    if not comp:
        print("send_message==Company Object not found, for user: ",current_user.id)
        return jsonify({'status': 'Company Object not found'}),400
    
    message = Messages(
        sender=current_user.name,
        receiver=data['to'],
        sender_id = current_user.id,
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

    if request.method == "POST":
        advert = Advert(
            usr_id = current_user.id,
            comp_id = current_user.company_id[0].id,
        )

        if form.advert_image.data:
            advert_img = process_file(form.advert_image.data)
            advert.advert_image = advert_img

        db.session.add(advert)
        db.session.commit()
        flash("Advert Uploaded Successfully","success")

    return render_template("advert_form.html",form=form)

@app.route("/adverts")
def adverts():

    adverts = Advert.query.all()
    companies = {c.id: c for c in company_info.query.all()}
    num_columns = 3
    columns = [[] for _ in range(num_columns)]
    for idx, ad in enumerate(adverts):
        print("idx % num_columns: ",idx % num_columns)
        columns[idx % num_columns].append(ad)
    # print("All Cols: ",columns)
    return render_template("adverts.html",columns=columns,companies=companies)

@app.route("/company_stories")
def news():

    news = News.query.all()
    all_news_imgs = NewsImages.query.all()
 
    # num_columns = 3
    # columns = [[] for _ in range(num_columns)]
    # for idx, story in enumerate(news):
    #     print("idx % num_columns: ",idx % num_columns)
    #     columns[idx % num_columns].append(story)

    return render_template("news.html",news=news,all_news_imgs=all_news_imgs)


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


@app.route('/news_form', methods=['POST',"GET"])
@login_required 
def news_form():

    form = StoryForm()
    
    if request.method == "POST":
        news_obj = News(
            usr_id = current_user.id,
            comp_id = current_user.company_id[0].id,
            story_title = form.story_title.data,
            story=form.story.data,
            timestamp=current_time_wlzone()
        )

        db.session.add(news_obj)
        db.session.commit()
        # After committing, news_obj.id will be automatically set by SQLAlchemy
        story = News.query.get(news_obj.id)

        if form.images.data:
            for image_file in form.images.data:
                image= process_file(image_file)
                news_images_obj = NewsImages(
                    image = image,
                    news_id = story.id
                    # caption = news_images_obj.caption.data,
                    # main = news_images_obj.main.data
                )
                
                db.session.add(news_images_obj)

            db.session.commit()
            flash("Thank You for Sharing Your Story","success")

    return render_template("news_updates_form.html",form=form)

@app.route('/business_community', methods=['POST',"GET"])
def business_community():

    companies = company_info.query.all()
    categories = {comp.category for comp in companies}

    return render_template("business_community.html",companies=companies,categories=categories)

@app.route('/get_messages', methods=['GET'])
@login_required
def get_messages():
    
    # user_messages = []
    if request.method == 'GET':

        other_usrname = request.args.get('key')
        other_user_obj = chat_user.query.filter_by(username=other_usrname).first()
        my_usrname = chat_user.query.get(current_user.cht_usr_fKey)
        if not other_usrname:
            print("**get_messages==No Username Found")
            return jsonify({'error': 'No username provided'}), 400
        
        print("Get Messages ==Username: ", other_usrname)
        print("Get Messages ==MY_Username: ", my_usrname.username)

        from sqlalchemy import or_

        # Fetch all messages between the two users
        all_chat_messages = Messages.query.filter(
            or_(
                (Messages.sender == my_usrname.username) & (Messages.receiver == other_usrname),
                (Messages.sender == other_usrname) & (Messages.receiver == my_usrname.username)
            )
        ).order_by(Messages.date.asc()).all()


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
    if current_user.is_authenticated:
        users = chat_user.query.all()
        user_name = chat_user.query.get(current_user.cht_usr_fKey)
        print("DEBUG: ", current_user.id)
        company = company_info.query.filter_by(usr_id=current_user.id).first()

        curr_user = User.query.filter_by(cht_usr_fKey=current_user.id).first()
        subject = message_form.get("subject")
        message = message_form.get("reply-message")
        print("Debug Reply MEssage: ", message)	
        # Receiver's Details'
        receiver = message_form.get("recipient_username")
        recipientMsg = message_form.get("rec_encrypted-msg")
        
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
            return redirect(url_for('get_messages', key=receiver))


    return render_template("message_blueprint.html", users=users,usr=curr_user,company=company)


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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    with app.app_context():
        db.create_all()
        db.session.commit()

    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
