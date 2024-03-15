import { ArrowSquareLeft, MapPin, UserCircle } from "phosphor-react";
import { useEffect } from "react";
import { useContext, useState } from "react";
import DeviceImageCard from "../components/DeviceImageCard";
import EditableTextField from "../components/EditableTextField";
import { BACKEND_URL } from "../Constants";
import CurrentUserContext from "../hooks/CurrentUserContext";

const SingleDevice = ({ setCurrentPage }) => {
  const [ownerHistory, setOwnerHistory] = useState([]);
  const [locationHistory, setLocationHistory] = useState([]);
  const { userData } = useContext(CurrentUserContext);
  const access_token = localStorage.getItem("access_token");
  const [deviceData, setDeviceData] = useState({
    title: "",
    device_type: "",
    description: "",
    accessories: "",
    serial_number: "",
    rz_username_buyer: "",
    // rz_username is the owner's rz username
    rz_username: "",
    room_code: "",
    price: "",
    timestamp_warranty_end: "",
    timestamp_purchase: "",
    cost_centre: "",
    seller: "",
  });

  const unixCodeToDatetimeString = (unixTimeCode) => {
    return new Date(unixTimeCode * 1000).toISOString().substring(0, 16);
  };

  const unixCodeToDateString = (unixTimeCode) => {
    return new Date(unixTimeCode * 1000).toISOString().substring(0, 10);
  };
  

  const backToDashboard = () => {
    setCurrentPage("dashboard-page");
  };

  useEffect(() => {
    fetch(BACKEND_URL + "/devices/" + userData.device_to_edit_id + "?detailed_data=true", {
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
        // remove device from list
        console.log(data);
        const ownersSorted = data.owners.sort((a, b) => b.timestamp_owner_since - a.timestamp_owner_since);
        setOwnerHistory(ownersSorted);
        const currentOwner = ownersSorted[0];
        const locationsSorted = data.location.sort((a, b) => b.timestamp_located_since - a.timestamp_located_since);
        setLocationHistory(locationsSorted);
        const currentLocation = locationsSorted[0];
        const purchasing_information = data.purchasing_information;
        // Source: https://www.w3schools.com/jsref/jsref_toisostring.asp / https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/getTimezoneOffset
        // As we want to display the timestamp for the user's timestamp, we need to convert it using getTimezoneOffset()
        var timezoneOffset = new Date().getTimezoneOffset() * 60;
        purchasing_information["timestamp_warranty_end"] = unixCodeToDateString(purchasing_information["timestamp_warranty_end"] - timezoneOffset);
        purchasing_information["timestamp_purchase"] = unixCodeToDatetimeString(purchasing_information["timestamp_purchase"] - timezoneOffset);

        setDeviceData({ ...deviceData, ...data.device, ...purchasing_information, ...currentOwner, ...currentLocation });
      })
      .catch((error) => {
        console.log(error);
      });
    // eslint-disable-next-line
  }, []);

  return (
    <div className="single-device-view">
      <div className="back-button" onClick={backToDashboard}>
        <ArrowSquareLeft size={16} color="#000000" weight="fill" />
        <span className="back-button-text">Zurück zum Dashboard</span>
      </div>
      <DeviceImageCard deviceData={deviceData} setDeviceData={setDeviceData} editable={userData.has_admin_privileges} />
      <h2 style={{ marginTop: "2rem" }}>Angaben zum Gerät</h2>
      <div className="line"></div>
      <div className="single-device-list">
        <div className="single-device-title">
          <EditableTextField
            fieldValueSize={"16px"}
            editable={userData.has_admin_privileges}
            label={"Gerätenamen"}
            fieldKey="title"
            deviceData={deviceData}
            setDeviceData={setDeviceData}
            databaseTable="devices"
          />
        </div>
        <EditableTextField
          fieldValueSize={"16px"}
          editable={userData.has_admin_privileges}
          label={"Gerätetyp"}
          fieldKey="device_type"
          deviceData={deviceData}
          setDeviceData={setDeviceData}
          dataType="text"
          databaseTable="devices"
        />
        <EditableTextField
          fieldValueSize={"16px"}
          editable={userData.has_admin_privileges}
          label={"Beschreibung"}
          fieldKey="description"
          deviceData={deviceData}
          setDeviceData={setDeviceData}
          dataType="text"
          databaseTable="devices"
        />
        <EditableTextField
          fieldValueSize={"16px"}
          editable={userData.has_admin_privileges}
          label={"Accessories"}
          fieldKey="accessories"
          deviceData={deviceData}
          setDeviceData={setDeviceData}
          dataType="text"
          databaseTable="devices"
        />
        <EditableTextField
          fieldValueSize={"16px"}
          editable={userData.has_admin_privileges}
          label={"Seriennummer"}
          fieldKey="serial_number"
          deviceData={deviceData}
          setDeviceData={setDeviceData}
          dataType="text"
          databaseTable="devices"
        />
        <EditableTextField
          fieldValueSize={"16px"}
          editable={userData.has_admin_privileges}
          label={"RZ-Nutzername des Käufers"}
          fieldKey="rz_username_buyer"
          deviceData={deviceData}
          setDeviceData={setDeviceData}
          dataType="text"
          databaseTable="devices"
        />
        <EditableTextField
          fieldValueSize={"16px"}
          editable={true}
          label={"RZ-Nutzername des aktuellen Besitzers"}
          fieldKey="rz_username"
          deviceData={deviceData}
          setDeviceData={setDeviceData}
          dataType="text"
          databaseTable="owner_transactions"
          ownerHistory={ownerHistory}
          setOwnerHistory={setOwnerHistory}
        />
        <EditableTextField
          fieldValueSize={"16px"}
          editable={true}
          label={"Raumcode (Aktueller Standort)"}
          fieldKey="room_code"
          deviceData={deviceData}
          setDeviceData={setDeviceData}
          dataType="text"
          databaseTable="location_transactions"
          setLocationHistory={setLocationHistory}
          locationHistory={locationHistory}
        />
        <EditableTextField
          fieldValueSize={"16px"}
          editable={userData.has_admin_privileges}
          label={"Einkaufspreis"}
          fieldKey="price"
          deviceData={deviceData}
          setDeviceData={setDeviceData}
          dataType="text"
          databaseTable="purchasing_information"
        />
        <EditableTextField
          fieldValueSize={"16px"}
          editable={userData.has_admin_privileges}
          label={"Garantie bis"}
          fieldKey="timestamp_warranty_end"
          deviceData={deviceData}
          setDeviceData={setDeviceData}
          dataType="date"
          databaseTable="purchasing_information"
        />
        <EditableTextField
          fieldValueSize={"16px"}
          editable={userData.has_admin_privileges}
          label={"Zeitpunkt des Kaufes"}
          fieldKey="timestamp_purchase"
          deviceData={deviceData}
          setDeviceData={setDeviceData}
          dataType="datetime-local"
          databaseTable="purchasing_information"
        />
        <EditableTextField
          fieldValueSize={"16px"}
          editable={userData.has_admin_privileges}
          label={"Kostenstelle"}
          fieldKey="cost_centre"
          deviceData={deviceData}
          setDeviceData={setDeviceData}
          dataType="number"
          databaseTable="purchasing_information"
        />
        <EditableTextField
          fieldValueSize={"16px"}
          editable={userData.has_admin_privileges}
          label={"Verkäufer"}
          fieldKey="seller"
          deviceData={deviceData}
          setDeviceData={setDeviceData}
          dataType="text"
          databaseTable="purchasing_information"
        />
      </div>
      {userData.has_admin_privileges && (
        <div>
          <h2>Verlauf</h2>
          <div className="line"></div>
          <div className="history-container">
            <h3>Besitzer</h3>
            <div className="history-list">
              {ownerHistory.map((device) => {
                return (
                  <div key={device.owner_transaction_id} className="history-card">
                    <div>
                      <UserCircle size={24} weight="fill" />
                    </div>
                    <div>
                      <div className="history-title">{device.rz_username}</div>
                      <div className="history-description">Besitzer ab: {unixCodeToDatetimeString(device.timestamp_owner_since)}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
          <div className="history-container">
            <h3>Standort des Geräts</h3>
            <div className="history-list">
              {locationHistory.map((location) => {
                return (
                  <div key={location.location_transaction_id} className="history-card">
                    <div>
                      <MapPin size={24} weight="fill" />
                    </div>
                    <div>
                      <div className="history-title">{location.room_code}</div>
                      <div className="history-description">Platziert seit: {unixCodeToDatetimeString(location.timestamp_located_since)}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SingleDevice;
