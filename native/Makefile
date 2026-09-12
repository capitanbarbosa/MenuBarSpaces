.PHONY: build package run clean open-accessibility doctor

APP_NAME := ActiveMenuBar
BUNDLE_ID := com.wiz.ActiveMenuBar
APP_DIR := $(APP_NAME).app
INSTALL_APP := $(HOME)/Applications/$(APP_NAME).app
BINARY := .build/release/$(APP_NAME)

build:
	swift build -c release

# Update the local .app in place (do not rm -rf — that breaks Accessibility TCC).
package: build
	mkdir -p "$(APP_DIR)/Contents/MacOS"
	cp Info.plist "$(APP_DIR)/Contents/Info.plist"
	cp "$(BINARY)" "$(APP_DIR)/Contents/MacOS/$(APP_NAME)"
	codesign --force --sign - --identifier "$(BUNDLE_ID)" "$(APP_DIR)/Contents/MacOS/$(APP_NAME)"
	codesign --force --sign - --identifier "$(BUNDLE_ID)" "$(APP_DIR)"

# Install to ~/Applications so System Settings has a stable path to grant.
install: package
	mkdir -p "$(HOME)/Applications"
	mkdir -p "$(INSTALL_APP)/Contents/MacOS"
	cp "$(APP_DIR)/Contents/Info.plist" "$(INSTALL_APP)/Contents/Info.plist"
	cp "$(APP_DIR)/Contents/MacOS/$(APP_NAME)" "$(INSTALL_APP)/Contents/MacOS/$(APP_NAME)"
	codesign --force --sign - --identifier "$(BUNDLE_ID)" "$(INSTALL_APP)/Contents/MacOS/$(APP_NAME)"
	codesign --force --sign - --identifier "$(BUNDLE_ID)" "$(INSTALL_APP)"

run: install
	pkill -x "$(APP_NAME)" || true
	sleep 0.3
	open "$(INSTALL_APP)"
	@echo ""
	@echo "Running: $(INSTALL_APP)"
	@echo "Enable Accessibility for ActiveMenuBar, then click 2/3/4."
	@echo "If you just toggled it on: Spaces → Quit, then make run again."

open-accessibility:
	open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"

doctor:
	@echo "Installed app: $(INSTALL_APP)"
	@ls -la "$(INSTALL_APP)/Contents/MacOS/$(APP_NAME)" 2>/dev/null || echo "(not installed yet — run make run)"
	@echo "Bundle id: $(BUNDLE_ID)"
	@echo "To reset Accessibility for this app:"
	@echo "  tccutil reset Accessibility $(BUNDLE_ID)"

clean:
	swift package clean
	rm -rf .build
	# Keep ~/Applications install + local .app so TCC entry stays valid.
