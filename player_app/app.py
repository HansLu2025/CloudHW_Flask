from flask import Flask, render_template, abort

app = Flask(__name__)

# 範例資料
players = [
    {
        "id": 1,
        "name": "大谷翔平",
        "team": "洛杉磯天使",
        "position": "投手 / 指定打擊",
        "batting_avg": 0.304,
        "bio": "日本職棒出身的二刀流球星，以投打兼優的表現聞名於世。"
    },
    {
        "id": 2,
        "name": "鈴木一朗",
        "team": "西雅圖水手",
        "position": "外野手",
        "batting_avg": 0.311,
        "bio": "傳奇日籍球員，以穩定打擊與速度著稱，生涯累積超過 3000 支安打。"
    },
    {
        "id": 3,
        "name": "亞倫·賈吉",
        "team": "紐約洋基",
        "position": "外野手",
        "batting_avg": 0.283,
        "bio": "以強大的長打能力與領導氣質聞名，為洋基隊現役看板球星。"
    }
]

@app.route('/')
def index():
    return render_template('index.html', players=players)

@app.route('/player/<int:player_id>')
def player_detail(player_id):
    player = next((p for p in players if p["id"] == player_id), None)
    if not player:
        abort(404)
    return render_template('player.html', player=player)

if __name__ == '__main__':
    app.run(debug=True)
