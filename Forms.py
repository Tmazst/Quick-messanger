from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField, TextAreaField,BooleanField, SelectField,DateField, URLField, RadioField, HiddenField, TelField, MultipleFileField,IntegerField,SelectMultipleField
from wtforms.validators import DataRequired,Length,Email, EqualTo, ValidationError, Optional
from flask_login import current_user
from flask_wtf.file import FileField , FileAllowed
from wtforms.widgets import ListWidget, CheckboxInput
# from app import db, User
import re
# from wtforms.fields.html5 import DateField,DateTimeField

class NormalizedPhoneField(TelField):
    def process_formdata(self, valuelist):
        if valuelist:
            # Normalize the number here before validation
            self.data = valuelist[0].replace(" ", "").replace("-", "")

class Register(FlaskForm):

    name = StringField('name', validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('email', validators=[DataRequired(),Email()])
    position= StringField('position', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=64)])
    confirm = PasswordField('confirm', validators=[DataRequired(),EqualTo('password'), Length(min=8, max=64)])
    phone = NormalizedPhoneField('Contact (Please include country code)', validators=[Length(min=8, max=64)])
    zip_code = StringField('Zip Code / Postal Code', validators=[Length(min=0, max=64)])
    address = StringField('Physical Address', validators=[DataRequired(), Length(min=8, max=100)])
    image= FileField('Profile Image', validators=[FileAllowed(['jpg','png'])])

    submit = SubmitField('Submit')

    def validate_email(self,email):
        from app import db, User,app

        # with db.init_app(app):
        user_email = User.query.filter_by(email = self.email.data).first()
        if user_email:
            return ValidationError(f"Email already registered in this platform")

