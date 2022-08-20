import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
# SQLALCHEMY_DATABASE_URI = 'dialect://username:password@localhost:port/database name
SQLALCHEMY_DATABASE_URI = 'postgresql://opeyimika:123456@localhost:5432/fyuur'
SQLALCHEMY_TRACK_MODIFICATIONS = False