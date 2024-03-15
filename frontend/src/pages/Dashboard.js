import { Download, Upload, Plus, Buildings } from "phosphor-react";
import Tooltip from "../components/Tooltip";
import { useContext, useEffect, useState } from "react";
import CurrentUserContext from "../hooks/CurrentUserContext";
import DeviceCard from "../components/DeviceCard";
import { getProfileColor } from "../utils/getProfileColor";
import { BACKEND_URL } from "../Constants";

const Dashboard = ({ setCurrentPage }) => {
  const { userData, setUserData } = useContext(CurrentUserContext);
  const [devices, setDevices] = useState([]);
  const [databaseActionErrorText, setDatabaseActionErrorText] = useState("");
  const access_token = localStorage.getItem("access_token");

  const initProfile = () => {
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
            throw new Error(`Error: ${response.status}`);
          });
        }
        return response.json();
      })
      .then((data) => {
        setUserData({ ...userData, rz_username: data.rz_username, has_admin_privileges: data.has_admin_privileges, full_name: data.full_name, organisation_unit: data.organisation_unit });
      })
      .catch((error) => {
        console.log(error);
      });
  };

  const initDevices = () => {
    fetch(BACKEND_URL + "/devices?show_owners=true", {
      method: "GET",
      headers: {
        Accept: "application/json",
        Authorization: "Bearer " + access_token,
      },
    })
      .then((response) => {
        if (!response.ok) {
          return response.json().then((json) => {
            throw new Error(`Error: ${response.status}`);
          });
        }
        return response.json();
      })
      .then((data) => {
        console.log("fetched device data: ", data);
        setDevices(data);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  useEffect(() => {
    initProfile();
    initDevices();
    // eslint-disable-next-line
  }, []);

  const onClickDownloadJSON = () => {
    fetch(BACKEND_URL + "/export", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + access_token,
      },
    })
      .then((response) => {
        if (!response.ok) {
          return response.json().then((json) => {
            throw new Error(`Error: ${response.status}`);
          });
        }
        return response.json();
      })
      .then((data) => {
        let downloadLink = document.createElement("a");
        downloadLink.href = URL.createObjectURL(new Blob([JSON.stringify(data)], { type: "application/json" }));
        // Source: https://www.w3schools.com/tags/att_a_download.asp
        downloadLink.download = "database.json";
        downloadLink.click();
      })
      .catch((error) => {
        console.log(error);
      });
  };

  const onClickUploadJSON = () => {
    document.querySelector(".json-upload-dummy").click();
  };

  const onUploadDatabaseChange = (e) => {
    const fileReader = new FileReader();
    try {
      // Source: https://developer.mozilla.org/en-US/docs/Web/API/FileReader/readAsText
      fileReader.readAsText(e.target.files[0], "UTF-8");
      fileReader.onload = (e) => {
        let body = e.target.result;
        fetch(BACKEND_URL + "/import", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + access_token,
          },
          body: body,
        })
          .then((response) => {
            if (!response.ok) {
              setDatabaseActionErrorText("Daten sind bereits in der Datenbank oder nicht korrekt formatiert.");
              throw new Error(`Error: ${response.status}`);
            }
            return response.json();
          })
          .then((data) => {
            window.location.reload();
            setDatabaseActionErrorText("");
            console.log(data);
          })
          .catch((error) => {
            console.log(error);
          });
      };
      // Reset database json upload input
      e.target.value = "";
    } catch (error) {}
  };

  const onAddNewDevice = () => {
    setCurrentPage("add-new-device-page");
  };

  return (
    <div className="dashboard">
      <div className="section">
        <h3>Ihr Profil</h3>
        <div className="profile">
          <div className="user-img" style={{ backgroundColor: getProfileColor(userData.rz_username) }}>
            {userData.rz_username.substr(0, 2).toUpperCase()}
          </div>
          <div className="user-info">
            <div className="username">
              <span>
                {userData.rz_username} {userData.full_name.length > 0 ? "(" + userData.full_name + ")" : ""}
              </span>
              <Tooltip text={userData.organisation_unit} position="bottom">
                <div className="organisation-type">
                  <Buildings size={14} color="#ffffff" weight="fill" />
                </div>
              </Tooltip>
            </div>
            <div className="type-list">
              <div className="user-type">{userData.has_admin_privileges ? "ADMINISTRATOR" : "STANDARD NUTZER"}</div>
            </div>
          </div>
        </div>
      </div>
      {userData.has_admin_privileges && (
        <div className="section">
          <h3>Upload / Download der Datenbank</h3>
          <p className="upload-description">
            Sie können die Datenbank austauschen/herunterladen. Bitte beachten Sie, dass <b>alle Einträge gelöscht werden</b>, wenn Sie die Datenbank als .JSON hochladen.
          </p>
          <div className="upload-download-actions">
            <Tooltip text="Herunterladen" position="bottom">
              <div className="square-button" onClick={onClickDownloadJSON}>
                <Download size={24} color="#000000" weight="fill" />
              </div>
            </Tooltip>
            <Tooltip text="Hochladen" position="bottom">
              <div className="square-button" onClick={onClickUploadJSON}>
                <Upload size={24} color="#000000" weight="fill" />
              </div>
            </Tooltip>
            <p className="error-text-database-actions">{databaseActionErrorText}</p>
          </div>
        </div>
      )}

      <input type="file" style={{ display: "none" }} className="json-upload-dummy" accept=".json" onChange={onUploadDatabaseChange} />
      <div className="section">
        <div className="all-devices-header">
          <h2>Alle Geräte</h2>
          <div className="add-device-button" onClick={onAddNewDevice}>
            <div className="add-device-button-text">Neues Gerät hinzufügen</div>
            <Plus size={18} color="#00570e" weight="fill" />
          </div>
        </div>
        <div className="devices-list">
          {devices.map((device) => {
            return (
              <DeviceCard
                key={device[0].device_id}
                id={device[0].device_id}
                title={device[0].title}
                serialnumber={device[0].serial_number}
                owner={device[1].rz_username}
                description={device[0].description}
                setDevices={setDevices}
                devices={devices}
                setCurrentPage={setCurrentPage}
                deviceType={device[0].device_type}
              />
            );
          })}
          {devices.length === 0 && (
            <p className="hint-no-devices">
              Es sind <b>keine</b> Geräte in der Datenbank verfügbar.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