class MessagesForm(FlaskForm):
    receiver = SelectField('To', validators=[Optional()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = SelectField('Subject',choices=sorted([
        ('Order', 'Order'),
        ('Service Enquiry', 'Service Enquiry'),
        ('Testimonial', 'Testimonial'),
        ('Message', 'Message'),
        ('Quote Request', 'Quote Request'),
        ('Report', 'Report'),
        ('Complaint', 'Complaint'),
        ('Partnership', 'Partnership'),
        (' ', 'Other')
    ]), validators=[Optional()])
    message = TextAreaField('Message', validators=[DataRequired()])
    name = StringField('Name', validators=[Optional(), Length(min=2, max=50)])
    phone = StringField('Phone', validators=[Optional(), Length(min=8, max=20)])
    cust_email = StringField('Email', validators=[Optional(), Email()])
    
    submit = SubmitField('Send')

class JobApplicationForm(FlaskForm):
    name =  StringField('Name', validators=[DataRequired()])
    email =  StringField('Email', validators=[DataRequired(), Email()])
    cv = FileField('Upload ID (JPG,JPEG)', validators=[DataRequired()])
    id = FileField('Upload CV (PDF/DOCX FILE)', validators=[DataRequired()])

    submit = SubmitField('Send Application')

HASHTAG_CHOICES = [
    ('public_relations', '#public_relations'),
    ('community_service', '#community_service'),
    ('product_campaign', '#product_campaign'),
    ('product_features', '#product_features'),
    ('new_product', '#new_product'),
    ('general_news', '#general_news'),
    ('upcoming_event', '#upcoming_event'),
    ('webinar_review', '#webinar_review'),
    ('company_history', '#company_history'),
    ('company_update', '#company_update'),
    ('milestone', '#milestone'),
    ('leadership', '#leadership'),
    ('team_spotlight', '#team_spotlight'),
    ('partnership', '#partnership'),
    ('awards', '#awards'),
    ('csr', '#csr'),
    ('sustainability', '#sustainability'),
    ('diversity', '#diversity'),
    ('inclusion', '#inclusion'),
    ('press_release', '#pressRelease'),
    ('expansion', '#expansion'),
    ('rebranding', '#rebranding'),
    ('anniversary', '#anniversary'),
    ('customer_story', '#customerStory'),
    ('testimonial', '#testimonial'),
    ('product_launch', '#productLaunch'),
    ('feature_update', '#featureUpdate'),
    ('how_to', '#howTo'),
    ('case_study', '#caseStudy'),
    ('user_guide', '#userGuide'),
    ('faq', '#faq'),
    ('service_alert', '#serviceAlert'),
    ('maintenance', '#maintenance'),
    ('promotion', '#promotion'),
    ('discount', '#discount'),
    ('limited_offer', '#limitedOffer'),
    ('event_recap', '#eventRecap'),
    ('event_announcement', '#eventAnnouncement'),
    ('webinar', '#webinar'),
    ('conference', '#conference'),
    ('meetup', '#meetup'),
    ('training', '#training'),
    ('workshop', '#workshop'),
    ('charity', '#charity'),
    ('volunteering', '#volunteering'),
    ('community_engagement', '#communityEngagement'),
    ('industry_news', '#industryNews'),
    ('market_trends', '#marketTrends'),
    ('thought_leadership', '#thoughtLeadership'),
    ('expert_opinion', '#expertOpinion'),
    ('innovation', '#innovation'),
    ('technology', '#technology'),
    ('research', '#research'),
    ('insights', '#insights'),
    ('best_practices', '#bestPractices'),
    ('employee_spotlight', '#employeeSpotlight'),
    ('culture', '#culture'),
    ('wellbeing', '#wellbeing'),
    ('career', '#career'),
    ('job_opening', '#jobOpening'),
    ('internship', '#internship'),
    ('team_building', '#teamBuilding'),
    ('announcement', '#announcement'),
    ('reminder', '#reminder'),
    ('safety', '#safety'),
    ('compliance', '#compliance'),
    ('policy_update', '#policyUpdate'),
    ('success_story', '#successStory'),
    ('behind_the_scenes', '#behindTheScenes'),
    ('fun_fact', '#funFact'),
    ('did_you_know', '#didYouKnow'),
]

class StoryForm(FlaskForm):

    story_title = StringField('Story Title', validators=[Optional()])
    story = TextAreaField('Story', validators=[Optional()])
    images = MultipleFileField("Images")
    main = BooleanField('Main Image?')
    hashtags = SelectMultipleField(
        'Select Hashtags',
        choices=HASHTAG_CHOICES,
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False)
    )
    submit = SubmitField('Send')

class QMUpdatesForm(FlaskForm):

    title = StringField('Title', validators=[DataRequired(), Length(min=4, max=40)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=10, max=100)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    days = SelectMultipleField('Days', choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday')],
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False)
    )
    url = URLField('Link')
    submit = SubmitField('Submit')

class SMSMarketingForm(FlaskForm):

    title = StringField('Title', validators=[DataRequired(), Length(min=4, max=20)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=200)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    days = SelectMultipleField('Days', choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday')],
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False)
    )
    url = URLField('Link (Do you want to add link to your SMS?)', validators=[Optional()])
    submit = SubmitField('Submit')

class EmailProspectsForm(FlaskForm):

    title = StringField('Title', validators=[DataRequired(), Length(min=4, max=20)])
    name = StringField('Person Name', validators=[DataRequired(), Length(min=10, max=200)])
    email = StringField('Email', validators=[DataRequired()])
    company = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Send')

class AdvertForm(FlaskForm):
    advert_title = StringField('Advert Title', validators=[DataRequired(), Length(min=4, max=100)])
    advert_image = FileField('Upload Advert', validators=[FileAllowed(['jpg', 'png'])])
    start_date = DateField('Start Date', validators=[DataRequired()])
    advert_days = IntegerField('How manys days?', validators=[DataRequired()])
    url= URLField('Pin URL (Optional)', validators=[Optional(), Length(max=200)])
    submit = SubmitField("Submit")

class Update_account_form(FlaskForm):

    email = StringField('Email', validators=[DataRequired(), Email()])

class Company_Register_Form(FlaskForm):

    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=120)])
    company_email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=100)])
    company_contacts = NormalizedPhoneField('Contact(s)', validators=[Length(min=8, max=64)])
    company_address = StringField('Physical Address', validators=[DataRequired(), Length(min=8, max=100)])
    abbreviation = StringField("Abbreviation",validators=[Optional(), Length(min=1, max=20)])
    category_other = StringField("Please Specify")
    category = SelectField(
        "Select Category",
        choices=sorted([
            ("Accounting", "Accounting"),
            ("Advertising", "Advertising"),
            ("Aerospace", "Aerospace"),
            ("Agriculture", "Agriculture"),
            ("Artificial Intelligence", "Artificial Intelligence"),
            ("Auto Parts & Accessories", "Auto Parts & Accessories"),
            ("Automotive", "Automotive"),
            ("Banking", "Banking"),
            ("Beauty & Wellness", "Beauty & Wellness"),
            ("Biotechnology", "Biotechnology"),
            ("Boot Camp", "Boot Camp"),
            ("Blockchain and Cryptocurrency", "Blockchain and Cryptocurrency"),
            ("Car Care", "Car Care"),
            ("Chemical Engineering", "Chemical Engineering"),
            ("Cleaning Services", "Cleaning Services"),
            ("Code Academy", "Code Academy"),
            ("Computer & Office Equipment Services", "Computer & Office Equipment Services"),
            ("Construction", "Construction"),
            ("Consulting", "Consulting"),
            ("Cooperative Society", "Cooperative Society"),
            ("Creative Multimedia", "Creative Multimedia"),
            ("Cultural", "Cultural"),
            ("Cybersecurity", "Cybersecurity"),
            ("Defense and Security", "Defense and Security"),
            ("Digital Marketing", "Digital Marketing"),
            ("E-learning", "E-learning"),
            ("E-commerce", "E-commerce"),
            ("Education", "Education"),
            ("Electrical", "Electrical"),
            ("Electronics & Electrotechnics", "Electronics & Electrotechnics"),
            ("Electronic Repairs & Maintenance", "Electronics & Maintenance"),
            ("Energy & Utilities", "Energy & Utilities"),
            ("Entertainment and Media", "Entertainment and Media"),
            ("Environmental Services", "Environmental Services"),
            ("Event Planning & Management", "Event Planning & Management"),
            ("Fashion", "Fashion"),
            ("Fashion & Design", "Fashion & Design"),
            ("Finance", "Finance"),
            ("Food and Beverage", "Food and Beverage"),
            ("Forex & Currency Exchange", "Forex & Currency Exchange"),
            ("Freelance & Gig Economy", "Freelance & Gig Economy"),
            ("Gaming", "Gaming"),
            ("Government", "Government"),
            ("Graphic Design", "Graphic Design"),
            ("Healthcare", "Healthcare"),
            ("Home Services", "Home Services"),
            ("Hospitality", "Hospitality"),
            ("Human Resources", "Human Resources"),
            ("Innovation & Startups", "Innovation & Startups"),
            ("Insurance", "Insurance"),
            ("Job Boards", "Job Boards"),
            ("Legal", "Legal"),
            ("Loans & Financial Services", "Loans & Financial Services"),
            ("Logistics & Supply Chain", "Logistics & Supply Chain"),
            ("Manufacturing", "Manufacturing"),
            ("Marine and Shipping", "Marine and Shipping"),
            ("Market Research", "Market Research"),
            ("Mechanical Engineering", "Mechanical Engineering"),
            ("Media & Technology", "Media & Technology"),
            ("Mining and Metals", "Mining and Metals"),
            ("News & Media", "News & Media"),
            ("Nonprofit", "Nonprofit"),
            ("Office Supplies & Stationery", "Office Supplies & Stationery"),
            ("Oil and Gas", "Oil and Gas"),
            ("Pet Services", "Pet Services"),
            ("Pharmaceutical", "Pharmaceutical"),
            ("Printer & Cartridge Services", "Printer & Cartridge Services"),
            ("Plumbing", "Plumbing"),
            ("Professional Services", "Professional Services"),
            ("Photography & Filming", "Photography & Filming"),
            ("Public Relations", "Public Relations"),
            ("Real Estate", "Real Estate"),
            ("Retail", "Retail"),
            ("Sustainability and CleanTech", "Sustainability and CleanTech"),
            ("Software Development", "Software Development"),
            ("Sports and Recreation", "Sports and Recreation"),
            ("Technology", "Technology"),
            ("Telecommunications", "Telecommunications"),
            ("Tourism & Travel", "Tourism & Travel"),
            ("Transportation and Logistics", "Transportation and Logistics"),
            ("Travel and Tourism", "Travel and Tourism"),
            ("Web Development", "Web Development"),
            ("Other", "Other"),
        ], key=lambda x: x[1]),
        validators=[DataRequired(), Length(min=2, max=100)]
    )
    tagline=StringField('Selling Tagline (Briefly describe your product or service offering)', validators=[Optional(), Length(min=4, max=150)])
    company_logo = FileField('Company Logo', validators=[FileAllowed(['jpg', 'png'])])
    website_link = URLField('Company Website Link')
    facebook_link = URLField('Facebook Link')
    twitter_link = StringField('X Link (former Twitter)')
    youtube_link = URLField('Youtube Link')
    payment_options = RadioField("Choose Payment Plan",
                                 choices=[("pay_plan_1", "Pay Monthly"), ("pay_plan_4", "Pay Annually"),
                                          ("pay_plan_2", "Pay Per Advert"), ("pay_plan_3", "Free For Now")])

    submit = SubmitField('Submit')

