import { useLocation } from "react-router-dom";

export default function ResultPage() {
  const { state } = useLocation();
  const data = state?.data;

  if (!data) return <p>No data available</p>;

  return (
    <div>
      <h2>EcoScore Result</h2>
      <p>Invoice: {data.invoice_number || "Not Found"}</p>
      <p>Total Products: {data.total_products}</p>

      <ul>
        {(data.products || []).map((p, i) => (
          <li key={i}>{p.name || p}</li>
        ))}
      </ul>

      {(data.products || []).map((p, i) => (
        <div key={i}>
          <p>Name: {p.name || p}</p>
          <p>EcoScore: {p.eco_score || "N/A"} / 10</p>
        </div>
      ))}

      <p>
        <strong>Average EcoScore:</strong> {data.average_score || "N/A"}
      </p>
    </div>
  );
}
