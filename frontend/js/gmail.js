const API_SECRET = "my_super_secret_key_123"; // 既存のやつを利用

document.getElementById("fetchGmailBtn").onclick = async () => {
  document.getElementById("gmailResult").textContent = "取得中...";

  try {
    const res = await fetch("https://geo-memory-support-backend.onrender.com/gmail/inbox", {
      method: "GET",
      headers: {
        "x-api-key": API_SECRET
      }
    });

    const data = await res.json();

    if (data.error) {
      document.getElementById("gmailResult").textContent =
        "取得失敗: " + data.error + "\n\nまず Gmail と連携（ログイン）をしてください。";
      return;
    }

    document.getElementById("gmailResult").textContent =
      JSON.stringify(data.messages, null, 2);

  } catch (err) {
    document.getElementById("gmailResult").textContent =
      "エラー: " + err.message;
  }
};
