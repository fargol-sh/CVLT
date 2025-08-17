import React, { useState, Fragment } from "react";
import { useParams } from "react-router-dom";
import "./Authentication.css";
import AuthAlert from "./AuthAlert";
import PuffLoader from "react-spinners/PuffLoader";
import { useLanguage } from './LanguageContext';

export default function ResetPassword() {
    const [newPassword, setNewPassword] = useState("");
    const [confirmNewPassword, setConfirmNewPassword] = useState("");
    const [resetPasswordStatus, setResetPasswordStatus] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [isModalVisible, setIsModalVisible] = useState(false);

    const { token } = useParams();
    const { language } = useLanguage();

    const onsubmit = async (event) => {
        event.preventDefault();
        setIsLoading(true);
        setResetPasswordStatus("");

        try {
            const response = await fetch(`/api/auth/password-reset/${token}`, {
                method: 'POST',
                body: JSON.stringify({
                    newPassword: newPassword,
                    confirmNewPassword: confirmNewPassword
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.status === 200) {
                if (data.reset === "successful") {
                    setIsModalVisible(true);
                    setNewPassword("");
                    setConfirmNewPassword("");
                } else {
                    setResetPasswordStatus(language === "en" ? "Unknown error" : "خطای ناشناخته");
                }
            } else {
                if (data.reset === "invalidToken") {
                    setResetPasswordStatus(language === "en" ? "Invalid password reset token!" : "توکن بازنشانی پسورد اشتباه است!");
                } else if (data.reset === "expiredToken") {
                    setResetPasswordStatus(language === "en" ? "Password reset token has expired!" : "توکن بازنشانی پسورد منقضی شده است!");
                } else if (data.reset === "unmatchedPasswords") {
                    setResetPasswordStatus(language === "en" ? "Passwords do not match!" : "رمز های عبور با هم مطابقت ندارند!");
                } else {
                    setResetPasswordStatus(data.error || "Something went wrong!");
                }
            }
        } catch (error) {
            console.error(error);
            setResetPasswordStatus(language === "en" ? "Network or server error!" : "خطا در شبکه یا سرور!");
        }

        setIsLoading(false);
    };

    return (
        <main>
            <Fragment>
                <AuthAlert
                    alertText={language === "en" ? "Your password has been successfully reset." : "رمز عبور شما با موفقیت بازنشانی شد."}
                    buttonText={language === "en" ? "Sign In" : "ورود"}
                    isVisible={isModalVisible}
                    onClose={() => setIsModalVisible(false)}
                />
                <div className="authentication">
                    <div className="container-fluid">
                        <div className="row">
                            <div className="col-5 half"></div>
                            <div className="col-7">
                                <form onSubmit={onsubmit}>
                                    {/* Absolute path for image */}
                                    <img src="/images/Logo.png" alt="logo" />
                                    
                                    <div className="mb-4">
                                        <label htmlFor="newPassword" className="form-label">
                                            {language === "en" ? "New Password" : "رمز عبور جدید"}
                                        </label>
                                        <input
                                            type="password"
                                            value={newPassword}
                                            onChange={(e) => setNewPassword(e.target.value)}
                                            className="form-control"
                                            id="newPassword"
                                            required
                                        />
                                    </div>
                                    
                                    <div className="mb-4">
                                        <label htmlFor="confirmNewPassword" className="form-label">
                                            {language === "en" ? "Confirm New Password" : "تایید رمز عبور جدید"}
                                        </label>
                                        <input
                                            type="password"
                                            value={confirmNewPassword}
                                            onChange={(e) => setConfirmNewPassword(e.target.value)}
                                            className="form-control"
                                            id="confirmNewPassword"
                                            required
                                        />
                                    </div>

                                    {resetPasswordStatus && (
                                        <p className="text-danger">{resetPasswordStatus}</p>
                                    )}

                                    <button
                                        type="submit"
                                        className="btn btn-primary PassForgot"
                                        disabled={isLoading}
                                        style={{
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center"
                                        }}
                                    >
                                        {isLoading
                                            ? <PuffLoader size={25} color="#fff" cssOverride={{ marginBottom: "0px" }} />
                                            : language === "en" ? "Reset Password →" : "بازنشانی رمز عبور ←"}
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </Fragment>
        </main>
    );
}
