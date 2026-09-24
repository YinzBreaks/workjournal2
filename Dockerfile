# One container: FastAPI serves the API at /api and the built React app at /.

FROM node:20-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run check:i18n && npm run build


FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN groupadd --system journal && useradd --system --gid journal --home /app journal
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=frontend /frontend/dist ./static
USER journal
EXPOSE 8000
# Migrate, make sure the class and its starter tasks exist, then serve.
# --proxy-headers: trust X-Forwarded-* from Caddy (the only thing that can
# reach this container on the beattie network).
CMD ["sh", "-c", "alembic upgrade head && python -m app.seed && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'"]
