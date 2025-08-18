import React, { useCallback, useEffect, useState } from "react";
import { useAudioRecorder } from "react-audio-voice-recorder";
import "./Test.css";
import { useDropzone } from "react-dropzone";
import { useLocation, useNavigate } from "react-router-dom";
import PuffLoader from "react-spinners/PuffLoader";
import { ConvertWebmToWav } from "./ConvertWebmToWav";
import { useLanguage } from './LanguageContext';

export default function Test() {
  const [uploadState, setUploadState] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [currentTest, setCurrentTest] = useState(1);
  const [currentRound, setCurrentRound] = useState(1);

  const [loading1, setLoading1] = useState(false);
  const [loading2, setLoading2] = useState(false);

  // اضافه کردن state برای نمایش خطاها
  const [errorMessage, setErrorMessage] = useState("");

  const location = useLocation();
  const navigate = useNavigate();

  const { language } = useLanguage();

  const {
    startRecording,
    stopRecording,
    recordingBlob,
    isRecording,
  } = useAudioRecorder();

  // محدودیت حجم فایل (10 مگابایت)
  const MAX_FILE_SIZE_MB = 5;
  const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

  // تابع validation برای فایل
  const validateAudioFile = (file) => {
    if (!file) {
      return {
        valid: false,
        error: language === "en" ? "Please select an audio file" : "لطفاً یک فایل صوتی انتخاب کنید"
      };
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      return {
        valid: false,
        error: language === "en" 
          ? `File size exceeds ${MAX_FILE_SIZE_MB} MB` 
          : `حجم فایل از ${MAX_FILE_SIZE_MB} مگابایت بیشتر است`
      };
    }

    const allowedTypes = ['audio/mp3', 'audio/mpeg', 'audio/m4a', 'audio/wav', 'audio/webm', 'audio/ogg'];
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(mp3|m4a|wav|webm|ogg)$/i)) {
      return {
        valid: false,
        error: language === "en" 
          ? "Please select a valid audio file (MP3, M4A, WAV, WebM, OGG)" 
          : "لطفاً یک فایل صوتی معتبر انتخاب کنید (MP3, M4A, WAV, WebM, OGG)"
      };
    }

    return { valid: true, error: null };
  };

  // تابع validation برای blob ضبط شده
  const validateRecordedBlob = (blob) => {
    if (!blob) {
      return {
        valid: false,
        error: language === "en" ? "Please record something first" : "لطفاً ابتدا صدای خود را ضبط کنید"
      };
    }

    if (blob.size > MAX_FILE_SIZE_BYTES) {
      return {
        valid: false,
        error: language === "en" 
          ? `Recording size exceeds ${MAX_FILE_SIZE_MB} MB` 
          : `حجم ضبط از ${MAX_FILE_SIZE_MB} مگابایت بیشتر است`
      };
    }

    return { valid: true, error: null };
  };

  // تابع نمایش خطا
  const showError = (message) => {
    setErrorMessage(message);
    setTimeout(() => setErrorMessage(""), 5000); // پاک کردن خطا بعد از 5 ثانیه
  };

  // Update test, round, and result path on route change
  useEffect(() => {
    const currentPath = location.pathname;
    const match = currentPath.match(/tests\/(\d+)\/(\d+)/);
    if (match) {
      setCurrentTest(parseInt(match[1], 10));
      setCurrentRound(parseInt(match[2], 10));
    } else {
      setCurrentTest(1);
      setCurrentRound(1);
    }
    // clear upload/record state whenever the route changes
    setUploadState(false);
    setUploadedFile(null);
    setRecordedBlob(null);
    setErrorMessage(""); // پاک کردن خطاها
  }, [location]);

  useEffect(() => {
    if (recordingBlob) {
      setRecordedBlob(recordingBlob);
    }
  }, [recordingBlob]);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      const validation = validateAudioFile(file);
      
      if (!validation.valid) {
        showError(validation.error);
        return;
      }

      setUploadState(true);
      setUploadedFile(file);
      setErrorMessage(""); // پاک کردن خطاهای قبلی
    }
  }, [language]);

  const { getRootProps, getInputProps, open } = useDropzone({
    onDrop,
    accept: { "audio/*": [] },
    multiple: false,
    noClick: true,
    noKeyboard: true,
    maxSize: MAX_FILE_SIZE_BYTES,
    onDropRejected: (fileRejections) => {
      if (fileRejections.length > 0) {
        const rejection = fileRejections[0];
        if (rejection.errors.some(e => e.code === 'file-too-large')) {
          showError(language === "en" 
            ? `File size exceeds ${MAX_FILE_SIZE_MB} MB` 
            : `حجم فایل از ${MAX_FILE_SIZE_MB} مگابایت بیشتر است`);
        } else if (rejection.errors.some(e => e.code === 'file-invalid-type')) {
          showError(language === "en" 
            ? "Please select a valid audio file" 
            : "لطفاً یک فایل صوتی معتبر انتخاب کنید");
        }
      }
    }
  });

  async function sendAudioToBackend(file) {
    const formData = new FormData();
    formData.append("audio", file);
    formData.append("test_number", currentTest);
    formData.append("round_number", currentRound);

    try {
      const response = await fetch("/api/tests/submit-audio", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const resultData = await response.json();
        // Go to the exact /tests/X/Y/result with the returned data
        navigate(`/profile/tests/${currentTest}/${currentRound}/result`, {
          state: {
            ...resultData,
            test_number: currentTest,
            round_number: currentRound,
          },
        });
      } else {
        const errorData = await response.json();
        showError(errorData.error || (language === "en" ? "Upload failed!" : "آپلود موفقیت آمیز نبود!"));
      }

    } catch (error) {
      console.error(language === "en" ? "Error uploading audio:" : "خطا در آپلود صدا", error);
      showError(language === "en" ? "Connection error. Please try again." : "خطا در اتصال. لطفاً دوباره امتحان کنید.");
    }

    setLoading1(false);
    setLoading2(false);
  }

  async function handleUploadSubmit(e) {
    e.preventDefault();

    const validation = validateAudioFile(uploadedFile);
    if (!validation.valid) {
      showError(validation.error);
      return;
    }

    setLoading1(true);
    await sendAudioToBackend(uploadedFile);
  }

  async function handleRecordSubmit(e) {
    e.preventDefault();

    const validation = validateRecordedBlob(recordedBlob);
    if (!validation.valid) {
      showError(validation.error);
      return;
    }

    setLoading2(true);

    try {
      const wavBlob = await ConvertWebmToWav(recordedBlob);
      
      // Validation بعد از تبدیل
      const wavValidation = validateRecordedBlob(wavBlob);
      if (!wavValidation.valid) {
        showError(wavValidation.error);
        setLoading2(false);
        return;
      }

      await sendAudioToBackend(wavBlob);
    } catch (err) {
      console.error(language === "en" ? "Conversion failed:" : "تبدیل صدا ناموفق بود!", err);
      showError(language === "en" ? "Audio conversion failed. Please try again." : "تبدیل صدا ناموفق بود. لطفاً دوباره امتحان کنید.");
      setLoading2(false);
    }
  }

  // تابع برای انتخاب فایل با کلیک
  const handleFileSelect = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'audio/*';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        const validation = validateAudioFile(file);
        
        if (!validation.valid) {
          showError(validation.error);
          return;
        }

        setUploadState(true);
        setUploadedFile(file);
        setErrorMessage("");
      }
    };
    input.click();
  };

  return (
    <div className="testRound">
      {/* Error Message Display */}
      {errorMessage && (
        <div className="row">
          <div className="col-12">
            <div className="alert alert-danger alert-dismissible fade show" role="alert" style={{
              position: 'fixed',
              top: '20px',
              right: '20px',
              zIndex: 1000,
              maxWidth: '400px',
              direction: language === 'fa' ? 'rtl' : 'ltr'
            }}>
              {errorMessage}
              <button type="button" className="btn-close" onClick={() => setErrorMessage("")}></button>
            </div>
          </div>
        </div>
      )}

      {/* Help Button */}
      <div className="row pt-4">
        <div className="offset-md-1 col-md-1">
          <a href="/help" className="help" target="_blank">
            {language === "en" ? "Help" : "راهنما" }
          </a>
        </div>
      </div>

      {/* Test Audio */}
      <div className="row pt-1 pb-5" style={{display: "flex", justifyContent: "center"}}>
        <div className="col-md-3">
          <audio controls key={`${currentTest}-${currentRound}`}>
            <source
              src={`http://127.0.0.1:5000/static/audio/test${currentTest}.m4a`}
              type="audio/x-m4a"
              preload="auto"
            />
          </audio>
          <div className="text-center pt-2">{language === "en" ? "Round " : "دور "} {currentRound} 
            {language === "en" ? " of 5" : " از 5"}</div>
        </div>
      </div>

      {/* Upload & Record Sections */}
      <div className="row p-5" style={{display: "flex", justifyContent: "center"}}>
        {/* Upload Section */}
        <div className="col-md-5 text-center">
          <div className="upload" {...getRootProps()}>
            <input {...getInputProps()} />
            <img
              src={"../../../images/feather_upload-cloud.png"}
              className="mx-auto d-block my-4"
              alt="upload"
            />
            <h6 className="uploadtitle">
              {uploadState ? (language === "en" ? "Choose another file or drag and drop here" : "فایل دیگری انتخاب کنید") : 
              (language === "en" ? "Select a file or drag and drop here" : "یک فایل انتخاب کرده یا یک فایل انتخاب کنید یا اینجا بکشید و رها کنید.")}
            </h6>
            <p className="types text-muted">
              {uploadState ? 
                <span style={{fontSize: '12px'}}>
                  {language === "en" ? `Selected: ${uploadedFile?.name} (${(uploadedFile?.size / (1024 * 1024)).toFixed(2)} MB)` : 
                  `انتخاب شده: ${uploadedFile?.name} (${(uploadedFile?.size / (1024 * 1024)).toFixed(2)} مگابایت)`}
                  <br />
                  {language === "en" ? `Max size: ${MAX_FILE_SIZE_MB} MB` : `حداکثر حجم: ${MAX_FILE_SIZE_MB} مگابایت`}
                </span>
                : 
                <span>
                  {language === "en" ? "MP3, M4A, OGG, WEBM and other audio files" : "MP3, M4A, OGG, WEBM و انواع فایل های دیگر"}
                  <br />
                  {language === "en" ? `Max size: ${MAX_FILE_SIZE_MB} MB` : `حداکثر حجم: ${MAX_FILE_SIZE_MB} مگابایت`}
                </span>
              }
            </p>
            <button
              type="button"
              className={`btn ${uploadState ? "UploadedBtn px-4" : "BrowseBtn"}`}
              onClick={handleFileSelect}
            >
              {uploadState ? (language === "en" ? "Uploaded" : "آپلود شده" ) : (language === "en" ? "Browse" : "انتخاب فایل")}
            </button>
            <hr className="line mx-auto d-block" />
            <button
              className="btn cardBtn mt-3"
              onClick={handleUploadSubmit}
              disabled={loading1 || loading2}
            >
              {loading1 ? <PuffLoader size={40} color="#fff" /> : (uploadedFile ? (language === "en" ? "Submit Upload" : "ثبت فایل") : (language === "en" ? "Upload a File" : "یک فایل آپلود کنید"))}
            </button>
          </div>
        </div>

        {/* Record Section */}
        <div className="col-md-5 text-center">
          <div className="upload">
            <h5 className="pb-3 pt-1">
              {language === "en" ? "Record your sound" : "صدای خود را ضبط کنید" }
            </h5>
            <div>
              <img
                src={"../../../images/mic.png"}
                className={`mx-auto d-block my-4 ${isRecording ? "startRecordingmod" : "startRecord"}`}
                alt="record"
                onClick={() => (isRecording ? stopRecording() : startRecording())}
              />
            </div>
            {recordedBlob && (
              <p className="text-muted" style={{fontSize: '12px'}}>
                {language === "en" ? `Recorded: ${(recordedBlob.size / (1024 * 1024)).toFixed(2)} MB` : 
                `ضبط شده: ${(recordedBlob.size / (1024 * 1024)).toFixed(2)} مگابایت`}
              </p>
            )}
            <hr className="line mx-auto d-block" />
            <button
              className="btn cardBtn mt-3"
              onClick={handleRecordSubmit}
              disabled={loading1 || loading2}
            >
              {loading2 ? <PuffLoader size={40} color="#fff" /> : (recordedBlob ? (language === "en" ? "Submit Recording" : "ثبت فایل") : (language === "en" ? "Record" : "ضبط کنید"))}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}