import React, {useState, useContext} from "react";
import "./Authentication.css";
import { useNavigate, Link } from "react-router-dom";
import { AuthContext } from "./AuthContext";
import PuffLoader from "react-spinners/PuffLoader";
import { useLanguage } from './LanguageContext';

export default function Login() {
  const navigate = useNavigate();

  const { setLogged } = useContext(AuthContext);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [loginStatus, setLoginStatus] = useState("");

  const [isLoading, setIsLoading] = useState(false);

  const { language } = useLanguage();
  
  // Function to translate error messages from backend
  const translateError = (errorMessage) => {
    if (language === "fa") {
      // Translate common error messages to Persian
      if (errorMessage.includes("Invalid credentials")) {
        if (errorMessage.includes("attempts remaining")) {
          const attempts = errorMessage.match(/(\d+) attempts remaining/);
          return attempts ? 
            `اطلاعات وارد شده اشتباه است. ${attempts[1]} تلاش باقی مانده.` :
            "اطلاعات وارد شده اشتباه است.";
        }
        return "اطلاعات وارد شده اشتباه است.";
      }
      
      if (errorMessage.includes("Account locked")) {
        const minutes = errorMessage.match(/(\d+) minutes/);
        return minutes ? 
          `حساب شما به دلیل تلاش‌های زیاد قفل شد. ${minutes[1]} دقیقه دیگر تلاش کنید.` :
          "حساب شما موقتاً قفل شده است.";
      }
      
      if (errorMessage.includes("Too many login attempts")) {
        return "تلاش‌های زیادی انجام داده‌اید. لطفاً بعداً تلاش کنید.";
      }
      
      if (errorMessage.includes("Username and password required")) {
        return "نام کاربری و رمز عبور الزامی است.";
      }
      
      if (errorMessage.includes("Invalid input length")) {
        return "طول ورودی نامعتبر است.";
      }
      
      // Fallback to original message if no translation found
      return errorMessage;
    }
    
    // Return English message as-is
    return errorMessage;
  };

  const onsubmit = async (e) => {
    e.preventDefault();

    setIsLoading(true);
    
    try {
      const response = await fetch("/api/auth/login", {
        method: 'POST',
        body: JSON.stringify({
          username: username,
          password: password,
        }),
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      
      if (response.status === 200) {
        if (data.login === "failed") {
          // Use the specific error message from backend
          const errorMessage = data.error || (language === "en" ? "Login failed" : "ورود ناموفق");
          setLoginStatus(translateError(errorMessage));
        } else if (data.login === "successful") {
          setLogged(true);
          navigate('/profile', true);
          // Reset inputs
          setUsername("");
          setPassword("");
          setLoginStatus("");
        }
      } else if (response.status === 401) {
        // Unauthorized - use backend error message
        const errorMessage = data.error || (language === "en" ? "Invalid credentials" : "اطلاعات نامعتبر");
        setLoginStatus(translateError(errorMessage));
      } else if (response.status === 429) {
        // Rate limited - use backend error message  
        const errorMessage = data.error || (language === "en" ? "Too many attempts. Please try again later." : "تلاش‌های زیاد. لطفاً بعداً تلاش کنید.");
        setLoginStatus(translateError(errorMessage));
      } else if (response.status === 423) {
        // Account locked - use backend error message
        const errorMessage = data.error || (language === "en" ? "Account temporarily locked" : "حساب موقتاً قفل شده");
        setLoginStatus(translateError(errorMessage));
      } else {
        // Other errors
        const errorMessage = data.error || `${response.statusText}!`;
        setLoginStatus(translateError(errorMessage));
      }
      
    } catch(error) {
      console.log(error);
      setLoginStatus(language === "en" ? 
        "Network error. Please try again." : 
        "خطای شبکه. لطفاً دوباره تلاش کنید."
      );
    }
    
    setIsLoading(false);
  }

  return (
    <div className="authentication">
      <div className="container-fluid">
        <div className="row">
          <div className="col-5 half">
            <p className="half_title">
              {language === "en" ? "Continue with your personalized health journey today" : 
                "امروز مسیر شخصی‌سازی‌شده سلامتی‌ات رو ادامه بده."
              }
            </p>
          </div>
          <div className="col-7">
            <form onSubmit={onsubmit}>
              <img src={"./images/Logo.png"} alt="logo" />

              <div className="mb-3">
                <label htmlFor="usernameInput" className="form-label">
                  {language === "en" ? "Username" : "نام کاربری"}
                </label>
                <input
                  type="text"
                  value={username}
                  className="form-control"
                  id="usernameInput"
                  onChange={(e) => setUsername(e.target.value)}
                  aria-describedby="username"
                  required
                />
              </div>
              <div className="mb-3">
                <label htmlFor="exampleInputPassword1" className="form-label">
                  {language === "en" ? "Password" : "رمز عبور" }
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="form-control"
                  id="exampleInputPassword1"
                  required
                />
              </div>
              <div id="PasswordHelp" className="form-text" style={{textAlign: language === "en" ? "right" : "left"}}>
                <Link to="/forgotpassword">
                  {language === "en" ? "Forgot Password?" : "پسورد خود را فراموش کرده اید؟" }
                </Link>
              </div>
              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={isLoading}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center"
                }}
              >
                {isLoading ? <PuffLoader size={25} color="#fff" cssOverride={{ marginBottom: "0px" }}/> : 
                language === "en" ? "Login →" : "ورود ←"}
              </button>
              <p className="login-status">{loginStatus}</p>
              <div className="bottomText form-text">
                {language === "en" ? "Don't have an account?" : "حساب کاربری ندارید؟" }<Link to="/register">{language === "en" ? " Sign up" : " ثبت نام" }</Link>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}