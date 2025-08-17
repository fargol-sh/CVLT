from flask import request, jsonify, session
from flask_login import current_user
from datetime import datetime
from app.models.score import Score
from app.tests.utils import save_and_keep_original, recognize_audio, calculate_score, allowed_upload
from app.tests import bp
from app import db

MAX_FILE_SIZE_MB = 5


@bp.route('/submit-audio', methods=['POST'])
def submit_audio():
    """
    آپلود و پردازش صدا (wav, mp3, m4a, ogg, webm و blob بدون نام فایل).
    حداکثر حجم: 5MB
    """
    if 'user_id' not in session:
        return jsonify({"error": "کاربر وارد سیستم نشده است"}), 401

    try:
        test_number = int(request.form.get('test_number'))
        round_number = int(request.form.get('round_number'))
    except (TypeError, ValueError):
        return jsonify({"error": "شماره تست یا دور نامعتبر است"}), 400

    if test_number not in [1, 2, 3, 4]:
        return jsonify({"error": "شماره تست باید بین 1 تا 4 باشد"}), 400
    if round_number not in [1, 2, 3, 4, 5]:
        return jsonify({"error": "شماره دور باید بین 1 تا 5 باشد"}), 400

    if 'audio' not in request.files:
        return jsonify({"error": "هیچ فایل صوتی ارسال نشده است"}), 400

    audio_file = request.files['audio']

    # اگر filename خالی است ولی mimetype مجاز است، اجازه بده
    if (not getattr(audio_file, 'filename', '')) and not allowed_upload('', getattr(audio_file, 'mimetype', None)):
        return jsonify({"error": "هیچ فایلی انتخاب نشده است"}), 400

    # چک حجم
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    audio_file.seek(0, 2)
    file_size = audio_file.tell()
    audio_file.seek(0)
    if file_size > max_bytes:
        return jsonify({"error": f"حجم فایل از {MAX_FILE_SIZE_MB} مگابایت بیشتر است"}), 400
    if file_size == 0:
        return jsonify({"error": "فایل خالی است"}), 400

    # چک فرمت (بر اساس filename یا mimetype برای blob)
    if not allowed_upload(getattr(audio_file, 'filename', ''), getattr(audio_file, 'mimetype', None)):
        return jsonify({"error": "فرمت فایل پشتیبانی نمی‌شود. فرمت‌های مجاز: MP3, M4A, WAV, OGG, WebM"}), 400

    username = current_user.username

    try:
        save_path, error = save_and_keep_original(audio_file, username, test_number, round_number)
        if error:
            return jsonify({"error": error}), 400

        text = recognize_audio(save_path)
        if not text or not text.strip():
            return jsonify({"error": "متن قابل تشخیصی در فایل صوتی یافت نشد. لطفاً مجدداً تلاش کنید."}), 400

        score, correct_words, incorrect_words = calculate_score(text, test_number)

        user_id = session['user_id']
        score_entry = Score.query.filter_by(
            user_id=user_id, test_number=test_number, round_number=round_number
        ).first()

        if score_entry:
            score_entry.score = score
            score_entry.correct_words = correct_words
            score_entry.incorrect_words = incorrect_words
            score_entry.test_time = datetime.now()
        else:
            score_entry = Score(
                user_id=user_id,
                test_number=test_number,
                round_number=round_number,
                score=score,
                correct_words=correct_words,
                incorrect_words=incorrect_words,
                test_time=datetime.now()
            )
            db.session.add(score_entry)

        db.session.commit()

        tokens = text.split()
        return jsonify({
            "transcribed_words": tokens,
            "total_words": len(tokens),
            "correct_words": score,
            "incorrect_words": incorrect_words,
            "round_completed": round_number == 5,
            "message": "فایل با موفقیت پردازش شد"
        })

    except Exception as e:
        print(f"Error processing audio for user {username}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "خطا در پردازش فایل صوتی. لطفاً مجدداً تلاش کنید."}), 500
