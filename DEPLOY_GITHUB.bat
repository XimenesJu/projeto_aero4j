@echo off
REM DEPLOY_GITHUB.bat
REM Criado para configurar remote e enviar o projeto ao repositório GitHub existente

setlocal EnableDelayedExpansion

REM Default repository (supplied by user)
set DEFAULT_REPO_URL=https://github.com/XimenesJu/projeto_aero4j.git

echo ==================================================
echo    DEPLOY - Enviar projeto para GitHub remoto
echo ==================================================
echo.

REM Check for git
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Git nao encontrado. Instale Git e tente novamente: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Ask for remote URL (default provided)
set /p REPO_URL="URL do repositório remoto (ENTER para usar %DEFAULT_REPO_URL%): "
if "%REPO_URL%"=="" set REPO_URL=%DEFAULT_REPO_URL%

echo.
echo Usando remote: %REPO_URL%

REM Initialize git repo if not present
if not exist .git (
    echo Inicializando repositório git local...
    git init || (
        echo ❌ Falha ao executar 'git init'
        pause
        exit /b 1
    )
) else (
    echo .git já existe — repositório já inicializado localmente
)

REM Remove existing origin if present and set the provided one
git remote remove origin 2>nul
git remote add origin %REPO_URL% 2>nul || (
    echo Atualizando URL do remote origin...
    git remote set-url origin %REPO_URL%
)

echo.
echo Verificando .gitignore
if not exist ".gitignore" (
    echo Criando .gitignore básico...
    >.gitignore echo # Environment
    >>.gitignore echo .env
    >>.gitignore echo backend/.env
    >>.gitignore echo node_modules/
    >>.gitignore echo __pycache__/
    >>.gitignore echo .venv/
)

echo.
echo Adicionando arquivos ao staging...
git add .

set /p COMMIT_MSG="Mensagem do commit (ENTER = 'Initial commit'): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Initial commit

REM Commit (allow empty commit if nothing changed)
git commit -m "%COMMIT_MSG%" 2>nul || (
    echo Nenhum novo arquivo para commitar ou commit falhou; prosseguindo.
)

echo.
echo Enviando para %REPO_URL% (branch main)...
git branch -M main 2>nul

REM Try normal push (will open credential prompt if needed)
git push -u origin main
if %errorlevel% equ 0 (
    echo.
    echo ✅ Projeto enviado com sucesso para %REPO_URL%
    pause
    exit /b 0
)

