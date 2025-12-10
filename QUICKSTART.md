# 🚀 AeroGraph Analytics - Quick Start

## Antes de Começar

Tenha pronto:
- Chave Google Gemini (gratuita): https://ai.google.dev
- Credenciais Neo4j Aura
- Conta GitHub (para fazer push)
- Conta Render.com
- Conta Vercel.com

---

## 1️⃣ Configuração Local

### Backend

```bash
cd backend

# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas credenciais
# NEO4J_URI=seu_uri
# NEO4J_PASSWORD=sua_senha
# GEMINI_API_KEY=sua_chave_gemini

# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
uvicorn server:app --reload
```

Teste: `curl http://localhost:8000/api/examples`

### Frontend

```bash
cd frontend

# Copiar arquivo de exemplo
cp .env.example .env.local

# Editar .env.local
# REACT_APP_BACKEND_URL=http://localhost:8000

# Instalar dependências
npm install

# Rodar
npm start
```

Acesse: `http://localhost:3000`

---

## 2️⃣ Deploy no Render (Backend)

1. **Fazer commit no GitHub**:
   ```bash
   git add .
   git commit -m "Fix runtime errors and prepare for deployment"
   git push
   ```

2. **Acessar Render.com**:
   - Clique em "New Web Service"
   - Conecte seu repositório
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `uvicorn backend.server:app --host 0.0.0.0 --port 8000`

3. **Adicionar Environment Variables**:
   ```
   NEO4J_URI=neo4j+s://86090040.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=sua_senha
   NEO4J_DATABASE=neo4j
   GEMINI_API_KEY=sua_chave
   CORS_ORIGINS=http://localhost:3000,https://seu-frontend.vercel.app
   ```

4. **Deploy** - Aguarde ~5 minutos

Seu backend estará em: `https://seu-app.onrender.com`

---

## 3️⃣ Deploy no Vercel (Frontend)

1. **Preparar ambiente**:
   ```bash
   cd frontend
   # Criar .env.production com URL do Render
   echo "REACT_APP_BACKEND_URL=https://seu-app.onrender.com" > .env.production
   git add .
   git commit -m "Add production environment"
   git push
   ```

2. **Acessar Vercel.com**:
   - Clique em "New Project"
   - Selecione seu repositório
   - Framework: "Create React App"
   - Root Directory: `./frontend`

3. **Environment Variables**:
   ```
   REACT_APP_BACKEND_URL=https://seu-app.onrender.com
   ```

4. **Deploy** - Vercel fará auto-deploy

Seu frontend estará em: `https://seu-app.vercel.app`

---

## 4️⃣ Atualizar CORS no Render

Após deploy do Vercel, atualize no Render:

```
CORS_ORIGINS=http://localhost:3000,https://seu-app.vercel.app
```

---

## Checklist de Deploy

- [ ] Chave Gemini obtida
- [ ] Backend testado localmente
- [ ] Frontend testado localmente
- [ ] Código commitado no GitHub
- [ ] Backend deployado no Render
- [ ] Frontend deployado no Vercel
- [ ] CORS atualizado no Render
- [ ] Aplicação testada em produção

---

## Erros Comuns

| Erro | Solução |
|------|---------|
| CORS Error | Verifique CORS_ORIGINS no Render |
| 401 Neo4j | Aguarde 60s após criar instância Aura |
| Blank page | Verifique REACT_APP_BACKEND_URL |
| LLM Error | Verifique chave Gemini e limite de requisições |

---

## Documentação Completa

Ver `DEPLOY_GUIDE.md` para mais detalhes
