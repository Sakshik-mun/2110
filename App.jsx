import { Routes, Route, Navigate, NavLink, useNavigate } from "react-router-dom";
import { getToken, clearToken, api } from "./api";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Profile from "./pages/Profile.jsx";
import Advisor from "./pages/Advisor.jsx";

function Protected({ children }) {
  return getToken() ? children : <Navigate to="/login" replace />;
}

function Shell({ children }) {
  const nav = useNavigate();
  const logout = async () => {
    try { await api("/auth/logout", { method: "POST" }); } catch {}
    clearToken();
    nav("/login");
  };
  return (
    <>
      <header className="bar">
        <strong className="brand">Credit Assistant</strong>
        <nav>
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/profile">Profile</NavLink>
          <NavLink to="/advisor">Advisor</NavLink>
          <button className="link" onClick={logout}>Log out</button>
        </nav>
      </header>
      <main>{children}</main>
    </>
  );
}

export default function App() {
  const page = (el) => <Protected><Shell>{el}</Shell></Protected>;
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={page(<Dashboard />)} />
      <Route path="/profile" element={page(<Profile />)} />
      <Route path="/advisor" element={page(<Advisor />)} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
