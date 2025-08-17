from flask import request, jsonify, session
from flask_login import current_user
from datetime import datetime
from app.models.score import Score
from app.tests.utils import save_and_convert_audio, recognize_audio, calculate_score
from app.tests import bp
from app import db

@bp.route('/submit-audio', methods=['POST'])
def submit_audio():
    """
    Submit audio file for processing with enhanced validation
    Supports both uploaded files and recorded audio
    Maximum file size: 5 MB
    """
    
    # بررسی احراز هویت
    if 'user_id' not in session:
        return jsonify({"error": "کاربر وارد سیستم نشده است"}), 401

    # بررسی وجود پارامترهای لازم
    try:
        test_number = int(request.form.get('test_number'))
        round_number = int(request.form.get('round_number'))
    except (TypeError, ValueError):
        return jsonify({"error": "شماره تست یا دور نامعتبر است"}), 400

    # بررسی محدوده معتبر تست و دور
    if test_number not in [1, 2, 3, 4]:
        return jsonify({"error": "شماره تست باید بین 1 تا 4 باشد"}), 400
    
    if round_number not in [1, 2, 3, 4, 5]:
        return jsonify({"error": "شماره دور باید بین 1 تا 5 باشد"}), 400

    # بررسی وجود فایل صوتی
    if 'audio' not in request.files:
        return jsonify({"error": "هیچ فایل صوتی ارسال نشده است"}), 400

    audio_file = request.files['audio']
    
    # بررسی انتخاب فایل
    if audio_file.filename == '':
        return jsonify({"error": "هیچ فایلی انتخاب نشده است"}), 400

    # بررسی فرمت فایل
    #allowed_extensions = {'mp3', 'm4a', 'wav', 'webm', 'ogg'}
    #file_extension = audio_file.filename.rsplit('.', 1)[-1].lower() if '.' in audio_file.filename else ''
    
    #if file_extension not in allowed_extensions:
    #   return jsonify({"error": "فرمت فایل پشتیبانی نمی‌شود. فرمت‌های مجاز: MP3, M4A, WAV, WebM, OGG"}), 400

    # بررسی حجم فایل در سطح route (اضافی برای اطمینان)
    MAX_FILE_SIZE_MB = 5
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    
    # خواندن حجم فایل
    audio_file.seek(0, 2)  # رفتن به انتهای فایل
    file_size = audio_file.tell()
    audio_file.seek(0)  # برگشت به ابتدای فایل
    
    if file_size > MAX_FILE_SIZE_BYTES:
        return jsonify({"error": f"حجم فایل از {MAX_FILE_SIZE_MB} مگابایت بیشتر است"}), 400
    
    if file_size == 0:
        return jsonify({"error": "فایل خالی است"}), 400

    username = current_user.username

    try:
        # ذخیره و تبدیل فایل
        save_path, error = save_and_convert_audio(audio_file, username, test_number, round_number)
        if error:
            return jsonify({"error": error}), 400

        # تشخیص متن از صدا
        text = recognize_audio(save_path)
        if text is None or text.strip() == "":
            return jsonify({"error": "متن قابل تشخیصی در فایل صوتی یافت نشد. لطفاً مجدداً تلاش کنید."}), 400

        # محاسبه امتیاز و کلمات درست/غلط
        score, correct_words, incorrect_words = calculate_score(text, test_number)
        
        # ذخیره/آپدیت در دیتابیس
        user_id = session['user_id']
        score_entry = Score.query.filter_by(
            user_id=user_id, 
            test_number=test_number, 
            round_number=round_number
        ).first()

        if score_entry:
            # آپدیت رکورد موجود
            score_entry.score = score
            score_entry.correct_words = correct_words
            score_entry.incorrect_words = incorrect_words
            score_entry.test_time = datetime.now()
        else:
            # ایجاد رکورد جدید
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
        
        # لاگ برای debug
        print(f"User {username} - Test {test_number}, Round {round_number}: Score = {score}")

        return jsonify({
            "transcribed_words": text.split(),
            "total_words": len(text.split()),
            "correct_words": score,
            "incorrect_words": incorrect_words,
            "round_completed": round_number == 5,
            "message": "فایل با موفقیت پردازش شد"
        })

    except Exception as e:
        # لاگ خطا
        print(f"Error processing audio for user {username}: {str(e)}")
        
        # بازگردانی تراکنش در صورت خطا
        db.session.rollback()
        
        return jsonify({
            "error": "خطا در پردازش فایل صوتی. لطفاً مجدداً تلاش کنید."
        }), 500