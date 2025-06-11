
# from alchemy_db import db.Model
from sqlalchemy import  MetaData, ForeignKey
from flask_login import login_user, UserMixin
from sqlalchemy.orm import backref, relationship
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
# from app import app

db = SQLAlchemy()


#from app import login_manager

metadata = MetaData()



class chat_user(db.Model,UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique=True)
    pkey = db.Column(db.String(2048))
    other = db.Column(db.String(200))
    other1 = db.Column(db.String(200)) 
    db.Column(db.DateTime(), default=datetime.now)
    company_details = relationship("company_info", backref='chat_user', lazy=True)
    user_details = relationship("User", backref='chat_user', lazy=True)
    visitors_id = relationship("Visitors", backref='chat_user', lazy=True)
    
#Users class, The class table name 'h1t_users_cvs'
class User(db.Model,UserMixin):

    #Create db.Columns
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20))
    cht_usr_fKey = db.Column(db.Integer, ForeignKey('chat_user.id'))
    image = db.Column(db.String(30), nullable=True)
    position = db.Column(db.String(30), nullable=True)
    contacts = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120),unique=True)
    password = db.Column(db.String(120), unique=True)
    confirm_password = db.Column(db.String(120), unique=True)
    verified = db.Column(db.Boolean, default=False)
    other = db.Column(db.String(200))
    other1 = db.Column(db.String(200)) 
    db.Column(db.DateTime(), default=datetime.now)
    role = db.Column(db.String(120))
    company_id = relationship("company_info", backref='user', lazy=True)
    notification_access = relationship("NotificationsAccess", backref='chat_user', lazy=True)

    def to_dict(self):
        return {
            "name": self.name if self.name else "",
            "image": self.image,
            "position": self.position if self.position else "",
            "contacts": self.contacts if self.contacts else "",
            # "timestamp": self.date if self.date else None,
            "email" :self.email if self.contacts else ""
        }

    __mapper_args__ = {
        "polymorphic_identity":'user',
        'polymorphic_on':role
    }


class Advert(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    usr_id = db.Column(db.Integer)
    comp_id = db.Column(db.Integer,ForeignKey('company_info.id'))
    advert_image = db.Column(db.String(100))
    advert_image = db.Column(db.String(100))
    advert_days = db.Column(db.Integer)
    start_date = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime)


class News(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    usr_id = db.Column(db.Integer)
    comp_id = db.Column(db.Integer,ForeignKey('company_info.id'))
    story_title = db.Column(db.String(50))
    story = db.Column(db.String(350))
    other = db.Column(db.String(50))
    other1 = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime())
    images_id = relationship("NewsImages",backref="news", lazy=True)
    views = relationship("Views", backref="news", lazy=True)
    comments = relationship("Comments", backref="news", lazy=True)

class Views(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, ForeignKey('news.id'))
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    ip = db.Column(db.String(50))  # IP address of the user
    view_date = db.Column(db.DateTime())

    def to_dict(self):
        return {
            "id": self.id,
            "news_id": self.news_id,
            "user_id": self.user_id,
            "view_date": self.view_date.strftime("%H:%M - %d %b %y") if self.view_date else None
        }

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, ForeignKey('news.id'))
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    comment = db.Column(db.String(500))
    comment_date = db.Column(db.DateTime(), default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "news_id": self.news_id,
            "user_id": self.user_id,
            "comment": self.comment,
            "comment_date": self.comment_date.strftime("%H:%M - %d %b %y") if self.comment_date else None
        }

