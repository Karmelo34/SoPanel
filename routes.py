from flask import flash, request, redirect, url_for, render_template, jsonify
from flask_login import login_user, login_required, current_user
from flask_admin import admin_required
from app.models import User, Device, db # type: ignore

def init_routes(app):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')
        return render_template('login.html')

    @app.route('/api/connect_device', methods=['POST'])
    @login_required
    @admin_required
    def connect_device():
        device_data = request.json
        new_device = Device(name=device_data['name'], type=device_data['type'], location=device_data['location'])
        db.session.add(new_device)
        db.session.commit()
        flash('Device connected successfully!', 'success')
        return jsonify({"success": True})
