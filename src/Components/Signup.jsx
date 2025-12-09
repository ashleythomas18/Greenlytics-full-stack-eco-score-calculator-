import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../Api/Api";

export default function Signup() {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    API.post("/signup", form)
      .then(res => {
        alert("Signup successful!");
        localStorage.setItem("user_id", res.data.user_id);
        navigate("/login"); // 🔁 Redirect after signup
      })
      .catch(err => alert("Signup failed"));
  };

  return (
    <form onSubmit={handleSubmit}>
      <input placeholder="Name" onChange={e => setForm({ ...form, name: e.target.value })} />
      <input placeholder="Email" onChange={e => setForm({ ...form, email: e.target.value })} />
      <input placeholder="Password" type="password" onChange={e => setForm({ ...form, password: e.target.value })} />
      <button type="submit">Signup</button>
    </form>
  );
}
