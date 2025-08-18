import React from "react";
import "./Help.css";
import { useLanguage } from './LanguageContext';


export default function Help() {
  const { language } = useLanguage();
  return (
    <div className="container TermsandConditions">
      {" "}
      <ol>
        <li>
          {language === "en" ? "Play the audio": "فایل صوتی را پخش کنید"}</li>
        <li>
          {language === "en" ? "Record your voice online or upload file" : "صدای خود را ضبط کرده یا فایل صدای خود را آپلود کنید." }
        </li>
        <li>
          {language === "en" ? "Click submit to see Results" : "روی گزینه ثبت کلیک کرده تا نتایج را مشاهده کنید"}
        </li>
      </ol>
    </div>
  );
}