class NewsImages(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    news_id = db.Column(db.Integer,ForeignKey("news.id"))
    image = db.Column(db.String(50))
    main = db.Column(db.String(50))
    caption = db.Column(db.String(50))

class clientuser(User):

    id = db.Column(db.Integer, ForeignKey('user.id'), primary_key=True)
    username = db.Column(db.String(20))
    pkey = db.Column(db.DateTime())
    other = db.Column(db.String(200))
    # other1 = db.Column(db.String(200)) #Resume
    # jobs_applied_for = relationship("Applications", backref='Applications.job_title', lazy=True)
    # hired_user = relationship("hired", backref='Hired Applicant', lazy=True)

    __mapper_args__={
            "polymorphic_identity":'clientuser'
        }

class company_info(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    usr_fKey = db.Column(db.Integer, ForeignKey('chat_user.id'))
    usr_id = db.Column(db.Integer, ForeignKey('user.id'))
    company_name = db.Column(db.String(50))
    email = db.Column(db.String(120),nullable=True)
    image = db.Column(db.String(120),default="default.jpg")
    category = db.Column(db.String(120))
    country = db.Column(db.String(50))
    company_address = db.Column(db.String(120))
    postal_address = db.Column(db.String(120)) #postal
    company_contacts = db.Column(db.String(120))
    website = db.Column(db.String(120))
    tagline=db.Column(db.String(255))
    fb_link = db.Column(db.String(120))
    linkedIn_link = db.Column(db.String(120))
    threads_link= db.Column(db.String(120))
    twitter_link = db.Column(db.String(120))
    instragram_link = db.Column(db.String(120))
    youtube = db.Column(db.String(120))
    other = db.Column(db.String(120)) 
    other2 = db.Column(db.String(120)) #Abbreviation
    payment_options = db.Column(db.String(100))
    adverts_id = relationship('Advert',backref="company_info",lazy=True)
    news_id = relationship('News',backref="company_info",lazy=True)

    def to_dict(self):
        return {
            "id" : str(self.id),
            "company_name": self.company_name,
            "abbreviation":self.other2 if self.other2 else "",
            "email": self.email if self.email else "",
            "company_address": self.company_address if self.company_address else "",
            "postal_address": self.postal_address if self.postal_address else "",
            "logo":self.image if self.image else "",
            "company_contacts": self.company_contacts if self.company_contacts else "",
            # "timestamp": self.date if self.date else None,
            "website" :self.website if self.website else "",
            "tagline" :self.tagline if self.tagline else "",
            "fb_link" :self.fb_link if self.fb_link  else "",
            "twitter_link" :self.twitter_link if self.twitter_link else "",
            "youtube" :self.youtube if self.youtube  else "",
            "country" :self.country if self.country  else ""
        }

class recovery_check(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cht_usr_id = db.Column(db.Integer)
    comp_id = db.Column(db.Integer)
    name =  db.Column(db.String(20))
    username =  db.Column(db.String(20))
    status = db.Column(db.String(20),default="False")
    timestamp = db.Column(db.DateTime)
    reg_timestamp = db.Column(db.DateTime)

class Messages(db.Model,UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(20))
    sender_id = db.Column(db.Integer)
    receiver = db.Column(db.String(20))
    subject = db.Column(db.String(50))
    message = db.Column(db.String(1024))
    date = db.Column(db.DateTime(), default=datetime.now)
    key = db.Column(db.String(50)) #for public key identification
    company_info_id = db.Column(db.Integer)
    company_info_name = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "subject": self.subject,
            "sender_id": self.sender_id,
            "receiver": self.receiver,
            "message": self.message,
            "timestamp": self.date.strftime("%H:%M - %d %b %y") if self.date else None,
            "key": self.key,
            "company_info_id" :self.company_info_id,
            "company_info_name" :self.company_info_name
        }

class Project_Brief(db.Model,UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,ForeignKey('user.id'))
    name = db.Column(db.String(120))
    brief_date = db.Column(db.String(120))
    token = db.Column(db.String(120))

class Curr_Projects(db.Model,UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    name = db.Column(db.String(120))
    deposit = db.Column(db.Numeric(20))
    installments = db.Column(db.Numeric(20))
    proj_charge = db.Column(db.Numeric(20))
    proj_started = db.Column(db.Date())
    proj_deadline = db.Column(db.Date())
    comments = db.Column(db.String(120))
    submitted = db.Column(db.Date())

class Visitors(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    cht_usr_id = db.Column(db.Integer, ForeignKey('chat_user.id'),nullable=True)
    ip = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime())
    first_visit = db.Column(db.DateTime())
    last_visit = db.Column(db.DateTime())
    n_visits = db.Column(db.Integer)
    country = db.Column(db.String(50))

class NotificationsAccess(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    usr_id = db.Column(db.Integer, ForeignKey('user.id'),nullable=False)
    endpoint = db.Column(db.String(255))
    p256dh = db.Column(db.String(255))
    auth = db.Column(db.String(255))
    ip = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime)