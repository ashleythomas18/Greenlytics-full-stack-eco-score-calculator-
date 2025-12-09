import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function UploadReceipt() {
  const [file, setFile] = useState(null);
  const [uploadedData, setUploadedData] = useState(null); // ✅ Store response here
  const navigate = useNavigate();

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!file) return alert("Upload a file");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/upload-bill", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setUploadedData(data); // ✅ store for preview
      console.log("📝 Extracted Products:", JSON.stringify(data.products, null, 2)); // ✅ readable log

      navigate("/result", { state: { data } });
    } catch (err) {
      alert("Upload failed: " + err.message);
    }
  };

  const handleGetStarted = async () => {
    try {
      await fetch("http://localhost:5000/api/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "User clicked get started" }),
      });

      window.location.href = "http://localhost:8000/";
    } catch (err) {
      console.error(err);
      window.location.href = "http://localhost:8000/";
    }
  };

  return (
    <div>
      <h2>Upload Receipt</h2>
      <form onSubmit={handleUpload}>
        <input type="file" onChange={e => setFile(e.target.files[0])} />
        <button type="submit">Upload</button>
      </form>

      <button onClick={handleGetStarted} style={{ marginTop: '20px' }}>
        Try ML UI
      </button>

      {/* ✅ Show extracted data preview here */}
      {uploadedData && (
        <div style={{ marginTop: '30px' }}>
          <h3>📝 Extracted Products Preview</h3>
          <pre>{JSON.stringify(uploadedData.products, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
