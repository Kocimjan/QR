from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qr_codes.db'
db = SQLAlchemy(app)


class QRCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }


@app.route('/qr', methods=['POST'])
def create_qr():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        content = data.get('content')
        if not content:
            return jsonify({'error': 'Content is required'}), 400

        new_qr = QRCode(content=content)
        db.session.add(new_qr)
        db.session.commit()

        return jsonify(new_qr.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/qr/<int:qr_id>', methods=['GET'])
def get_qr(qr_id):
    qr = QRCode.query.get_or_404(qr_id)
    return jsonify(qr.to_dict())
@app.route('/')
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080, debug=True)


