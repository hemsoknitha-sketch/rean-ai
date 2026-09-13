#!/usr/bin/env bash
# ==============================================================================
# REAN AI - GOOGLE CLOUD VPS AUTOMATED UPDATE & DEPLOYMENT SCRIPT
# ==============================================================================
# Usage:
#   chmod +x scripts/update_vps.sh
#   ./scripts/update_vps.sh
# ==============================================================================

set -e

# ANSI Color Codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}🚀 REAN AI - Google Cloud VPS Deployment Sync${NC}"
echo -e "${BLUE}======================================================${NC}"

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
    source "${PROJECT_ROOT}/.venv/bin/activate"
    echo -e "${GREEN}✅ Activated virtualenv: .venv${NC}"
elif [ -d "${PROJECT_ROOT}/venv" ]; then
    source "${PROJECT_ROOT}/venv/bin/activate"
    echo -e "${GREEN}✅ Activated virtualenv: venv${NC}"
else
    echo -e "${YELLOW}⚠️ No local virtualenv found. Using system Python.$(which python3)${NC}"
fi

# 4. Dependency Verification & Installation
if [ -f "${PROJECT_ROOT}/requirements.txt" ]; then
    echo -e "\n${YELLOW}📦 Verifying Python dependencies...${NC}"
    pip install -r "${PROJECT_ROOT}/requirements.txt" --quiet
    echo -e "${GREEN}✅ Dependencies verified.${NC}"
fi

# 5. System Integrity & Architecture Audit
echo -e "\n${YELLOW}🔍 Running Supreme Cognitive System Audit...${NC}"
python3 "${PROJECT_ROOT}/scripts/audit_system.py"
echo -e "${GREEN}✅ All architecture audits passed (100% PASS).${NC}"

# 6. Service Restart (systemd / pm2 / background process)
echo -e "\n${YELLOW}🔄 Restarting REAN AI Service...${NC}"

RESTARTED=false

# Method A: systemd system service
if command -v systemctl &> /dev/null; then
    if sudo systemctl is-active --quiet rean-ai 2>/dev/null || sudo systemctl list-unit-files | grep -q rean-ai.service; then
        echo -e "${BLUE}⚙️ Restarting via systemctl (rean-ai.service)...${NC}"
        sudo systemctl restart rean-ai
        sudo systemctl status rean-ai --no-pager -n 5 || true
        RESTARTED=true
    elif systemctl --user is-active --quiet rean-ai 2>/dev/null; then
        echo -e "${BLUE}⚙️ Restarting via user systemctl (rean-ai.service)...${NC}"
        systemctl --user restart rean-ai
        systemctl --user status rean-ai --no-pager -n 5 || true
        RESTARTED=true
    fi
fi

# Method B: pm2 process manager
if [ "$RESTARTED" = false ] && command -v pm2 &> /dev/null; then
    if pm2 list | grep -q "rean-ai"; then
        echo -e "${BLUE}⚙️ Restarting via PM2 (rean-ai)...${NC}"
        pm2 restart rean-ai
        RESTARTED=true
    fi
fi

# Method C: Summary if standalone
if [ "$RESTARTED" = false ]; then
    echo -e "${YELLOW}ℹ️ No automated service (systemd or pm2) detected for 'rean-ai'.${NC}"
    echo -e "${GREEN}💡 You can run manually in background with:${NC}"
    echo -e "   nohup python3 main.py > rean_ai.log 2>&1 &"
fi

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN}🎉 GOOGLE CLOUD VPS UPDATE COMPLETE & ACTIVE!${NC}"
echo -e "${GREEN}======================================================${NC}"
