let map = null;
let currentMarker = null;
let currentPosition = null;
let destinations = [];
let directionsService = null;
let directionsRenderer = null;

// Google Maps 初期化
function initializeMap() {
  if (!google || !google.maps) return;

  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 35.681236, lng: 139.767125 },
    zoom: 14,
  });

  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer({ map });

  startLocationTracking();
}

// 現在地トラッキング
function startLocationTracking() {
  updateCurrentPosition();
  setInterval(updateCurrentPosition, 10000);
}

function updateCurrentPosition() {
  navigator.geolocation.getCurrentPosition(
    pos => {
      const lat = pos.coords.latitude;
      const lng = pos.coords.longitude;
      currentPosition = { lat, lng };

      document.getElementById("current-position").textContent =
        `緯度: ${lat.toFixed(6)}, 経度: ${lng.toFixed(6)}`;

      if (map) {
        if (currentMarker) currentMarker.setPosition(currentPosition);
        else {
          currentMarker = new google.maps.Marker({
            map,
            position: currentPosition,
            icon: { url: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png" }
          });
        }
        map.setCenter(currentPosition);
      }
    },
    () => document.getElementById("current-position").textContent = "取得失敗"
  );
}

// =======================
// 目的地登録
// =======================
document.getElementById("registerDestBtn").onclick = async () => {
  const checks = document.querySelectorAll("#placesArea input:checked");
  if (!checks.length) return alert("チェックしてください");

  for (const cb of checks) {
    const place = cb.value;

    const geo = await fetch("https://geo-memory-support-backend.onrender.com/geocode", {
      method:"POST",
      headers:{
        "Content-Type": "application/json",
        "x-api-key": API_SECRET
      },
      body:JSON.stringify({ place })
    }).then(r => r.json());

    const marker = new google.maps.Marker({
      map,
      position: { lat: geo.lat, lng: geo.lng },
      title: place
    });

    destinations.push({
      name: place,
      lat: geo.lat,
      lng: geo.lng,
      marker,
    });
  }

  updateDestList();
};

function updateDestList() {
  const ul = document.getElementById("destList");
  ul.innerHTML = destinations.map((d,i)=>`
    <li>${d.name}
      <button onclick="showRoute(${i})">ルート</button>
      <button onclick="deleteDest(${i})">削除</button>
    </li>
  `).join("");
}

// ルート表示
function showRoute(i) {
  const d = destinations[i];
  const mode = document.getElementById("travelMode").value;

  directionsService.route({
    origin: currentPosition,
    destination: { lat: d.lat, lng: d.lng },
    travelMode: google.maps.TravelMode[mode]
  }, (res, status) => {
    if (status === "OK") {
      directionsRenderer.setDirections(res);
      showMapPage();
    } else {
      alert("ルート取得失敗");
    }
  });
}

function deleteDest(i) {
  destinations[i].marker.setMap(null);
  destinations.splice(i,1);
  updateDestList();
}

// Google Maps 読み込み完了を待つ
window.addEventListener("load", () => {
  const timer = setInterval(() => {
    if (google && google.maps) {
      clearInterval(timer);
      initializeMap();
    }
  }, 200);
});
