import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../Api/Api";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    API.post("/login", form)
      .then(res => {
        localStorage.setItem("user_id", res.data.user_id); // store the user
        alert("Login successful!");
        navigate("/home"); // redirect to home page
      })
      .catch(err => {
        console.error(err);
        alert("Login failed");
      });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input placeholder="Email" onChange={e => setForm({ ...form, email: e.target.value })} />
      <input placeholder="Password" type="password" onChange={e => setForm({ ...form, password: e.target.value })} />
      <button type="submit">Login</button>
    </form>
  );
}
