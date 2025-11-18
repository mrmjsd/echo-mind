# 🐳 EchoMind Docker Setup

This guide will help you run EchoMind using Docker containers following the Single Responsibility Principle (SRP).

## 📋 Architecture Overview

The application is split into two separate services:

1. **Backend Service** (Port 3030) - FastAPI server handling:
   - Document processing
   - RAG (Retrieval Augmented Generation)
   - Chat responses
   - API endpoints

2. **Frontend Service** (Port 6000) - Streamlit UI handling:
   - User interface
   - Voice recognition
   - Document uploads
   - Conversation display

## 🚀 Quick Start

### Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

### Running the Application

1. **Clone or navigate to the project directory:**
   ```bash
   cd /path/to/EchoMind
   ```

2. **Build and start the containers:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend (UI): http://0.0.0.0:6000
   - Backend (API): http://0.0.0.0:3030

4. **Stop the application:**
   ```bash
   # Press Ctrl+C in the terminal, then run:
   docker-compose down
   ```

## 🔧 Advanced Usage

### Run in detached mode (background)
```bash
docker-compose up -d
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuild containers
```bash
docker-compose up --build
```

### Stop and remove containers
```bash
docker-compose down
```

### Remove containers and volumes
```bash
docker-compose down -v
```

## 📂 Persistent Data

The following directories are mounted as volumes to persist data:

- `./data` - Uploaded documents
- `./models` - AI models
- `./vector_store.pkl` - Vector embeddings

## 🔌 Port Configuration

Default ports:
- Frontend: 6000
- Backend: 3030

To change ports, edit `docker-compose.yml`:
```yaml
ports:
  - "YOUR_PORT:6000"  # Frontend
  - "YOUR_PORT:3030"  # Backend
```

## 🛠️ Environment Variables

The frontend automatically connects to the backend using:
- `BACKEND_HOST=backend` (Docker service name)
- `BACKEND_PORT=3030`

For local development (without Docker), these default to `0.0.0.0:3030`.

## 🐛 Troubleshooting

### Containers won't start
```bash
# Check for port conflicts
docker-compose ps
netstat -an | grep 6000
netstat -an | grep 3030

# Force rebuild
docker-compose down
docker-compose up --build --force-recreate
```

### Frontend can't connect to backend
```bash
# Check if both containers are running
docker-compose ps

# Check backend logs
docker-compose logs backend
```

### Clear all data and restart
```bash
docker-compose down -v
rm -rf ./data/* ./models/*
docker-compose up --build
```

## 📝 Development Tips

### Run only backend
```bash
docker-compose up backend
```

### Run only frontend
```bash
docker-compose up frontend
```

### Access container shell
```bash
# Backend
docker exec -it echomind-backend /bin/bash

# Frontend
docker exec -it echomind-frontend /bin/bash
```

## 🔐 Security Notes

- The GROQ API key in `app/core/config.py` should be moved to environment variables
- Consider using `.env` file for sensitive data
- Don't commit API keys to version control

## 📖 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Made with ❤️ using Docker**
