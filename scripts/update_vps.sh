#!/usr/bin/env bash
# ──────────
# REAN AI - GOOGLE CLOUD VPS AUTOMATED UPDATE & DEPLOYMENT SCRIPT
# ──────────
# Usage:
#   chmod +x scripts/update_vps.sh
#   ./scripts/update_vps.sh
# ──────────

set -e

# ANSI Color Codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 REAN AI - Google Cloud VPS Deployment Sync${NC}"
echo -e "${BLUE}──────────${NC}"

# 1. Navigate to Project Root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"
echo -e "${GREEN}📂 Working Directory:${NC} ${PROJECT_ROOT}"

# 2. Synchronize with GitHub Origin Main
echo -e "\n${YELLOW}📥 Pulling latest updates from origin/main...${NC}"
git fetch origin main
git reset --hard origin/main
git log -1 --oneline
echo -e "${GREEN}✅ Git repository synchronized successfully.${NC}"

# 3. Virtual Environment Detection & Activation
echo -e "\n${YELLOW}🐍 Checking Python environment...${NC}"
if [ -d "${PROJECT_ROOT}/.venv" ]; then
    PYTHON_BIN="${PROJECT_ROOT}/.venv/bin/python"
    source "${PROJECT_ROOT}/.venv/bin/activate"
    echo -e "${GREEN}✅ Activated virtualenv: .venv (${PYTHON_BIN})${NC}"
elif [ -d "${PROJECT_ROOT}/venv" ]; then
    PYTHON_BIN="${PROJECT_ROOT}/venv/bin/python"
    source "${PROJECT_ROOT}/venv/bin/activate"
    echo -e "${GREEN}✅ Activated virtualenv: venv (${PYTHON_BIN})${NC}"
else
    PYTHON_BIN="$(which python3 || which python)"
    echo -e "${YELLOW}⚠️ No local virtualenv found. Using system Python: ${PYTHON_BIN}${NC}"
fi

# 4. Dependency Verification & Installation
if [ -f "${PROJECT_ROOT}/requirements.txt" ]; then
    echo -e "\n${YELLOW}📦 Verifying Python dependencies...${NC}"
    "${PYTHON_BIN}" -m pip install -r "${PROJECT_ROOT}/requirements.txt" --quiet
    echo -e "${GREEN}✅ Dependencies verified.${NC}"
fi

# 5. System Integrity & Architecture Audit
echo -e "\n${YELLOW}🔍 Running Supreme Cognitive System Audit...${NC}"
"${PYTHON_BIN}" "${PROJECT_ROOT}/scripts/audit_system.py"
echo -e "${GREEN}✅ All architecture audits passed (100% PASS).${NC}"

# 6. Service Restart (systemd / pm2 / background process)
echo -e "\n${YELLOW}🔄 Restarting REAN AI Service...${NC}"

RESTARTED=false

# Method A: Check systemd services (rean-ai, polymath, polymath-bot, bot)
if command -v systemctl &> /dev/null; then
    for SVC in rean-ai polymath-bot polymath telegram-bot bot; do
        if sudo systemctl is-active --quiet "${SVC}" 2>/dev/null || sudo systemctl list-unit-files 2>/dev/null | grep -q "${SVC}.service"; then
            echo -e "${BLUE}⚙️ Restarting via systemctl (${SVC}.service)...${NC}"
            sudo systemctl restart "${SVC}"
            sudo systemctl status "${SVC}" --no-pager -n 5 || true
            RESTARTED=true
            break
        elif systemctl --user is-active --quiet "${SVC}" 2>/dev/null; then
            echo -e "${BLUE}⚙️ Restarting via user systemctl (${SVC}.service)...${NC}"
            systemctl --user restart "${SVC}"
            systemctl --user status "${SVC}" --no-pager -n 5 || true
            RESTARTED=true
            break
        fi
    done
fi

# Method B: pm2 process manager
if [ "$RESTARTED" = false ] && command -v pm2 &> /dev/null; then
    for APP in rean-ai polymath polymath-bot bot; do
        if pm2 list 2>/dev/null | grep -q "${APP}"; then
            echo -e "${BLUE}⚙️ Restarting via PM2 (${APP})...${NC}"
            pm2 restart "${APP}"
            RESTARTED=true
            break
        fi
    done
fi

# Method C: Background Process Manager (kill existing main.py and launch)
if [ "$RESTARTED" = false ]; then
    OLD_PIDS=$(pgrep -f "python.*main\.py" || true)
    if [ -n "$OLD_PIDS" ]; then
        echo -e "${YELLOW}🛑 Stopping previous main.py process (PID: ${OLD_PIDS})...${NC}"
        kill -15 $OLD_PIDS 2>/dev/null || kill -9 $OLD_PIDS 2>/dev/null || true
        sleep 2
    fi
    
    echo -e "${BLUE}🚀 Starting REAN AI Bot in background...${NC}"
    OWNER_USER=$(stat -c '%U' "${PROJECT_ROOT}/main.py" 2>/dev/null || whoami)
    if [ "$(whoami)" = "root" ] && [ "$OWNER_USER" != "root" ]; then
        su - "$OWNER_USER" -c "cd '${PROJECT_ROOT}' && nohup '${PYTHON_BIN}' main.py > '${PROJECT_ROOT}/rean_ai.log' 2>&1 &"
    else
        nohup "$PYTHON_BIN" "${PROJECT_ROOT}/main.py" > "${PROJECT_ROOT}/rean_ai.log" 2>&1 &
    fi
    sleep 2
    
    NEW_PID=$(pgrep -f "python.*main\.py" || true)
    if [ -n "$NEW_PID" ]; then
        echo -e "${GREEN}✅ REAN AI Bot is running smoothly in background (PID: ${NEW_PID}).${NC}"
        RESTARTED=true
    else
        echo -e "${RED}⚠️ Warning: Bot process could not be confirmed. Check ${PROJECT_ROOT}/rean_ai.log${NC}"
    fi
fi

echo -e "\n${GREEN}🎉 GOOGLE CLOUD VPS UPDATE COMPLETE & ACTIVE!${NC}"
echo -e "${GREEN}──────────${NC}"
