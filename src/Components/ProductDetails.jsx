import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import API from "../Api/Api";

function ProductDetails() {
  const { name } = useParams();
  const [product, setProduct] = useState(null);

  useEffect(() => {
    API.get(`/product/${name}`)
      .then(res => setProduct(res.data))
      .catch(err => console.error(err));
  }, [name]);

  if (!product) return <div>Loading...</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">{product.name}</h1>
      <p className="text-gray-500">{product.brand}</p>
      <p>Eco Score: <strong>{product.eco_score}</strong></p>
      <p>Carbon Footprint: {product.carbon_footprint} kg CO₂e</p>
      <p>Tags: {product.sustainability_tags.join(", ")}</p>
      <p>Sentiment Score: {product.user_sentiment_score}</p>
      <p className="mt-4 text-sm text-gray-600">Last updated: {product.last_updated}</p>
    </div>
  );
}

export default ProductDetails;
