// Gemini 抽出
document.getElementById("extractBtn").onclick = async () => {
  const text = document.getElementById("message").value.trim();
  if (!text) return alert("入力してください");

  document.getElementById("status").textContent = "抽出中...";

  const res = await fetch("https://geo-memory-support-backend.onrender.com/extract_with_gemini", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": API_SECRET
    },
    body: JSON.stringify({ text })
  });

  const data = await res.json();
  renderExtractResult(data);
};

function renderExtractResult(data) {
  const places = data.places || [];
  const times = data.times || [];
  const actions = data.actions || [];

  document.getElementById("placesArea").innerHTML =
    places.map(p => `<label><input type="checkbox" value="${p}">${p}</label><br>`).join("");

  document.getElementById("timesArea").innerHTML =
    times.map(t => `<span class="pill">${t}</span>`).join("");

  document.getElementById("actionsArea").innerHTML =
    actions.map(a => `<span class="pill">${a}</span>`).join("");

  document.getElementById("resultCard").style.display = "block";
  document.getElementById("status").textContent = "抽出完了";
}
