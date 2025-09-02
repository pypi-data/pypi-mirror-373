socket.addEventListener("message", (event) => {
  const data = JSON.parse(event.data);
  if (data.type === "location.update") {
    const location = data.location;
    updateCurrentLocation(
      location.latitude,
      location.longitude,
      location.altitude,
      location.gps_timestamp,
    );
  }
});

function updateCurrentLocation(lat, lon, alt, ts) {
  const latitude = document.getElementById("latitude");
  const longitude = document.getElementById("longitude");
  const altitude = document.getElementById("altitude");
  const gps_timestamp = document.getElementById("gps-timestamp");

  latitude.textContent = lat;
  longitude.textContent = lon;
  altitude.textContent = alt;
  gps_timestamp.textContent = ts;
}