class Company_UpdateAcc_Form(FlaskForm):

    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=60)])
    company_email = StringField('Email', validators=[DataRequired(), Email(), Length(min=5, max=60)])
    company_logo = FileField('Company Logo', validators=[ FileAllowed(['jpg','png'])])
    company_contacts = StringField('Contact(s)', validators=[Length(min=8, max=64)])
    company_address = StringField('Physical Address', validators=[DataRequired(), Length(min=8, max=100)])
    website_link = URLField('Company Website Link')
    facebook_link = URLField('Facebook Link')
    twitter_link = URLField('Twitter Link')
    youtube_link = URLField('Youtube Link')
    payment_options = RadioField("Choose Payment Plan", choices=[("pay_plan_1", "Pay Monthly"),("pay_plan_4", "Pay Annually"),
                                                                 ("pay_plan_2", "Pay Per Advert"),("pay_plan_3", "Free For Now")])

    # Validate email before saving it in database
    def validate_email(self,company_email):
        from app import db, company_user
        if current_user.company_email != self.company_email.data:
            #Check if email exeists in database
            cmp_user_email = db.query(company_user).filter_by(company_email = self.company_name.data).first()
            cmp_name = db.query(company_user).filter_by(company_email=self.company_name.data).first()
            if cmp_user_email or cmp_name:
                raise ValidationError(f"email, {company_email.value}, already taken.")

    def validate_company_name(self, company_name):
        from app import db, company_user
        if current_user.comapny_name != self.company_name.data:
            # Check if email exists in database
            cmp_name = db.query(company_user).filter_by(comapny_name=self.company_name.data).first()
            if cmp_name:
                raise ValidationError(f"Company Name, {company_name.value} , already taken.")

    company_submit = SubmitField('Update')

