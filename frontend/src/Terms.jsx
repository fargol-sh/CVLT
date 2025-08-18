import React from "react";
import "./Terms.css";
import { useLanguage } from './LanguageContext';

export default function Terms() {
  const { language } = useLanguage();

  return (
    <div className="container TermsandConditions">
      {" "}
      <ul>
        <li>
          {language === "en" ? "I agree to my voice being recorded." 
          : "موافقت می کنم که صدایم ضبط شود."}
        </li>
        <li>
          {language === "en" ? "I agree to my voice used as test voice in future." 
         : "موافقت می کنم که صدایم به عنوان تست در آینده مورد استفاده قرار بگیرد." }
        </li>
      </ul>
    </div>
  );
}
