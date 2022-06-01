from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import true
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/test.db'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
db.create_all() #remove


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            
        if not token:
            return jsonify({'error': 'missing access token'}), 400
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS512')                                    
            current_user = User.query.filter_by(email=data['email']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'token is expired'}), 400
        except:
            return jsonify({'error': 'token is invalid'}), 400                        
        
        return f(current_user, *args, **kwargs)
    return decorated

# to test route
# curl -v -d '{"email": "example@example.com", "password": "password"}' -H 'Content-Type: application/json'  http://127.0.0.1:5000/adduser
@app.route('/adduser', methods=['POST'])
def add_user():
    data = request.get_json()
    
    if data.get('email') is None or data.get('password') is None:
        response = jsonify({'error': 'lacking fields'}), 400
        return response
    
    newuser_email = data['email']
    if User.query.filter_by(email=newuser_email).first() == None:        
        newuser_hpassword = generate_password_hash(data['password'], method='pbkdf2:sha512')
        new_user = User(email=newuser_email, password=newuser_hpassword)
    
        db.session.add(new_user)
        db.session.commit()
        
        response = jsonify({'message': 'user added'})
        return response
    else:
        response = jsonify({'error': 'a user with this email already exists'}), 400
        # response.headers['headername'] = 'newvalue'
        return response

# curl -v -d '{"email": "example@example.com", "password": "password"}' -H 'Content-Type: application/json'  http://127.0.0.1:5000/login
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    
    if data.get('email') is None or data.get('password') is None:
        response = jsonify({'error': 'lacking fields'}), 400
        return response
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user is None:
        response = jsonify({'error': 'user doesn\'t exist'}), 400
        return response
    
    if check_password_hash(user.password, data['password']):
        token = jwt.encode({'email': user.email, 'id': user.id, 'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=1)}, 
                           app.config['SECRET_KEY'], algorithm='HS512')
        # response = jsonify({'token': token.decode('UTF-8')})
        response = jsonify({'token': token})
        return response
        
    return jsonify({'error': 'password doesn\'t match'}), 400

# curl -v -H 'Content-Type: application/json' -H 'x-access-token:'  http://127.0.0.1:5000/data
@app.route('/data')
@token_required
def send_data_to_user(current_user):
    return jsonify({'message': f'Acesso permitido para {current_user.email}'})

if __name__ == '__main__':
    app.run(debug=true)