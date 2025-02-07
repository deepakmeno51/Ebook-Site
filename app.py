from flask import Flask, render_template, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

# Create a Flask application instance
app = Flask(__name__)

# Configure the database connection.  This line specifies the database file.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./ebook_library.db'
# This disables a warning that Flask-SQLAlchemy sometimes generates.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Set a secret key for security (important for sessions later)
app.config['SECRET_KEY'] = 'your_secret_key'
# Set the folder for ebook files (must exist).  Crucially, this is relative to the root of your app.
app.config['UPLOAD_FOLDER'] = 'static/ebooks'
# Set the folder for serving static files (must exist, and must match the folder in your HTML).
app.config['STATIC_FOLDER'] = 'static'


# Initialize the SQLAlchemy database object with Flask.
db = SQLAlchemy(app)


# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


    def __repr__(self):
        return f'<User {self.username}>'


# Define the EBook model
class EBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    # The path to the ePub file, relative to the 'static' folder.
    file_path = db.Column(db.String(255), nullable=False)
    # The path to the cover image, relative to the 'static' folder.
    cover_image = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)


    def __repr__(self):
        return f'<EBook {self.title}>'


# This route handles requests for static files (like images and ebooks).
@app.route('/static/<path:filename>')
def send_static_file(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)


# Route for the homepage
@app.route('/')
def index():
    return render_template('home.html')


# Route to display the list of ebooks
@app.route('/ebooks')
def ebooks():
    ebooks = EBook.query.all()
    return render_template('ebooks.html', ebooks=ebooks)


# Route to display a specific ebook for reading.
@app.route('/read/<int:ebook_id>')
def read_ebook(ebook_id):
    ebook = EBook.query.get_or_404(ebook_id)
    return render_template('reader.html', ebook=ebook)


if __name__ == '__main__':
    # Important: The database setup and sample data loading should be within the 'with app.app_context():' block.
    with app.app_context():
        db.create_all()  # Create all tables defined by the models

        # Only add sample data if the database is empty
        if EBook.query.count() == 0:
            ebook1 = EBook(
                title="The Lord of the Rings",
                author="J.R.R. Tolkien",
                file_path="ebooks/lotr.epub",
                cover_image="ebooks/lotr.jpg",
                description="A classic fantasy novel.",
            )
            ebook2 = EBook(
                title="Pride and Prejudice",
                author="Jane Austen",
                file_path="ebooks/pride.epub",
                cover_image="ebooks/pride.jpg",
                description="A beloved romance novel.",
            )
            db.session.add_all([ebook1, ebook2])
            db.session.commit()

    # Initialize and add user if there are no users yet.  Keep within with app.app_context()
        if User.query.count() == 0:
            user1 = User(username="TestUser", email="test@example.com")
            db.session.add(user1)
            db.session.commit()

    # Run the Flask development server.
    app.run(debug=True)