import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import DonutChart from 'react-donut-chart';
import './Result.css';
import { useLanguage } from './LanguageContext';

export default function Result() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const {
    correct_words,
    round_completed
  } = state || {};

  const { language } = useLanguage();

  // parse URL to compute next path
  const [nextPath, setNextPath] = useState('/');
  const [showCompletionMessage, setShowCompletionMessage] = useState(false);

  useEffect(() => {
    const path = window.location.pathname;
    const parts = path.split('/');
    const t = Number(parts[3]);
    const r = Number(parts[4]);

    if (!isNaN(t) && !isNaN(r)) {
      if (r < 5) setNextPath(`/profile/tests/${t}/${r + 1}`);
      else setNextPath('/profile/tests');
    }
    console.log(t, r);
  }, []);

  const handleButtonClick = () => {
    if (round_completed) {
      // نمایش پیام تکمیل تست
      setShowCompletionMessage(true);
      
      // بعد از یک ثانیه به صفحه بعدی برو
      setTimeout(() => {
        navigate(nextPath);
      }, 2000);
    } else {
      // اگر تست تموم نشده، مستقیم به راند بعدی برو
      navigate(nextPath);
    }
  };

  if (!state) {
    return <p>
      {language === "en" ? "Error: no result data" : "خطا: داده ای برای نتایج یافت نشد."}
    </p>;
  }

  const percent = Math.round((correct_words / 16) * 100);

  const testNum = Number(window.location.pathname.split('/')[3]);
  const roundNum = Number(window.location.pathname.split('/')[4]);

  return (
    <div className="resultPage">
{showCompletionMessage && (
  <div className="completion-message" style={{
    position: 'fixed',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    backgroundColor: '#8ec2f2',
    color: 'white',
    padding: '20px 40px',
    borderRadius: '10px',
    fontSize: '18px',
    fontWeight: 'bold',
    zIndex: 1000,
    boxShadow: '0 4px 8px rgba(0,0,0,0.2)'
  }}>
    {language === "en" ? `Test ${testNum} Completed!` : `تست ${testNum} تکمیل شد!`}
  </div>
)}
      
      <div className="tests">
        <div className="container py-5">
          <div className="row pb-5" style={{display: "flex", justifyContent: "center"}}>
            <div className="col-md-6">
              <div className="results mb-3 py-5 text-center">
                <h3 className="pb-4">
                  {language === "en" ? `Test ${testNum} Round ${roundNum} Result` :
                   `نتیجه تست ${testNum} دور ${roundNum}`}
                </h3>
                <h4 className="text-muted pb-4">
                  {language === "en" ? "You have scored:" : "امتیاز به دست آمده:"}
                </h4>
                <h5>{language === "en" ? `${correct_words} / 16` : `16 / ${correct_words}`}</h5>
                <DonutChart
                  data={[
                    {
                      label: "",
                      value: percent,
                    },
                    {
                      label: "",
                      value: 100 - percent,
                    },
                  ]}
                  height={150}
                  width={150}
                  colors={["#8ec2f2", "#f9f9f9"]}
                  emptyColor="#ded6d6"
                  legend={false}
                  strokeColor="#8ec2f2"
                  interactive={false}
                />
              </div>
              <div className="d-flex justify-content-center">
                <button
                  className="btn cardBtn px-5 py-2"
                  onClick={handleButtonClick}
                  disabled={showCompletionMessage}
                >
                  {round_completed ? (language === "en" ? "Finish" : "پایان") :
                   (language === "en" ? "Next Round" : "دور بعدی")}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}