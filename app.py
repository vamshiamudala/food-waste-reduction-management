from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate
from flask import jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saveplatesite.db?timeout=30'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Add a role field (either 'manager' or 'volunteer')


class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    expiry_date = db.Column(db.String(10), nullable=False)


class AvailablePost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    expiry_date = db.Column(db.String(10), nullable=False)

class WastageLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    date_logged = db.Column(db.String(10), nullable=False)

class ScheduledPickup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('available_post.id'), nullable=False)  # This should not be NULL
    pickup_time = db.Column(db.DateTime, nullable=False)
    is_picked = db.Column(db.Boolean, default=False, nullable=False)

    post = db.relationship('AvailablePost', backref='scheduled_pickups')  # Reference to the AvailablePost model




def create_tables():
    with app.app_context():
        db.create_all()

# Route to handle the root URL
@app.route('/')
def index():
    if 'user_id' in session:  # If the user is logged in, redirect to the home page
        return redirect(url_for('home'))
    return redirect(url_for('login'))  # Otherwise, redirect to login page

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        role = request.form['role']  # Capture the selected role
        hashed_password = generate_password_hash(password)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered')
            return redirect(url_for('signin'))

        new_user = User(email=email, name=name, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash('Sign-up successful. Please log in.')
        return redirect(url_for('login'))

    return render_template('signin.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role  # Store the user's role in the session
            return redirect(url_for('home'))  # Redirect to the home page
        else:
            flash('Invalid email or password')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/home')
def home():
    if 'user_id' not in session:  # Check if the user is logged in
        flash('Please log in to access the dashboard.')
        return redirect(url_for('login'))

    # Serve the dashboard template here
    return render_template('home.html')  # Ensure you have a 'home.html' template

@app.route('/volunteerhome')
def volunteer_dashboard():
    if 'user_id' not in session or session['role'] != 'volunteer':
        flash('Unauthorized access.')
        return redirect(url_for('login'))

    # Fetch statistics related to the volunteer from the database (mock data here)
    total_pickups = 10  # Replace with real data from DB
    total_donation_requests = 5  # Replace with real data from DB
    total_feedbacks = 7  # Replace with real data from DB
    total_alerts = 3  # Replace with real data from DB

    # Pass data to the volunteer dashboard template
    return render_template('volunteerhome.html', 
                           total_pickups=total_pickups, 
                           total_donation_requests=total_donation_requests,
                           total_feedbacks=total_feedbacks,
                           total_alerts=total_alerts)


@app.route('/managerProfile')
def managerProfile():
    if 'user_id' not in session or session['role'] != 'manager':
        flash('Unauthorized access.')
        return redirect(url_for('login'))

    return render_template('managerProfile.html')


@app.route('/logout', methods=['POST'])
def logout():
    # Clear session data
    session.pop('user_id', None)
    session.pop('role', None)
    session.pop('user_name', None)
    
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))



@app.route('/inventoryManagement')
def inventoryManagement():
    if 'user_id' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))
    
    inventory = InventoryItem.query.all()  # Fetch the inventory data
    return render_template('inventoryManagement.html', inventory=inventory)



@app.route('/addItem', methods=['POST'])
def addItem():
    name = request.form['name']
    quantity = request.form['quantity']
    expiry_date = request.form['expiry_date']

    new_item = InventoryItem(name=name, quantity=quantity, expiry_date=expiry_date)
    db.session.add(new_item)
    db.session.commit()

    flash('Item added successfully!')
    return redirect(url_for('inventoryManagement'))


@app.route('/postItem/<int:item_id>', methods=['POST'])
def postItem(item_id):
    item = InventoryItem.query.get(item_id)
    if item:
        # Add the item to the available_posts table
        new_post = AvailablePost(name=item.name, quantity=item.quantity, expiry_date=item.expiry_date)
        db.session.add(new_post)
        db.session.commit()
        flash('Item posted successfully!')
    else:
        flash('Item not found.')
    
    return redirect(url_for('inventoryManagement'))


@app.route('/foodposting', methods=['GET'])
def foodPosting():
    available_posts = AvailablePost.query.all()  # Fetch all posted items
    return render_template('foodposting.html', available_posts=available_posts)


@app.route('/foodposts')
def foodposts():
    if 'user_id' not in session or session['role'] != 'volunteer':
        flash('Unauthorized access.')
        return redirect(url_for('login'))

    # Fetch available posts from the database
    available_posts = AvailablePost.query.all()

    # Render the foodposts page with the available posts
    return render_template('foodposts.html', available_posts=available_posts)

from datetime import datetime