class Login(FlaskForm):
    email = StringField('email', validators=[DataRequired(),Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=64)])
    submit = SubmitField('Login')

class Contact_Form(FlaskForm):

    name = StringField('name')
    email = StringField('email', validators=[DataRequired(),Email()])
    subject = StringField("subject")
    message = TextAreaField("Message",validators=[Length(min=8, max=2000)])
    submit = SubmitField("Send")

class Project_Form(FlaskForm):

    target_audience = SelectField('Customers Age Range', choices=[("18 - 25 years","18 - 25 years"),("18 - 36 years","18 - 36 years"),("25 - 45 years","25 - 45 years"),("+18 years","+18 years"),("+36 years","+36 years")])
    targetm_area = SelectField('Customers Locations',
                                  choices=[("Urban Set-up", "Urban Set-up"), ("Rural", "Rural"),
                                           ("No Specific Area", "No Specific Area")])
    targetm_segment = SelectField('Customers Categorised',
                               choices=[("Working Class", "Working Class"), ("Students", "Students"),("Tourists", "Tourists"),
                                        ("Non Working Class", "Non Working Class"),("No Specific Category", "No Specific Category")])
    artwork_name = StringField('Verbiage')
    company_category = SelectField('Category', choices=[("Technology","Technology"), ("Healthcare","Healthcare"),("Finance","Finance"),("Retail","Retail"),
                                                        ("Manufacturing","Manufacturing"),("Energy","Energy"), ("Transportation and Logistics","Transportation and Logistics"),
                                                        ("Entertainment and Media","Entertainment and Media"),("Real Estate","Real Estate"),("Professional Services","Professional Services")])
    other_services = StringField('Services')
    vision = StringField('Vision')
    mission = StringField('Mission')
    slogan = StringField('Slogan / Tagline')
    proj_deadline = DateField('When are you expecting your Project?')
    comments = TextAreaField('What can you add?')
    upload_profile = FileField("Upload Profile Content")
    company_document = FileField("Upload any Company Document")
    upload_logo = FileField("Upload Company Logo")
    comp_colors1 = StringField('Choose Color')
    comp_colors2 = StringField('Choose Color')

    submit = SubmitField('Submit')

