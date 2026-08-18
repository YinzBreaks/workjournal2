import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../lib/api";

export default function OidcCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState("");

  useEffect(() => {
    const code = searchParams.get("code");
    const state = searchParams.get("state");
    const callbackError = searchParams.get("error");

    if (callbackError) {
      setError(searchParams.get("error_description") || callbackError);
      return;
    }

    if (!code) {
      setError("Missing authorization code");
      return;
    }

    api
      .post("/auth/oidc/callback", { code, state })
      .then(({ data }) => {
        login(data.access_token, data.refresh_token);
        navigate("/", { replace: true });
      })
      .catch((err) => {
        setError(err.response?.data?.detail || "Authentication failed");
      });
  }, [searchParams, login, navigate]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="text-center space-y-4">
          <p className="text-red-600">{error}</p>
          <a href="/login" className="text-blue-600 hover:underline text-sm">
            Back to login
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center space-y-2">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto" />
        <p className="text-gray-600 text-sm">Completing sign in...</p>
      </div>
    </div>
  );
}
