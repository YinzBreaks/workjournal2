import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Layout from "./components/Layout";
import RequireRole from "./components/RequireRole";
import Login from "./pages/Login";
import TasksPage from "./pages/student/TasksPage";
import HoursPage from "./pages/student/HoursPage";
import ProgramPage from "./pages/teacher/ProgramPage";
import OverviewPage from "./pages/admin/OverviewPage";

const HOME = {
  student: "/student/tasks",
  teacher: "/teacher",
  admin: "/admin",
};

function HomeRedirect() {
  const { user } = useAuth();
  return <Navigate to={user ? HOME[user.role] : "/login"} replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<HomeRedirect />} />

      <Route element={<RequireRole roles={["student"]} />}>
        <Route element={<Layout />}>
          <Route path="/student/tasks" element={<TasksPage />} />
          <Route path="/student/hours" element={<HoursPage />} />
        </Route>
      </Route>

      <Route element={<RequireRole roles={["teacher"]} />}>
        <Route element={<Layout />}>
          <Route path="/teacher" element={<ProgramPage />} />
        </Route>
      </Route>

      <Route element={<RequireRole roles={["admin"]} />}>
        <Route element={<Layout />}>
          <Route path="/admin" element={<OverviewPage />} />
        </Route>
      </Route>

      <Route path="*" element={<HomeRedirect />} />
    </Routes>
  );
}
