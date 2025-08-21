# admin/routes.py
from flask import jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models.user import User
from app.models.score import Score
from . import bp  # admin blueprint
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': 'Forbidden'}), 403
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/user-results', methods=['GET'])
@login_required
@admin_required
def api_user_results():
    """
    Returns all user test results for admin.
    Supports optional filters:
    - username: filter by username
    - test_number: filter by test number
    - test_time: filter by ISO datetime string (e.g., "2025-08-13T14:30")
    """
    
    # Filters
    filter_username = request.args.get('username')
    filter_test_number = request.args.get('test_number')
    filter_test_time = request.args.get('test_time')

    # Base query with join to User
    scores_query = Score.query.join(User, Score.user_id == User.id)

    if filter_username:
        scores_query = scores_query.filter(User.username == filter_username)
    
    if filter_test_number:
        try:
            scores_query = scores_query.filter(Score.test_number == int(filter_test_number))
        except ValueError:
            return jsonify({'error': 'Invalid test_number'}), 400

    if filter_test_time:
        try:
            test_time_dt = datetime.fromisoformat(filter_test_time)
            test_time_end = test_time_dt + timedelta(minutes=1)
            scores_query = scores_query.filter(
                Score.test_time >= test_time_dt,
                Score.test_time < test_time_end
            )
        except ValueError:
            return jsonify({'error': 'Invalid test_time format'}), 400

    scores = scores_query.all()

    # Compute approved tests and total scores
    approved_tests = set()
    total_scores = {}

    for score in scores:
        key = (score.user_id, score.test_number)
        if key in approved_tests:
            continue
        test_scores = Score.query.filter_by(user_id=score.user_id, test_number=score.test_number).all()
        rounds = [s.round_number for s in test_scores]
        if set(range(1, 6)) == set(rounds):
            times = [s.test_time for s in sorted(test_scores, key=lambda x: x.round_number)]
            if times == sorted(times):
                approved_tests.add(key)
                total_scores[key] = sum(s.score for s in test_scores)

    # Build response
    result = []
    for score in scores:
        key = (score.user_id, score.test_number)
        result.append({
            'username': score.user.username,
            'age': score.user.age,
            'sex': score.user.sex,
            'test_number': score.test_number,
            'round_number': score.round_number,
            'score': score.score,
            'test_time': score.test_time.isoformat(),
            'approved': 'Yes' if key in approved_tests else 'No',
            'total_score': total_scores.get(key, 'N/A')
        })

    return jsonify(result)


@bp.route('/user/<int:user_id>')
@login_required
@admin_required
def get_user_email(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({'email': user.email})
    else:
        return jsonify({'error': 'User not found'}), 404
    
    
@bp.route('/current-user', methods=['GET'])
@login_required
def get_current_user():
    
        if not current_user.is_authenticated:
            return jsonify({'error': 'Unauthorized'}), 401

        response = jsonify({
            'id': current_user.id,
            'username': current_user.username,
            'profile_photo': current_user.profile_photo if hasattr(current_user, 'profile_photo') else None
        })
        
        # Prevent caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
        
