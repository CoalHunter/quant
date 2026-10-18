let stockData = [];
let currentFilter = 'all';

async function loadData() {
    try {
        const response = await fetch('output/data.json');
        const data = await response.json();
        stockData = data.recommendations;
        document.getElementById('lastUpdate').textContent = 'Update: ' + new Date(data.metadata.last_updated).toLocaleString('id-ID');
        renderCards();
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('stockGrid').innerHTML = 
            '<div style="padding:40px;text-align:center;color:#B12704;grid-column:1/-1;">' +
            '<h3>Gagal memuat data</h3>' +
            '<p>Pastikan file output/data.json sudah diupload ke GitHub</p>' +
            '</div>';
    }
}

function renderCards() {
    const grid = document.getElementById('stockGrid');
    grid.innerHTML = '';
    
    // Tampilkan SEMUA emiten, tidak ada filter hide
    let displayData = stockData;
    
    // Sort berdasarkan filter (highlight yang relevan di atas)
    if (currentFilter === 'swing') {
        displayData = [...stockData].sort((a, b) => {
            const aBuy = a.swing_strategy?.status === 'BUY' ? 1 : 0;
            const bBuy = b.swing_strategy?.status === 'BUY' ? 1 : 0;
            return bBuy - aBuy;
        });
    } else if (currentFilter === 'dividend') {
        displayData = [...stockData].sort((a, b) => {
            const aAcc = a.dividend_strategy?.status === 'ACCUMULATE' ? 1 : 0;
            const bAcc = b.dividend_strategy?.status === 'ACCUMULATE' ? 1 : 0;
            return bAcc - aAcc;
        });
    }
    
    displayData.forEach(stock => {
        const card = document.createElement('div');
        card.className = 'stock-card';
        card.onclick = () => openModal(stock);
        
        const accScore = stock.swing_strategy?.accumulation_score || 0;
        const swingStatus = stock.swing_strategy?.status || 'WAIT';
        const divStatus = stock.dividend_strategy?.status || 'HOLD';
        
        // Badge dinamis berdasarkan status
        let swingBadgeClass = 'badge-swing-wait';
        let swingBadgeText = 'Swing: WAIT';
        if (swingStatus === 'BUY') {
            swingBadgeClass = 'badge-swing-buy';
            swingBadgeText = 'Swing: BUY';
        }
        
        let divBadgeClass = 'badge-div-hold';
        let divBadgeText = 'Dividen: HOLD';
        if (divStatus === 'ACCUMULATE') {
            divBadgeClass = 'badge-div-acc';
            divBadgeText = 'Dividen: ACCUMULATE';
        }
        
        // Highlight card jika ada sinyal aktif sesuai filter
        let highlightClass = '';
        if (currentFilter === 'swing' && swingStatus === 'BUY') {
            highlightClass = 'card-highlight';
        } else if (currentFilter === 'dividend' && divStatus === 'ACCUMULATE') {
            highlightClass = 'card-highlight';
        }
        
        card.className = `stock-card ${highlightClass}`;
        
        card.innerHTML = `
            <div class="card-image">
                <div class="card-ticker-large">${stock.ticker}</div>
            </div>
            <div class="card-body">
                <div class="card-ticker">${stock.ticker}</div>
                <div class="card-name">${stock.name}</div>
                
                <div class="card-price-section">
                    <div class="price-label">Harga Saat Ini</div>
                    <div class="price-value">$${stock.current_price}</div>
                </div>
                
                <div class="card-badges">
                    <span class="badge ${swingBadgeClass}">${swingBadgeText}</span>
                    <span class="badge ${divBadgeClass}">${divBadgeText}</span>
                </div>
                
                <div class="card-volume">
                    Volume: ${formatVolume(stock.daily_volume)}
                </div>
                
                <div class="accumulation-section">
                    <div class="accumulation-label">
                        <span>Akumulasi Bandar</span>
                        <span>${accScore}%</span>
                    </div>
                    <div class="accumulation-bar">
                        <div class="accumulation-fill" style="width: ${accScore}%"></div>
                    </div>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

function formatVolume(vol) {
    if (vol >= 1000000) return (vol/1000000).toFixed(2) + 'M';
    if (vol >= 1000) return (vol/1000).toFixed(2) + 'K';
    return vol.toString();
}

function searchStock() {
    const input = document.getElementById('searchInput').value.toUpperCase();
    if (!input) {
        renderCards();
        return;
    }
    
    const filtered = stockData.filter(s => s.ticker.includes(input) || s.name.toUpperCase().includes(input));
    const grid = document.getElementById('stockGrid');
    grid.innerHTML = '';
    
    if (filtered.length === 0) {
        grid.innerHTML = '<div style="padding:40px;text-align:center;color:#565959;grid-column:1/-1;"><h3>Tidak ditemukan</h3></div>';
        return;
    }
    
    filtered.forEach(stock => {
        const card = document.createElement('div');
        card.className = 'stock-card';
        card.onclick = () => openModal(stock);
        
        const accScore = stock.swing_strategy?.accumulation_score || 0;
        const swingStatus = stock.swing_strategy?.status || 'WAIT';
        const divStatus = stock.dividend_strategy?.status || 'HOLD';
        
        let swingBadgeClass = 'badge-swing-wait';
        let swingBadgeText = 'Swing: WAIT';
        if (swingStatus === 'BUY') {
            swingBadgeClass = 'badge-swing-buy';
            swingBadgeText = 'Swing: BUY';
        }
        
        let divBadgeClass = 'badge-div-hold';
        let divBadgeText = 'Dividen: HOLD';
        if (divStatus === 'ACCUMULATE') {
            divBadgeClass = 'badge-div-acc';
            divBadgeText = 'Dividen: ACCUMULATE';
        }
        
        card.innerHTML = `
            <div class="card-image">
                <div class="card-ticker-large">${stock.ticker}</div>
            </div>
            <div class="card-body">
                <div class="card-ticker">${stock.ticker}</div>
                <div class="card-name">${stock.name}</div>
                <div class="card-price-section">
                    <div class="price-label">Harga Saat Ini</div>
                    <div class="price-value">$${stock.current_price}</div>
                </div>
                <div class="card-badges">
                    <span class="badge ${swingBadgeClass}">${swingBadgeText}</span>
                    <span class="badge ${divBadgeClass}">${divBadgeText}</span>
                </div>
                <div class="card-volume">Volume: ${formatVolume(stock.daily_volume)}</div>
                <div class="accumulation-section">
                    <div class="accumulation-label">
                        <span>Akumulasi Bandar</span>
                        <span>${accScore}%</span>
                    </div>
                    <div class="accumulation-bar">
                        <div class="accumulation-fill" style="width: ${accScore}%"></div>
                    </div>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

// Update filter buttons - tambah tombol "Semua"
document.querySelectorAll('.subnav-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.subnav-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentFilter = e.target.dataset.filter;
        renderCards();
    });
});

