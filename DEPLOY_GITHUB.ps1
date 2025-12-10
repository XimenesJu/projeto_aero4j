#!/usr/bin/env pwsh
# Deploy Script para GitHub - PowerShell
# Execute: .\DEPLOY_GITHUB.ps1

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          Script de Deploy - AeroGraph Analytics               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar se Git está instalado
try {
    git --version | Out-Null
    Write-Host "✅ Git encontrado`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Git não está instalado!`n" -ForegroundColor Red
    Write-Host "Baixe em: https://git-scm.com/download/win"
    exit
}

# Obter informações (preenchido por padrão com o repositório fornecido)
$defaultRepoUser = "XimenesJu"
$defaultRepoName = "projeto_aero4j"
$defaultRepoUrl = "https://github.com/$defaultRepoUser/$defaultRepoName.git"

$userInput = Read-Host "Pressione ENTER para usar o repositório padrão $defaultRepoUrl ou cole outro URL"
if ([string]::IsNullOrWhiteSpace($userInput)) {
    $repoUrl = $defaultRepoUrl
    $gitUser = $defaultRepoUser
    $repoName = $defaultRepoName
} else {
    $repoUrl = $userInput
    # Tentar extrair owner/name do URL
    if ($repoUrl -match "github.com[/|:](?<owner>[^/]+)/(?<repo>.+?)(\.git)?$") {
        $gitUser = $matches['owner']
        $repoName = $matches['repo'] -replace '\.git$',''
    } else {
        Write-Host "Não foi possível extrair usuário/repositório do URL. Você será solicitado a fornecer manualmente.`n"
        $gitUser = Read-Host "Seu usuário GitHub (ex: seu-usuario)"
        $repoName = Read-Host "Nome do repositório (ex: aero-graph-analytics)"
        $repoUrl = "https://github.com/$gitUser/$repoName.git"
    }
}

Write-Host "`n📍 Configurando:" -ForegroundColor Yellow
Write-Host "   Usuário: $gitUser"
Write-Host "   Repositório: $repoName"
Write-Host "   URL: $repoUrl`n"

# Verificar se já existe remote
$remoteExists = git remote -v 2>$null
if ($remoteExists) {
    Write-Host "❌ Git já foi inicializado" -ForegroundColor Red
    Write-Host "Removendo remote antigo...`n"
    git remote remove origin 2>$null
}

# Tentar criar o repositório remoto automaticamente (gh ou API)
Write-Host "`n🔎 Tentando criar o repositório remoto (se ainda não existir)..." -ForegroundColor Yellow

# If gh available, try to create repo and push
try {
    gh --version >$null 2>&1
    $ghAvailable = $true
} catch {
    $ghAvailable = $false
}

if ($ghAvailable) {
    Write-Host "GitHub CLI encontrado. Tentando criar/usar o repositório com 'gh'..." -ForegroundColor Green
    # gh repo create will fail if repo exists; ignore errors
    gh repo create "$gitUser/$repoName" --public --source="." --remote=origin --push 2>$null
} else {
    Write-Host "GitHub CLI não encontrado. Tentando criar com token via API (se fornecido)..." -ForegroundColor Yellow
    # If GITHUB_TOKEN env var exists, try to create repo
    $token = $env:GITHUB_TOKEN
    if ([string]::IsNullOrWhiteSpace($token)) {
        $token = Read-Host "Cole aqui um Personal Access Token (scopes: repo) para criar o repositório (ou deixe vazio para pular)"
    }
    if (-not [string]::IsNullOrWhiteSpace($token)) {
        $body = @{ name = $repoName; description = "AeroGraph Analytics"; @private = $false } | ConvertTo-Json
        try {
            $resp = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers @{ Authorization = "token $token"; Accept = "application/vnd.github+json" } -Body $body
            Write-Host "✅ Repositório criado via API: $($resp.full_name)" -ForegroundColor Green
            # Ensure origin remote points to the desired URL
            git remote remove origin 2>$null
            git remote add origin $repoUrl
        } catch {
            Write-Host "❌ Falha ao criar repositório via API: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "Se o repositório já existir, apenas prossiga; caso contrário, crie manualmente em: https://github.com/new" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Nenhum token fornecido; pulando tentativa de criação automática via API." -ForegroundColor Yellow
    }
}

# Inicializar Git
Write-Host "1️⃣  Inicializando Git..." -ForegroundColor Cyan
git init

# Adicionar remote
Write-Host "`n2️⃣  Adicionando repositório remoto..." -ForegroundColor Cyan
git remote add origin $repoUrl
git remote -v

# Criar .gitignore se não existir
if (!(Test-Path ".gitignore")) {
    Write-Host "`n3️⃣  Criando .gitignore..." -ForegroundColor Cyan
    $gitignoreContent = @"
# Environment variables
.env
*.env.local
backend/.env

# Python
__pycache__/
*.py[cod]
*`$py.class
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
"@
    $gitignoreContent | Out-File -Encoding UTF8 ".gitignore"
} else {
    Write-Host "`n3️⃣  .gitignore já existe" -ForegroundColor Cyan
}

# Adicionar arquivos
Write-Host "`n4️⃣  Adicionando arquivos..." -ForegroundColor Cyan
git add .

# Mostrar status
Write-Host "`n5️⃣  Status dos arquivos:" -ForegroundColor Cyan
git status

# Commit
Write-Host "`nDigite a mensagem de commit (padrão: Initial commit):"
$commitMsg = Read-Host "Mensagem"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "Initial commit - AeroGraph Analytics"
}

Write-Host "`n6️⃣  Fazendo commit..." -ForegroundColor Cyan
git commit -m $commitMsg

# Renomear branch
Write-Host "`n7️⃣  Configurando branch..." -ForegroundColor Cyan
git branch -M main

# Push
Write-Host "`n8️⃣  Enviando para GitHub..." -ForegroundColor Cyan
Write-Host "(Pode pedir seu GitHub token ou autenticação)`n"
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                      ✅ SUCESSO!                              ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green
    
    Write-Host "📍 Seu repositório está em:" -ForegroundColor Green
    Write-Host "   $repoUrl`n"
    
    Write-Host "🚀 Próximo passo:" -ForegroundColor Yellow
    Write-Host "   1. Abra https://render.com"
    Write-Host "   2. Clique em 'New Web Service'"
    Write-Host "   3. Conecte seu repositório GitHub"
    Write-Host "   4. Configure (ver: GITHUB_E_RENDER.md)`n"
} else {
    Write-Host "`n❌ Erro ao fazer push!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Se tiver erro de autenticação:"
    Write-Host "1. Acesse: https://github.com/settings/tokens"
    Write-Host "2. Generate new token"
    Write-Host "3. Cole o token como senha"
}

Write-Host ""
pause
