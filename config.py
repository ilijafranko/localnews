from localnews import app
from datetime import timedelta


#SQLALCHEMY_DATABASE_URI = "postgresql://user:TWljaGHFgiBCYXJ0b3N6a2lld2ljeiEh@localhost/databasename"
app.config['SECRET_KEY'] = 'Erna164PotusLoftF3'
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=365)


app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['PostgresDB'] = 'postgresql://postgres:[SupersecretPassword]@[DATABASEIP]/postgres'

"""
This file contains all of the configuration values for the application.
Update this file with the values for your specific Google Cloud project.
You can create and manage projects at https://console.developers.google.com
"""

# The secret key is used by Flask to encrypt session cookies.
SECRET_KEY = 'super-secret'

# There are three different ways to store the data in the application.
# You can choose 'datastore', 'cloudsql', or 'mongodb'. Be sure to
# configure the respective settings for the one you choose below.
# You do not have to configure the other data backends. If unsure, choose
# 'datastore' as it does not require any additional configuration.
DATA_BACKEND = 'datastore'

# Google Cloud Project ID. This can be found on the 'Overview' page at
# https://console.developers.google.com
PROJECT_ID = 'Project-ID'


GOOGLE_OAUTH2_CLIENT_ID = ''
GOOGLE_OAUTH2_CLIENT_SECRET = ''


# administrator list
ADMINS = ['ADMIN']