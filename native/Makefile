.PHONY: setup-signing build package install run enable-login disable-login login-status clean open-accessibility doctor

APP_NAME := ActiveMenuBar
BUNDLE_ID := com.wiz.ActiveMenuBar
SIGN_IDENTITY := ActiveMenuBar Local Development
APP_DIR := $(APP_NAME).app
INSTALL_APP := $(HOME)/Applications/$(APP_NAME).app
BINARY := .build/release/$(APP_NAME)

setup-signing:
	./setup-signing.sh

build:
	swift build -c release

# A persistent certificate gives every rebuild the same designated requirement.
package: setup-signing build
	mkdir -p "$(APP_DIR)/Contents/MacOS"
	cp Info.plist "$(APP_DIR)/Contents/Info.plist"
	cp "$(BINARY)" "$(APP_DIR)/Contents/MacOS/$(APP_NAME)"
	codesign --force --sign "$(SIGN_IDENTITY)" --identifier "$(BUNDLE_ID)" "$(APP_DIR)"

# Install at a stable path and sign it with the same persistent identity.
install: package
	mkdir -p "$(HOME)/Applications"
	mkdir -p "$(INSTALL_APP)/Contents/MacOS"
	cp Info.plist "$(INSTALL_APP)/Contents/Info.plist"
	cp "$(BINARY)" "$(INSTALL_APP)/Contents/MacOS/$(APP_NAME)"
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
	rm -rf .build
	# Keep ~/Applications install + local .app so TCC entry stays valid.
