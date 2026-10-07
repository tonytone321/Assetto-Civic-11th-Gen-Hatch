#!/usr/bin/env bash
# One-time sandbox setup for research scripts: Python packages and browser CA trust.
set -euo pipefail
pip3 install -q playwright pymupdf pillow numpy scipy opencv-python-headless beautifulsoup4 lxml soundfile matplotlib requests pytest
if ! command -v certutil >/dev/null; then apt-get install -y -q libnss3-tools || (apt-get update -q && apt-get install -y -q libnss3-tools); fi
mkdir -p "$HOME/.pki/nssdb"
if [ -f /root/.ccr/agent-proxy-ca.crt ] && ! certutil -d "sql:$HOME/.pki/nssdb" -L | grep -q ccr-agent-proxy; then
  certutil -d "sql:$HOME/.pki/nssdb" -A -t "C,," -n ccr-agent-proxy -i /root/.ccr/agent-proxy-ca.crt
fi
echo "setup ok"
