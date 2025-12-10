const API_BASE = ""; // same origin (FastAPI serves frontend)

const indexStatus = document.getElementById("index-status");
const askStatus = document.getElementById("ask-status");
const answerDiv = document.getElementById("answer");
const sourcesDiv = document.getElementById("sources");

document.getElementById("btn-index-default").addEventListener("click", async () => {
  indexStatus.textContent = "Indexing default PDF...";
  try {
    const res = await fetch("/api/index-default", { method: "POST" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error");
    indexStatus.textContent = data.message || "Indexed.";
  } catch (err) {
    indexStatus.textContent = "Error: " + err.message;
  }
});

document.getElementById("btn-upload").addEventListener("click", async () => {
  const fileInput = document.getElementById("file-input");
  if (!fileInput.files.length) {
    indexStatus.textContent = "Please select a PDF file.";
    return;
  }

  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append("file", file);

  indexStatus.textContent = "Uploading & indexing...";
  try {
    const res = await fetch("/api/upload-and-index", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error");
    indexStatus.textContent = data.message || "Uploaded & indexed.";
  } catch (err) {
    indexStatus.textContent = "Error: " + err.message;
  }
});

document.getElementById("btn-ask").addEventListener("click", async () => {
  const question = document.getElementById("question").value.trim();
  if (!question) {
    askStatus.textContent = "Please type a question.";
    return;
  }

  askStatus.textContent = "Thinking...";
  answerDiv.textContent = "";
  sourcesDiv.textContent = "";

  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: question, top_k: 5 }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error");

    askStatus.textContent = "Done.";
    answerDiv.textContent = data.answer;
    sourcesDiv.textContent = "Sources: " + (data.sources || []).join(" | ");
  } catch (err) {
    askStatus.textContent = "Error: " + err.message;
  }
});
