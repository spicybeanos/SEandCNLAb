from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# MySQL database configuration (using PyMySQL)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 'mysql+pymysql://root:Tiger@localhost/se_project')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'profile_pics'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.String(200), nullable=True)
    pfp_url = db.Column(db.String(200), nullable=True)  # Profile picture URL


with app.app_context():
    db.create_all()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/api/profile', methods=['POST'])
def create_profile():
    if 'pfp' not in request.files:
        return jsonify({'error': 'No file part for profile picture'}), 400
    
    file = request.files['pfp']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Create new profile with file path as pfp_url
        new_profile = Profile(
            username=request.form['username'],
            name=request.form['name'],
            bio=request.form.get('bio', ''),
            pfp_url=file_path
        )

        try:
            db.session.add(new_profile)
            db.session.commit()
            return jsonify({'message': 'Profile created successfully!'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/api/profile/<username>', methods=['GET'])
def get_profile(username):
    profile = Profile.query.filter_by(username=username).first()
    if not profile:
        return jsonify({'error': 'User not found'}), 404
    
    result = {
        'id': profile.id,
        'username': profile.username,
        'name': profile.name,
        'bio': profile.bio,
        'pfp_url': request.host_url + profile.pfp_url if profile.pfp_url else None
    }
    return jsonify(result)


@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    profiles = Profile.query.all()
    result = [{
        'id': profile.id,
        'username': profile.username,
        'name': profile.name,
        'bio': profile.bio,
        'pfp_url': request.host_url + profile.pfp_url if profile.pfp_url else None
    } for profile in profiles]
    return jsonify(result)


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    app.run(debug=True)
