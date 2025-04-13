const { app, BrowserWindow, Tray, Menu, ipcMain, shell } = require("electron");
const fs = require("fs");
const path = require("path");
const RPC = require("discord-rpc");

app.disableHardwareAcceleration();

let win, tray, rpc, activityInterval;
let config = {};
let isConnected = false;

function createWindow() {
  win = new BrowserWindow({
    width: 600,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  win.loadFile("index.html");

  win.on("minimize", (e) => {
    e.preventDefault();
    win.hide();
  });

  createTray();
}

function createTray() {
  tray = new Tray(path.join(__dirname, "icon.png"));
  const contextMenu = Menu.buildFromTemplate([
    { label: "Show", click: () => win.show() },
    {
      label: "Start RPC",
      click: () => {
        if (config.clientId) startRPC(config);
      },
    },
    {
      label: "Stop RPC",
      click: () => stopRPC(),
    },
    { type: "separator" },
    { label: "Quit", click: () => app.quit() },
  ]);
  tray.setToolTip("StonerRPC");
  tray.setContextMenu(contextMenu);
}

const updateActivity = () => {
  let rip = "0";
  try {
    rip = fs.readFileSync(config.filePath, "utf-8").trim();
  } catch {}

  const presence = {
    state: config.state,
    details: config.details.replace("{rip}", rip),
    startTimestamp: Date.now(),
    instance: false,
    buttons: config.buttons?.filter(b => b.label && b.url),
    assets: {}
  };
  
  if (config.largeImageKey) presence.assets.largeImageKey = config.largeImageKey;
  if (config.largeImageText) presence.assets.largeImageText = config.largeImageText;
  if (config.smallImageKey) presence.assets.smallImageKey = config.smallImageKey;
  if (config.smallImageText) presence.assets.smallImageText = config.smallImageText;
  
  rpc.setActivity(presence);
};

function startRPC(newConfig) {
  config = newConfig;

  if (!RPC) return;

  rpc = new RPC.Client({ transport: "ipc" });
  RPC.register(config.clientId);

  rpc.on("ready", () => {
    isConnected = true;
    win.webContents.send("rpc-status", true);
    updateActivity();
    activityInterval = setInterval(updateActivity, 15_000);
  });

  rpc.login({ clientId: config.clientId }).catch(console.error);
}

function stopRPC() {
  if (rpc) {
    rpc.clearActivity();
    rpc.destroy();
    rpc = null;
  }

  if (activityInterval) clearInterval(activityInterval);
  isConnected = false;
  win?.webContents?.send("rpc-status", false);
}

ipcMain.on("start-rpc", (_, data) => startRPC(data));
ipcMain.on("stop-rpc", stopRPC);
ipcMain.on("update-activity", () => {
  if (isConnected) updateActivity();
});


const startupFolder = path.join(
  process.env.APPDATA,
  "Microsoft\\Windows\\Start Menu\\Programs\\Startup"
);
const shortcutPath = path.join(startupFolder, "RippyRPC.lnk");

ipcMain.on("set-startup", (_, enable) => {
  const exePath = process.execPath;

  if (enable) {
    try {
      const shortcutOptions = {
        target: exePath,
        args: "",
        description: "Stoner RPC",
        icon: exePath,
      };
      shell.writeShortcutLink(shortcutPath, shortcutOptions);
      console.log("Added to startup successfully");
    } catch (err) {
      console.error("Failed to set startup:", err);
    }
  } else {
    try {
      if (fs.existsSync(shortcutPath)) {
        fs.unlinkSync(shortcutPath);
        console.log("Removed from startup successfully");
      }
    } catch (err) {
      console.error("Failed to remove from startup:", err);
    }
  }
});

ipcMain.on("check-startup", (event) => {
  const startupExists = fs.existsSync(shortcutPath);
  event.reply("startup-status", startupExists);
});

app.whenReady().then(() => {
  createWindow();
});
