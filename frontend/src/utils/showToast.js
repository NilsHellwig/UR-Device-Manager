import { toast } from "react-toastify";
export const showToast = (message) => {
  toast(message, {
    position: "top-right",
    autoClose: 5000,
    hideProgressBar: true,
    closeOnClick: true,
    pauseOnHover: false,
    draggable: false,
    theme: "dark",
  });
};
