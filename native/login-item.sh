#!/bin/bash
set -euo pipefail

LABEL="com.wiz.ActiveMenuBar"
APP_PATH="${HOME}/Applications/ActiveMenuBar.app"
PLIST_PATH="${HOME}/Library/LaunchAgents/${LABEL}.plist"
SERVICE="gui/$(id -u)/${LABEL}"

enable_login() {
    if [[ ! -d "${APP_PATH}" ]]; then
        echo "ActiveMenuBar is not installed at ${APP_PATH}."
        echo "Run 'make install' first."
        exit 1
    fi

    mkdir -p "${HOME}/Library/LaunchAgents"
    cat > "${PLIST_PATH}" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/open</string>
        <string>-g</string>
        <string>-j</string>
        <string>${APP_PATH}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>LimitLoadToSessionType</key>
    <string>Aqua</string>
</dict>
</plist>
EOF

    plutil -lint "${PLIST_PATH}"
    launchctl bootout "${SERVICE}" >/dev/null 2>&1 || true
    launchctl bootstrap "gui/$(id -u)" "${PLIST_PATH}"
    launchctl enable "${SERVICE}"
    echo "Launch at login enabled for ${APP_PATH}"
}

disable_login() {
    launchctl bootout "${SERVICE}" >/dev/null 2>&1 || true
    rm -f "${PLIST_PATH}"
    echo "Launch at login disabled"
}

show_status() {
    if launchctl print "${SERVICE}" >/dev/null 2>&1; then
        echo "Launch at login: enabled"
        echo "App: ${APP_PATH}"
        echo "LaunchAgent: ${PLIST_PATH}"
    else
        echo "Launch at login: disabled"
        exit 1
    fi
}

case "${1:-status}" in
    enable) enable_login ;;
    disable) disable_login ;;
    status) show_status ;;
    *)
        echo "Usage: $0 {enable|disable|status}"
        exit 2
        ;;
esac
