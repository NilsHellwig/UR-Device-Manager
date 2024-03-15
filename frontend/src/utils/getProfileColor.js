export const getProfileColor = (username) => {
  let firstChar = username.toLowerCase().charAt(0);

  switch (firstChar) {
    case "a":
      return "#144272";
    case "b":
      return "#2C849A";
    case "c":
      return "#A99A6A";
    case "d":
      return "#995656";
    case "e":
      return "#912175";
    case "f":
      return "#912175";
    case "g":
      return "#F99417";
    case "h":
      return "#645CAA";
    case "i":
      return "#004259";
    case "j":
      return "#1F8970";
    case "k":
      return "#AFDA28";
    case "l":
      return "#201E67";
    case "m":
      return "#004259";
    case "n":
      return "#F48484";
    case "o":
      return "#99CA72";
    case "p":
      return "#A05979";
    case "q":
      return "#CF4DCE";
    case "r":
      return "#4E6C50";
    case "s":
      return "#6F19A6";
    case "t":
      return "#FF7A54";
    case "u":
      return "#BB656F";
    case "v":
      return "#2C79F5";
    case "w":
      return "#9D2C72";
    case "x":
      return "#579AA1";
    case "y":
      return "#2C6255";
    case "z":
      return "#144272";
    default:
      return "#20262E";
  }
};
