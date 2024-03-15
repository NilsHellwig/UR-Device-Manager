import { CaretCircleDown, Pen } from "phosphor-react";
import { useState, useRef } from "react";
import { BACKEND_URL } from "../Constants";
import { getRoomCodes } from "../utils/getRoomCodes";
import { AutoComplete } from "@react-md/autocomplete";

const EditableTextField = ({ fieldValueSize, editable, label, fieldKey, deviceData, setDeviceData, dataType, databaseTable, setOwnerHistory, ownerHistory, locationHistory, setLocationHistory }) => {
  const inputField = useRef();
  const roomInputRef = useRef();
  const [errorText, setErrorText] = useState("");
  const [showSave, setShowSave] = useState(false);
  const access_token = localStorage.getItem("access_token");

  const editValue = () => {
    if (fieldKey === "room_code") {
      roomInputRef.current.focus();
    } else {
      inputField.disabled = false;
      inputField.current.focus();
    }
  };

  const saveChanges = () => {
    if (databaseTable === "purchasing_information" || databaseTable === "devices") {
      let tableId = "";
      if (databaseTable === "purchasing_information") {
        tableId = deviceData.purchasing_information_id;
      } else {
        tableId = deviceData.device_id;
      }

      let body_object = { [fieldKey]: deviceData[fieldKey] };

      // check if datetime key. if it's a datetime key, we need to make sure
      // it will be converted to a unix timecode.
      if (dataType === "datetime-local" || dataType === "date") {
        body_object[fieldKey] = new Date(body_object[fieldKey]).getTime() / 1000;
      }

      let body = JSON.stringify(body_object);
      fetch(BACKEND_URL + "/" + databaseTable + "/" + tableId, {
        method: "PUT",
        headers: {
          accept: "application/json",
          "Content-Type": "application/json",
          Authorization: "Bearer " + access_token,
        },
        body: body,
      })
        .then((response) => {
          if (!response.ok) {
            return response.json().then((json) => {
              setErrorText("Fehler: " + json.detail);
              throw new Error(`Error: ${response.status}`);
            });
          }
          return response.json();
        })
        .then((data) => {
          setShowSave(false);
          setErrorText("");
        })
        .catch((error) => {
          console.log(error);
        });
    }
    if (databaseTable === "location_transactions" || databaseTable === "owner_transactions") {
      let bodyObject = {};
      if (databaseTable === "location_transactions") {
        bodyObject = { room_code: deviceData["room_code"], device_id: deviceData["device_id"] };
      } else {
        bodyObject = { rz_username: deviceData["rz_username"], device_id: deviceData["device_id"] };
      }

      let body = JSON.stringify(bodyObject);
      fetch(BACKEND_URL + "/" + databaseTable, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + access_token,
        },
        body: body,
      })
        .then((response) => {
          if (!response.ok) {
            return response.json().then((json) => {
              console.log(response);
              setErrorText("Fehler: " + json.detail);
            });
          }
          return response.json();
        })
        .then((data) => {
          if (!(data.ok === false)) {
            console.log(data);
            if (databaseTable === "owner_transactions") {
              setOwnerHistory([data, ...ownerHistory]);
            }
            if (databaseTable === "location_transactions") {
              setLocationHistory([data, ...locationHistory]);
            }
            setShowSave(false);
            setErrorText("");
          }
        })
        .catch((error) => {
          console.log(error);
        });
    }
  };

  const onInputValueChange = (e) => {
    setShowSave(true);
    setDeviceData({ ...deviceData, [fieldKey]: e.target.value });
  };

  return (
    <div className="editable-text-field">
      {fieldKey === "room_code" ? (
        <AutoComplete
          style={{pointerEvents: "none"}}
          ref={roomInputRef}
          id="search-rooms"
          inputClassName="search-rooms-edit"
          placeholder="Raumnummer suchen..."
          data={getRoomCodes()}
          value={deviceData[fieldKey]}
          onChange={(e) => {
            onInputValueChange(e);
          }}
          onAutoComplete={(clickedItem) => {
            console.log("enter");
            setDeviceData({ ...deviceData, [fieldKey]: clickedItem.value });
          }}
        />
      ) : fieldKey === "device_type" ? (
        <div className="edit-dropdown-menu">
          <select
            className={"edit-dropdown" + (!editable ? " edit-dropdown-no-pointer" : "")}
            value={deviceData[fieldKey]}
            onChange={(e) => {
              onInputValueChange(e);
            }}
          >
            <option value="projektor">Projektor</option>
            <option value="computer">Computer</option>
            <option value="laptop">Laptop</option>
            <option value="mikrofon">Mikrofon</option>
            <option value="whiteboard">Whiteboard</option>
            <option value="unbekannt">Unbekannt</option>
          </select>
          <CaretCircleDown className="arrow-down" size={16} color="#000000" weight="fill" />
        </div>
      ) : (
        <input
          readOnly={!editable}
          ref={inputField}
          value={deviceData[fieldKey]}
          onChange={(e) => onInputValueChange(e)}
          type={dataType}
          className="editable-text-field-input"
          style={{ fontSize: fieldValueSize }}
        ></input>
      )}
      <div className="editable-text-field-footer">
        <div className="editable-text-field-title">{label}</div>
        {editable && (
          <div className="editable-text-field-edit" onClick={editValue}>
            <Pen size={12} color="#000000" weight="fill" />
          </div>
        )}
        {showSave && (
          <div className="save-changes-button" onClick={saveChanges}>
            Änderung speichern
          </div>
        )}
        <div className="edit-error-text">{errorText}</div>
      </div>
    </div>
  );
};

export default EditableTextField;
