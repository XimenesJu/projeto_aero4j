# 📤 Publicar no GitHub e Deploy no Render

## 📍 Passo 1: Criar Repositório no GitHub

### 1a. Acessar GitHub
1. Abra: https://github.com
2. Faça login (ou crie conta se não tiver)
3. Clique em **"+"** (canto superior direito) → **"New repository"**

### 1b. Criar Repositório
```
Repository name: seu-nome-aqui
Descrição: AeroGraph Analytics - GraphRAG com Neo4j e Gemini

☑ Add a README file
☑ Add .gitignore (escolha: Python)
☑ Choose a license (MIT é bom)

[Create repository]
```

Exemplo de nome: `aero-graph-analytics` ou `novo-projeto-aero`

---

## 📍 Passo 2: Preparar Seu Projeto Local

### 2a. Abrir Terminal na Pasta do Projeto

```bash
# Navegue até a pasta
cd c:\Users\jucx\Downloads\aero4j\novo_projeto_aero_final
```

### 2b. Verificar Status do Git

```bash
git status
```

Se aparecer `fatal: not a git repository`, significa que ainda não foi inicializado. Continue para 2c.

Se já existe, pule para Passo 3.

### 2c. Inicializar Git (se necessário)

```bash
git init
```

---

## 📍 Passo 3: Adicionar Remote (Conectar ao GitHub)

```bash
# Substitua SeuUsuario e seu-repo pelo seu
git remote add origin https://github.com/SeuUsuario/seu-repo.git

# Verifique se funcionou
git remote -v
```

Deve mostrar:
```
origin  https://github.com/SeuUsuario/seu-repo.git (fetch)
origin  https://github.com/SeuUsuario/seu-repo.git (push)
```

---

## 📍 Passo 4: Criar/Verificar .gitignore

✅ **IMPORTANTE**: Você **NÃO** deve fazer upload do `.env` com suas senhas!

Crie (ou verifique se existe) um arquivo `.gitignore` na raiz:

```bash
# Cria .gitignore se não existir
cat > .gitignore << EOF
# Environment variables
.env
*.env.local
backend/.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv

# Node
node_modules/
npm-debug.log
yarn-error.log
.next
build/
dist/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Database
*.db
*.sqlite

EOF
```

---

## 📍 Passo 5: Adicionar Arquivos ao Git

```bash
# Adicionar todos os arquivos (menos .env por causa do .gitignore)
git add .

# Verificar o que será commitado
git status
```

⚠️ **Certifique-se de que `backend/.env` aparece em "Ignored files"**

---

## 📍 Passo 6: Fazer Commit Inicial

```bash
git commit -m "Initial commit - AeroGraph Analytics com correções de runtime"
```

---

## 📍 Passo 7: Enviar para GitHub

```bash
# Branch principal
git branch -M main

# Fazer push
git push -u origin main
```

Se pedir autenticação:
- **Opção 1**: GitHub CLI (recomendado)
  ```bash
  gh auth login
  ```

- **Opção 2**: Personal Access Token
  1. GitHub → Settings → Developer settings → Personal access tokens
  2. Generate new token → repo (check)
  3. Copie o token
  4. Cole como senha ao fazer push

---

## 🎯 Verificar no GitHub

1. Acesse: https://github.com/SeuUsuario/seu-repo
2. Deve ver todos seus arquivos (menos `.env`)
3. Pronto! ✅

---

## 🚀 Próximo Passo: Conectar ao Render

Agora você pode conectar ao Render!

1. Acesse: https://render.com
2. Clique: **"New Web Service"**
3. Clique: **"Connect a repository"**
4. Busque seu repositório `seu-repo`
5. Selecione
6. Configure (ver próximo passo)

---

## ⚙️ Configuração no Render

### Name
```
aero-graph-api
```

### Runtime
```
Python 3.11
```

### Build Command
```
pip install -r backend/requirements.txt
```

### Start Command
```
uvicorn backend.server:app --host 0.0.0.0 --port 8000
```

### Environment Variables (Advanced)

Clique em "Add Environment Variable" e adicione:

```
NEO4J_URI=neo4j+s://86090040.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=B89og2TnLbJgoY7UxfhF1IedvooHOLW9Z2KCJgQGsqE
NEO4J_DATABASE=neo4j
GEMINI_API_KEY=AIzaSyB0r4ZYqjHblgTP_rlVUMqaKum6ca7ayAI
CORS_ORIGINS=http://localhost:3000,https://seu-frontend.vercel.app
```

### Deploy
Clique: **"Create Web Service"**

Aguarde 5-10 minutos...

---

## ✅ Resultado

Seu backend estará em:
```
https://seu-app-name.onrender.com
```

---

## 🆘 Troubleshooting

### Erro: "Could not find a version that satisfies"
- Verifique `requirements.txt`
- Remova `requirements_clean.txt` (é um backup)

### Erro: "git remote already exists"
```bash
git remote remove origin
git remote add origin https://github.com/SeuUsuario/seu-repo.git
```

### Erro: "fatal: 'origin' does not appear to be a 'git' repository"
```bash
# Você está em pasta errada
cd c:\Users\jucx\Downloads\aero4j\novo_projeto_aero_final
git status
```

---

## 📝 Resumo dos Comandos

```bash
# 1. Navegue até a pasta
cd c:\Users\jucx\Downloads\aero4j\novo_projeto_aero_final

# 2. Configure remote
git remote add origin https://github.com/SeuUsuario/seu-repo.git

# 3. Adicione arquivos
git add .

# 4. Commit
git commit -m "Initial commit - AeroGraph Analytics"

# 5. Push
git push -u origin main
```

---

Pronto! Seu projeto está no GitHub e conectado ao Render! 🚀
