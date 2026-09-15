#!/bin/bash
set -euo pipefail

IDENTITY="ActiveMenuBar Local Development"
KEYCHAIN="${HOME}/Library/Keychains/login.keychain-db"

if security find-identity -v -p codesigning "$KEYCHAIN" | grep -Fq "\"${IDENTITY}\""; then
    echo "Signing identity already available: ${IDENTITY}"
    exit 0
fi

if security find-certificate -c "${IDENTITY}" "${KEYCHAIN}" >/dev/null 2>&1; then
    echo "A certificate named '${IDENTITY}' exists but is not a valid signing identity."
    echo "Delete that certificate and its private key in Keychain Access, then rerun this script."
    exit 1
fi

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT
PASSWORD="$(uuidgen)"

openssl req \
    -newkey rsa:2048 \
    -x509 \
    -sha256 \
    -days 3650 \
    -nodes \
    -subj "/CN=${IDENTITY}" \
    -addext "keyUsage=critical,digitalSignature" \
    -addext "extendedKeyUsage=codeSigning" \
    -keyout "${WORK_DIR}/key.pem" \
    -out "${WORK_DIR}/certificate.pem"

openssl pkcs12 \
    -export \
    -name "${IDENTITY}" \
    -inkey "${WORK_DIR}/key.pem" \
    -in "${WORK_DIR}/certificate.pem" \
    -out "${WORK_DIR}/identity.p12" \
    -passout "pass:${PASSWORD}"

security import "${WORK_DIR}/identity.p12" \
    -k "${KEYCHAIN}" \
    -P "${PASSWORD}" \
    -T /usr/bin/codesign \
    -T /usr/bin/security

security add-trusted-cert \
    -d \
    -r trustRoot \
    -p codeSign \
    -k "${KEYCHAIN}" \
    "${WORK_DIR}/certificate.pem"

if ! security find-identity -v -p codesigning "${KEYCHAIN}" | grep -Fq "\"${IDENTITY}\""; then
    echo "The certificate was imported but is not trusted for code signing."
    echo "Open Keychain Access, find '${IDENTITY}', and set Code Signing to Always Trust."
    exit 1
fi

echo "Created persistent signing identity: ${IDENTITY}"
