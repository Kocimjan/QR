from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qr_codes.db'
app.config['QR_CODE_DIR'] = 'qr_codes'
db = SQLAlchemy(app)

class QRCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    label = db.Column(db.String(200))
    file_path = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'label': self.label,
            'file_path': self.file_path
        }

def generate_qr_with_label(content, label=None):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(content)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")

    if label:
        # Создаем новое изображение с дополнительным пространством для текста
        label_font = ImageFont.load_default()
        label_bbox = label_font.getbbox(label)  # Используем getbbox вместо устаревшего getsize
        label_width, label_height = label_bbox[2] - label_bbox[0], label_bbox[3] - label_bbox[1]

        padding = 10  # Отступ для текста
        new_img = Image.new('RGB', (qr_image.size[0], qr_image.size[1] + label_height + padding * 2), color='white')
        new_img.paste(qr_image, (0, label_height + padding))  # Сдвигаем QR-код вниз
        
        # Добавляем текст
        draw = ImageDraw.Draw(new_img)
        text_position = ((new_img.size[0] - label_width) // 2, padding)  # Размещаем текст выше с отступом
        draw.text(text_position, label, font=label_font, fill='black')
        
        return new_img
    else:
        return qr_image

@app.route('/qr', methods=['POST'])
def create_qr():
    content = request.json.get('content')
    label = request.json.get('label')
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    # Генерация QR-кода с меткой
    img = generate_qr_with_label(content, label)
    
    # Сохранение QR-кода
    if not os.path.exists(app.config['QR_CODE_DIR']):
        os.makedirs(app.config['QR_CODE_DIR'])
    file_path = os.path.join(app.config['QR_CODE_DIR'], f'qr_{len(os.listdir(app.config["QR_CODE_DIR"]))}.png')
    img.save(file_path)
    
    # Сохранение в базе данных
    new_qr = QRCode(content=content, label=label, file_path=file_path)
    db.session.add(new_qr)
    db.session.commit()
    
    return jsonify(new_qr.to_dict()), 201

@app.route('/qr/<int:qr_id>', methods=['GET'])
def get_qr(qr_id):
    qr = QRCode.query.get_or_404(qr_id)
    return send_file(qr.file_path, mimetype='image/png')


@app.route('/')
def index():
    return 'QR Code Generator API'


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080, debug=True)

