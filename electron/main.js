const { app, BrowserWindow, screen } = require("electron");
const path = require("path");

function createWindow() {
  const { width } = screen.getPrimaryDisplay().bounds; // Use bounds, not workAreaSize
  const menuBarHeight = 30;
  const win = new BrowserWindow({
    x: 0,
    y: 0,
    width: width,
    height: menuBarHeight,
    frame: false,
    transparent: false,
    alwaysOnTop: true,
    resizable: false,
    movable: false,
    skipTaskbar: true,
    fullscreenable: false,
    focusable: false, // Prevents stealing focus
    hasShadow: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });
  win.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
  win.loadFile("index.html");
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