class Reset(FlaskForm):

    old_password = PasswordField('old password', validators=[DataRequired(), Length(min=8, max=64)])
    new_password = PasswordField('new password', validators=[DataRequired(), Length(min=8, max=64)])
    confirm_password = PasswordField('confirm password', validators=[DataRequired(), EqualTo('new_password'), Length(min=8, max=64)])

    reset = SubmitField('Reset')

class Reset_Request(FlaskForm):

    phone = NormalizedPhoneField('Enter Registered Cell Number', validators=[DataRequired()])

    reset = SubmitField('Submit')

    # def validate_email(self,email):
    #     user = user.query.filter_by

class EmailMarketingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=4, max=20)])
    description = TextAreaField('Other Info', validators=[DataRequired(), Length(min=10, max=200)])
    content_file = FileField('Upload Content', validators=[DataRequired()])
    days = SelectMultipleField('Which days would you like us to send your campaign or advert?', choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday')],
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False)
    )
    
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])
    submit = SubmitField('Submit')

class QMPartnershipForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=8, max=20)])
    company = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=100)])
    partnership_program = SelectField('Partnership Program',choices=[
        ("referral","Referral Partnership"),
        ("custom_partnership","Custom Partnership Inquiry")
        ], validators=[DataRequired(), Length(min=10, max=500)])
    organization = SelectField('Partnership Program',choices=[
        ("consultant","Business Consultant"),
        ("agency","Registration Agency"),
        ("freelance","Marketing Freelancer")
        ], validators=[DataRequired(), Length(min=10, max=500)])
    
    submit = SubmitField('Send Partnership Request')

class EmailPasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

    def validate_email(self, email):
        from app import db, User
        user = User.query.filter_by(email=self.email.data).first()
        if not user:
            raise ValidationError("No account found with that email address.")
        
class SMSPasswordResetForm(FlaskForm):
    phone = NormalizedPhoneField('Enter Registered Cell Number', validators=[DataRequired()])
    submit = SubmitField('Get Code')

    def validate_phone(self, field):
        phone = field.data.strip()
        if not re.match(r'^\+?\d{9,15}$', phone):
            raise ValidationError("Enter a valid phone number with country code (e.g., +26876xxxxxx)")

class SMSCodeVerificationForm(FlaskForm):
    code = StringField('Verification Code', validators=[DataRequired(), Length(min=5, max=5)])
    submit = SubmitField('Verify Code')

    def validate_code(self, code):
        # Here you would typically check the code against a database or cache
        if not re.match(r'^\d{5}$', self.code.data):
            raise ValidationError("Invalid verification code. Please enter a 5-digit code.")

class RegistrationForm(FlaskForm):

    username = HiddenField(validators=[DataRequired()])
    name = StringField("Name",validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email",validators=[DataRequired(), Email()])
    phone = NormalizedPhoneField("Phone Number",validators=[DataRequired()])
    company_name = StringField("Company Name",validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])
    pKey = HiddenField(validators=[DataRequired()])
    country = SelectField(choices=[
        ('Eswatini', 'Eswatini'), ('South Africa', 'South Africa'),
        ('Lesotho', 'Lesotho'), ('Mozambique', 'Mozambique'),
        ('Namibia', 'Namibia'), ('Botswana', 'Botswana'),
        ('Zimbabwe', 'Zimbabwe'), ('Malawi', 'Malawi'),
    ])
    submit = SubmitField('Register')

class PasswordResetWizard(FlaskForm):

    new_password = PasswordField('new password', validators=[DataRequired(), Length(min=8, max=64)])
    confirm_password = PasswordField('confirm password', validators=[DataRequired(), EqualTo('new_password'), Length(min=8, max=64)])

    reset = SubmitField('Reset')
   