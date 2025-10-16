from flask import Flask, jsonify, request, render_template, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os

app = Flask(__name__)

# --- Config ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///players.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Model ---
class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    team = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(80), nullable=False)
    batting_avg = db.Column(db.Float, nullable=False, default=0.000)
    bio = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "team": self.team,
            "position": self.position,
            "batting_avg": round(self.batting_avg, 3) if self.batting_avg is not None else None,
            "bio": self.bio or ""
        }

# --- DB init & seed ---
def seed_if_empty():
    if Player.query.count() == 0:
        demo = [
            Player(name="大谷翔平", team="洛杉磯天使", position="投手 / 指定打擊", batting_avg=0.304, bio="二刀流球星。"),
            Player(name="鈴木一朗", team="西雅圖水手", position="外野手", batting_avg=0.311, bio="安打製造機，速度出眾。"),
            Player(name="亞倫·賈吉", team="紐約洋基", position="外野手", batting_avg=0.283, bio="強打者，領袖氣質。"),
        ]
        db.session.add_all(demo)
        db.session.commit()

with app.app_context():
    db.create_all()
    seed_if_empty()

# =========================
# RESTful API (JSON)
# =========================
# Create & Read all
@app.route('/api/players', methods=['GET', 'POST'])
def api_players():
    if request.method == 'GET':
        players = Player.query.order_by(func.lower(Player.name)).all()
        return jsonify([p.to_dict() for p in players]), 200

    # POST create
    data = request.get_json(silent=True) or {}
    # 基本驗證
    required = ['name', 'team', 'position', 'batting_avg', 'bio']
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        batting = float(data['batting_avg'])
    except (TypeError, ValueError):
        return jsonify({"error": "batting_avg must be a number"}), 400

    # 名稱唯一
    if Player.query.filter(func.lower(Player.name) == data['name'].strip().lower()).first():
        return jsonify({"error": "Player with the same name already exists"}), 409

    player = Player(
        name=data['name'].strip(),
        team=data['team'].strip(),
        position=data['position'].strip(),
        batting_avg=batting,
        bio=data.get('bio', '').strip()
    )
    db.session.add(player)
    db.session.commit()
    return jsonify(player.to_dict()), 201

# Read one / Update / Delete
@app.route('/api/players/<int:player_id>', methods=['GET', 'PUT', 'DELETE'])
def api_player_detail(player_id):
    player = Player.query.get_or_404(player_id)

    if request.method == 'GET':
        return jsonify(player.to_dict()), 200

    if request.method == 'PUT':
        data = request.get_json(silent=True) or {}
        # 允許部分更新，但前端範例會送全欄位
        if 'name' in data:
            # 如果改名，仍需確保唯一
            new_name = data['name'].strip()
            conflict = Player.query.filter(func.lower(Player.name) == new_name.lower(), Player.id != player.id).first()
            if conflict:
                return jsonify({"error": "Another player with this name already exists"}), 409
            player.name = new_name
        if 'team' in data:
            player.team = data['team'].strip()
        if 'position' in data:
            player.position = data['position'].strip()
        if 'batting_avg' in data:
            try:
                player.batting_avg = float(data['batting_avg'])
            except (TypeError, ValueError):
                return jsonify({"error": "batting_avg must be a number"}), 400
        if 'bio' in data:
            player.bio = data['bio'].strip()

        db.session.commit()
        return jsonify(player.to_dict()), 200

    if request.method == 'DELETE':
        db.session.delete(player)
        db.session.commit()
        return jsonify({"message": "deleted"}), 200

# =========================
# Pages (Jinja2)
# =========================
@app.route('/')
def index():
    # 列表頁：頁面載入後由前端 JS 呼叫 /api/players 取得資料
    return render_template('index.html')

@app.route('/players/new')
def page_new_player():
    # 新增頁面：使用 form.html，mode="create"
    return render_template('form.html', mode='create', player=None)

@app.route('/players/<int:player_id>')
def page_player_detail(player_id):
    # 詳細頁：頁面載入後由前端 JS 呼叫 /api/players/<id>
    return render_template('player.html', player_id=player_id)

@app.route('/players/<int:player_id>/edit')
def page_edit_player(player_id):
    # 編輯頁面：頁面載入後由前端 JS 呼叫 /api/players/<id> 帶入資料
    return render_template('form.html', mode='edit', player_id=player_id)

if __name__ == '__main__':
    # 本地開發方便觀察
    app.run(debug=True)
