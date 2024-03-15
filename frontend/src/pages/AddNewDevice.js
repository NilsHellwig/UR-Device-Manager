import { XCircle, Plus, CaretCircleDown, ArrowSquareLeft } from "phosphor-react";
import { useState, useRef } from "react";
import { BACKEND_URL } from "../Constants";
import { getRoomCodes } from "../utils/getRoomCodes";
import { AutoComplete } from "@react-md/autocomplete";
import { confirmAlert } from "react-confirm-alert";
import "react-confirm-alert/src/react-confirm-alert.css";
import { showToast } from "../utils/showToast";

const timezoneOffset = new Date().getTimezoneOffset() * 60;

const AddNewDeviceView = ({ setCurrentPage }) => {
  const uploadInputRef = useRef(null);
  const [title, setTitle] = useState("");

  const currentTime = new Date() + timezoneOffset
  const [warrantyDate, setWarrantyDate] = useState(new Date(currentTime).toISOString().slice(0,16));
  const [purchaseDate, setPurchaseDate] = useState(new Date(currentTime).toISOString().slice(0,16));

  const [deviceType, setDeviceType] = useState("unbekannt");
  const [serialNumber, setSerialNumber] = useState("");
  const [costCentre, setCostCentre] = useState("");
  const [price, setPrice] = useState("");
  const [accessories, setaccessories] = useState("");
  const [RZUsernameBuyer, setRZUsernameBuyer] = useState("");
  const [RZUsernameOwner, setRZUsernameOwner] = useState("");
  const [seller, setSeller] = useState("");
  const [selectedRoom, setSelectedRoom] = useState("");
  const [description, setDescription] = useState("");
  const [errorText, setErrorText] = useState("");
  const [deviceImage, setDeviceImage] = useState(null);
  const [previewURLImage, setPreviewURLImage] = useState(null);
  const [imageAsBase64, setImageAsBase64] = useState(null);

  const access_token = localStorage.getItem("access_token");

  const onCancelCreateDeviceForm = () => {
    confirmAlert({
      title: "Formular Schließen?",
      message: "Möchten Sie wirklich das Formular schließen? Eingaben werden nicht gespeichert!",
      buttons: [
        {
          label: "Bestätigen",
          onClick: () => {
            setCurrentPage("dashboard-page");
          },
        },
        {
          label: "Abbrechen",
        },
      ],
    });
  };

  const onAddDevice = () => {
    let body = {
      title: title,
      device_type: deviceType,
      description: description,
      accessories: accessories,
      serial_number: serialNumber,
      rz_username_buyer: RZUsernameBuyer,
      rz_username_owner: RZUsernameOwner,
      room_code: selectedRoom,
      cost_centre: parseInt(costCentre),
      seller: seller,
      timestamp_warranty_end: new Date(warrantyDate).getTime() / 1000,
      timestamp_purchase: new Date(purchaseDate).getTime() / 1000,
      price: price,
    };

    if (deviceImage) {
      console.log(imageAsBase64);
      body.uploaded_device_image = imageAsBase64;
    }

    body = JSON.stringify(body);

    fetch(BACKEND_URL + "/devices", {
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
            setErrorText(json.detail);
          });
        }
        return response.json();
      })
      .then((data) => {
        if (data !== undefined) {
          showToast("Neues Gerät wurde gespeichert!");
          setCurrentPage("dashboard-page");
        }
      })
      .catch((error) => {
        console.log(error);
      });
  };

  const onButtonUploadClick = () => {
    uploadInputRef.current.click();
  };

  const onUploadImage = (event) => {
    setDeviceImage(event.target.files[0]);
    setPreviewURLImage(URL.createObjectURL(event.target.files[0]));

    // Source: https://developer.mozilla.org/en-US/docs/Web/API/FileReader/readAsDataURL
    const reader = new FileReader();
    reader.readAsDataURL(event.target.files[0]);
    reader.onload = function () {
      setImageAsBase64(reader.result);
    };
  };

  return (
    <div className="add-new-device-view">
      <div className="top-button-menu">
        <div className="standard-button back-button-create-device" onClick={onCancelCreateDeviceForm}>
          <ArrowSquareLeft size={20} color="#000000" weight="fill" />
          <span>Zurück</span>
        </div>
      </div>
      <h3>Neues Gerät hinzufügen</h3>
      <div className="add-new-device-small-fields">
        <div className="form-field form-field-flexible">
          <span className="form-field-title">
            GERÄTENAMEN <span className="red-star">*</span>
          </span>
          <input
            type={"text"}
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
            }}
            placeholder={"Gerätenamen eingeben..."}
            className="form-field-input"
          ></input>
        </div>
        <div className="form-field form-field-flexible">
          <span className="form-field-title">
            GERÄTETYP <span className="red-star">*</span>
          </span>
          <div className="dropdown-menu">
            <select
              className="form-field-input dropdown-menu-selector"
              value={deviceType}
              onChange={(e) => {
                setDeviceType(e.target.value);
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
        </div>
        <div className="form-field form-field-flexible">
          <span className="form-field-title">
            SERIENNUMMER <span className="red-star">*</span>
          </span>
          <input
            value={serialNumber}
            onChange={(e) => {
              setSerialNumber(e.target.value);
            }}
            type={"text"}
            placeholder={"Seriennummer eingeben..."}
            className="form-field-input"
          ></input>
        </div>
        <div className="form-field form-field-flexible">
          <span className="form-field-title">ACCESSORIES</span>
          <input
            value={accessories}
            onChange={(e) => {
              setaccessories(e.target.value);
            }}
            type={"text"}
            placeholder={"Accessories eingeben..."}
            className="form-field-input"
          ></input>
        </div>
        <div className="form-field form-field-flexible">
          <span className="form-field-title">
            RZ-NUTZERNAME DES KÄUFERS <span className="red-star">*</span>
          </span>
          <input
            value={RZUsernameBuyer}
            onChange={(e) => {
              setRZUsernameBuyer(e.target.value);
            }}
            type={"text"}
            placeholder={"RZ-Nutzername des Käufers eingeben..."}
            className="form-field-input"
          ></input>
        </div>
        <div className="form-field form-field-flexible">
          <span className="form-field-title">
            RZ-NUTZERNAME DES AKTUELLEN BESITZERS <span className="red-star">*</span>
          </span>
          <input
            value={RZUsernameOwner}
            onChange={(e) => {
              setRZUsernameOwner(e.target.value);
            }}
            type={"text"}
            placeholder={"RZ-Nutzername des aktuellen Besitzers eingeben..."}
            className="form-field-input"
          ></input>
        </div>
        <div className="form-field form-field-flexible">
          <span className="form-field-title">
            RAUMNUMMER (AKTUELLER STANDORT) <span className="red-star">*</span>
          </span>
          <AutoComplete
            id="search-rooms"
            placeholder="Raumnummer suchen..."
            data={getRoomCodes()}
            value={selectedRoom}
            onChange={(e) => {
              setSelectedRoom(e.target.value);
            }}
            onAutoComplete={(clickedItem) => {
              setSelectedRoom(clickedItem.value);
            }}
            maxLength={5}
            defaultValue={""}
          />
        </div>
        <div className="form-field form-field-flexible">
          <span className="form-field-title">
            GARANTIE BIS <span className="red-star">*</span>
          </span>
          <input
            value={warrantyDate}
            onChange={(e) => {
              setWarrantyDate(e.target.value);
            }}
            type="date"
            className="form-field-input"
          />
        </div>
        <div className="form-field form-field-flexible">
          <span className="form-field-title">
            GEKAUFT AM <span className="red-star">*</span>
          </span>
          <input
            value={purchaseDate}
            onChange={(e) => {
              setPurchaseDate(e.target.value);
            }}
            type="datetime-local"
            className="form-field-input"
          />
        </div>
        <div className="form-field form-field-flexible">
          <span className="form-field-title">
            KOSTENSTELLE <span className="red-star">*</span>
          </span>
          <input
            value={costCentre}
            onChange={(e) => {
              setCostCentre(e.target.value);
            }}
            type={"number"}
            placeholder={"Kostenstelle eingeben..."}
            className="form-field-input"
          ></input>
        </div>
        <div className="form-field form-field-flexible">
          <span className="form-field-title">
            EINKAUFSPREIS <span className="red-star">*</span>
          </span>
          <input
            value={price}
            onChange={(e) => {
              setPrice(e.target.value);
            }}
            type={"text"}
            placeholder={"Einkaufspreis eingeben..."}
            className="form-field-input"
          ></input>
        </div>
        <div className="form-field form-field-flexible">
          <span className="form-field-title">
            VERKÄUFER <span className="red-star">*</span>
          </span>
          <input
            value={seller}
            onChange={(e) => {
              setSeller(e.target.value);
            }}
            type={"text"}
            placeholder={"Verkäufer eingeben..."}
            className="form-field-input"
          ></input>
        </div>
      </div>
      <div className="upload-image-area">
        <div className="form-field form-field-flexible">
          <span className="form-field-title">
            FOTOGRAFIE DES GERÄTS<span className="red-star"></span>
          </span>
          <div className="upload-image-container">
            <div className="upload-image-button" onClick={onButtonUploadClick}>
              Bild Hochladen
            </div>
            <span className="upload-image-file-name">{deviceImage && deviceImage.name}</span>
          </div>
          <input
            ref={uploadInputRef}
            style={{ display: "none" }}
            type="file"
            accept=".jpg, .png"
            onChange={(e) => {
              onUploadImage(e);
            }}
          />
          {previewURLImage && <img className="uploaded-image-preview" src={previewURLImage} alt="Preview" />}
        </div>
      </div>
      <div className="add-new-device-textareas">
        <div className="form-field form-field-flexible">
          <span className="form-field-title">BESCHREIBUNG</span>
          <textarea
            value={description}
            onChange={(e) => {
              setDescription(e.target.value);
            }}
            rows={5}
            placeholder={"Beschreibung eingeben..."}
            className="form-field-input"
          ></textarea>
        </div>
      </div>
      <p className="error-text">
        {errorText !== "" && "Fehler:"} {errorText}
      </p>
      <div className="add-new-device-actions">
        <div className="add-new-device-cancel" onClick={onCancelCreateDeviceForm}>
          <span>Abbrechen</span>
          <XCircle size={20} color="#3e0000" weight="fill" />
        </div>
        <div className="add-new-device-add" onClick={onAddDevice}>
          <span>Hinzufügen</span>
          <Plus size={20} color="#ffffff" weight="fill" />
        </div>
      </div>
      <p className="red-star-description">* Pflichtfelder</p>
    </div>
  );
};

export default AddNewDeviceView;
