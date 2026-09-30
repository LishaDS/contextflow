chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "send-to-contextflow",
        title: "Send to ContextFlow",
        contexts: ["selection"]
    });
});

chrome.contextMenus.onClicked.addListener((info) => {
    if (info.menuItemId === "send-to-contextflow" && info.selectionText) {
        chrome.storage.local.set({
            selectedContext: info.selectionText
        });

        chrome.notifications.create({
            type: "basic",
            iconUrl: "icon.png",
            title: "ContextFlow",
            message: "Your selected context was sent to ContextFlow."
        });
    }
});