@app.route('/schedulePickup/<int:post_id>', methods=['POST'])
def schedule_pickup(post_id):
    if 'user_id' not in session or session['role'] != 'volunteer':
        return jsonify({'error': 'Unauthorized access.'}), 403

    # Check if the post exists
    post = AvailablePost.query.get(post_id)
    if not post:
        return jsonify({'error': 'Post not found.'}), 404

    # Create a new scheduled pickup
    try:
        new_pickup = ScheduledPickup(
            volunteer_id=session['user_id'],
            post_id=post_id,
            pickup_time=datetime.now(),
            is_picked=False
        )
        db.session.add(new_pickup)
        db.session.commit()

        return jsonify({'message': 'Pickup scheduled successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@app.route('/pickupschedule')
def pickup_schedule():
    if 'user_id' not in session or session['role'] != 'volunteer':
        flash('Unauthorized access.')
        return redirect(url_for('login'))

    # Fetch scheduled pickups for the logged-in volunteer
    scheduled_pickups = ScheduledPickup.query.filter_by(volunteer_id=session['user_id']).all()

    # Render the pickup schedule page with the scheduled pickups
    return render_template('pickupschedule.html', scheduled_pickups=scheduled_pickups)



@app.route('/markPicked/<int:pickup_id>', methods=['POST'])
def mark_picked(pickup_id):
    if 'user_id' not in session or session['role'] != 'volunteer':
        flash('Unauthorized access.')
        return redirect(url_for('login'))

    # Fetch the scheduled pickup within a session
    with app.app_context():
        # Get the pickup item
        pickup = ScheduledPickup.query.get(pickup_id)

        if not pickup:
            flash('Pickup not found.')
            return redirect(url_for('pickup_schedule'))

        # Ensure that the post_id is valid before proceeding
        post = AvailablePost.query.get(pickup.post_id)
        
        if not post:
            flash('Post not found in available posts.')
            print(f"Post ID {pickup.post_id} not found in AvailablePost")
            return redirect(url_for('pickup_schedule'))

        # Mark the pickup as done
        pickup.is_picked = True
        print(f"Marking pickup {pickup_id} as done, related post {pickup.post_id}")

        # Remove the corresponding post from available posts
        try:
            db.session.delete(post)
            print(f"Post ID {pickup.post_id} deleted from AvailablePost")
            db.session.commit()
            flash('Pickup marked as done!')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}')
            print(f"Error during commit: {e}")
        finally:
            db.session.close()

    return redirect(url_for('pickup_schedule'))







@app.route('/wasteLogging', methods=['GET'])
def wasteLogging():
    inventory_items = InventoryItem.query.all()  # Fetch all inventory items
    wastage_logs = WastageLog.query.all()  # Fetch all waste logs
    return render_template('wasteLogging.html', inventory_items=inventory_items, wastage_logs=wastage_logs)

# Handle waste logging form submission
@app.route('/logWaste', methods=['POST'])
def logWaste():
    item_id = request.form['item_id']
    quantity = float(request.form['quantity'])
    reason = request.form['reason']
    date_logged = datetime.today().strftime('%Y-%m-%d')

    # Fetch the inventory item
    item = InventoryItem.query.get(item_id)
    if not item or item.quantity < quantity:
        flash('Invalid item or quantity.')
        return redirect(url_for('wasteLogging'))

    # Add the waste log to the wastage_logs table
    new_waste_log = WastageLog(item_name=item.name, quantity=quantity, reason=reason, date_logged=date_logged)
    db.session.add(new_waste_log)

    # Update the inventory (subtract the quantity or remove the item)
    item.quantity -= quantity
    if item.quantity <= 0:
        db.session.delete(item)  # Remove the item from inventory if no quantity left
    db.session.commit()

    flash('Waste log added successfully!')
    return redirect(url_for('wasteLogging'))

# Handle deleting a waste log
@app.route('/deleteWasteLog/<int:log_id>', methods=['POST'])
def deleteWasteLog(log_id):
    log_to_delete = WastageLog.query.get(log_id)
    if log_to_delete:
        db.session.delete(log_to_delete)
        db.session.commit()
        flash('Waste log deleted successfully!')
    else:
        flash('Log not found.')

    return redirect(url_for('wasteLogging'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in to access your profile.')
        return redirect(url_for('login'))

    # Fetch user details from the database based on session user_id
    user = User.query.get(session['user_id'])
    
    if not user:
        flash('User not found.')
        return redirect(url_for('login'))

    # Render profile page and pass user details to the template
    return render_template('profile.html', user=user)


if __name__ == '__main__':
    create_tables()  # Create tables before the first request if not already created
    app.run(debug=True)
