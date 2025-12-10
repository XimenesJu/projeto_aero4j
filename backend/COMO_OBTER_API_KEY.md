# 🔑 Como Obter a Chave API Google Generative AI (Gemini)

## Guia Passo a Passo (3 minutos)

### 📍 Passo 1: Acessar Google AI Studio

1. Abra seu navegador
2. Acesse: **https://ai.google.dev**

Você verá a página inicial do Google AI Studio

```
┌─────────────────────────────────────────────────────────────┐
│                    Google AI Studio                         │
│                  (ai.google.dev)                            │
│                                                             │
│  [Get Started] [Documentation] [Pricing] [Sign In]          │
└─────────────────────────────────────────────────────────────┘
```

---

### 📍 Passo 2: Clicar em "Get API Key"

Procure no menu superior e clique no botão **"Get API Key"**

```
┌─────────────────────────────────────────────────────────────┐
│ Google AI Studio                                            │
│ ┌──────────────────────────────────────────────────────────┐│
│ │  [Get API Key] ←← CLIQUE AQUI                           ││
│ │                                                          ││
│ │  Build with Gemini                                      ││
│ │  Generate text, images, code...                         ││
│ └──────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

### 📍 Passo 3: Escolher Projeto

Após clicar, você verá uma tela pedindo para escolher um projeto:

**Opção 1: Criar novo projeto (RECOMENDADO)**
```
┌─────────────────────────────────────────────────────────────┐
│ Get API Key                                                 │
│                                                             │
│ Select a Project:                                           │
│                                                             │
│ ○ My first project                                          │
│ ○ [Create a new project] ← CLIQUE AQUI                    │
│                                                             │
│ [Next] [Cancel]                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 📍 Passo 4: Criar Novo Projeto

Se você clicou em "Create a new project":

```
┌─────────────────────────────────────────────────────────────┐
│ Create new project                                          │
│                                                             │
│ Project name:                                               │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ aero-graph-project                                    │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                             │
│ [Create] [Cancel]                                           │
└─────────────────────────────────────────────────────────────┘
```

**Digite um nome qualquer**, por exemplo:
- `aero-graph-project`
- `meu-projeto`
- `graphrag-demo`

Depois clique **[Create]**

---

### 📍 Passo 5: Criar Chave API

Após criar o projeto, você será redirecionado para uma página que mostra:

```
┌─────────────────────────────────────────────────────────────┐
│ API Keys                                                    │
│                                                             │
│ Project: aero-graph-project                                │
│                                                             │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ + Create API Key                                      │  │
│ │                                                       │  │
│ │ in new project    ← CLIQUE AQUI                      │  │
│ └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

Clique em **"Create API Key in new project"**

---

### 📍 Passo 6: Copiar a Chave

Pronto! Você verá sua chave API gerada:

```
┌─────────────────────────────────────────────────────────────┐
│ Your API Key                                                │
│                                                             │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ sk-AIzaSyD4gZ9mK3pL5q8vN2xY1aB7cD0eF3gH4iJ           │  │
│ │                                                       │  │
│ │ [Copy] ← CLIQUE PARA COPIAR                          │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                             │
│ Keep this key secure!                                       │
│ Do not share or commit to version control.                 │
└─────────────────────────────────────────────────────────────┘
```

**Clique em [Copy]** para copiar a chave para o clipboard

---

## 📝 Usando a Chave

### No Arquivo `.env` do Backend

1. Abra a pasta do projeto
2. Vá para: `backend/`
3. Procure o arquivo `.env`
4. Edite e adicione:

```env
GEMINI_API_KEY=sk-AIzaSyD4gZ9mK3pL5q8vN2xY1aB7cD0eF3gH4iJ
```

**Substitua** `sk-AIzaSyD4gZ9mK3pL5q8vN2xY1aB7cD0eF3gH4iJ` pela chave que você copiou

---

### No Render (Para Produção)

1. Acesse: https://render.com/dashboard
2. Clique no seu serviço "aero-graph-api"
3. Vá para **Settings** → **Environment**
4. Adicione variável:
   - **Key**: `GEMINI_API_KEY`
   - **Value**: Cole a chave que você copiou
5. Clique **Save**

```
┌─────────────────────────────────────────────────────────┐
│ Environment Variables                                   │
│                                                         │
│ Key              │ Value                               │
│ ─────────────────┼───────────────────────────────────  │
│ GEMINI_API_KEY   │ sk-AIzaSyD4gZ9mK3pL5q8vN2xY1aB...  │
│ NEO4J_URI        │ neo4j+s://86090040.databases...    │
│ NEO4J_USERNAME   │ neo4j                              │
│ NEO4J_PASSWORD   │ B89og2TnLbJgoY7UxfhF1IedvooH...   │
│                                                         │
│ [Save]                                                  │
└─────────────────────────────────────────────────────────┘
```

---

## ⚠️ Segurança - NÃO FAÇA ISSO!

### ❌ NUNCA:
- Compartilhe sua chave com outras pessoas
- Commite `.env` no GitHub
- Poste a chave em redes sociais
- Deixe visível em screenshots

### ✅ SEMPRE:
- Guarde em local seguro
- Use variáveis de ambiente
- Ignore `.env` no `.gitignore`
- Revogue a chave se vazar

---

## 🧪 Testar se Funciona

Após adicionar a chave no `.env`, teste:

```bash
cd backend

