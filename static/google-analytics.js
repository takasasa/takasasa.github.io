(function() {
    const measurementId = process.env.GA_MEASUREMENT_ID;
    if (!measurementId) {
        console.error('Google Analytics Measurement ID is not set in environment variables.');
        return;
    }

    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
    document.head.appendChild(script);

    window.dataLayer = window.dataLayer || [];
    function gtag() {
        dataLayer.push(arguments);
    }
    gtag('js', new Date());
    gtag('config', measurementId);
})();
