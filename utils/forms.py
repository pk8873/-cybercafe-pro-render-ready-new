from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, Regexp


class RegisterForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(2, 120)])
    shop_name = StringField("Shop Name", validators=[Optional(), Length(max=120)])
    mobile_number = StringField("Mobile Number", validators=[DataRequired(), Regexp(r"^\d{10}$", message="Enter 10-digit mobile")])
    email = StringField("Email", validators=[DataRequired(), Email()])
    district = StringField("District", validators=[Optional(), Length(max=80)])
    address = StringField("Address", validators=[Optional(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")


class CustomerForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(2, 120)])
    mobile_number = StringField("Mobile Number", validators=[Optional(), Length(max=20)])
    aadhaar_last_4 = StringField("Aadhaar Last 4", validators=[Optional(), Regexp(r"^\d{0,4}$")])
    address = StringField("Address", validators=[Optional(), Length(max=255)])
    village = StringField("Village", validators=[Optional(), Length(max=120)])
    notes = TextAreaField("Notes", validators=[Optional()])


class ServiceForm(FlaskForm):
    customer_id = SelectField("Customer", coerce=int, validators=[DataRequired()])
    service_type = StringField("Service Type", validators=[DataRequired(), Length(max=100)])
    status = SelectField("Status", choices=[("Pending", "Pending"), ("In Progress", "In Progress"), ("Completed", "Completed")])
    amount = FloatField("Amount", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])
