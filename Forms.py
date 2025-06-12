from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField, TextAreaField,BooleanField, SelectField,DateField, URLField, RadioField, TelField, MultipleFileField,IntegerField,SelectMultipleField
from wtforms.validators import DataRequired,Length,Email, EqualTo, ValidationError, Optional
from flask_login import current_user
from flask_wtf.file import FileField , FileAllowed
from wtforms.widgets import ListWidget, CheckboxInput
# from wtforms.fields.html5 import DateField,DateTimeField


class Register(FlaskForm):

    name = StringField('name', validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('email', validators=[DataRequired(),Email()])
    position= StringField('position', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=64)])
    confirm = PasswordField('confirm', validators=[DataRequired(),EqualTo('password'), Length(min=8, max=64)])
    contacts = StringField('Contact(s)', validators=[Length(min=8, max=64)])
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
    subject = StringField('Subject', validators=[Optional()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')


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

class AdvertForm(FlaskForm):
    
    advert_image = FileField('Upload Advert', validators=[FileAllowed(['jpg', 'png'])])
    start_date = DateField('Start Date', validators=[DataRequired()])
    advert_days = IntegerField('How manys days?', validators=[DataRequired()])
    submit = SubmitField("Submit")

class Update_account_form(FlaskForm):

    email = StringField('Email', validators=[DataRequired(), Email()])

class Company_Register_Form(FlaskForm):

    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=120)])
    company_email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=100)])
    company_contacts = TelField('Contact(s)', validators=[Length(min=8, max=64)])
    company_address = StringField('Physical Address', validators=[DataRequired(), Length(min=8, max=100)])
    abbreviation = StringField("Abbreviation",validators=[Optional(), Length(min=1, max=20)])
    category_other = StringField("Please Specify")
    category = SelectField(
    "Select Category",
choices = [
    ("Technology", "Technology"),
    ("Healthcare", "Healthcare"),
    ("Finance", "Finance"),
    ("Retail", "Retail"),
    ("Manufacturing", "Manufacturing"),
    ("Energy", "Energy"),
    ("Transportation and Logistics", "Transportation and Logistics"),
    ("Entertainment and Media", "Entertainment and Media"),
    ("Electrical", "Electrical"),
    ("Environmental Services", "Environmental Services"),
    ("E-commerce", "E-commerce"),
    ("Real Estate", "Real Estate"),
    ("Professional Services", "Professional Services"),
    ("Education", "Education"),
    ("Hospitality", "Hospitality"),
    ("Food and Beverage", "Food and Beverage"),
    ("Cooperative Society", "Cooperative Society"),
    ("Construction", "Construction"),
    ("Agriculture", "Agriculture"),
    ("Web Development", "Web Development"),
    ("Creative Multimedia", "Creative Multimedia"),
    ("Fashion & Design", "Fashion & Design"),
    ("Media & Technology", "Media & Technology"),  # Fixed typo from "Techonology"
    ("News & Media", "News & Media"),
    ("Telecommunications", "Telecommunications"),
    ("Automotive", "Automotive"),
    ("Nonprofit", "Nonprofit"),
    ("Government", "Government"),
    ("Legal", "Legal"),
    ("Consulting", "Consulting"),
    ("Cultural", "Cultural"),
    ("Pharmaceutical", "Pharmaceutical"),
    ("Aerospace", "Aerospace"),
    ("Fashion", "Fashion"),
    ("Sports and Recreation", "Sports and Recreation"),
    ("Artificial Intelligence", "Artificial Intelligence"),
    ("Blockchain and Cryptocurrency", "Blockchain and Cryptocurrency"),
    ("Cybersecurity", "Cybersecurity"),
    ("Chemical Engineering", "Chemical Engineering"),
    ("Biotechnology", "Biotechnology"),
    ("Sustainability and CleanTech", "Sustainability and CleanTech"),
    ("Human Resources", "Human Resources"),
    ("Logistics & Supply Chain", "Logistics & Supply Chain"),
    ("Event Planning", "Event Planning"),
    ("Travel and Tourism", "Travel and Tourism"),
    ("Pet Services", "Pet Services"),
    ("Gaming", "Gaming"),
    ("Home Services", "Home Services"),
    ("Freelance & Gig Economy", "Freelance & Gig Economy"),
    ("Market Research", "Market Research"),
    ("Public Relations", "Public Relations"),
    ("Defense and Security", "Defense and Security"),
    ("Mining and Metals", "Mining and Metals"),
    ("Marine and Shipping", "Marine and Shipping"),
    ("Mechanical Engineering", "Mechanical Engineering"),
    ("Other", "Other"),
],
    validators=[DataRequired(), Length(min=2, max=100)]
)
    tagline=StringField('Selling Tagline (Briefly describe your product or service offering)', validators=[Optional(), Length(min=4, max=100)])
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


