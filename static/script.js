function main() {
  let isWindowFocused = true;

  function fetchStations() {
    fetch("/stations")
      .then((response) => response.json())
      .then((data) => {
        const stationTableBody = document
          .getElementById("station-table")
          .getElementsByTagName("tbody")[0];
        stationTableBody.innerHTML = "";
        data.forEach((station) => {
          const stationId = station[0];
          const stationAddress = station[1];
          const stationName = station[2];

          const row = document.createElement("tr");
          const nameCell = document.createElement("td");
          const addressCell = document.createElement("td");
          const deleteCell = document.createElement("td");

          nameCell.textContent = stationName; // station_name

          const addressLink = document.createElement("a");
          addressLink.href = "#";
          addressLink.textContent = stationAddress; // station_address
          addressLink.onclick = (event) => {
            event.preventDefault();
            playStation(stationAddress); // pass the station address
            document.getElementById("url").value = stationAddress; // station_address
            fetchMetadata();
          };

          const deleteButton = document.createElement("button");
          deleteButton.innerHTML = "&#128465;"; // Unicode for trash can icon
          deleteButton.onclick = () => {
            deleteStation(stationId, row); // pass the row to be deleted
          };

          addressCell.appendChild(addressLink);
          deleteCell.appendChild(deleteButton);

          row.appendChild(nameCell);
          row.appendChild(addressCell);
          row.appendChild(deleteCell);

          stationTableBody.appendChild(row);
        });
      })
      .catch((error) => {
        console.error("Error fetching stations:", error);
      });
  }

  function playStation(stationAddress) {
    fetch("/play", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        url: stationAddress,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
      })
      .catch((error) => {
        console.error("Error playing station:", error);
      });
  }

  function deleteStation(stationId, row) {
    fetch(`/delete_station/${stationId}`, { method: "DELETE" })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        row.remove(); // remove the row from the table
      })
      .catch((error) => {
        console.error("Error deleting station:", error);
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
  // setInterval(fetchMetadata, 20000);
  fetchStations();
  // fetchMetadata();  // Fetch metadata when the page loads
}

document.addEventListener("DOMContentLoaded", main);
