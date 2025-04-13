
const fs = require("fs");
const os = require("os");
const path = require("path");
const { ipcRenderer } = require("electron");

const configDir = path.join(os.homedir(), "Documents", "RippyRPC");
const configPath = path.join(configDir, "config.json");

let config = {
  clientId: "",
  state: "",
  details: "",
  filePath: "",
  buttons: [],
  largeImageKey: "",
  largeImageText: "",
  smallImageKey: "",
  smallImageText: "",
};


function loadConfig() {
  if (!fs.existsSync(configPath)) return;

  const data = fs.readFileSync(configPath, "utf-8");
  config = JSON.parse(data);

  document.getElementById("clientId").value = config.clientId || "";
  document.getElementById("state").value = config.state || "";
  document.getElementById("details").value = config.details || "";
  document.getElementById("filePath").value = config.filePath || "";

  if (config.buttons && config.buttons.length >= 2) {
    document.getElementById("b1Label").value = config.buttons[0].label;
    document.getElementById("b1Url").value = config.buttons[0].url;
    document.getElementById("b2Label").value = config.buttons[1].label;
    document.getElementById("b2Url").value = config.buttons[1].url;
  }

  document.getElementById("largeImageKey").value = config.largeImageKey || "";
  document.getElementById("largeImageText").value = config.largeImageText || "";
  document.getElementById("smallImageKey").value = config.smallImageKey || "";
  document.getElementById("smallImageText").value = config.smallImageText || "";

  ipcRenderer.send("check-startup");
}

function saveConfig() {
  config.clientId = document.getElementById("clientId").value;
  config.state = document.getElementById("state").value;
  config.details = document.getElementById("details").value;
  config.filePath = document.getElementById("filePath").value;

  config.buttons = [
    {
      label: document.getElementById("b1Label").value,
      url: document.getElementById("b1Url").value,
    },
    {
      label: document.getElementById("b2Label").value,
      url: document.getElementById("b2Url").value,
    },
  ];

  config.largeImageKey = document.getElementById("largeImageKey").value;
  config.largeImageText = document.getElementById("largeImageText").value;
  config.smallImageKey = document.getElementById("smallImageKey").value;
  config.smallImageText = document.getElementById("smallImageText").value;

  if (!fs.existsSync(configDir)) fs.mkdirSync(configDir);
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2), "utf-8");

  try {
    if (!fs.existsSync(configDir)) {
      fs.mkdirSync(configDir, { recursive: true });
      console.log("Created config directory:", configDir);
    }

    fs.writeFileSync(configPath, JSON.stringify(config, null, 2), "utf-8");
    console.log("Config saved to:", configPath);

    ipcRenderer.send("save-config", config);
  } catch (err) {
    console.error("Failed to save config:", err);
  }
}

function updateStatus(connected) {
  const status = document.getElementById("status");
  status.textContent = connected ? "RPC: 🟢 Connected" : "RPC: 🔴 Disconnected";
}

function updateRipDisplay() {
  if (!config.filePath) return;
  try {
    const raw = fs.readFileSync(config.filePath, "utf-8");
    const count = raw.trim();
    document.getElementById("ripCountDisplay").textContent = `Rips: ${count}`;
  } catch {
    document.getElementById("ripCountDisplay").textContent = "N/A";
  }
}

function adjustRip(action) {
  if (!config.filePath) return;
  let count = 0;
  try {
    count = parseInt(fs.readFileSync(config.filePath, "utf-8").trim()) || 0;
  } catch {}

  if (action === "inc") count++;
  if (action === "dec") count--;
  if (action === "reset") count = 0;

  fs.writeFileSync(config.filePath, count.toString(), "utf-8");
  updateRipDisplay();
  ipcRenderer.send("update-activity", count);
}

function startRPC() {
  saveConfig();
  ipcRenderer.send("start-rpc", config);
}

function stopRPC() {
  ipcRenderer.send("stop-rpc");
}

document.getElementById("startup").addEventListener("change", (e) => {
  ipcRenderer.send("set-startup", e.target.checked);
});

ipcRenderer.on("rpc-status", (_, status) => updateStatus(status));
ipcRenderer.on("startup-status", (_, isEnabled) => {
  document.getElementById("startup").checked = isEnabled;
});

loadConfig();
updateRipDisplay()
setInterval(updateRipDisplay, 5000);
