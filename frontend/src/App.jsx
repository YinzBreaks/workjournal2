import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import OidcCallback from "./pages/OidcCallback";
import Dashboard from "./pages/Dashboard";
import ProtectedRoute from "./components/ProtectedRoute";
import RoleRoute from "./components/RoleRoute";
import Layout from "./components/Layout";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/auth/callback" element={<OidcCallback />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />

          <Route element={<RoleRoute allowed={["teacher", "admin"]} />}>
            <Route path="/teacher/*" element={<div>Teacher Area</div>} />
          </Route>

          <Route element={<RoleRoute allowed={["student"]} />}>
            <Route path="/student/*" element={<div>Student Area</div>} />
          </Route>

          <Route element={<RoleRoute allowed={["admin"]} />}>
            <Route path="/admin/*" element={<div>Admin Area</div>} />
          </Route>
        </Route>
      </Route>
    </Routes>
  );
}
