from flask import Blueprint, flash, redirect, url_for, render_template, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os, json
from app.image_to_json import image_to_json
from app.json_to_products import json_to_products
from app.models import Item, db
from datetime import datetime

receipt = Blueprint('receipt', __name__)

@receipt.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_receipt():
    if request.method == 'POST':
        if 'receipt' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['receipt']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            try:
                json_path = image_to_json(file)
                if json_path:
                    return redirect(url_for('receipt.process_receipt', json_path=json_path))
                else:
                    flash('Image proce