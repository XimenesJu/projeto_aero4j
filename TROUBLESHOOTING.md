# 🐛 Troubleshooting Guide - AeroGraph Analytics

## Erros Comuns e Soluções

---

## 🔴 Backend não inicia

### Erro: `ModuleNotFoundError: No module named 'emergentintegrations'`

**Causa**: Você está usando a versão antiga do `requirements.txt`

**Solução**:
```bash
cd backend
pip uninstall -y emergentintegrations
pip install -r requirements.txt
```

---

### Erro: `No module named 'google.generativeai'`

**Causa**: Google GenAI não foi instalado

**Solução**:
```bash
pip install google-generativeai
```

---

## 🔴 Neo4j Connection Error

### Erro: `neo4j.exceptions.AuthError: Unauthorized`

**Causa**: Credenciais Neo4j incorretas

**Solução**:
1. Verifique `NEO4J_PASSWORD` em `.env`
2. Acesse https://console.neo4j.io
3. Copie a senha correta
4. Aguarde 60 segundos após criar a instância Aura

---

### Erro: `neo4j.exceptions.ServiceUnavailable`

**Causa**: Neo4j Aura não está pronto

**Solução**:
```bash
# Aguarde 60 segundos após criar a instância
# Verifique em https://console.neo4j.io se está "Running"
# Teste a conexão
python backend/test_config.py
```

---

## 🔴 GEMINI_API_KEY Issues

### Erro: `google.api_core.exceptions.InvalidArgument`

**Causa**: Chave Gemini inválida

**Solução**:
1. Acesse https://ai.google.dev
2. Clique "Get API Key"
3. Clique "Create API Key"
4. Copie exatamente (sem espaços)
5. Cole em `.env`: `GEMINI_API_KEY=sua_chave_aqui`

---

### Erro: `429 Too Many Requests`

**Causa**: Limite gratuito atingido (15 req/min)

**Solução**:
- Aguarde 1 minuto
- Considere upgrade (pago)
- Para testes, comente a chamada LLM em `server.py`

---

### Erro: `GEMINI_API_KEY not configured`

**Causa**: Variável não foi carregada

**Solução**:
```bash
# Verifique .env
grep GEMINI_API_KEY backend/.env

# Deve aparecer:
# GEMINI_API_KEY=sk-...

# Se vazio, adicione sua chave
echo "GEMINI_API_KEY=sua_chave" >> backend/.env
```

---

## 🔴 CORS Errors

### Erro: `Access to XMLHttpRequest blocked by CORS policy`

**Frontend Error**: 
```
Access to XMLHttpRequest at 'http://localhost:8000/api/...' 
from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Causa**: CORS não está permitido para sua origem

**Solução (Desenvolvimento)**:
```bash
# backend/.env
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

**Solução (Produção)**:
```bash
# No Render, adicione variável:
CORS_ORIGINS=https://seu-frontend.vercel.app,https://seu-backend.onrender.com
```

---

## 🔴 Frontend Issues

### Erro: `REACT_APP_BACKEND_URL is not defined`

**Causa**: Variável de ambiente não foi carregada

**Solução**:
```bash
cd frontend

# Crie .env.local
cat > .env.local << EOF
REACT_APP_BACKEND_URL=http://localhost:8000
EOF

# Reinicie npm
npm start
```

---

### Erro: Página branca, sem conteúdo

**Causa 1**: Backend não está rodando
```bash
# Verifique
curl http://localhost:8000/api/examples
```

**Causa 2**: REACT_APP_BACKEND_URL está errado
```bash
# Edite .env.local
REACT_APP_BACKEND_URL=http://localhost:8000
```

**Solução**:
1. Inicie o backend primeiro
2. Verifique REACT_APP_BACKEND_URL
3. Limpe cache: `npm start -- --reset-cache`

---

### Erro: "Cannot POST /api/graphrag/query"

**Causa**: Backend não tem a rota

**Solução**:
```bash
# Verifique que server.py foi atualizado corretamente
grep "graphrag/query" backend/server.py

# Deve retornar a linha da rota
# Se vazio, reaplique o patch
```

---

## 🔴 Database Issues

### Erro: `No data seeded` - Botão "Popular Dados" não funciona

**Causa**: Backend não retorna resposta

**Solução**:
```bash
# Teste manualmente
curl -X POST http://localhost:8000/api/seed-data \
  -H "Content-Type: application/json" \
  -d '{"clear_existing": true}'

# Deve retornar JSON com airports, airlines, routes
```

---

### Erro: Graph visualization vazia

**Causa 1**: Nenhum dado foi carregado
```bash
# Carregue dados clicando "Popular Dados de Exemplo"
```

**Causa 2**: Dados não estão no Neo4j
```bash
# Teste a conexão
python backend/test_config.py
```

---

## 🔴 Deploy Issues

### Erro ao fazer push no GitHub

```bash
# Verifica status
git status

# Adiciona todos os arquivos
git add .

# Commit
git commit -m "Fix runtime errors and prepare for deployment"

# Push
git push -u origin main
```

---

### Erro: Render deploy falha

**Verificar logs**:
1. Acesse https://dashboard.render.com
2. Clique no seu serviço
3. Vá para "Logs"
4. Procure por erros

**Causas comuns**:
- `pip install` falha → Verifique `requirements.txt`
- Port erro → Deve ser porta `8000`
- Timeout → Aumentar timeout em Render settings

---

### Erro: Vercel deploy falha

**Verificar**:
1. Acesse https://vercel.com/dashboard
2. Clique no seu projeto
3. Vá para "Deployments"
4. Clique em "Logs"

**Causas comuns**:
- `npm install` falha → Limpar cache: `npm ci`
- Build timeout → Otimizar build
- Environment var missing → Adicionar em Vercel Settings

---

## 🟡 Performance Issues

### Queries são lentas

**Solução**:
```python
# backend/server.py
# Adicione índices no Neo4j
# Ou reduza LIMIT de 50 para 20
```

---

### Memory leak / Uso alto de RAM

**Solução**:
```python
# Feche conexões Neo4j
driver.close()

# Ou use context managers
with driver.session() as session:
    result = session.run(query)
```

---

## 🟡 Testing Issues

### test_config.py não encontrado

```bash
cd backend
python test_config.py
```

---

### test_graphrag.py falha

**Solução**:
```bash
cd backend
python -m asyncio
# Depois rodar test_graphrag.py
```

---

## ✅ Verificação Completa

Execute este script para verificar tudo:

```bash
# 1. Configuração
python backend/test_config.py

# 2. GraphRAG
python backend/test_graphrag.py

# 3. API
curl http://localhost:8000/api/examples

# 4. Frontend
npm start
```

---

## 📞 Ainda com dúvidas?

1. Verifique **DEPLOY_GUIDE.md**
2. Verifique **QUICKSTART.md**
3. Verifique **CHANGES.md**
4. Revise este arquivo

---

## 🔍 Debug Mode

Para mais detalhes, adicione em `.env`:

```env
# Backend
PYTHONUNBUFFERED=1
LOG_LEVEL=DEBUG

# Frontend
REACT_APP_DEBUG=true
```

Depois reinicie a aplicação.

---

**Última atualização**: Dezembro 2025
