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

MAX_FILE_SIZE_MB = 5  # محدودیت حجم فایل به 10 مگابایت

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

def save_and_convert_audio(audio_file, username, test_number, round_number):
    """
    Save uploaded audio and convert to WAV if needed.
    Files saved under voices/username/test_X/round_Y/
    Only last 2 files for each round are kept.
    Max file size: 5 MB
    """
    # بررسی حجم فایل
    audio_file.seek(0, os.SEEK_END)
    file_size_mb = audio_file.tell() / (1024 * 1024)
    audio_file.seek(0)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return None, f"حجم فایل از {MAX_FILE_SIZE_MB} مگابایت بیشتر است"

    audio_format = audio_file.filename.split('.')[-1]
    save_directory = os.path.join('voices', username, f'test_{test_number}', f'round_{round_number}')
    os.makedirs(save_directory, exist_ok=True)

    # ذخیره فایل اصلی
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = os.path.join(save_directory, f"{timestamp}.{audio_format}")
    audio_file.save(save_path)

    # تبدیل به WAV در صورت نیاز
    if audio_format in ['m4a', 'mp3']:
        audio_content = AudioSegment.from_file(save_path, format=audio_format)
        audio_content = audio_content.set_frame_rate(16000).set_channels(1)
        wav_save_path = os.path.splitext(save_path)[0] + '.wav'
        audio_content.export(wav_save_path, format='wav')
        save_path = wav_save_path

    # فقط 2 فایل آخر نگه داشته شود
    clean_old_files(save_directory, keep_last=2)

    return save_path, None

def recognize_audio(file_path):
    """Transcribe audio file to text (Farsi)"""
    recognizer = sr.Recognizer()
    text = ""
    try:
        with sr.AudioFile(file_path) as source:
            audio_content = recognizer.record(source)
            results = recognizer.recognize_google(audio_content, language="fa-IR", show_all=True)
            if len(results) > 0:
                text = " ".join([alt["transcript"] for alt in results["alternative"]])
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