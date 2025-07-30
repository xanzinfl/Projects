const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    getNext420: () => ipcRenderer.invoke('get-next-420'),
    notify420: (notificationText) => ipcRenderer.send('notify-420', notificationText),
    getSettings: () => ipcRenderer.invoke('get-settings'),
    saveSettings: (settings) => ipcRenderer.send('save-settings', settings),
    closeApp: () => ipcRenderer.send('close-app'),
});