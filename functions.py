from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, validators

class RegistrationForm(FlaskForm):
    username = StringField("Username", [validators.Length(min=4, max=30)])
    email = StringField(
        "Email",
        [
            validators.Email(message="Invalid email address"),
            validators.Regexp(
                ".*@akgec.ac.in$", message="Email must end with @akgec.ac.in"
            ),
        ],
    )
    confirm_email = StringField(
        "Repeat Email",
        [validators.EqualTo("email", message="Emails must match")],
    )
    password = PasswordField("Password", [validators.DataRequired()])
    confirm_password = PasswordField(
        "Repeat Password",
        [validators.EqualTo("password", message="Passwords must match")],
    )
    submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):
    username = StringField("Username", [validators.Length(min=4, max=30)])
    email = StringField(
        "Email",
        [
            validators.Email(message="Invalid email address"),
            validators.Regexp(
                ".*@akgec.ac.in$", message="Email must end with @akgec.ac.in"
            ),
        ],
    )
    password = PasswordField("Password",[validators.DataRequired()])
    remember= BooleanField("Remember Me")
    submit = SubmitField("Login")

class UpdateForm(FlaskForm):
    username = StringField("Username", [validators.Length(min=4, max=30)])
    password = PasswordField("Password", [validators.DataRequired()])
    confirm_password = PasswordField(
        "Repeat Password",
        [validators.EqualTo("password", message="Passwords must match")],
    )
    submit = SubmitField("Update")