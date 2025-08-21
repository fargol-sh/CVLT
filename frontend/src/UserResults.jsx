import React, { useState, useEffect, useCallback } from "react";
import DataTable from "react-data-table-component";
import { useLanguage } from './LanguageContext';
import ProfileImageUpload from "./ProfileImageUpload";


const BASE_URL = process.env.REACT_APP_API_URL;

const UserResults = () => {
  const { language } = useLanguage();

  const columns = [
    { name: (language === "en" ? "Username" : "نام کاربری"), selector: (row) => row.username, sortable: true, width: "200px" },
    { name: (language === "en" ? "Age" : "سن"), selector: (row) => row.age, sortable: true, width: "100px" },
    {
      name: (language === "en" ? "Gender" : "جنسیت"),
      selector: row =>
        row.gender === "female"
          ? (language === "en" ? "female" : "زن")
          : (language === "en" ? "male" : "مرد"),
      sortable: true,
      width: "120px"
    },
    { name: (language === "en" ? "Test Number" : "شماره آزمون"), selector: (row) => row.test_number, sortable: true, width: "150px" },
    { name: (language === "en" ? "Round 1 Score" : "امتیاز دور ۱"), selector: (row) => row.round1 ?? "-", sortable: true, width: "160px" },
    { name: (language === "en" ? "Round 2 Score" : "امتیاز دور ۲"), selector: (row) => row.round2 ?? "-", sortable: true, width: "160px" },
    { name: (language === "en" ? "Round 3 Score" : "امتیاز دور ۳"), selector: (row) => row.round3 ?? "-", sortable: true, width: "160px" },
    { name: (language === "en" ? "Round 4 Score" : "امتیاز دور ۴"), selector: (row) => row.round4 ?? "-", sortable: true, width: "160px" },
    { name: (language === "en" ? "Round 5 Score" : "امتیاز دور ۵"), selector: (row) => row.round5 ?? "-", sortable: true, width: "160px" },
    { name: (language === "en" ? "Test Time" : "تاریخ آزمون"), selector: (row) => row.test_time, sortable: true, width: "250px" },
    {
      name: (language === "en" ? "Approved" : "تایید شده"),
      selector: row =>
        row.approved === "Yes"
          ? (language === "en" ? "Yes" : "بله")
          : (language === "en" ? "No" : "خیر"),
      sortable: true,
      width: "150px"
    },
    { name: (language === "en" ? "Total Score" : "مجموع امتیاز"), selector: (row) => row.total_score, sortable: true, width: "160px" },
  ];

  const [adminInfo, setAdminInfo] = useState({ username: '', profile_photo: '' });
  const [filters, setFilters] = useState({ username: "", test_number: "", test_time: "" });
  const [data, setData] = useState([]);
  const [userOptions, setUserOptions] = useState([]);

  // fetch admin info
  useEffect(() => {
    const fetchAdminInfo = async () => {
      try {
        const res = await fetch(`/api/admin/current-user`, {
          credentials: 'include'
        });
        const json = await res.json();
        if (res.ok) {
            setAdminInfo(json);
        }
      } catch (err) {
        console.error(language === "en" ? "Failed to fetch admin info:" : "خطا در واکشی اطلاعات ادمین", err);
      }
    };

    fetchAdminInfo();
  }, [language]);

  // fetch and group user results
  const fetchData = useCallback(async () => {
    try {
      let testTime = filters.test_time;

      // Convert from "2024-02-05T17:30" to full ISO if needed
      if (testTime && !testTime.includes("seconds")) {
        testTime = testTime + ":00"; // adds seconds
      }

      const formattedFilters = {
        ...filters,
        test_time: testTime || ""
      };

      const query = new URLSearchParams(formattedFilters).toString();
      const response = await fetch(`/api/admin/user-results?${query}`);
      if (response.ok) {
        const result = await response.json();
        // group by username + test_number
        const grouped = {};
        result.forEach(item => {
          const key = `${item.username}-${item.test_number}`;
          if (!grouped[key]) {
            grouped[key] = {
              username: item.username,
              age: item.age,
              gender: item.sex,
              test_number: item.test_number,
              test_time: new Date(item.test_time).toLocaleString(), // initialize with first
              approved: item.approved,
              total_score: item.total_score,
            };
          }
          // assign round score
          grouped[key][`round${item.round_number}`] = item.score;

          // update test_time always to the latest round
          grouped[key].test_time = new Date(item.test_time).toLocaleString();
        });

        setData(Object.values(grouped));

        // user filter options
        const uniqueUsers = [...new Set(result.map(item => item.username))];
        setUserOptions(uniqueUsers);
      }
    } catch (err) {
      console.error(language === "en" ? "Fetch error:" : "خطا در واکشی اطلاعات", err);
    }
  }, [filters, language]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    });
  };

  const handleReset = () => {
    setFilters({ username: "", test_number: "", test_time: "" });
  };

  // Handle Profile Picture
  const handlePhotoChange = async (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('photo', file);
    formData.append('user_id', adminInfo.id);

    const res = await fetch('/api/upload-profile-photo', {
      method: 'POST',
      body: formData
    });

    if (res.ok) {
      const result = await res.json();
      setAdminInfo(prev => ({ ...prev, profile_photo: result.photo }));
    } else {
      alert(language === "en" ? "Upload failed." : "خطا در آپلود!");
    }
  };

  return (
    <div className="container-fluid profile">
      <div className="row">
        <div
          className="col-1 sidebar px-0 pt-5 pb-5"
          style={{ display: "flex", flexDirection: "column", alignItems: "center" }}
        >
          <ProfileImageUpload
            onChange={handlePhotoChange}
            source={adminInfo.profile_photo
              ? `${BASE_URL}/static/profile_photos/${adminInfo.profile_photo}`
              : "../images/profile.png"}
          />
          <h5 className="text-center">
            {language === "en" ? "admin" : "مدیر"}
          </h5>
        </div>
        <div className="col-11 py-5 px-5">
          <div className="px-2 py-5">
            <h3 className="mb-5">
              {language === "en" ? "User Results" : "نتایج کاربران"}
            </h3>
            <form className="d-flex gap-1 mb-1" onSubmit={(e) => e.preventDefault()}>
              <input
                className="form-control"
                name="test_number"
                type="text"
                placeholder={language === "en" ? "Filter by Test Number" : "فیلتر بر اساس شماره آزمون"}
                onChange={handleChange}
                value={filters.test_number}
              />
              <input
                className="form-control"
                name="test_time"
                type="datetime-local"
                onChange={handleChange}
                value={filters.test_time}
              />
              <select
                className="form-control"
                name="username"
                value={filters.username}
                onChange={handleChange}
              >
                <option value="">
                  {language === "en" ? "All Users" : "تمام کاربران"}
                </option>
                {userOptions.map((username, idx) => (
                  <option key={idx} value={username}>
                    {username}
                  </option>
                ))}
              </select>
              <button className="btn btn-primary" onClick={handleReset}>
                {language === "en" ? "Reset" : "حذف فیلترها"}
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
              customStyles={{
                table: {
                    style: {
                    padding: "20px 40px", // overrides the big default padding
                    },
                },
                headCells: {
                    style: {
                    paddingLeft: "8px",
                    paddingRight: "8px",
                    },
                },
                cells: {
                    style: {
                    paddingLeft: "18px",
                    paddingRight: "8px",
                    },
                },
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserResults;