class Logo_Options(FlaskForm):

    email_signature = BooleanField("Email Signature")
    letterhead = BooleanField("Letterhead")
    mock_up = BooleanField("Mock Up")
    artwork = BooleanField("Logo Artwork",default=True)
    file_types = BooleanField("EPS, PDF, JPG, PNG",default=True)

class Poster_Options(FlaskForm):

    poster_types = SelectField('Type of Poster',
                                  choices=[("Travel Poster", "Travel Poster"), ("Advertising Poster", "Advertising Poster"),
                                           ("Event Poster", "Event Poster"),("Campaign Poster", "Campaign Poster"),
                                           ("Research Poster", "Research Poster"),("Promotional Poster", "Promotional Poster"),("Fashion Poster", "Fashion Poster")
                                           ,("Product Promo", "Product Promo")])
    theme_color = StringField("Theme Color(s)")
    poster_title = StringField("Poster Title")
    tag_line = StringField("Tag Line (Optional)")
    hash_tags = StringField("#tag(s)")
    poster_content = TextAreaField("Poster Content")
    instructional_info = TextAreaField("Poster Design Instructions")
    file_type1 = BooleanField("EPS")
    file_type2 = BooleanField("PDF", default=True)
    file_type3 = BooleanField("JPG", default=True)
    file_type4 = BooleanField("PNG")


class Flyer_Options(FlaskForm):

    theme_color = StringField("Theme Color(s)")
    flyer_title = StringField("Flyer Title")
    tag_line = StringField("Tag Line (Optional)")
    hash_tags = StringField("#tag(s)")
    content = TextAreaField("Content")
    instructional_info = TextAreaField("Design Instructions")
    file_type1 = BooleanField("EPS")
    file_type2 = BooleanField("PDF", default=True)
    file_type3 = BooleanField("JPG", default=True)
    file_type4 = BooleanField("PNG")


class Brochure_Options(FlaskForm):

    brochure_types = SelectField('Type of Brochure',
                                  choices=[("Half Fold", "Half Fold"), ("Tri Fold", "Tri Fold"),
                                           ("Z Fold", "Z Fold"),("Parallel Fold", "Parallel Fold"),
                                           ("Gate Fold", "Gate Fold"),("Double Gate Fold", "Double Gate Fold"),("Roll Fold", "Roll Fold")
                                           ,("Accordion Fold", "Accordion Fold"),("Half then Half", "Half then Half"),("Half then Tri", "Half then Tri")])
    theme_color = StringField("Theme Color(s)")
    brochure_title = StringField("Flyer Title")
    tag_line = StringField("Tag Line (Optional)")
    hash_tags = StringField("#tag(s)")
    brochure_content = TextAreaField("Content")
    instructional_info = TextAreaField("Design Instructions")
    file_type1 = BooleanField("EPS")
    file_type2 = BooleanField("PDF", default=True)
    file_type3 = BooleanField("JPG", default=True)
    file_type4 = BooleanField("PNG")


class Ecommerce_Options(FlaskForm):

    theme_color = StringField("Theme Color(s)")
    flyer_title = StringField("Flyer Title")
    tag_line = StringField("Tag Line (Optional)")
    hash_tags = StringField("#tag(s)")
    content = TextAreaField("Content")
    instructional_info = TextAreaField("Design Instructions")
    file_type1 = BooleanField("EPS")
    file_type2 = BooleanField("PDF", default=True)
    file_type3 = BooleanField("JPG", default=True)
    file_type4 = BooleanField("PNG")

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


