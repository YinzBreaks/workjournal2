import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Layout from "./components/Layout";
import RequireRole from "./components/RequireRole";
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
  return <Navigate to={HOME[user.role]} replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomeRedirect />} />

      <Route element={<Layout />}>
        <Route element={<RequireRole roles={["student"]} />}>
          <Route path="/student/tasks" element={<TasksPage />} />
          <Route path="/student/hours" element={<HoursPage />} />
        </Route>

        <Route element={<RequireRole roles={["teacher", "admin"]} />}>
          <Route path="/teacher" element={<ProgramPage />} />
        </Route>

        <Route element={<RequireRole roles={["admin"]} />}>
          <Route path="/admin" element={<OverviewPage />} />
        </Route>
      </Route>

      <Route path="*" element={<HomeRedirect />} />
    </Routes>
  );
}
