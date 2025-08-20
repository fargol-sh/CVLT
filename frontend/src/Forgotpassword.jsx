import React, { useState } from "react";
import "./Authentication.css";
import AuthAlert from "./AuthAlert";
import PuffLoader from "react-spinners/PuffLoader";
import { useLanguage } from './LanguageContext';
import { Link } from "react-router-dom";

export default function Forgotpassword() {
  // Email State
  const [email, setEmail] = useState("");
  // Email Status (store only the error key from backend, not the final translated string)
  const [emailStatusKey, setEmailStatusKey] = useState("");
  // Modal Visibility State
  const [isModalVisible, setIsModalVisible] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  
  const { language } = useLanguage();
  
  // Email validation function
  const isValidEmail = (email) => {
    const pattern = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i;
    return pattern.test(email);
  };

  // Translation map for backend error messages
  const errorMessages = {
    "Please enter a valid email address!": {
      en: "Please enter a valid email address!",
      fa: "لطفاً یک آدرس ایمیل معتبر وارد کنید!"
    },
    "Email is required.": {
      en: "Email is required.",
      fa: "ایمیل الزامی است."
    },
    "Invalid email format.": {
      en: "Invalid email format.",
      fa: "فرمت ایمیل نامعتبر است."
    },
    "Too many reset requests. Please try again later.": {
      en: "Too many reset requests. Please try again later.",
      fa: "تعداد درخواست‌های بازنشانی بیش از حد است. لطفاً بعداً دوباره تلاش کنید."
    },
    "Reset email already sent recently.": {
      en: "Reset email already sent recently.",
      fa: "ایمیل بازنشانی اخیراً ارسال شده است."
    },
    "Email does not exist!": {
      en: "Email address does not exist!",
      fa: "آدرس ایمیل موجود نیست!"
    },
    "Internal server error.": {
      en: "Internal server error.",
      fa: "خطای داخلی سرور."
    }
  };

  // Function to get translated message based on key + language
  const translateError = (key) => {
    if (!key) return "";
    if (errorMessages[key]) {
      return language === "en" ? errorMessages[key].en : errorMessages[key].fa;
    }
    // fallback if backend sends unexpected error
    return key;
  };

  const onsubmit = async (event) => {
    event.preventDefault();

    if (!isValidEmail(email)) {
      setEmailStatusKey("Please enter a valid email address!");
      return;
    }

    setIsLoading(true);
    
    // Send User Inputs
    try {
      const response = await fetch("/api/auth/reset-password", {
        method: "POST",
        body: JSON.stringify({
          email: email,
        }),
        headers: {
          "Content-Type": "application/json",
        },
      });
      const data = await response.json();
      if (response.status === 200) {
        if (data.reset === "failed") {
          setEmailStatusKey(data.error || "Email does not exist!");
        } else if (data.reset === "successful") {
          localStorage.setItem("resetPasswordToken", data.token);
          // Reset Input
          setEmail("");
          // Clear status
          setEmailStatusKey("");
          // Show Modal
          setIsModalVisible(true);
        }
      } else {
        setEmailStatusKey(data.error || response.statusText);
      }
    } catch (error) {
      console.log(error);
      setEmailStatusKey("Internal server error.");
    }
    
    setIsLoading(false);
  };

  return (
    <main>
      <AuthAlert
        alertText={language === "en" ? 
          "An email has been sent to you with instructions on how to reset your password." 
          : "یک ایمیل با دستورالعمل‌های بازنشانی رمز عبور برای شما ارسال شده است." }
        buttonText={language === "en" ? "Log In" : "ورود" }
        isVisible={isModalVisible}
        onClose={() => setIsModalVisible(false)}
      />
      <div className="authentication">
        <div className="container-fluid">
          <div className="row">
            <div className="col-5 halfForget">
              <p className="halfForget_title">
                {language === "en" ? "Continue with your personalized health journey today" : 
                  "امروز مسیر شخصی‌سازی‌شده سلامتی‌ات رو ادامه بده."
                }
              </p>
            </div>
            <div className="col-7">
              <form onSubmit={onsubmit} noValidate>
                <img src={"./images/Logo.png"} alt="logo" />
                <div className="mb-4">
                  <label htmlFor="exampleInputPassword1" className="form-label">
                    {language === "en" ? "Email" : "ایمیل" }
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="form-control"
                    id="exampleInputPassword1"
                    required
                  />
                </div>
                <button
                  type="submit"
                  className="btn btn-primary PassForgot"
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center"
                  }}
                  disabled={isLoading}
                >
                  {isLoading ? <PuffLoader size={25} color="#fff" cssOverride={{ marginBottom: "0px" }}/> : 
                  (language === "en" ? "Reset Password →" : "بازنشانی رمز عبور ←" )
                  }
                </button>
                <p className="forgotpassword-status">{translateError(emailStatusKey)}</p>
                <div className="bottomText form-text">
                  {language === "en" ? "Don't have an account?" : "حساب کاربری ندارید؟"} 
                  <Link to="/register">
                    {language === "en" ? "Sign up" : " ثبت نام" }
                  </Link>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
