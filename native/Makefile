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

# Install to ~/Applications. Only replace/resign when the binary actually changed,
# so Accessibility TCC is less likely to go stale after every make run.
install: package
	mkdir -p "$(HOME)/Applications"
	mkdir -p "$(INSTALL_APP)/Contents/MacOS"
	@src="$(APP_DIR)/Contents/MacOS/$(APP_NAME)"; \
	dst="$(INSTALL_APP)/Contents/MacOS/$(APP_NAME)"; \
	if [ -f "$$dst" ] && cmp -s "$$src" "$$dst"; then \
		echo "Install up to date (binary unchanged) — keeping existing signature/TCC."; \
		cp Info.plist "$(INSTALL_APP)/Contents/Info.plist"; \
	else \
		echo "Updating installed app binary…"; \
		cp Info.plist "$(INSTALL_APP)/Contents/Info.plist"; \
		cp "$$src" "$$dst"; \
		codesign --force --sign - --identifier "$(BUNDLE_ID)" "$$dst"; \
		codesign --force --sign - --identifier "$(BUNDLE_ID)" "$(INSTALL_APP)"; \
		echo "NOTE: binary changed — if Accessibility shows ON but popup says OFF, toggle it OFF/ON once."; \
	fi

run: install
	pkill -x "$(APP_NAME)" || true
	sleep 0.3
	open "$(INSTALL_APP)"
	@echo ""
	@echo "Running: $(INSTALL_APP)"
	@echo "Space switching uses Space API. Accessibility is optional (key fallback)."

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
