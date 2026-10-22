// ═══════════════════════════════════════════════
// KONFIGURASI ADSENSE & IKLAN
// ═══════════════════════════════════════════════
const ADSENSE_CONFIG = {
    // 🔑 INFORMASI AKUN ADSENSE — Isi kode Pub-Id kamu di sini
    publisher_id: "ca-pub-XXXXXXXXXXXXXXXX",
    
    // 📍 POSISI IKLAN — Aktifkan/nonaktifkan tiap lokasi
    ad_slots: {
        // Banner di atas tombol ganti bahasa (sebelumnya tombol hapus cache)
        top_banner: {
            enabled: true,
            ad_client: "ca-pub-XXXXXXXXXXXXXXXX",
            ad_slot: "1234567890",
            ad_format: "auto",
            full_width_responsive: true,
            description: "Banner di bagian atas, di bawah judul"
        },
        
        // Banner di antara tab dan daftar saham
        between_tab_and_content: {
            enabled: true,
            ad_client: "ca-pub-XXXXXXXXXXXXXXXX",
            ad_slot: "2345678901",
            ad_format: "fluid",
            full_width_responsive: true,
            description: "Banner di bawah tab navigasi"
        },
        
        // Banner di bawah daftar saham
        bottom_banner: {
            enabled: true,
            ad_client: "ca-pub-XXXXXXXXXXXXXXXX",
            ad_slot: "3456789012",
            ad_format: "auto",
            full_width_responsive: true,
            description: "Banner di bagian bawah sebelum footer"
        },
        
        // Iklan di dalam kartu (opsional)
        in_feed: {
            enabled: false,
            ad_client: "ca-pub-XXXXXXXXXXXXXXXX",
            ad_slot: "4567890123",
            ad_format: "fluid",
            description: "Iklan aliran di antara daftar saham"
        }
    },
    
    // 🎨 PENGATURAN TAMPILAN IKLAN
    display: {
        show_label: true,           // Tampilkan label "Iklan" / "Ad"
        label_text_id: "Iklan",     // Teks label Bahasa Indonesia
        label_text_en: "Ad",        // Teks label Bahasa Inggris
        label_font_size: "11px",
        label_color: "#94a3b8",
        margin_vertical: "12px",    // Jarak atas-bawah iklan
        padding: "8px",             // Ruang dalam kotak iklan
        border_radius: "8px",       // Sudut melengkung
        background: "#f8fafc"       // Latar belakang iklan
    },
    
    // 🔄 PENGATURAN PERILAKU
    behavior: {
        load_on_scroll: true,       // Muat iklan saat di-scroll saja
        show_on_mobile: true,       // Tampilkan di HP
        show_on_desktop: true,      // Tampilkan di komputer
        min_content_height: 200     // Tinggi konten minimal sebelum iklan muncul
    }
};

// Fungsi bantu untuk ambil pengaturan iklan
function getAdConfig(slotName) {
    return ADSENSE_CONFIG.ad_slots[slotName] || null;
}

function isAdEnabled(slotName) {
    const slot = ADSENSE_CONFIG.ad_slots[slotName];
    return slot && slot.enabled;
}
