import { Fragment, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { useLanguage } from './LanguageContext';

function AuthAlert({ title, alertText, buttonText, isVisible, onClose }) {
  const { language } = useLanguage();
  const modalRef = useRef(null);
  const modalInstance = useRef(null);

  useEffect(() => {
    const modalElement = modalRef.current;
    if (!modalElement) return;

    // Create modal only once
    if (!modalInstance.current) {
      modalInstance.current = new window.bootstrap.Modal(modalElement);

      // stable handler reference
      const handleHidden = () => {
        onClose?.();
      };

      modalElement.addEventListener("hidden.bs.modal", handleHidden);

      // cleanup on unmount
      return () => {
        modalElement.removeEventListener("hidden.bs.modal", handleHidden);
        modalInstance.current?.dispose();
        modalInstance.current = null;
      };
    }
  }, [onClose]);

  useEffect(() => {
    if (!modalInstance.current) return;

    if (isVisible) {
      modalInstance.current.show();
    } else {
      modalInstance.current.hide();
    }
  }, [isVisible]);

  return (
    <Fragment>
      <div
        className="modal fade"
        id="exampleModalCenter"
        tabIndex="-1"
        role="dialog"
        aria-labelledby="exampleModalCenterTitle"
        aria-hidden="true"
        ref={modalRef} // use ref instead of getElementById
      >
        <div className="modal-dialog modal-dialog-centered" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">{title}</h5>
              <button
                type="button"
                className="close"
                data-bs-dismiss="modal"
                aria-label="Close"
              >
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div className="modal-body">{alertText}</div>
            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-secondary"
                data-bs-dismiss="modal"
                style={{ marginRight: "1rem", marginBottom: "2rem" }}
              >
                {language === "en" ? "Close" : "انصراف"}
              </button>
              <Link to="/login" style={{ marginRight: "1rem", marginBottom: "2rem" }}>
                <button type="button" className="btn btn-primary" data-bs-dismiss="modal">
                  {buttonText}
                </button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </Fragment>
  );
}

export default AuthAlert;
