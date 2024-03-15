import { Upload } from "phosphor-react";
import { useState, useRef } from "react";
import { BACKEND_URL } from "../Constants";

const DeviceImageCard = ({ deviceData, setDeviceData, editable }) => {
  const uploadNewImageRef = useRef(null);
  const [previewURLImage, setPreviewURLImage] = useState("");
  const [imageAsBase64, setImageAsBase64] = useState(null);
  const [showSave, setShowSave] = useState(false);
  const [errorText, setErrorText] = useState("");

  const access_token = localStorage.getItem("access_token");

  const onUploadImage = (event) => {
    const imageFileAsUrl = URL.createObjectURL(event.target.files[0]);
    setPreviewURLImage(imageFileAsUrl);
    setDeviceData({ ...deviceData, image_url: imageFileAsUrl });

    // Source: https://developer.mozilla.org/en-US/docs/Web/API/FileReader/readAsDataURL
    const reader = new FileReader();
    reader.readAsDataURL(event.target.files[0]);
    reader.onload = function () {
      setImageAsBase64(reader.result);
    };
    setShowSave(true);
  };

  const onButtonNewImageUploadClick = () => {
    uploadNewImageRef.current.click();
  };

  const onSaveChanges = () => {
    let body = JSON.stringify({ uploaded_device_image: imageAsBase64 });
    fetch(BACKEND_URL + "/devices/" + deviceData.device_id, {
      method: "PUT",
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
          setErrorText("");
          setShowSave(false);
        }
      })
      .catch((error) => {
        console.log(error);
      });
  };

  return (
    <div className="device-image-card">
      <img className="device-image-card-img" src={previewURLImage ? previewURLImage : deviceData.image_url} alt="Foto des Geräts"></img>
      {editable && (
        <div className="change-image-button" onClick={onButtonNewImageUploadClick}>
          <Upload size={20} className="upload-image-icon" />
        </div>
      )}

      <input
        ref={uploadNewImageRef}
        style={{ display: "none" }}
        type="file"
        accept=".jpg, .png"
        onChange={(e) => {
          onUploadImage(e);
        }}
      />
      {showSave && (
        <div className="save-changes-footer">
          <div className="save-changes-button" onClick={onSaveChanges}>
            Änderung speichern
          </div>
        </div>
      )}
      {errorText !== "" && <span className="error-text">{errorText}</span>}
    </div>
  );
};

export default DeviceImageCard;
