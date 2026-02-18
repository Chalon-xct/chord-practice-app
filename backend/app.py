from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
import base64
from dotenv import load_dotenv

from models import db, User, Practice
from midi_generator import generate_chord_midi, generate_chord_progression_midi, get_chord_notes, generate_single_note_midi
from guitar_chords import get_chord_positions
from deepseek_service import generate_daily_practice, generate_practice_summary, generate_next_practice_plan

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chord_practice.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

db.init_app(app)
jwt = JWTManager(app)


with app.app_context():
    db.create_all()


@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'error': '所有字段必填'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': '邮箱已被注册'}), 400
    
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': '注册成功',
        'token': access_token,
        'user': user.to_dict()
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': '登录成功',
        'token': access_token,
        'user': user.to_dict()
    })


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({'user': user.to_dict()})


@app.route('/api/practice/start', methods=['POST'])
@jwt_required()
def start_practice():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    today = datetime.now().date()
    
    if user.last_practice_date == today:
        last_practice = Practice.query.filter(
            Practice.user_id == user_id,
            db.func.date(Practice.practice_date) == today
        ).order_by(Practice.practice_date.desc()).first()
        
        if last_practice and last_practice.deepseek_next_plan:
            next_plan = json.loads(last_practice.deepseek_next_plan)
            previous_summary = json.loads(last_practice.deepseek_summary) if last_practice.deepseek_summary else None
            
            practice_data = generate_daily_practice(
                level=next_plan.get('suggested_level', user.current_level),
                previous_summary=json.dumps(previous_summary, ensure_ascii=False) if previous_summary else None,
                previous_plan=json.dumps(next_plan, ensure_ascii=False)
            )
        else:
            practice_data = generate_daily_practice(level=user.current_level)
    else:
        practice_data = generate_daily_practice(level=user.current_level)
    
    chords = practice_data['chords']
    
    for chord in chords:
        chord['midi'] = generate_chord_midi(chord['name'])
        chord['positions'] = get_chord_positions(chord['name'])
    
    progress_midi = generate_chord_progression_midi([c['name'] for c in chords])
    
    return jsonify({
        'chords': chords,
        'progression_midi': progress_midi,
        'focus_area': practice_data.get('focus_area', ''),
        'tips': practice_data.get('tips', '')
    })


@app.route('/api/practice/submit', methods=['POST'])
@jwt_required()
def submit_practice():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    answers = data.get('answers', [])
    duration = data.get('duration', 60)
    chords_practiced = data.get('chords', [])
    
    correct = 0
    chord_accuracy = {}
    
    for answer in answers:
        chord_name = answer.get('chord')
        is_correct = answer.get('correct', False)
        
        if is_correct:
            correct += 1
        
        if chord_name not in chord_accuracy:
            chord_accuracy[chord_name] = {'correct': 0, 'total': 0}
        
        chord_accuracy[chord_name]['total'] += 1
        if is_correct:
            chord_accuracy[chord_name]['correct'] += 1
    
    for chord in chord_accuracy:
        stats = chord_accuracy[chord]
        chord_accuracy[chord] = f"{stats['correct']}/{stats['total']} ({stats['correct']/stats['total']*100:.0f}%)"
    
    total = len(answers)
    score = int((correct / total) * 100) if total > 0 else 0
    
    user = User.query.get(user_id)
    user.total_practices += 1
    user.last_practice_date = datetime.now().date()
    
    exp_gained = correct * 10
    if score >= 80:
        exp_gained += 20
    if score == 100:
        exp_gained += 30
    
    user.experience += exp_gained
    user.total_experience += exp_gained
    
    while user.current_level < 50:
        current_threshold = user.get_level_exp_threshold(user.current_level)
        next_threshold = user.get_level_exp_threshold(user.current_level + 1)
        if user.total_experience >= next_threshold:
            user.current_level += 1
        else:
            break
    
    chords_str = ', '.join(chords_practiced)
    
    practice = Practice(
        user_id=user_id,
        level=user.current_level,
        score=score,
        total_questions=total,
        correct_answers=correct,
        chords_practiced=chords_str,
        duration_seconds=duration
    )
    
    db.session.add(practice)
    db.session.commit()
    
    practice_data = {
        'level': user.current_level,
        'score': score,
        'total_questions': total,
        'correct_answers': correct,
        'duration_seconds': duration,
        'chords_practiced': chords_str,
        'chord_accuracy': chord_accuracy
    }
    
    summary = generate_practice_summary(practice_data)
    next_plan = generate_next_practice_plan(summary, user.current_level)
    
    practice.deepseek_summary = json.dumps(summary, ensure_ascii=False)
    practice.deepseek_next_plan = json.dumps(next_plan, ensure_ascii=False)
    
    db.session.commit()
    
    chords_with_positions = []
    for chord_name in chords_practiced:
        positions = get_chord_positions(chord_name)
        chords_with_positions.append({
            'name': chord_name,
            'notes': get_chord_notes(chord_name),
            'positions': positions
        })
    
    return jsonify({
        'score': score,
        'correct': correct,
        'total': total,
        'exp_gained': exp_gained,
        'summary': summary,
        'next_plan': next_plan,
        'chords_reference': chords_with_positions,
        'level_updated': user.current_level,
        'total_experience': user.total_experience,
        'level_progress': user.to_dict()['level_progress']
    })


@app.route('/api/practice/history', methods=['GET'])
@jwt_required()
def get_practice_history():
    user_id = get_jwt_identity()
    
    practices = Practice.query.filter_by(user_id=user_id).order_by(
        Practice.practice_date.desc()
    ).limit(30).all()
    
    return jsonify({
        'practices': [p.to_dict() for p in practices]
    })


@app.route('/api/user/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    practices = Practice.query.filter_by(user_id=user_id).all()
    
    total_practices = len(practices)
    if total_practices == 0:
        avg_score = 0
        best_score = 0
    else:
        avg_score = sum(p.score for p in practices) / total_practices
        best_score = max(p.score for p in practices)
    
    current_streak = 0
    today = datetime.now().date()
    
    if user.last_practice_date == today:
        current_streak = 1
        check_date = today - timedelta(days=1)
        
        while True:
            practice = Practice.query.filter(
                Practice.user_id == user_id,
                db.func.date(Practice.practice_date) == check_date
            ).first()
            
            if practice:
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break
    
    return jsonify({
        'total_practices': total_practices,
        'average_score': round(avg_score, 1),
        'best_score': best_score,
        'current_streak': current_streak,
        'current_level': user.current_level
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
