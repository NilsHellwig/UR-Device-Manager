import "./style.css";
import { SignOut } from "phosphor-react";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import SingleDevice from "./pages/SingleDevice";
import AddNewDeviceView from "./pages/AddNewDevice";
import { useState, useEffect } from "react";
import CurrentUserContext from "./hooks/CurrentUserContext";
import { BACKEND_URL } from "./Constants";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { showToast } from "./utils/showToast";

function App() {
  const [currentPage, setCurrentPage] = useState("login-page");
  const [userData, setUserData] = useState({ rz_username: "", full_name: "", has_admin_privileges: false, organisation_unit: "" });

  // check if token is available
  const access_token = localStorage.getItem("access_token");

  const onLogout = () => {
    localStorage.removeItem("access_token");
    showToast("Erfolgreich ausgeloggt!");
    setCurrentPage("login-page");
  };

  useEffect(() => {
    if (access_token !== null) {
      fetch(BACKEND_URL + "/check_auth", {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: "Bearer " + access_token,
        },
      })
        .then((response) => {
          if (!response.ok) {
            return response.json().then((json) => {
              // if the token stored in localstorage isn't valid anymore, we can remove it
              localStorage.removeItem("access_token");
              throw new Error(`Error: ${response.status}`);
            });
          }
          return response.json();
        })
        .then((data) => {
          setUserData({ ...userData, rz_username: data.rz_username, has_admin_privileges: data.has_admin_privileges, full_name: data.full_name, organisation_unit: data.organisation_unit });
          setCurrentPage("dashboard-page");
        })
        .catch((error) => {
          console.log(error);
        });
    }
    // eslint-disable-next-line
  }, []);

  return (
    <div className="App">
      <header>
        <h1>Device Manager</h1>
        {currentPage !== "login-page" && (
          <div className="logout-button" onClick={onLogout}>
            <div className="logout-button-text">Ausloggen</div>
            <SignOut size={16} color="#3e0000" weight="fill" />
          </div>
        )}
      </header>
      <CurrentUserContext.Provider value={{ userData, setUserData }}>
        <main>
          {currentPage === "dashboard-page" && <Dashboard setCurrentPage={setCurrentPage} />}
          {currentPage === "login-page" && <Login setCurrentPage={setCurrentPage} />}
          {currentPage === "single-device-page" && <SingleDevice setCurrentPage={setCurrentPage} />}
          {currentPage === "add-new-device-page" && <AddNewDeviceView setCurrentPage={setCurrentPage} />}
        </main>
      </CurrentUserContext.Provider>
      <ToastContainer />
    </div>
  );
}

export default App;
