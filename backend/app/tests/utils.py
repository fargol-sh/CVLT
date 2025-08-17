import os
from datetime import datetime
from pydub import AudioSegment
import speech_recognition as sr

TARGET_WORDS = {
    1: ['تراکتور', 'هویج', 'قناری', 'موکت', 'سیر', 'دوچرخه', 'یخچال', 'ببر', 'اتوبوس', 'میز', 'فلفل', 'گوریل',
        'پرده', 'پارو', 'سوسمار', 'فیلم'],
    2: ['لودر', 'گوجه', 'شتر', 'بخاری', 'ریحان', 'وانت', 'فریزر', 'گربه', 'مینی بوس', 'تخته', 'جعفری', 'گوسفند',
        'پنجره', 'ویلچر', 'کلاغ', 'نعنا'],
    3: ['فرش', 'قطار', 'خیار', 'طوطی', 'کدو', 'هواپیما', 'اجاق', 'موش', 'ماشین', 'صندلی', 'کاهو', 'میمون', 'کمد', 'موتور',
        'فیل', 'پیاز'],
    4: ['مترو', 'کامیون', 'اسفناج', 'زرافه', 'کمد', 'پیاز', 'موتور', 'کابینت', 'گورخر', 'چراغ', 'کرفس', 'گاو', 'مبل', 'قایق',
        'سنجاب', 'کلم']
}

MAX_FILE_SIZE_MB = 5
ALLOWED_EXTENSIONS = {'mp3', 'm4a', 'wav', 'ogg', 'webm'}


def allowed_upload(filename, mimetype=None):
    """Check if uploaded file has a valid extension or mimetype"""
    if not filename:
        return False
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext in ALLOWED_EXTENSIONS:
        return True
    if mimetype:
        if any(fmt in mimetype for fmt in ['wav', 'mpeg', 'ogg', 'webm', 'mp3']):
            return True
    return False


def _infer_extension(filename, mimetype):
    """Infer correct extension from filename or mimetype (fallback = wav)"""
    if filename and '.' in filename:
        return filename.rsplit('.', 1)[-1].lower()
    if mimetype:
        if 'wav' in mimetype:
            return 'wav'
        if 'webm' in mimetype:
            return 'webm'
        if 'ogg' in mimetype:
            return 'ogg'
        if 'mpeg' in mimetype or 'mp3' in mimetype:
            return 'mp3'
        if 'm4a' in mimetype:
            return 'm4a'
    return 'wav'  # fallback default


def clean_old_files(folder_path, keep_last=3):
    """Keep only the last `keep_last` files in folder"""
    if not os.path.exists(folder_path):
        return
    files = sorted(
        [os.path.join(folder_path, f) for f in os.listdir(folder_path)],
        key=os.path.getmtime
    )
    for old_file in files[:-keep_last]:
        os.remove(old_file)


def save_and_keep_original(audio_file, username, test_number, round_number):
    """
    Save uploaded audio exactly as sent (m4a, wav, mp3, ogg, webm).
    Keep only last 2 files in each round.
    """
    # check file size
    audio_file.seek(0, os.SEEK_END)
    file_size_mb = audio_file.tell() / (1024 * 1024)
    audio_file.seek(0)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return None, f"حجم فایل از {MAX_FILE_SIZE_MB} مگابایت بیشتر است"

    # determine extension
    ext = _infer_extension(audio_file.filename, audio_file.mimetype)
    save_directory = os.path.join('voices', username, f'test_{test_number}', f'round_{round_number}')
    os.makedirs(save_directory, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = os.path.join(save_directory, f"{timestamp}.{ext}")
    audio_file.save(save_path)

    clean_old_files(save_directory, keep_last=2)

    return save_path, None


def recognize_audio(file_path):
    """Transcribe audio file to text (Farsi)"""
    recognizer = sr.Recognizer()
    text = ""
    try:
        # if not wav, convert temporarily
        ext = file_path.rsplit('.', 1)[-1].lower()
        wav_path = file_path
        if ext != 'wav':
            tmp_path = os.path.splitext(file_path)[0] + "_tmp.wav"
            audio_content = AudioSegment.from_file(file_path, format=ext)
            audio_content = audio_content.set_frame_rate(16000).set_channels(1)
            audio_content.export(tmp_path, format='wav')
            wav_path = tmp_path

        with sr.AudioFile(wav_path) as source:
            audio_content = recognizer.record(source)
            results = recognizer.recognize_google(audio_content, language="fa-IR", show_all=True)
            if len(results) > 0:
                text = " ".join([alt["transcript"] for alt in results["alternative"]])

        if wav_path != file_path and os.path.exists(wav_path):
            os.remove(wav_path)

    except sr.UnknownValueError:
        return None
    return text


def calculate_score(transcribed_words, test_number):
    """Compare words with target list and return score, correct, and incorrect words"""
    words_list = transcribed_words.split()
    target_set = set(TARGET_WORDS[test_number])
    correct_words_all = [word for word in words_list if word in target_set]
    correct_words_unique = list(set(correct_words_all))
    incorrect_words = [word for word in words_list if word not in target_set]
    score = len(correct_words_unique)
    return score, correct_words_all, incorrect_words
