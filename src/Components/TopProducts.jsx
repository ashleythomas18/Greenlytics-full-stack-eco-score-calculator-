import React, { useEffect, useState } from "react";
import API from "../Api/Api";

export default function TopEcoProducts() {
  const [topProducts, setTopProducts] = useState([]);

  useEffect(() => {
    API.get("/top-eco-products")
      .then(res => setTopProducts(res.data))
      .catch(err => console.error(err));
  }, []);

  const getColor = (score) => {
    if (score >= 8) return "bg-green-500";
    if (score >= 5) return "bg-yellow-400";
    return "bg-red-400";
  };

  return (
    <div className="mb-6">
      <h3 className="text-xl font-semibold mb-2">Top Eco-Friendly Products</h3>
      {topProducts.map(p => (
        <div key={p.name} className="bg-green-50 border p-3 rounded mb-2">
          <div className="flex justify-between items-center">
            <div>
              <div className="font-bold">{p.name}</div>
              <div className="text-sm text-gray-600">{p.brand}</div>
            </div>
            <div
              className={`text-white px-3 py-1 rounded-full text-sm ${getColor(p.eco_score)}`}
            >
              {p.eco_score}/10
            </div>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div
              className={`${getColor(p.eco_score)} h-2 rounded-full`}
              style={{ width: `${p.eco_score * 10}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
