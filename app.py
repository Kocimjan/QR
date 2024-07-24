from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Настройка подключения к базе данных PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kocimjan:19739@localhost/QR'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Инициализация SQLAlchemy
db = SQLAlchemy(app)

# Модель для хранения QR-кодов
class QRCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(255), nullable=False)

# Маршрут для генерации QR-кодов
@app.route('/generate', methods=['POST'])
def generate_qr():
    data = request.json.get('data')
    qr = QRCode(data=data)
    db.session.add(qr)
    db.session.commit()
    return jsonify({'id': qr.id})

# Маршрут для получения QR-кодов по ID
@app.route('/get/<int:id>', methods=['GET'])
def get_qr(id):
    qr = QRCode.query.get(id)
    if not qr:
        return jsonify({'error': 'QR code not found'}), 404
    return jsonify({'data': qr.data})

# Основной блок для запуска приложения и создания таблиц
if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()  # Создание таблиц в базе данных
            print("Database tables created successfully.")
        except Exception as e:
            print(f"Error creating database tables: {e}")
    app.run(debug=True)  # Запуск сервера
    
    