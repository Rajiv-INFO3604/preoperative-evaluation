from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, url_for, flash, session
from werkzeug.utils import secure_filename
from collections import defaultdict
import os
from datetime import datetime
from App.models import Patient, Anesthesiologist, Doctor
from App.models import db
from App.controllers import *

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index_page():
    return render_template('index.html', title= 'Home')

@index_views.route('/init', methods=['GET'])
def init():
    initialize_db()  
    return jsonify(message='db initialized!')

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})


