var iframe = document.createElement('iframe');
iframe.style.display = 'none';
document.body.appendChild(iframe);

// rescue console
window.console = iframe.contentWindow.console;

// rescue mouse operations
window.document.body.style.userSelect = 'auto'
document.oncontextmenu = iframe.contentWindow.document.oncontextmenu
document.onselectstart = iframe.contentWindow.document.onselectstart
document.oncopy = iframe.contentWindow.document.oncopy
document.oncut = iframe.contentWindow.document.oncut
