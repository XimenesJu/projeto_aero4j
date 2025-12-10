# Guia de Deploy Gratuito - AeroGraph Analytics

## Correções Implementadas

✅ Removida dependência problemática `emergentintegrations`
✅ Substituído por `google-generativeai` (API oficial gratuita)
✅ Atualizado backend para usar Gemini 1.5 Flash
✅ Simplificado `requirements.txt` (7 dependências apenas)
✅ Configuração via variáveis de ambiente

---

## Opção 1: Deploy Backend no Render (Gratuito)

### 1. Preparação no GitHub

```bash
cd seu-projeto
git init
git add .
git commit -m "Initial commit with fixes"
```

Crie um repositório no GitHub e faça push:
```bash
git remote add origin https://github.com/seu-usuario/seu-repo.git
git push -u origin main
```

### 2. Configurar Render

1. Acesse https://render.com
2. Clique em **"New Web Service"**
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: aero-graph-api
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn backend.server:app --host 0.0.0.0 --port 8000`

5. Clique em **"Advanced"** e adicione variáveis de ambiente:

```
NEO4J_URI=neo4j+s://86090040.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=B89og2TnLbJgoY7UxfhF1IedvooHOLW9Z2KCJgQGsqE
NEO4J_DATABASE=neo4j
GEMINI_API_KEY=sua-chave-gemini-aqui
CORS_ORIGINS=http://localhost:3000,https://seu-frontend.vercel.app
```

6. Clique em **"Create Web Service"**

Seu backend estará em: `https://seu-app-name.onrender.com`

---

## Obter Chave Gratuita Google Gemini

1. Acesse: https://ai.google.dev
2. Clique em **"Get API Key"**
3. Clique em **"Create API Key in new project"**
4. Copie a chave gerada
5. Cole no Render como `GEMINI_API_KEY`

**Limite Gratuito**: 15 requisições por minuto

---

## Opção 2: Deploy Frontend no Vercel (Gratuito)

### 1. Preparação do Frontend

Crie um arquivo `.env.production`:

```
REACT_APP_BACKEND_URL=https://seu-app-name.onrender.com
```

### 2. Deploy no Vercel

1. Acesse https://vercel.com
2. Clique em **"New Project"**
3. Selecione seu repositório GitHub
4. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: `./frontend`

5. Em **"Environment Variables"**, adicione:
   ```
   REACT_APP_BACKEND_URL=https://seu-app-name.onrender.com
   ```

6. Clique em **"Deploy"**

Seu frontend estará em: `https://seu-app-name.vercel.app`

---

## Opção 3: Deploy Local com Docker

### 1. Criar `Dockerfile` no backend:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Criar `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      NEO4J_URI: neo4j+s://86090040.databases.neo4j.io
      NEO4J_USERNAME: neo4j
      NEO4J_PASSWORD: B89og2TnLbJgoY7UxfhF1IedvooHOLW9Z2KCJgQGsqE
      NEO4J_DATABASE: neo4j
      GEMINI_API_KEY: sua-chave-aqui
      CORS_ORIGINS: http://localhost:3000

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "3000:3000"
    environment:
      REACT_APP_BACKEND_URL: http://backend:8000
    depends_on:
      - backend
```

### 3. Rodar localmente:

```bash
docker-compose up
```

Acesse: `http://localhost:3000`

---

## Teste Local Antes do Deploy

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edite .env com suas credenciais
python -m uvicorn server:app --reload
```

Teste: `http://localhost:8000/api/examples`

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Edite .env.local com URL do backend
npm start
```

---

## Plataformas Gratuitas Recomendadas

| Serviço | Plataforma | Link |
|---------|-----------|------|
| Backend | Render | https://render.com |
| Frontend | Vercel | https://vercel.app |
| Alternativa Backend | Railway | https://railway.app |
| Alternativa Backend | Fly.io | https://fly.io |
| LLM | Google Gemini | https://ai.google.dev |

---

## Troubleshooting

### "CORS Error"
- Verifique `CORS_ORIGINS` no Render
- Deve incluir exatamente o domínio do seu frontend

### "GEMINI_API_KEY not configured"
- Verifique se a chave foi adicionada nas variáveis de ambiente
- Use `gemini-1.5-flash` (não `gemini-2.5-flash`)

### "Neo4j Connection Error"
- Espere 60 segundos após criar a instância Aura
- Verifique se as credenciais estão corretas

---

## Próximos Passos

1. ✅ Fazer commit das alterações
2. ✅ Obter chave Gemini
3. ✅ Fazer deploy no Render
4. ✅ Fazer deploy no Vercel
5. ✅ Atualizar CORS_ORIGINS com domínio Vercel
