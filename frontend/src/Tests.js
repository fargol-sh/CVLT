import React from "react";
import "./Tests.css";
import { Link } from "react-router-dom";
import { useLanguage } from './LanguageContext';


export default function Tests() {
  const { language } = useLanguage();
  
  return (
    <div className="tests">
      <div className="container py-5">
        <div className="row pb-5">
          <div className="col">
            <div className="card mb-3 customCard" style={{ maxWidth: "540px" }}>
              <div className="row g-0">
                <div className="col-md-4">
                  <img
                    src={"../images/speech.png"}
                    className="img-fluid rounded-start"
                    alt={language === "en" ? "speech icon" : "آیکون مکالمه" }
                  />
                </div>
                <div className="col-md-8">
                  <div className="card-body cardbodycustom">
                    <h5 className="card-title">
                      {language === "en" ? "Test 1" : "تست ۱"}
                    </h5>
                    <p className="card-text text-muted">
                      {language === "en" ? "5 rounds in a row; 16 words to recall." : "۵ مرحله پشت سر هم؛ ۱۶ کلمه برای به خاطر سپردن." }
                    </p>
                    <div className="text-end">
                      <Link to="/profile/tests/1/1" className="btn cardBtn">
                        {language === "en" ? "Start Test" : "شروع تست" }
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="col">
            <div className="card mb-3 customCard" style={{ maxWidth: "540px" }}>
              <div className="row g-0">
                <div className="col-md-4">
                  <img
                    src={"../images/speech.png"}
                    className="img-fluid rounded-start"
                    alt="test icon"
                  />
                </div>
                <div className="col-md-8">
                  <div className="card-body cardbodycustom">
                    <h5 className="card-title">
                      {language === "en" ? "Test 2" : "تست ۲"}
                    </h5>
                    <p className="card-text text-muted">
                      {language === "en" ? "5 rounds in a row; 16 words to recall." : "۵ مرحله پشت سر هم؛ ۱۶ کلمه برای به خاطر سپردن." }
                    </p>
                    <div className="text-end">
                      <Link to="/profile/tests/2/1" className="btn cardBtn">
                        {language === "en" ? "Start Test" : "شروع تست" }
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="row pb-5">
          <div className="col">
            <div className="card mb-3 customCard" style={{ maxWidth: "540px" }}>
              <div className="row g-0">
                <div className="col-md-4">
                  <img
                    src={"../images/speech.png"}
                    className="img-fluid rounded-start"
                    alt="test icon"
                  />
                </div>
                <div className="col-md-8">
                  <div className="card-body cardbodycustom">
                    <h5 className="card-title">
                      {language === "en" ? "Test 3" : "تست ۳"}
                    </h5>
                    <p className="card-text text-muted">
                      {language === "en" ? "5 rounds in a row; 16 words to recall." : "۵ مرحله پشت سر هم؛ ۱۶ کلمه برای به خاطر سپردن." }
                    </p>
                    <div className="text-end">
                      <Link to="/profile/tests/3/1" className="btn cardBtn">
                        {language === "en" ? "Start Test" : "شروع تست" }
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="col">
            <div className="card mb-3 customCard" style={{ maxWidth: "540px" }}>
              <div className="row g-0">
                <div className="col-md-4">
                  <img
                    src={"../images/speech.png"}
                    className="img-fluid rounded-start"
                    alt="test icon"
                  />
                </div>
                <div className="col-md-8">
                  <div className="card-body cardbodycustom">
                    <h5 className="card-title">
                      {language === "en" ? "Test 4" : "تست ۴"}
                    </h5>
                    <p className="card-text text-muted">
                      {language === "en" ? "5 rounds in a row; 16 words to recall." : "۵ مرحله پشت سر هم؛ ۱۶ کلمه برای به خاطر سپردن." }
                    </p>
                    <div className="text-end">
                      <Link to="/profile/tests/4/1" className="btn cardBtn">
                        {language === "en" ? "Start Test" : "شروع تست" }
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
