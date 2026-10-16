#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="MenuBarSpaces"
BUNDLE_ID="com.wiz.ActiveMenuBar"
DIST_DIR="${ROOT}/dist"
APP_PATH="${DIST_DIR}/${APP_NAME}.app"
STAGE_DIR="${DIST_DIR}/dmg-root"
VERSION="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "${ROOT}/Info.plist")"
DMG_PATH="${DIST_DIR}/${APP_NAME}-${VERSION}.dmg"
ENTITLEMENTS="${ROOT}/Distribution.entitlements"

die() {
    echo "error: $*" >&2
    exit 1
}

developer_identity() {
    if [[ -n "${DEVELOPER_ID_APPLICATION:-}" ]]; then
        printf '%s\n' "${DEVELOPER_ID_APPLICATION}"
        return
    fi

    local identities
    identities="$(security find-identity -v -p codesigning 2>/dev/null \
        | awk -F'"' '/Developer ID Application/ { print $2 }')"
    local count
    count="$(printf '%s\n' "${identities}" | awk 'NF { count++ } END { print count+0 }')"

    [[ "${count}" -eq 1 ]] || die \
        "Set DEVELOPER_ID_APPLICATION to your full 'Developer ID Application: …' identity."
    printf '%s\n' "${identities}"
}

require_tools() {
    for tool in swift lipo codesign hdiutil xcrun; do
        command -v "${tool}" >/dev/null || die "Required tool not found: ${tool}"
    done
}

build_arch() {
    local arch="$1"
    local triple="${arch}-apple-macosx13.0"
    local scratch="${ROOT}/.build/distribution-${arch}"

    swift build \
        --package-path "${ROOT}" \
        --configuration release \
        --scratch-path "${scratch}" \
        --triple "${triple}" >&2

    swift build \
        --package-path "${ROOT}" \
        --configuration release \
        --scratch-path "${scratch}" \
        --triple "${triple}" \
        --show-bin-path
}

create_dmg() {
    local identity="$1"

    rm -rf "${STAGE_DIR}"
    mkdir -p "${STAGE_DIR}"
    ditto "${APP_PATH}" "${STAGE_DIR}/${APP_NAME}.app"
    ln -s /Applications "${STAGE_DIR}/Applications"

    rm -f "${DMG_PATH}"
    hdiutil create \
        -volname "${APP_NAME}" \
        -srcfolder "${STAGE_DIR}" \
        -format UDZO \
        -ov \
        "${DMG_PATH}"

    codesign --force --timestamp --sign "${identity}" "${DMG_PATH}"
    rm -rf "${STAGE_DIR}"
}

build_release() {
    require_tools
    local identity
    identity="$(developer_identity)"

    echo "Using signing identity: ${identity}"
    rm -rf "${DIST_DIR}"
    mkdir -p "${APP_PATH}/Contents/MacOS" "${APP_PATH}/Contents/Resources"

    local arm_bin_dir x86_bin_dir
    arm_bin_dir="$(build_arch arm64)"
    x86_bin_dir="$(build_arch x86_64)"

    lipo -create \
        "${arm_bin_dir}/${APP_NAME}" \
        "${x86_bin_dir}/${APP_NAME}" \
        -output "${APP_PATH}/Contents/MacOS/${APP_NAME}"

    cp "${ROOT}/Info.plist" "${APP_PATH}/Contents/Info.plist"
    "${ROOT}/generate-icon.sh" "${APP_PATH}/Contents/Resources/AppIcon.icns"

    codesign \
        --force \
        --timestamp \
        --options runtime \
        --entitlements "${ENTITLEMENTS}" \
        --identifier "${BUNDLE_ID}" \
        --sign "${identity}" \
        "${APP_PATH}"

    codesign --verify --deep --strict --verbose=2 "${APP_PATH}"
    create_dmg "${identity}"

    echo
    echo "Developer ID release created:"
    echo "  ${DMG_PATH}"
    echo "Next: NOTARY_PROFILE=<profile> ./release.sh notarize"
}

notarize_release() {
    require_tools
    [[ -f "${DMG_PATH}" ]] || die "Build the DMG first: ./release.sh build"
    [[ -n "${NOTARY_PROFILE:-}" ]] || die \
        "Set NOTARY_PROFILE to a notarytool keychain profile."

    xcrun notarytool submit \
        "${DMG_PATH}" \
        --keychain-profile "${NOTARY_PROFILE}" \
        --wait

    xcrun stapler staple "${DMG_PATH}"
    xcrun stapler validate "${DMG_PATH}"
    spctl --assess --type open --context context:primary-signature --verbose=2 "${DMG_PATH}"

    echo
    echo "Notarized release ready:"
    echo "  ${DMG_PATH}"
}

show_status() {
    echo "Developer ID identities:"
    local identities
    identities="$(security find-identity -v -p codesigning 2>/dev/null \
        | awk '/Developer ID Application/')"
    if [[ -n "${identities}" ]]; then
        printf '%s\n' "${identities}"
    else
        echo "  (none installed)"
    fi
    echo
    echo "notarytool:"
    xcrun notarytool --version 2>/dev/null || echo "  (not available)"
    echo
    echo "Bundle ID: ${BUNDLE_ID}"
    echo "Version:   ${VERSION}"
}

case "${1:-status}" in
    build) build_release ;;
    notarize) notarize_release ;;
    all)
        build_release
        notarize_release
        ;;
    status) show_status ;;
    *)
        echo "Usage: $0 {status|build|notarize|all}"
        exit 2
        ;;
esac
