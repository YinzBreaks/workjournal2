import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import OidcCallback from "./pages/OidcCallback";
import Dashboard from "./pages/Dashboard";
import StudentDashboard from "./pages/StudentDashboard";
import TeacherDashboard from "./pages/TeacherDashboard";
import AdminDashboard from "./pages/AdminDashboard";
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
            <Route path="/teacher/*" element={<TeacherDashboard />} />
          </Route>

          <Route element={<RoleRoute allowed={["student"]} />}>
            <Route path="/student/*" element={<StudentDashboard />} />
          </Route>

          <Route element={<RoleRoute allowed={["admin"]} />}>
            <Route path="/admin/*" element={<AdminDashboard />} />
          </Route>
        </Route>
      </Route>
    </Routes>
  );
}