echo.
echo ❌ Falha ao enviar automaticamente (erro de autenticação ou configuração).
echo Opcões para resolver:
echo 1) Autenticar localmente com 'gh auth login' (GitHub CLI) e executar novamente.
echo 2) Criar um Personal Access Token em https://github.com/settings/tokens com escopo 'repo',
echo    e usar a URL com token (temporariamente) para push:
echo.
echo    git push -u https://<TOKEN>@github.com/XimenesJu/projeto_aero4j.git main
echo.
echo 3) Configurar credential helper do Git (Windows Credential Manager) para salvar credenciais.
echo.
echo Após resolver a autenticação, execute novamente este script.
pause
exit /b 1
@echo off
REM Deploy Script para GitHub e Render
REM Execute este arquivo para fazer upload automático
REM Execute este arquivo para fazer upload automático
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          Script de Deploy - AeroGraph Analytics               ║╗
echo ╚════════════════════════════════════════════════════════════════╝
echo.╚════════════════════════════════════════════════════════════════╝
echo.
REM Verificar se Git está instalado
where git >nul 2>nul está instalado
if %errorlevel% neq 0 (
    echo ❌ Git não está instalado!
    echo.❌ Git não está instalado!
    echo Baixe em: https://git-scm.com/download/win
    pauseBaixe em: https://git-scm.com/download/win
    exit /b 1
)   exit /b 1
)
echo ✅ Git encontrado
echo ✅ Git encontrado
REM Obter informações
set /p GITHUB_USER="Seu usuário GitHub (ex: seu-usuario): "
set /p REPO_NAME="Nome do repositório (ex: aero-graph-analytics): "
set /p REPO_URL=https://github.com/%GITHUB_USER%/%REPO_NAME%.git: "
set /p REPO_URL=https://github.com/%GITHUB_USER%/%REPO_NAME%.git
echo.
echo 📍 Configurando:
echo    Usuário: %GITHUB_USER%
echo    Repositório: %REPO_NAME%
echo    URL: %REPO_URL%EPO_NAME%
echo.   URL: %REPO_URL%
echo.
REM Verificar se já existe remote
git remote -v >nul 2>nulte remote
if %errorlevel% equ 0 (l
    echo ❌ Git já foi inicializado
    echo.❌ Git já foi inicializado
    echo Removendo remote antigo...
    git remote remove origin 2>nul.
)   git remote remove origin 2>nul
)
REM Inicializar Git
echo.nicializar Git
echo 1️⃣  Inicializando Git...
git init  Inicializando Git...
git init
REM Adicionar remote
echo 2️⃣  Adicionando repositório remoto...
git remote add origin %REPO_URL%o remoto...
git remote -vd origin %REPO_URL%
git remote -v
REM Criar .gitignore se não existir
if not exist ".gitignore" ( existir
    echo 3️⃣  Criando .gitignore...
    (cho 3️⃣  Criando .gitignore...
        echo # Environment variables
        echo .envvironment variables
        echo *.env.local
        echo backend/.env
        echo.backend/.env
        echo # Python
        echo __pycache__/
        echo *.py[cod]__/
        echo *$py.class
        echo *.so.class
        echo .Python
        echo venv/on
        echo env//
        echo .venv
        echo..venv
        echo # Node
        echo node_modules/
        echo npm-debug.log
        echo yarn-error.log
        echo .nexterror.log
        echo build/
        echo dist//
        echo.dist/
        echo # IDE
        echo .vscode/
        echo .idea/e/
        echo *.swp/
        echo *.swo
        echo.*.swo
        echo # OS
        echo .DS_Store
        echo Thumbs.db
    ) > .gitignores.db
) else (.gitignore
    echo 3️⃣  .gitignore já existe
)   echo 3️⃣  .gitignore já existe
)
REM Adicionar arquivos
echo 4️⃣  Adicionando arquivos...
git add . Adicionando arquivos...
git add .
REM Mostrar status
echo.ostrar status
echo 5️⃣  Status dos arquivos:
git statusStatus dos arquivos:
echo.tatus
echo.
REM Commit
set /p COMMIT_MSG="Mensagem de commit (padrão: Initial commit): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Initial commit - AeroGraph Analytics
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Initial commit - AeroGraph Analytics
echo 6️⃣  Fazendo commit...
git commit -m "%COMMIT_MSG%"
git commit -m "%COMMIT_MSG%"
REM Renomear branch
echo 7️⃣  Configurando branch...
git branch -M mainando branch...
git branch -M main
REM Push
echo 8️⃣  Enviando para GitHub...
echo.8️⃣  Enviando para GitHub...
echo AGUARDE - pode pedir seu GitHub token...
echo.AGUARDE - pode pedir seu GitHub token...
git push -u origin main
git push -u origin main
if %errorlevel% equ 0 (
    echo.level% equ 0 (
    echo ╔════════════════════════════════════════════════════════════════╗
    echo ║                      ✅ SUCESSO!                              ║═╗
    echo ╚════════════════════════════════════════════════════════════════╝
    echo.╚════════════════════════════════════════════════════════════════╝
    echo 📍 Seu repositório está em:
    echo    %REPO_URL%tório está em:
    echo.   %REPO_URL%
    echo 🚀 Próximo passo:
    echo    1. Abra https://render.com
    echo    2. Clique em "New Web Service"
    echo    3. Conecte seu repositório GitHub
    echo    4. Configure (ver: GITHUB_E_RENDER.md)
    echo.   4. Configure (ver: GITHUB_E_RENDER.md)
) else (.
    echo.
    echo ❌ Erro ao fazer push!
    echo.❌ Erro ao fazer push!
    echo Se tiver erro de autenticação:
    echo 1. Acesse: https://github.com/settings/tokens
    echo 2. Generate new tokenthub.com/settings/tokens
    echo 3. Cole o token como senha
    echo.3. Cole o token como senha
)   echo.
)
pause
echo.pause


echo 👉 Duplo clique em: DEPLOY_GITHUB.bat