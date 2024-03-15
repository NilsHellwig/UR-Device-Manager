import roomData from "../data/hoersaal_raumcode.json";

export const getRoomCodes = () => {
  let roomCodes = [];
  roomData.forEach((element) => {
    roomCodes.push(element.room_code);
  });
  return roomCodes;
};
