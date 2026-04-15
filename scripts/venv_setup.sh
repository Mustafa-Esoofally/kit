#!/bin/bash

############################################################################
#
#    Kit Virtual Environment Setup
#
#    Usage: ./scripts/venv_setup.sh
#
############################################################################

set -e

CURR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "${CURR_DIR}")"
VENV_DIR="${REPO_ROOT}/.venv"

# Colors
ORANGE='\033[38;5;208m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${ORANGE}"
cat << 'BANNER'
     █████╗  ██████╗ ███╗   ██╗ ██████╗
    ██╔══██╗██╔════╝ ████╗  ██║██╔═══██╗
    ███████║██║  ███╗██╔██╗ ██║██║   ██║
    ██╔══██║██║   ██║██║╚██╗██║██║   ██║
    ██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝
BANNER
echo -e "${NC}"
echo -e "    ${DIM}Virtual Environment Setup${NC}"
echo ""

# Preflight
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "    Deactivate your current venv first."
    exit 1
fi

if ! command -v uv &> /dev/null; then
    echo "    uv not found. Install: https://docs.astral.sh/uv/"
    exit 1
fi

# Setup
echo -e "    ${DIM}Removing old environment...${NC}"
echo -e "    ${DIM}> rm -rf ${VENV_DIR}${NC}"
rm -rf ${VENV_DIR}

echo ""
echo -e "    ${DIM}Creating Python 3.12 venv...${NC}"
echo -e "    ${DIM}> uv venv ${VENV_DIR} --python 3.12${NC}"
uv venv ${VENV_DIR} --python 3.12 --quiet

echo ""
echo -e "    ${DIM}Installing project in editable mode with dev dependencies...${NC}"
echo -e "    ${DIM}> uv pip install -e .[dev]${NC}"
VIRTUAL_ENV=${VENV_DIR} uv pip install -e ${REPO_ROOT}[dev] --quiet

# Copy activation command to clipboard
ACTIVATE_CMD="source .venv/bin/activate"
if command -v pbcopy &> /dev/null; then
    echo -n "${ACTIVATE_CMD}" | pbcopy
    CLIPBOARD_MSG="(Copied to clipboard)"
elif command -v xclip &> /dev/null; then
    echo -n "${ACTIVATE_CMD}" | xclip -selection clipboard
    CLIPBOARD_MSG="(Copied to clipboard)"
else
    CLIPBOARD_MSG=""
fi

echo ""
echo -e "    ${BOLD}Done.${NC}"
echo ""
echo -e "    ${DIM}Activate:${NC}  ${ACTIVATE_CMD} ${DIM}${CLIPBOARD_MSG}${NC}"
echo ""
