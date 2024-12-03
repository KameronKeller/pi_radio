let isWindowFocused = true;

function fetchStations() {
  fetch("/stations")
    .then((response) => response.json())
    .then((data) => {
      const stationList = document.getElementById("station-list");
      stationList.innerHTML = "";
      data.forEach((station) => {
        const li = document.createElement("li");
        li.textContent = station[2] + "|" + station[1]; // station_name
        li.onclick = () => playStation(station[0]); // station_id
        stationList.appendChild(li);
      });
    })
    .catch((error) => {
      console.error("Error fetching stations:", error);
    });
}

function fetchMetadata() {
  if (!isWindowFocused) return;

  fetch("/metadata")
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        document.getElementById("metadata-display").innerText = data.error;
      } else {
        document.getElementById("station-name").innerText =
          "Station: " + data.station_name;
        document.getElementById("genre").innerText = "Genre: " + data.genre;
        document.getElementById("track-title").innerText =
          "Track: " + data.track_title;
        document.getElementById("station-url").innerText = "URL: " + data.url;
      }
    })
    .catch((error) => {
      console.error("Error fetching metadata:", error);
    });
}

window.addEventListener("focus", () => {
  isWindowFocused = true;
  fetchMetadata();
});

window.addEventListener("blur", () => {
  isWindowFocused = false;
});

// Periodically fetch metadata every 20 seconds
setInterval(fetchMetadata, 20000);
window.onload = fetchStations;
// window.onload = fetchMetadata;  // Fetch metadata when the page loads
