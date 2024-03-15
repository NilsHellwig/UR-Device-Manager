import { Binoculars, Trash } from "phosphor-react";
import Tooltip from "./Tooltip";
import { useContext } from "react";
import { BACKEND_URL, MAX_LENGTH_DESCRIPTION } from "../Constants";
import { getProfileColor } from "../utils/getProfileColor";
import CurrentUserContext from "../hooks/CurrentUserContext";
import { deviceTypeGerman } from "../utils/getDeviceTypeGerman";

const DeviceCard = ({ title, serialnumber, description, owner, id, setDevices, devices, setCurrentPage, deviceType }) => {
  const { userData, setUserData } = useContext(CurrentUserContext);
  const showDetailView = () => {
    setUserData({ ...userData, device_to_edit_id: id });
    setCurrentPage("single-device-page");
  };
  const access_token = localStorage.getItem("access_token");

  const deleteDevice = (e) => {
    console.log("delete device", id);
    fetch(BACKEND_URL + "/devices/" + id, {
      method: "DELETE",
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
      })
      .then(() => {
        // remove device from list
        setDevices(devices.filter((device) => device[0].device_id !== id));
      })
      .catch((error) => {
        console.log(error);
      });
  };

  return (
    <div className="device-card">
      <div className="device-card-main">
        <div className="device-card-title">{title}</div>
        <div className="device-card-serial">
          <div className="device-card-serial-card">
            <span className="device-card-serial-card-text">{deviceTypeGerman[deviceType]}</span>
            <div className="blue-line"></div>
            <span className="device-card-serial-card-text">Serial No.: {serialnumber}</span>
          </div>
        </div>
        {description !== null && <p className="device-card-description">{description.length > MAX_LENGTH_DESCRIPTION ? description.substr(0, MAX_LENGTH_DESCRIPTION) + "..." : description}</p>}
      </div>
      <div className="device-card-footer">
        <div className="device-card-grey-line"></div>
        <div className="device-card-footer-inner">
          <div className="device-card-owner">
            <div className="device-card-profile-img" style={{ backgroundColor: getProfileColor(owner) }}>
              {owner.substr(0, 2).toUpperCase()}
            </div>
            <div className="device-card-text">
              <div className="device-card-owener-username">{owner}</div>
              <div className="device-card-owner-description">AKTUELLER BESITZER</div>
            </div>
          </div>
          <div className="device-card-buttons">
            {userData.has_admin_privileges && (
              <Tooltip text="Löschen" position="bottom">
                <div
                  className="square-button square-button-delete"
                  onClick={(e) => {
                    deleteDevice(e);
                  }}
                >
                  <Trash size={20} color="#FF2222" weight="fill" />
                </div>
              </Tooltip>
            )}
            <Tooltip text="Mehr Anzeigen" position="bottom">
              <div className="square-button" onClick={showDetailView}>
                <Binoculars size={20} color="#000000" weight="fill" />
              </div>
            </Tooltip>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DeviceCard;
