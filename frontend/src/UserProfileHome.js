import React from "react";
import DataTable from "react-data-table-component";
import { useState, useEffect } from "react";
import ProfileImageUpload from "./ProfileImageUpload";
import { useLanguage } from './LanguageContext';

const BASE_URL = process.env.REACT_APP_API_URL;

const UserProfileHome = () => {
  const [filters, setFilters] = useState({ test_number: '', test_time: '' });
  const [data, setData] = useState([]);
  const [userData, setUserData] = useState([]);
  const { language } = useLanguage();

  const columns = [
    {
      name: (language === "en" ? "Test Number" : "شماره آزمون"),
      selector: row => row.test_number, 
      sortable: true,
    },
    {
      name: (language === "en" ? "Test Round" : "شماره دور"),
      selector: row => row.round_number,
      sortable: true,
    },
    {
      name: (language === "en" ? "Score" : "امتیاز"),
      selector: row => row.score,
      sortable: true,
    },
    {
      name: (language === "en" ? "Test Time" : "تاریخ آزمون"),
      selector: row => row.test_time,   
      sortable: true,
      width: "300px",
    },
    {
      name: (language === "en" ? "Approved" : "تایید شده"),
      selector: row => (row.approved === "Yes" ? (language === "en" ? "Yes" : "بله") : (language === "en" ? "No" : "خیر")),
      sortable: true,
    },
    {
      name: (language === "en" ? "Total Score" : "مجموع امتیاز"),
      selector: row => row.total_score, 
      sortable: true,
    },
  ];

  // whenever filters change, re‑fetch
  useEffect(() => {
    const load = async () => {
      const qs = new URLSearchParams(filters).toString();
      const res = await fetch(`/api/user-profile?${qs}`);
      const result = await res.json();
  
      if (res.ok) {
        const mapped = result.scores.map((item, index) => ({
          id: index + 1,
          test_number: item.test_number,
          round_number: item.round_number,
          score: item.score,
          test_time: new Date(item.test_time).toLocaleString(),
          approved: item.approved,
          total_score: item.total_score,
        }));
  
        setUserData(result.user);
        setData(mapped);
      }
    };
    load();
  }, [filters]);
  

  const onChange = (e) => {
    setFilters(f => ({ ...f, [e.target.name]: e.target.value }));
  };

  const onReset = () => setFilters({ test_number: '', test_time: '' });

  // Handle Profile Picture
  const handlePhotoChange = async (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('photo', file);
    formData.append('user_id', userData.id); // Make sure you include user ID

    const res = await fetch('/api/upload-profile-photo', {
      method: 'POST',
      body: formData
    });

    if (res.ok) {
      const result = await res.json();
      setUserData(prev => ({ ...prev, profile_photo: result.photo }));
    } else {
      alert(language === "en" ? "Upload failed." : "خطا در آپلود!");
    }
  };

  
  return (
    <div className="container-fluid profile">
      <div className="row">
        <div className="col-1 sidebar px-0 pt-5 pb-5">
          <ProfileImageUpload onChange={handlePhotoChange} source={userData.profile_photo ? `${BASE_URL}/static/profile_photos/${userData.profile_photo}` : "./images/profile.png"}/>
          <h5 className="text-center">
            {userData.username ? userData.username : ""}
          </h5>
        </div>
        <div className="col-11 py-5 px-5">
          <div className="px-2 py-5">
            <h3 className="mb-5">
              {language === "en" ? "Test Results" : "نتایج آزمون ها" }
            </h3>
            <form className="d-flex gap-1 mb-1" onSubmit={e => e.preventDefault()}>
              <input
                name="test_number"
                className="form-control search-input"
                type="text"
                placeholder={language === "en" ? "Filter By Test Number" : "فیلتر بر اساس شماره آزمون" }
                onChange={onChange}
                value={filters.test_number}
              />
              <input
                name="test_time"
                className="form-control search-input"
                type="datetime-local"
                onChange={onChange}
                value={filters.test_time}
              />
              <button onClick={onReset} className="btn btn-primary px-3">
                {language === "en" ? "Reset" : "حذف فیلترها" }
              </button>
            </form>
            <DataTable
              className="tableCustom"
              columns={columns}
              data={data}
              highlightOnHover={true}
              pagination={true}
              paginationPerPage={5}
              paginationRowsPerPageOptions={[5, 10, 15]}
              noDataComponent={language === "en" ? "There are no records to display" : "هیچ داده ای برای نمایش وجود ندارد."}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default UserProfileHome;