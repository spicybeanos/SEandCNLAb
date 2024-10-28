from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# MySQL database configuration (using PyMySQL)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:Tiger@localhost/se_project')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder where images will be saved
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file extensions

db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    caption = db.Column(db.String(200), nullable=True)
    image_url = db.Column(db.String(200), nullable=False)
    likes = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    result = [{
        'id': post.id,
        'username': post.username,
        'caption': post.caption,
        'image_url': request.host_url + post.image_url,
        'likes': post.likes,
        'comments': [{'username': c.username, 'text': c.text} for c in post.comments]
    } for post in posts]
    return jsonify(result)

@app.route('/api/posts', methods=['POST'])
def upload_post():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        new_post = Post(
            username=request.form['username'],
            caption=request.form.get('caption', ''),
            image_url=file_path,
            likes=0
        )
        
        try:
            db.session.add(new_post)
            db.session.commit()
            return jsonify({'message': 'Post uploaded successfully!'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    app.run(debug=True)