function openModal(stock) {
    document.getElementById('modalTicker').textContent = stock.ticker;
    document.getElementById('modalName').textContent = stock.name;
    document.getElementById('modalPrice').textContent = '$' + stock.current_price;
    
    document.getElementById('tab-overview').innerHTML = `
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Sektor</div>
                <div class="info-value">${stock.sector}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Volume Harian</div>
                <div class="info-value">${formatVolume(stock.daily_volume)}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Swing Status</div>
                <div class="info-value">
                    <span class="status-badge ${stock.swing_strategy?.status === 'BUY' ? 'status-buy' : 'status-wait'}">
                        ${stock.swing_strategy?.status || 'N/A'}
                    </span>
                </div>
            </div>
            <div class="info-item">
                <div class="info-label">Dividend Status</div>
                <div class="info-value">
                    <span class="status-badge ${stock.dividend_strategy?.status === 'ACCUMULATE' ? 'status-accumulate' : 'status-hold'}">
                        ${stock.dividend_strategy?.status || 'N/A'}
                    </span>
                </div>
            </div>
        </div>
    `;
    
    const swing = stock.swing_strategy || {};
    document.getElementById('tab-swing').innerHTML = `
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Status</div>
                <div class="info-value">
                    <span class="status-badge ${swing.status === 'BUY' ? 'status-buy' : 'status-wait'}">${swing.status || 'N/A'}</span>
                </div>
            </div>
            <div class="info-item">
                <div class="info-label">Entry Zone</div>
                <div class="info-value">$${swing.entry_zone?.[0] || '-'} - $${swing.entry_zone?.[1] || '-'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Target Jual</div>
                <div class="info-value" style="color:#B12704">$${swing.target_price || '-'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Stop Loss</div>
                <div class="info-value">$${swing.stop_loss || '-'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Timeframe</div>
                <div class="info-value">${swing.timeframe || '-'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">RSI</div>
                <div class="info-value">${swing.current_rsi || '-'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Akumulasi Bandar</div>
                <div class="info-value">${swing.accumulation_score || 0}%</div>
            </div>
        </div>
    `;
    
    const div = stock.dividend_strategy || {};
    document.getElementById('tab-dividend').innerHTML = `
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Status</div>
                <div class="info-value">
                    <span class="status-badge ${div.status === 'ACCUMULATE' ? 'status-accumulate' : 'status-hold'}">${div.status || 'N/A'}</span>
                </div>
            </div>
            <div class="info-item">
                <div class="info-label">Safe Entry</div>
                <div class="info-value">$${div.safe_entry || '-'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Dividend Yield</div>
                <div class="info-value" style="color:#0a7e0a">${div.dividend_yield || 0}%</div>
            </div>
            <div class="info-item">
                <div class="info-label">Payout Ratio</div>
                <div class="info-value">${div.payout_ratio || 0}%</div>
            </div>
            <div class="info-item">
                <div class="info-label">Frekuensi</div>
                <div class="info-value">${div.frequency || '-'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Aman dari Dividend Trap</div>
                <div class="info-value">${div.is_safe_from_trap ? '✅ Ya' : '⚠️ Tidak'}</div>
            </div>
        </div>
    `;
    
    document.getElementById('stockModal').classList.add('active');
}

function closeModal() {
    document.getElementById('stockModal').classList.remove('active');
}

document.getElementById('stockModal').addEventListener('click', (e) => {
    if (e.target.id === 'stockModal') closeModal();
});

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        e.target.classList.add('active');
        document.getElementById('tab-' + e.target.dataset.tab).classList.add('active');
    });
});

loadData();
