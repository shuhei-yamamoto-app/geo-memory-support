// ページ切り替え
function showMessagePage() {
  document.getElementById("page-message").classList.add("active");
  document.getElementById("page-map").classList.remove("active");
}

function showMapPage() {
  document.getElementById("page-map").classList.add("active");
  document.getElementById("page-message").classList.remove("active");
  setTimeout(() => {
    if (map) {
      google.maps.event.trigger(map, "resize");
      if (currentPosition) map.setCenter(currentPosition);
    }
  }, 200);
}

const API_SECRET = "my_super_secret_key_123";
