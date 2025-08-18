import React, { useState } from "react";
import "./Authentication.css";
import AuthAlert from "./AuthAlert";
import PuffLoader from "react-spinners/PuffLoader";
import { useLanguage } from './LanguageContext';
import { Link } from "react-router-dom";


export default function Forgotpassword() {
  // Email State
  const [email, setEmail] = useState("");
  // Email Status
  const [emailStatus, setEmailStatus] = useState("");
  // Modal Visibility State
  const [isModalVisible, setIsModalVisible] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  
  const { language } = useLanguage();
  
  // Email validation function
  const isValidEmail = (email) => {
    const pattern = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i;
    return pattern.test(email);
  };

  const onsubmit = async (event) => {
    event.preventDefault();

    if (!isValidEmail(email)) {
      setEmailStatus(
        language === "en"
          ? "Please enter a valid email address!"
          : "لطفاً یک آدرس ایمیل معتبر وارد کنید!"
      );
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
      if (response.status === 200) {
        const data = await response.json();
        if (data.reset === "failed") {
          setEmailStatus(language === "en" ? "Email address does not exist!" : "آدرس ایمیل موجود نیست!" );
        } else if (data.reset === "successful") {
          localStorage.setItem("resetPasswordToken", data.token);
          // Reset Input
          setEmail("");
          // Show Modal
          setIsModalVisible(true);
        }
      } else {
        setEmailStatus(`${response.statusText}!`);
      }
    } catch (error) {
      console.log(error);
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
              <form onSubmit={onsubmit}>
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
                <p className="forgotpassword-status">{emailStatus}</p>
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
