// ═══════════════════════════════════════════════════════════
// ⚙️ KONFIGURASI UTAMA — Edit file ini saja!
// ═══════════════════════════════════════════════════════════

const SITE_CONFIG = {
    // ──────────────────────────────────────────────
    // 🌐 INFORMASI SITUS — SEO
    // ──────────────────────────────────────────────
    site: {
        name: "Stock Analysis Tool",
        title: "Stock Analysis Tool — Swing Trading & Dividend Strategy",
        description: "Free stock analysis tool focusing on Swing Trading technical analysis and Dividend Strategy. Find best buy price for SO, ED, O, WTRG stocks.",
        keywords: "stock analysis, swing trading, dividend strategy, best buy price, high yield stocks, technical analysis, SO stock, ED stock, O stock, WTRG stock",
        url: "https://coalhunter.github.io/quant/",
        logo: "https://coalhunter.github.io/quant/favicon.ico",
        author: "Coalhunter",
        language: "en",
        themeColor: "#7c3aed",
        backgroundColor: "#f0f4f8"
    },

    // ──────────────────────────────────────────────
    // ✅ VERIFIKASI GOOGLE & ALAT WEBMASTER
    // ──────────────────────────────────────────────
    verification: {
        google: "ISI_KODE_VERIFIKASI_GOOGLE_KAMU",
        bing: "",
        yandex: ""
    },

    // ──────────────────────────────────────────────
    // 📢 GOOGLE ADSENSE — PENGATURAN LENGKAP
    // Semua kode iklan HANYA diatur di sini
    // ──────────────────────────────────────────────
    adsense: {
        enabled: true,                          // Aktifkan/matikan SEMUA iklan sekaligus
        publisherId: "ca-pub-XXXXXXXXXXXXXXXX", // Ganti dengan Pub-Id kamu
        
        // Lokasi iklan
        slots: {
            topBanner: {
                enabled: true,
                adSlot: "1234567890",
                adFormat: "auto",
                fullWidthResponsive: true,
                description: "Banner di bawah judul"
            },
            betweenTabContent: {
                enabled: true,
                adSlot: "2345678901",
                adFormat: "fluid",
                fullWidthResponsive: true,
                description: "Banner di antara tab & konten"
            },
            bottomBanner: {
                enabled: true,
                adSlot: "3456789012",
                adFormat: "auto",
                fullWidthResponsive: true,
                description: "Banner di bagian bawah sebelum footer"
            }
        },

        // 🎨 TAMPILAN IKLAN
        display: {
            showLabel: true,
            labelText: { id: "Iklan", en: "Ad" },
            labelFontSize: "11px",
            labelColor: "#94a3b8",
            marginVertical: "12px",
            padding: "8px",
            borderRadius: "8px",
            background: "#f8fafc",
            border: "1px solid #e2e8f0",
            textAlign: "left"
        },

        // 🔄 PERILAKU IKLAN
        behavior: {
            loadOnScroll: true,       // Muat saat di-scroll (performa lebih baik)
            showOnMobile: true,
            showOnDesktop: true,
            refreshOnCacheClear: true
        }
    },

    // ──────────────────────────────────────────────
    // 📈 PENGATURAN SOSIAL MEDIA / OPEN GRAPH
    // ──────────────────────────────────────────────
    social: {
        ogImage: "https://coalhunter.github.io/quant/og-image.png",
        twitterCardType: "summary_large_image",
        twitterHandle: ""
    },

    // ──────────────────────────────────────────────
    // 🔤 BAHASA DEFAULT
    // ──────────────────────────────────────────────
    defaultLanguage: "en",
    supportedLanguages: ["en", "id"],

    // ──────────────────────────────────────────────
    // 📄 TAUTAN NAVIGASI
    // ──────────────────────────────────────────────
    links: {
        home: "index.html",
        privacy: "privacy.html",
        terms: "terms.html",
        contact: "contact.html"
    }
};

// ═══════════════════════════════════════════════
// FUNGSI PEMBANTU — JANGAN DIUBAH
// ═══════════════════════════════════════════════

// Ambil konfigurasi iklan
function getAdSlot(slotName) {
    return SITE_CONFIG.adsense.slots[slotName] || null;
}

function isAdEnabled(slotName) {
    const adConfig = SITE_CONFIG.adsense;
    if (!adConfig.enabled) return false;
    const slot = adConfig.slots[slotName];
    return slot && slot.enabled;
}

// Muat kode iklan — dipanggil otomatis oleh index.html
function loadAdCode(slotId, containerId) {
    const adConfig = SITE_CONFIG.adsense;
    const slot = adConfig.slots[slotId];
    const container = document.getElementById(containerId);
    
    if (!container || !isAdEnabled(slotId)) {
        if (container) container.style.display = 'none';
        return;
    }

    container.style.display = 'block';
    
    // Terapkan gaya dari config
    const display = adConfig.display;
    container.style.background = display.background;
    container.style.borderRadius = display.borderRadius;
    container.style.padding = display.padding;
    container.style.margin = display.marginVertical;
    container.style.border = display.border;
    
    // Tampilkan label iklan
    const lang = document.documentElement.lang || SITE_CONFIG.defaultLanguage;
    const labelText = display.showLabel ? (lang === 'id' ? display.labelText.id : display.labelText.en) : '';
    
    // Isi kontainer dengan kode iklan yang benar
    const contentId = containerId + 'Content';
    const content = document.getElementById(contentId);
    if (content && adConfig.publisherId !== "ca-pub-XXXXXXXXXXXXXXXX") {
        content.innerHTML = `
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="${adConfig.publisherId}"
                 data-ad-slot="${slot.adSlot}"
                 data-ad-format="${slot.adFormat}"
                 data-full-width-responsive="${slot.fullWidthResponsive}"></ins>
        `;
        // (adsbygoogle = window.adsbygoogle || []).push({});
    }
}

// Terapkan meta tag verifikasi & SEO ke halaman
function applyMetaConfig() {
    // Google Site Verification
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
