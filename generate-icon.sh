#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SOURCE="${ROOT}/AppIcon.png"
ICONSET="${ROOT}/.build/AppIcon.iconset"
ICNS="${1:-${ROOT}/.build/AppIcon.icns}"

mkdir -p "$(dirname "${ICNS}")" "${ICONSET}"
rm -rf "${ICONSET}"
mkdir -p "${ICONSET}"

sips -z 16 16 "${SOURCE}" --out "${ICONSET}/icon_16x16.png" >/dev/null
sips -z 32 32 "${SOURCE}" --out "${ICONSET}/icon_16x16@2x.png" >/dev/null
sips -z 32 32 "${SOURCE}" --out "${ICONSET}/icon_32x32.png" >/dev/null
sips -z 64 64 "${SOURCE}" --out "${ICONSET}/icon_32x32@2x.png" >/dev/null
sips -z 128 128 "${SOURCE}" --out "${ICONSET}/icon_128x128.png" >/dev/null
sips -z 256 256 "${SOURCE}" --out "${ICONSET}/icon_128x128@2x.png" >/dev/null
sips -z 256 256 "${SOURCE}" --out "${ICONSET}/icon_256x256.png" >/dev/null
sips -z 512 512 "${SOURCE}" --out "${ICONSET}/icon_256x256@2x.png" >/dev/null
sips -z 512 512 "${SOURCE}" --out "${ICONSET}/icon_512x512.png" >/dev/null
sips -z 1024 1024 "${SOURCE}" --out "${ICONSET}/icon_512x512@2x.png" >/dev/null

iconutil -c icns "${ICONSET}" -o "${ICNS}"
