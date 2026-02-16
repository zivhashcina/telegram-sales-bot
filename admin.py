import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.utils import secure_filename
from functools import wraps
import config
from database import db_session, init_db
from models import User, Product, Interaction, Search, Campaign
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == config.ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('סיסמה שגויה')
    return render_template('login.html')

@app.route('/admin/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def dashboard():
    total_users = db_session.query(User).count()
    total_products = db_session.query(Product).count()
    total_clicks = db_session.query(Interaction).filter(Interaction.action == 'click').count()
    total_views = db_session.query(Interaction).filter(Interaction.action == 'view').count()
    top_products = db_session.query(Product).order_by(Product.clicks.desc()).limit(5).all()
    recent_searches = db_session.query(Search).order_by(Search.created_at.desc()).limit(10).all()
    return render_template('dashboard.html',
                           total_users=total_users,
                           total_products=total_products,
                           total_clicks=total_clicks,
                           total_views=total_views,
                           top_products=top_products,
                           recent_searches=recent_searches)

@app.route('/admin/products')
@login_required
def products():
    products = db_session.query(Product).all()
    return render_template('products.html', products=products)

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = db_session.get(Product, product_id)
    if not product:
        abort(404)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.category = request.form['category']
        product.price = float(request.form['price'])
        product.affiliate_link = request.form['affiliate_link']
        product.tags = request.form.getlist('tags')
        product.image_url = request.form['image_url']
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.image_url = url_for('static', filename=f'uploads/{filename}')
        db_session.commit()
        flash('המוצר עודכן')
        return redirect(url_for('products'))
    return render_template('edit_product.html', product=product)

@app.route('/admin/product/delete/<int:product_id>')
@login_required
def delete_product(product_id):
    product = db_session.get(Product, product_id)
    if not product:
        abort(404)
    db_session.delete(product)
    db_session.commit()
    flash('המוצר נמחק')
    return redirect(url_for('products'))

@app.route('/admin/campaigns')
@login_required
def campaigns():
    campaigns = db_session.query(Campaign).all()
    return render_template('campaigns.html', campaigns=campaigns)

@app.route('/admin/campaign/add', methods=['GET', 'POST'])
@login_required
def add_campaign():
    if request.method == 'POST':
        name = request.form['name']
        message = request.form['message']
        filter_criteria = {
            'category': request.form.get('category'),
            'min_views': request.form.get('min_views', type=int),
        }
        scheduled_at = request.form.get('scheduled_at')
        if scheduled_at:
            scheduled_at = datetime.fromisoformat(scheduled_at)
        campaign = Campaign(
            name=name,
            message=message,
            filter_criteria=filter_criteria,
            scheduled_at=scheduled_at,
            created_by=0
        )
        db_session.add(campaign)
        db_session.commit()
        flash('קמפיין נוצר')
        return redirect(url_for('campaigns'))
    return render_template('add_campaign.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)