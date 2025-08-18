import React from "react";
import DataTable from "react-data-table-component";
import { useState, useEffect, useCallback } from "react";
import { useLanguage } from './LanguageContext';

const BASE_URL = process.env.REACT_APP_API_URL;

const UserResults = () => {
    const { language } = useLanguage();
    const columns = [
        { name: (language === "en" ? "Username" : "نام کاربری" ), selector: (row) => row.username, sortable: true, width: "200px" },
        { name: (language === "en" ? "Age" : "سن" ), selector: (row) => row.age, sortable: true, width: "100px" },
        { name: (language === "en" ? "Sex" : "جنسیت" ), selector: (row) => row.sex, sortable: true, width: "100px" },
        { name: (language === "en" ? "Test Number" : "شماره آزمون" ), selector: (row) => row.test_number, sortable: true, width: "150px" },
        { name: (language === "en" ? "Test Round" : "شماره دور" ), selector: (row) => row.round_number, sortable: true, width: "150px" },
        { name: (language === "en" ? "Score" : "امتیاز" ), selector: (row) => row.score, sortable: true, width: "150px" },
        { name: (language === "en" ? "Test Time" : "تاریخ آزمون" ), selector: (row) => row.test_time, sortable: true, width: "250px" },
        { name: (language === "en" ? "Approved" : "تایید شده" ), selector: (row) => row.approved, sortable: true, width: "150px" },
        { name: (language === "en" ? "Total Score" : "مجموع امتیاز" ), selector: (row) => row.total_score, sortable: true, width: "200px" },
    ];
    const [adminInfo, setAdminInfo] = useState({ username: '', profile_photo: '' });

    const [filters, setFilters] = useState({
        username: "",
        test_number: "",
        test_time: ""
    });
      
    const [data, setData] = useState([]);
    const [userOptions, setUserOptions] = useState([]);

    
    useEffect(() => {
        const fetchAdminInfo = async () => {
            try {
                const res = await fetch(`/api/admin/current-user`, {
                    credentials: 'include'
                });
                const json = await res.json();
                if (res.ok) {
                    setAdminInfo(json);
                    console.log(json);
                }
            } catch (err) {
                console.error(language === "en " ? "Failed to fetch admin info:" : "خطا در واکشی اطلاعات ادمین", err);
            }
        };

        fetchAdminInfo();
    }, [language]);

    const fetchData = useCallback(async () => {
        try {
          let testTime = filters.test_time;
      
          // Convert from "2024-02-05T17:30" to full ISO if needed
          if (testTime && !testTime.includes("seconds")) {
            testTime = testTime + ":00"; // adds seconds, becomes "2024-02-05T17:30:00"
          }
      
          const formattedFilters = {
            ...filters,
            test_time: testTime || ""
          };
      
          const query = new URLSearchParams(formattedFilters).toString();
          const response = await fetch(`/api/admin/user-results?${query}`);
          if (response.ok) {
            const result = await response.json();
      
            // Format the date to readable version for display
            const formattedData = result.map((item) => ({
              ...item,
              test_time: item.test_time
                ? new Date(item.test_time).toLocaleString()
                : "N/A"
            }));
      
            setData(formattedData);
      
            const uniqueUsers = [...new Set(result.map(item => item.username))];
            setUserOptions(uniqueUsers);
          }
        } catch (err) {
          console.error(language === "en " ? "Fetch error:" : "خطا در واکشی اطلاعات", err);
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
      
    return (
        <div className="container-fluid profile">
            <div className="row">
                <div className="col-1 sidebar px-0 pt-5 pb-5" style={{
      display: "flex", flexDirection: "column", alignItems: "center"}}>
                <img src={
                    adminInfo.profile_photo
                    ? `${BASE_URL}/static/profile_photos/${adminInfo.profile_photo}`
                    : "./images/profile.png"
                } 
                className="rounded-circle"
                style={{ 
                    width: "80px", 
                    height: "80px", 
                    objectFit: "cover", 
                    border: "3px solid #5971d1",
                }}
                alt={language === "en " ? "profile" : "پروفایل" }
                />

                <h5 className="text-center">
                    {language === "en" ? "admin" : "مدیر" }
                </h5>
                </div>
                <div className="col-11 py-5 px-5">
                <div className="px-2 py-5">
                    <h3 className="mb-5">
                        {language === "en" ? "User Results" : "نتایج کاربران" }
                    </h3>
                    <form className="d-flex gap-1 mb-1" onSubmit={(e) => e.preventDefault()}>
                    <input
                        className="form-control"
                        name="test_number"
                        type="text"
                        placeholder={language === "en " ? "Filter by Test Number" : "فیلتر بر اساس شماره آزمون" }
                        onChange={handleChange}
                        value={filters.test_number}
                    />
                    <input
                        className="form-control"
                        name="test_time"
                        type="datetime-local"
                        placeholder="Filter by Test Time (yyyy-mm-dd hh:mm)"
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
                            {language === "en" ? "All Users" : "تمام کاربران" }
                        </option>
                        {userOptions.map((username, idx) => (
                        <option key={idx} value={username}>
                            {username}
                        </option>
                        ))}
                    </select>
                    <button className="btn btn-primary" onClick={handleReset}>
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
                    />
                </div>
                </div>
            </div>
        </div>
    );
}

export default UserResults;