# Verificar se está tudo configurado
python test_config.py
```

Se funcionar, você verá:
```
1️⃣ Testing Neo4j Configuration...
   ✅ Neo4j connection successful!

2️⃣ Testing Google Generative AI (Gemini)...
   ✅ Gemini API working! Response: Hello...

...

✅ All configurations are valid!
```

---

## 🔄 Trocar ou Resetar a Chave

### Se você quer trocar:

1. Volte para: https://ai.google.dev
2. Vá para a sua chave
3. Clique em **Delete** (ícone de lixeira)
4. Crie uma nova chave
5. Atualize no `.env` e no Render

### Se você quer criar múltiplas chaves:

Você pode ter várias chaves para diferentes projetos:
- Uma para desenvolvimento local
- Uma para produção (Render)
- Uma para testes

---

## 📊 Limite Gratuito

A chave Gemini tem limites:

| Métrica | Limite |
|---------|--------|
| Requisições por minuto | 15 |
| Requisições por dia | 1.500 |
| Caracteres por requisição | Sem limite |
| Modelos disponíveis | gemini-1.5-flash, gemini-1.5-pro |

**Para aumentar o limite**: Coloque um cartão de crédito na Google Cloud (você continuará no free tier, mas terá mais requisições)

---

## 🆘 Problemas Comuns

### Erro: "GEMINI_API_KEY not configured"

**Causa**: A variável não foi adicionada

**Solução**:
```bash
# Verifique se .env existe
cd backend
cat .env

# Deve mostrar:
# GEMINI_API_KEY=sk-...

# Se não aparecer, adicione:
echo "GEMINI_API_KEY=sua-chave-aqui" >> .env
```

### Erro: "Invalid API Key"

**Causa**: Chave foi mal copiada ou expirou

**Solução**:
1. Gere uma nova chave em https://ai.google.dev
2. Copie novamente (sem espaços)
3. Atualize no `.env`

### Erro: "429 Too Many Requests"

**Causa**: Atingiu o limite de 15 requisições por minuto

**Solução**:
- Aguarde 1 minuto
- Ou aumentar limite colocando cartão de crédito

### Erro: "403 Permission Denied"

**Causa**: Pode ser de permissões no projeto Google

**Solução**:
1. Volte a https://ai.google.dev
2. Verifique se o projeto está ativo
3. Crie uma nova chave

---

## 📞 Resumo Rápido

```
1. Abra: https://ai.google.dev
2. Clique: Get API Key
3. Criar novo projeto
4. Clique: Create API Key in new project
5. Copie a chave
6. Cole no backend/.env
7. Pronto! ✅
```

---

**Tempo total: ~3 minutos**

Dúvidas? Leia `TROUBLESHOOTING.md`
