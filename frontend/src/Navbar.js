import React, { useEffect, useState, useContext, Fragment } from "react";
import "./Navbar.css";
import { AuthContext } from "./AuthContext";
import { Link, useLocation } from "react-router-dom";
import LogoutAlert from "./LogoutAlert";
import { useLanguage } from './LanguageContext';
import { GrLanguage } from "react-icons/gr";
import { LuLogOut } from "react-icons/lu";



export default function Navbar(props) {
  let [bgClass, setBgClass] = useState("HomeBackgrond");
  let [linkClass, setLinkClass] = useState("HomeLinkColor");
  let [generalClass, setGeneralClass] = useState("navbarHome");
  const { logged } = useContext(AuthContext);
  const { isAdmin } = useContext(AuthContext);

  // Logout Modal Visibility State
  const [isModalVisible, setIsModalVisible] = useState(false);

  const location = useLocation();

  const { language, toggleLanguage } = useLanguage();

  const logoutHandler = (e) => {
    e.preventDefault();

    setIsModalVisible(true);
  }

  useEffect(() => {
    if (location.pathname === "/") {
      setBgClass("HomeBackgrond");
      setLinkClass("HomeLinkColor");
      setGeneralClass("NavbarHome");
    } else {
      setBgClass("GeneralBackground");
      setLinkClass("GeneralLinkColor");
      setGeneralClass("GeneralHome");
    }
  }, [location.pathname]);

  if (!logged) {
    return (
      <nav
        dir={language === "en" ? "ltr" : "rtl"}
        className={`navbar navbar-expand-lg px-5 pt-3 pb-3 ${bgClass} ${generalClass}`}
      >
        <div className="container-fluid px-5">
          <Link className={`navbar-brand ${linkClass} navbarBrand`} to="/">
            NeuroRecall
          </Link>
          <button
            className={`navbar-toggler ${linkClass}`}
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarSupportedContent"
            aria-controls="navbarSupportedContent"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarSupportedContent"
          style={{justifyContent: "space-between"}}
          >
            <ul className="navbar-nav mb-2 mb-lg-0 pr-0 nav-ul">
              <li className="nav-item pe-3">
                <Link
                  className={`nav-link ${linkClass}`}
                  aria-current="page"
                  to="/"
                >
                  {language === "en" ? "Home" : "خانه"}
                </Link>
              </li>
              <li className="nav-item pe-3 mt-1">
                <button 
                  onClick={toggleLanguage}
                  className="language-toggle" 
                >
                  <GrLanguage style={{marginInlineEnd: "0.5rem"}}/>
                  {language === "en" ? "Persian" : "انگلیسی"}
                </button>
              </li>
              
              {/*               <li className="nav-item">
                <a className="nav-link" href="/help">
                  Help
                </a>
              </li> */}
            </ul>
            <ul className="navbar-nav mb-2 mb-lg-0">
              <li className="nav-item  pe-3">
                <Link
                  className={`nav-link ${linkClass}`}
                  aria-current="page"
                  to="/login"
                >
                  {language === "en" ? "Login" : "ورود"}
                </Link>
              </li>
              <li className="nav-item">
                <Link
                  className={`nav-link btn btn-primary px-4 navbarBtn`}
                  aria-current="page"
                  to="/register"
                >
                  {language === "en" ? "Register →" : "ثبت نام"}
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    );
  } else {
    return (
      <Fragment>
        <LogoutAlert
          alertText={language === "en" ? "Are you sure you want to log out of your account?" : 
            "آیا مطمئن هستید که می خواهید از حساب خود خارج شوید؟"}
          buttonText={language === "en" ? "Log out" : "خروج" }
          isVisible={isModalVisible}
          onClose={() => setIsModalVisible(false)}
        />
        <nav
          dir={language === "en" ? "ltr" : "rtl"}
          className={`navbar navbar-expand-lg px-5 pt-3 ${bgClass} ${generalClass}`}
        >
          <div className="container-fluid px-5">
            <Link className={`navbar-brand ${linkClass} navbarBrand`} to="/">
              NeuroRecall
            </Link>
            <button
              className={`navbar-toggler ${linkClass}`}
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#navbarSupportedContent"
              aria-controls="navbarSupportedContent"
              aria-expanded="false"
              aria-label="Toggle navigation"
            >
              <span className="navbar-toggler-icon"></span>
            </button>
            <div className="collapse navbar-collapse" id="navbarSupportedContent"
              style={{justifyContent: "space-between"}}>
              <ul className="navbar-nav nav-ul mb-2 mb-lg-0">
                <li className="nav-item pe-3">
                  <Link
                    className={`nav-link ${linkClass}`}
                    aria-current="page"
                    to="/"
                  >
                    {language === "en" ? "Home" : "خانه"}
                  </Link>
                </li>
                <li className="nav-item pe-3">
                  <Link
                    className={`nav-link ${linkClass}`}
                    aria-current="page"
                    to="/profile"
                  >
                    {language === "en" ? "Profile" : "پروفایل"}
                  </Link>
                </li>
                <li className="nav-item pe-3">
                  <Link
                    className={`nav-link ${linkClass}`}
                    aria-current="page"
                    to="/profile/tests"
                  >
                    {language === "en" ? "Tests" : "آزمون ها"}
                  </Link>
                </li>
                {isAdmin ? <li className="nav-item pe-3">
                  <Link
                    className={`nav-link ${linkClass}`}
                    aria-current="page"
                    to="/profile/user-results"
                  >
                    {language === "en" ? "User Results" : "نتایج کاربران"}
                  </Link>
                </li> : null}
                <li className="nav-item pe-3 mt-1">
                  <button 
                    onClick={toggleLanguage}
                    className="language-toggle" 
                  >
                    <GrLanguage style={{ marginInlineEnd: "0.5rem" }} />
                    {language === "en" ? "Persian" : "انگلیسی"}
                  </button>
                </li>
                {/*
                <li className="nav-item">
                  <a className="nav-link" href="/help">
                    Help
                  </a>
                </li> */}
              </ul>
              <ul className="navbar-nav mb-2 mb-lg-0" >
                <li className="nav-item">
                  <button
                    className={`nav-link btn btn-primary px-4 navbarBtn`}
                    aria-current="page"
                    onClick={(e) => logoutHandler(e)}
                  >
                    {language === "en" ? `Logout${" "}` : "خروج"}
                    <LuLogOut style={{marginInlineStart: "0.5rem"}}/>
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </nav>
      </Fragment>
      
    );
  }
}