class Web_Design_Brief(Project_Form):

    current_website = BooleanField("Do you currently have a website?")
    # Project Goals
    # Ask for your client’s definition of success.Do they want to increase the amount of visitors, up the average order size, or boost the users on their web forum? Perhaps
    # they want to encourage greater engagement via their blog, increase their brand visibility, or encourage people to sign up for their email newsletter/free trial/white paper, etc.
    web_traffic = BooleanField("We aim to increase traffic and establish an online presence")
    web_forum = BooleanField("We aim to boost the number users on our web forum")
    build_brand = BooleanField("We want to building our brand")
    web_ui_interactivity = BooleanField("We want improve the User Interactivity")
    web_new_look= BooleanField("We want a whole new on our Website")
    curr_web_comments = StringField("Comments about the current website")

    company_profile = BooleanField("Do you have any document you can upload i.e. business profile?")

    payment_options = SelectField('Choose Best Payment Option', choices=[("On-time Payment","On-time Payment"),("Pay Deposit + Balance Later","Pay Deposit + Balance Later"),
                                                                         ("Pay Deposit + with 2-3 Months Installments"),("Pay Deposit + with 2-3 Months Installments")])
    hosting = SelectField('Do you a Domain Name for site', choices=[("Yes, I have a domain","Yes, I have a domain"),("Yes, but I need a new one","Yes, but I need a new one"),
                                                                         ("No, I will need advice from You","No, I will need advice from You")])
    dns = SelectField('Do you a Hosting Server', choices=[("Yes, I have a hosting site", "Yes, I have a hosting site"),("Yes, but I need a new one","Yes, but I need a new one"),
                                                                ("No, I will need your advice","No, I will need your advice")])
    pages = SelectField('How many page does your site need?', choices=[("1 Page Website", "1 Page Website"),("1 Page divided by Sections","1 Page divided by Sections"),
                                                                ("3-4 Pages","3-4 Pages"),("4+ Pages","4+ Pages")])
    type = SelectField('Type of Website', choices=[("Business website", "Business website"), ("Business with eCommerce website", "Business with eCommerce website"),
                                                  ("Blog website", "Blog website"),("Portfolio website", "Portfolio website"),("Nonprofit website", "Nonprofit website"),
                                                   ("Other", "Other")])

    model = SelectField('Your business with your clients', choices=[("B2B - Business-to-Business", "B2B - Business-to-Business"), ("B2C - Business-to-Customer", "B2C - Business-to-Customer"),
                                                   ("Both", "Both")])

    feel1= BooleanField("Executive")
    feel2 = BooleanField("Modern Look")
    feel3 = BooleanField("Youthful")
    feel4 = BooleanField("Motion Effects")
    feel5 = BooleanField("More Graphics than content")
    feel6 = BooleanField("Content & Pictures")

    inspiration = URLField("Can you link us to an any website that inspires you")
    inspiration2 = URLField("Can you link us to an any website that inspires you")




    def validate_email(self,email):
        from app import db, User
        if current_user.email != self.email.data:
            #Check if email exeists in database
            user_email = User.query.filter_by(email = self.email.data).first()
            if user_email:
                raise ValidationError(f"email, {email.value}, already taken by someone")


    update = SubmitField('Update')


class Reset(FlaskForm):

    old_password = PasswordField('old password', validators=[DataRequired(), Length(min=8, max=64)])
    new_password = PasswordField('new password', validators=[DataRequired(), Length(min=8, max=64)])
    confirm_password = PasswordField('confirm password', validators=[DataRequired(), EqualTo('new_password'), Length(min=8, max=64)])

    reset = SubmitField('Reset')


class Reset_Request(FlaskForm):

    email = StringField('email', validators=[DataRequired(), Email()])

    reset = SubmitField('Submit')

    # def validate_email(self,email):
    #     user = user.query.filter_by