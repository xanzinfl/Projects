const { app, BrowserWindow, ipcMain, Tray, Menu, nativeImage } = require('electron');
const path = require('path');
const Store = require('electron-store');
const moment = require('moment-timezone');
const notifier = require('node-notifier');

let mainWindow;
let tray = null;
const store = new Store();

function handleStartup() {
    if (process.platform !== 'darwin') {
        app.setLoginItemSettings({
            openAtLogin: store.get('runOnStartup', false),
            path: app.getPath('exe'),
        });
    }
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 420,
        height: 350,
        resizable: false,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
        },
        frame: true,
        backgroundColor: '#2D2D2D',
        show: false
    });

    mainWindow.loadFile('index.html');
    mainWindow.removeMenu();

    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    mainWindow.on('close', (event) => {
        if (store.get('minimizeToTray', false) && !app.isQuitting) {
            event.preventDefault();
            mainWindow.hide();
            createTray();
        } else {
            app.quit();
        }
    });

    handleStartup();
}

function createTray() {
    if (tray) return;
    const iconPath = path.join(__dirname, 'assets/icon.png');
    const icon = nativeImage.createFromPath(iconPath);
    tray = new Tray(icon);
    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'Show App',
            click: () => {
                mainWindow.show();
                tray.destroy();
                tray = null;
            },
        },
        {
            label: 'Quit',
            click: () => {
                app.isQuitting = true;
                app.quit();
            },
        },
    ]);
    tray.setToolTip('420 Finder');
    tray.setContextMenu(contextMenu);
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    } else {
        mainWindow.show();
    }
});

ipcMain.handle('get-next-420', () => {
    const now = moment.utc();
    const timezones = moment.tz.names();
    let next420Info = {};
    let minTimeUntil = null;

    const systemTz = moment.tz.guess();

    for (const tzName of timezones) {
        const localizedNow = now.clone().tz(tzName);
        let next420Time;

        const am420 = localizedNow.clone().hour(4).minute(20).second(0);
        const pm420 = localizedNow.clone().hour(16).minute(20).second(0);

        if (localizedNow.isBefore(am420)) {
            next420Time = am420;
        } else if (localizedNow.isBefore(pm420)) {
            next420Time = pm420;
        } else {
            next420Time = localizedNow.clone().add(1, 'day').hour(4).minute(20).second(0);
        }

        const timeUntil = next420Time.diff(now);

        if (minTimeUntil === null || timeUntil < minTimeUntil) {
            minTimeUntil = timeUntil;
            next420Info = {
                next420TimeUtc: next420Time.clone().utc().toISOString(),
                timezone: tzName.replace(/_/g, ' '),
                localTime: next420Time.clone().tz(systemTz).format('h:mm A'),
            };
        }
    }
    return next420Info;
});

ipcMain.on('notify-420', (event, notificationText) => {
    notifier.notify({
        title: "It's 4:20!",
        message: notificationText || "It's 4:20 somewhere!",
        icon: path.join(__dirname, 'assets/icon.png'),
        sound: true,
    });
});

ipcMain.handle('get-settings', () => {
    return {
        minimizeToTray: store.get('minimizeToTray', false),
        notificationText: store.get('notificationText', "It's 4:20 somewhere!"),
        runOnStartup: store.get('runOnStartup', false),
    };
});

ipcMain.on('save-settings', (event, settings) => {
    store.set('minimizeToTray', settings.minimizeToTray);
    store.set('notificationText', settings.notificationText);
    store.set('runOnStartup', settings.runOnStartup);
    handleStartup();
});