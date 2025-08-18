import { Fragment, useEffect } from "react";
import { Link } from "react-router-dom";
import { useLanguage } from './LanguageContext';

function AuthAlert({ title, alertText, buttonText, isVisible, onClose }) {
  const { language } = useLanguage();
  
  useEffect(() => {
    const modalElement = document.getElementById("exampleModalCenter");
    if (!modalElement) return;

    // Create the modal instance once
    const modal = new window.bootstrap.Modal(modalElement);

    // Add event listener to dispose of the modal after it’s hidden
    modalElement.addEventListener("hidden.bs.modal", () => {
      modal.dispose();
      onClose(); // also update your state in parent if needed
    });

    if (isVisible) {
      modal.show();
    } else {
      modal.hide();
    }

    // Cleanup the event listener when the component unmounts
    return () => {
      modalElement.removeEventListener("hidden.bs.modal", () => {
        modal.dispose();
        onClose();
      });
    };
  }, [isVisible, onClose]);

  return (
    <Fragment>
      {/* Modal */}
      <div
        className="modal fade"
        id="exampleModalCenter"
        tabIndex="-1"
        role="dialog"
        aria-labelledby="exampleModalCenterTitle"
        aria-hidden="true"
      >
        <div className="modal-dialog modal-dialog-centered" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title" id="exampleModalLongTitle">
                {title}
              </h5>
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
                {language === "en" ? "Close" : "انصراف" }
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
