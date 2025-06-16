function initializeIframe(iframeId) {
    const iframe = document.getElementById(iframeId);
    if (iframe) {
        console.log(`Initializing iframe with ID: ${iframeId}`);
        iframe.onload = () => {
            console.log(`Iframe with ID: ${iframeId} loaded`);
            adjustIframeHeight(iframeId); // 高さ調整を実行
        };

        // ウィンドウサイズ変更時に高さを再調整
        window.addEventListener('resize', () => {
            console.log(`Window resized, adjusting iframe height for ID: ${iframeId}`);
            adjustIframeHeight(iframeId);
        });
    } else {
        console.error(`Iframe with ID: ${iframeId} not found`);
    }
}

function adjustAllIframeHeights() {
    const iframes = document.querySelectorAll("iframe");
    iframes.forEach(iframe => {
        const iframeId = iframe.id;
        if (iframeId) {
            console.log(`Adjusting height for iframe with ID: ${iframeId}`);
            adjustIframeHeight(iframeId);
        }
    });
}

function adjustIframeHeight(iframeId) {
    const iframe = document.getElementById(iframeId);
    if (iframe && iframe.contentWindow && iframe.contentWindow.document) {
        const iframeContentHeight = (iframe.contentWindow.document.body.scrollHeight || iframe.contentWindow.document.documentElement.scrollHeight) + 50; // 高さに50ピクセルを追加
        console.log(`Adjusting iframe height for ID: ${iframeId} to ${iframeContentHeight}px`);
        iframe.style.height = `${iframeContentHeight}px`;
    } else {
        console.warn(`Unable to adjust height for iframe with ID: ${iframeId}`);
    }
}

// ページ全体のロード完了後にすべてのiframeの高さを調整
window.onload = () => {
    console.log("Window.onload event triggered, adjusting all iframe heights");
    setTimeout(adjustAllIframeHeights, 100); // 100msの待機後に高さ調整を実行
};

// Export functions for use in HTML
export { initializeIframe, adjustIframeHeight, adjustAllIframeHeights };