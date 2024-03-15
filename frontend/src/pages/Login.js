import { LockOpen } from "phosphor-react";
import { useState } from "react";
import { BACKEND_URL } from "../Constants";
import { showToast } from "../utils/showToast";

const Login = ({ setCurrentPage }) => {
  const [RZUsername, setRZUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorText, setErrorText] = useState("");

  const onRZUsernameValueChange = (e) => {
    setRZUsername(e.target.value);
  };
  const onPasswordValueChange = (e) => {
    setPassword(e.target.value);
  };

  const onLoginButtonClick = () => {
    if (RZUsername === "" || password === "") {
      setErrorText("Fehler: Bitte geben Sie Ihren RZ-Username und ein Passwort ein!");
    } else {
      const searchParamas = new URLSearchParams();
      searchParamas.append("username", RZUsername);
      searchParamas.append("password", password);
      fetch(BACKEND_URL + "/login", {
        method: "POST",
        headers: {
          accept: "application/json",
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: searchParamas,
      })
        .then((response) => {
          if (!response.ok) {
            return response.json().then((json) => {
              const errorMessage = json.detail + " ist nicht korrekt." || "Ein unbekannter Fehler ist aufgetreten.";
              setErrorText(`Fehler: ${errorMessage}`);
              throw new Error(`Error: ${response.status}`);
            });
          }
          return response.json();
        })
        .then((data) => {
          localStorage.setItem("access_token", data.access_token);
          showToast("Erfolgreich eingeloggt!");
          setCurrentPage("dashboard-page");
        })
        .catch((error) => {
          console.log(error);
        });
    }
  };

  return (
    <div className="login-page">
      <div className="login-form">
        <div className="form-field">
          <span className="form-field-title">RZ-USERNAME</span>
          <input value={RZUsername} onChange={onRZUsernameValueChange} type={"text"} placeholder={"RZ-Username eingeben..."} className="form-field-input"></input>
        </div>
        <div className="form-field">
          <span className="form-field-title">PASSWORT</span>
          <input value={password} onChange={onPasswordValueChange} type={"password"} placeholder={"Passwort eingeben..."} className="form-field-input"></input>
        </div>
        <p className="error-text">{errorText}</p>
        <div className="login-footer">
          <div className="standard-button" onClick={onLoginButtonClick}>
            <span>Einloggen</span>
            <LockOpen size={20} color="#ffffff" weight="fill" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
