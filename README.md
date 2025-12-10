# 🛫 AeroGraph Analytics

Aplicação web de análise de redes de aviação com **GraphRAG + Neo4j + Gemini AI**

Demonstração de integração de **grafos de conhecimento** com **LLMs** para consultas em linguagem natural.

---

## ✨ Características

- 🤖 **GraphRAG**: Converta perguntas em linguagem natural para queries Cypher
- 🗺️ **Visualização**: Grafo interativo de rotas aéreas
- 🛫 **Base de Dados**: Neo4j Aura com dados de aeroportos e rotas
- 🎨 **Dark Analytics**: Design profissional com tema cinza/ciano/âmbar
- ⚡ **100% Gratuito**: Deploy em Render + Vercel + Google Gemini

---

## 🚀 Quick Start (5 minutos)

### 1. Obter Chave Gratuita

- Acesse: https://ai.google.dev
- Clique "Get API Key" → "Create API Key"
- Copie a chave

### 2. Clonar e Configurar

```bash
git clone seu-repositorio
cd seu-repositorio

# Backend
cd backend
cp .env.example .env
# Edite .env e adicione sua GEMINI_API_KEY
pip install -r requirements.txt
uvicorn server:app --reload

# Frontend (em outro terminal)
cd frontend
cp .env.example .env.local
# Edite .env.local
npm install
npm start
```

Acesse: http://localhost:3000

### 3. Popular Dados

- Clique em "Popular Dados de Exemplo"
- Clique em um exemplo ou faça uma pergunta
- Veja a query Cypher gerada e os resultados

---

## 📚 Documentação

| Documento | Conteúdo |
|-----------|----------|
| [QUICKSTART.md](./QUICKSTART.md) | Início rápido em 5 minutos |
| [DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md) | Deploy em Render + Vercel |
| [CHANGES.md](./CHANGES.md) | Mudanças e correções aplicadas |

---

## 🏗️ Arquitetura

```
┌─────────────┐
│  Frontend   │  React + Tailwind + Force Graph
│  (Vercel)   │
└──────┬──────┘
       │ (HTTP)
       ▼
┌─────────────────────────────┐
│  Backend API (Render)       │  FastAPI + Python
│  - GraphRAG Query Handler   │
│  - Cypher Generation        │
│  - Graph Visualization Data │
└──────┬──────────────────────┘
       │ (Cypher)
       ▼
┌─────────────────────────────┐
│  Neo4j Aura Database        │  Cloud Neo4j
│  - Airports                 │
│  - Airlines                 │
│  - Routes                   │
└─────────────────────────────┘
```

---

## 🔑 APIs Utilizadas

| API | Plano | Limite | Custo |
|-----|-------|--------|-------|
| Google Generative AI | Free | 15 req/min | $0 |
| Neo4j Aura | Free | 16GB | $0 |
| Render | Free | 750h/mês | $0 |
| Vercel | Free | Ilimitado | $0 |

**Total: Completamente Gratuito** ✅

---

## 📝 Exemplos de Queries

1. **"Quais aeroportos estão no Brasil?"**
   - Gera: `MATCH (a:Airport {country: 'Brazil'}) RETURN a`

2. **"Mostre todas as rotas saindo de GRU"**
   - Gera: `MATCH (a:Airport {code: 'GRU'})-[r:ROUTE]->(b:Airport) RETURN a, r, b`

3. **"Quais companhias aéreas operam rotas internacionais?"**
   - Gera: `MATCH (al:Airline)-[:OPERATES]->(a:Airport)-[r:ROUTE]->(b:Airport) WHERE a.country <> b.country RETURN DISTINCT al`

4. **"Qual é a rota mais longa?"**
   - Gera: `MATCH (a:Airport)-[r:ROUTE]->(b:Airport) RETURN a, b, r ORDER BY r.distance_km DESC LIMIT 1`

---

## 🛠️ Stack Técnico

### Backend
```
FastAPI         - Web framework
Neo4j Driver    - Database
Google GenAI    - LLM
Python 3.11     - Runtime
```

### Frontend
```
React 19        - UI Framework
Tailwind CSS    - Styling
Force Graph 2D  - Visualization
Lucide Icons    - Icons
```

### Deploy
```
Render          - Backend hosting
Vercel          - Frontend hosting
Docker          - Containerization
GitHub          - Version control
```

---

## 📊 Dados Inclusos

### Aeroportos (10)
- GRU, CGH, GIG, BSB (Brasil)
- JFK, LAX (USA)
- LHR, CDG (Europa)
- NRT (Japão)
- DXB (UAE)

### Companhias Aéreas (5)
- LATAM, GOL (Brasil)
- AA (USA)
- BA (UK)
- EK (UAE)

### Rotas (10)
- Conexões domésticas e internacionais
- Distâncias reais em km
- Duração de voos em horas

---

## 🔧 Configuração

### Variáveis de Ambiente

**Backend** (`.env`):
```env
NEO4J_URI=neo4j+s://seu-uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=sua-senha
NEO4J_DATABASE=neo4j
GEMINI_API_KEY=sua-chave
CORS_ORIGINS=http://localhost:3000
```

**Frontend** (`.env.local`):
```env
REACT_APP_BACKEND_URL=http://localhost:8000
```

---

## 🐳 Docker

### Build Backend
```bash
docker build -f backend/Dockerfile -t aero-api .
docker run -p 8000:8000 \
  -e NEO4J_URI=... \
  -e GEMINI_API_KEY=... \
  aero-api
```

---

## 📱 Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/` | Health check |
| GET | `/api/examples` | Lista exemplos de queries |
| POST | `/api/graphrag/query` | Executar query natural |
| GET | `/api/graph/data` | Dados do grafo |
| POST | `/api/seed-data` | Popular dados exemplo |

---

## ✅ Teste Local

```bash
# Backend
python backend/test_config.py

# Verificar todas as conexões
```

---

## 🚢 Deploy

### Render (Backend)
```bash
git push
# Render faz deploy automaticamente
```

### Vercel (Frontend)
```bash
# Conectar repositório no Vercel
# Deploy automático em cada push
```

---

## 📞 Troubleshooting

| Problema | Solução |
|----------|---------|
| CORS Error | Atualize `CORS_ORIGINS` no Render |
| 401 Neo4j | Aguarde 60s após criar instância |
| Blank page | Verifique `REACT_APP_BACKEND_URL` |
| LLM Error | Verifique `GEMINI_API_KEY` e limite |

---

## 📈 Próximos Passos

- [ ] Adicionar autenticação
- [ ] Persistência de histórico de queries
- [ ] Múltiplas bases de conhecimento
- [ ] Análise de performance de queries
- [ ] Dashboard de estatísticas
- [ ] Export de resultados (CSV, JSON)

---

## 📄 Licença

MIT License - Sinta-se livre para usar em projetos comerciais

---

## 🙏 Créditos

Desenvolvido como demonstração de **GraphRAG** para fins educacionais.

**Tecnologias**:
- Neo4j
- Google Generative AI
- FastAPI
- React

---

## 🔗 Links Úteis

- 🔑 [Google AI Studio](https://ai.google.dev) - Obter API Key
- 🗄️ [Neo4j Aura](https://neo4j.com/cloud/aura/) - Database
- 🚀 [Render](https://render.com) - Backend Deploy
- 📦 [Vercel](https://vercel.com) - Frontend Deploy

---

**Última atualização**: Dezembro 2025
**Status**: Pronto para Deploy ✅
