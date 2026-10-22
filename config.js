const SITE_CONFIG = {
    site: {
        name: "Quant.",
        title: "Quant. — Stock Analysis Tool | Swing Trading & Dividend Strategy",
        description: "Quant. — Professional stock analysis for US markets. Find best entry prices for Swing Trading and Dividend investing. SO, ED, O, WTRG.",
        keywords: "Quant, stock analysis, swing trading, dividend strategy, US stocks, SO stock, ED stock, O stock, WTRG stock, best entry price, yield calculation",
        url: "https://coalhunter.github.io/quant/",
        author: "Quant.",
        language: "en",
        themeColor: "#7c3aed",
        backgroundColor: "#f0f4f8"
    },

    verification: {
        google: "ISI_KODE_VERIFIKASI_GOOGLE_KAMU",
        bing: "",
        yandex: ""
    },

    adsense: {
        enabled: true,
        publisherId: "ca-pub-XXXXXXXXXXXXXXXX",

        slots: {
            topBanner: {
                enabled: true,
                adSlot: "1234567890",
                adFormat: "auto",
                fullWidthResponsive: true
            },
            betweenTabContent: {
                enabled: true,
                adSlot: "2345678901",
                adFormat: "fluid",
                fullWidthResponsive: true
            },
            bottomBanner: {
                enabled: true,
                adSlot: "3456789012",
                adFormat: "auto",
                fullWidthResponsive: true
            }
        },

        display: {
            showLabel: true,
            labelText: { id: "Iklan", en: "Ad" },
            labelFontSize: "11px",
            labelColor: "#94a3b8",
            marginVertical: "12px",
            padding: "8px",
            borderRadius: "8px",
            background: "#f8fafc",
            border: "1px solid #e2e8f0"
        }
    },

    defaultLanguage: "en",
    supportedLanguages: ["en", "id"]
};

function getAdSlot(slotName) {
    return SITE_CONFIG.adsense.slots[slotName] || null;
}

function isAdEnabled(slotName) {
    const adConfig = SITE_CONFIG.adsense;
    if (!adConfig.enabled) return false;
    const slot = adConfig.slots[slotName];
    return slot && slot.enabled;
}

function loadAdCode(slotId, containerId) {
    const adConfig = SITE_CONFIG.adsense;
    const slot = adConfig.slots[slotId];
    const container = document.getElementById(containerId);
    
    if (!container || !isAdEnabled(slotId)) {
        if (container) container.style.display = 'none';
        return;
    }

    container.style.display = 'block';
    
    const display = adConfig.display;
    container.style.background = display.background;
    container.style.borderRadius = display.borderRadius;
    container.style.padding = display.padding;
    container.style.margin = display.marginVertical;
    container.style.border = display.border;
    
    const content = document.getElementById(containerId + 'Content');
    if (content && adConfig.publisherId !== "ca-pub-XXXXXXXXXXXXXXXX") {
        content.innerHTML = `
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="${adConfig.publisherId}"
                 data-ad-slot="${slot.adSlot}"
                 data-ad-format="${slot.adFormat}"
                 data-full-width-responsive="${slot.fullWidthResponsive}"></ins>
        `;
    }
}

function applyMetaConfig() {
    if (SITE_CONFIG.verification.google) {
        let meta = document.querySelector('meta[name="google-site-verification"]');
        if (!meta) {
            meta = document.createElement('meta');
            meta.name = "google-site-verification";
            document.head.appendChild(meta);
        }
        meta.content = SITE_CONFIG.verification.google;
    }
}

if (typeof applyMetaConfig === 'function') {
    document.addEventListener('DOMContentLoaded', applyMetaConfig);
}
