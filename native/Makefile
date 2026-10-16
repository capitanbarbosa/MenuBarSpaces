.PHONY: setup-signing build package install run enable-login disable-login login-status release-status release-dmg notarize release clean open-accessibility doctor

APP_NAME := MenuBarSpaces
BUNDLE_ID := com.wiz.ActiveMenuBar
SIGN_IDENTITY := ActiveMenuBar Local Development
APP_DIR := $(APP_NAME).app
INSTALL_APP := /Applications/$(APP_NAME).app
BINARY := .build/release/$(APP_NAME)
ICNS := .build/AppIcon.icns

setup-signing:
	./setup-signing.sh

build:
	swift build -c release

$(ICNS): AppIcon.png generate-icon.sh
	./generate-icon.sh "$(ICNS)"

# A persistent certificate gives every rebuild the same designated requirement.
package: setup-signing build $(ICNS)
	mkdir -p "$(APP_DIR)/Contents/MacOS" "$(APP_DIR)/Contents/Resources"
	cp Info.plist "$(APP_DIR)/Contents/Info.plist"
	cp "$(BINARY)" "$(APP_DIR)/Contents/MacOS/$(APP_NAME)"
	cp "$(ICNS)" "$(APP_DIR)/Contents/Resources/AppIcon.icns"
	codesign --force --sign "$(SIGN_IDENTITY)" --identifier "$(BUNDLE_ID)" "$(APP_DIR)"

# Install at a stable path and sign it with the same persistent identity.
install: package
	mkdir -p "$(INSTALL_APP)/Contents/MacOS" "$(INSTALL_APP)/Contents/Resources"
	cp Info.plist "$(INSTALL_APP)/Contents/Info.plist"
	cp "$(BINARY)" "$(INSTALL_APP)/Contents/MacOS/$(APP_NAME)"
	cp "$(ICNS)" "$(INSTALL_APP)/Contents/Resources/AppIcon.icns"
	codesign --force --sign "$(SIGN_IDENTITY)" --identifier "$(BUNDLE_ID)" "$(INSTALL_APP)"

run: install
	pkill -x "$(APP_NAME)" || true
	sleep 0.3
	open "$(INSTALL_APP)"
	@echo ""
	@echo "Running: $(INSTALL_APP)"
	@echo "Space switching uses Space API. Accessibility is optional (key fallback)."

enable-login: install
	./login-item.sh enable

disable-login:
	./login-item.sh disable

login-status:
	./login-item.sh status

release-status:
	./release.sh status

release-dmg:
	DEVELOPER_ID_APPLICATION="$(DEVELOPER_ID_APPLICATION)" ./release.sh build

notarize:
	NOTARY_PROFILE="$(NOTARY_PROFILE)" ./release.sh notarize

release:
	DEVELOPER_ID_APPLICATION="$(DEVELOPER_ID_APPLICATION)" NOTARY_PROFILE="$(NOTARY_PROFILE)" ./release.sh all

open-accessibility:
	open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"

doctor:
	@echo "Installed app: $(INSTALL_APP)"
	@ls -la "$(INSTALL_APP)/Contents/MacOS/$(APP_NAME)" 2>/dev/null || echo "(not installed yet — run make run)"
	@echo "Bundle id: $(BUNDLE_ID)"
	@echo "Expected signing identity: $(SIGN_IDENTITY)"
	@codesign -d -r- "$(INSTALL_APP)" 2>&1 || true
	@echo "To reset Accessibility for this app:"
	@echo "  tccutil reset Accessibility $(BUNDLE_ID)"

clean:
	swift package clean
	rm -rf .build dist
	# Keep /Applications install + local .app so TCC entry stays valid.
