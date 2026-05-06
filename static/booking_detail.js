(function() {
    var map = null;
    var userMarker = null;
    var artistMarker = null;
    var refreshInterval = null;
    var bookingId = null;
    
    function initTrackingMap() {
        var mapEl = document.getElementById('trackingMap');
        var userLat = parseFloat(mapEl.dataset.userLat || '0');
        var userLng = parseFloat(mapEl.dataset.userLng || '0');
        
        var centerLat = userLat || -2.5;
        var centerLng = userLng || 118;
        
        if (typeof L !== 'undefined') {
            map = L.map('trackingMap').setView([centerLat, centerLng], 14);
            
            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);
            
            document.getElementById('mapLoading').style.display = 'none';
            
            if (userLat && userLng) {
                var userIcon = L.divIcon({
                    className: 'user-marker',
                    html: '<div style="background: #3B82F6; width: 24px; height: 24px; border-radius: 50%; border: 4px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.4);"></div>',
                    iconSize: [24, 24],
                    iconAnchor: [12, 12]
                });
                userMarker = L.marker([userLat, userLng], {icon: userIcon}).addTo(map).bindPopup('<b style="color: #3B82F6;">Lokasi Anda</b>');
            }
            
            refreshTracking();
        } else {
            document.getElementById('mapLoading').innerHTML = '<p style="color: var(--text-secondary);">Peta tidak tersedia</p>';
        }
    }
    
    function refreshTracking() {
        if (!bookingId) {
            console.warn('Booking ID not initialized');
            return;
        }
        
        var btn = document.getElementById('refreshBtn');
        if (btn) {
            btn.innerHTML = '<div class="loading-spinner" style="width:16px;height:16px;border-width:2px;"></div> Memuat...';
        }

        fetch('/api/booking/' + bookingId + '/track/')
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                updateTrackingInfo(data);
                if (btn) {
                    btn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh';
                }
            })
            .catch(function() {
                document.getElementById('trackingInfo').innerHTML = '<p style="color: #f87171;">Gagal memuat lokasi</p>';
                if (btn) {
                    btn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh';
                }
            });
    }
    
    function updateTrackingInfo(data) {
        if (!data) return;
        
        var statusDisplay = data.status_display || 'Unknown';
        var distanceKm = data.distance_km ? data.distance_km.toFixed(1) + ' km' : '-';
        
        var statusText = '';
        if (data.status === 'on_the_way') {
            statusText = 'Seniman sedang dalam perjalanan. Jarak: ' + distanceKm;
        } else if (data.status === 'arrived') {
            statusText = 'Seniman telah tiba!';
        } else if (data.status === 'confirmed') {
            statusText = 'Menunggu seniman memulai perjalanan';
        } else if (data.status === 'pending') {
            statusText = 'Menunggu konfirmasi seniman';
        } else if (data.status === 'completed') {
            statusText = 'Tattoo selesai!';
        }
        
        var statusTextEl = document.getElementById('statusText');
        var statusStatusEl = document.getElementById('trackingStatus');
        if (statusTextEl) statusTextEl.textContent = statusText;
        if (statusStatusEl) statusStatusEl.style.display = 'block';
        
        if (data.artist_lat && data.artist_lng && map) {
            if (artistMarker) {
                artistMarker.remove();
            }
            
            var artistIcon = L.divIcon({
                className: 'artist-marker',
                html: '<div style="background: linear-gradient(135deg, #6B21A8, #2563EB); width: 36px; height: 36px; border-radius: 50%; border: 3px solid white; display: flex; align-items: center; justify-content: center; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.4);"><i class="bi bi-brush" style="font-size: 16px;"></i></div>',
                iconSize: [36, 36],
                iconAnchor: [18, 36],
                popupAnchor: [0, -36]
            });
            artistMarker = L.marker([data.artist_lat, data.artist_lng], {icon: artistIcon}).addTo(map).bindPopup('<b style="color: #6B21A8;">' + (data.artist_name || 'Seniman') + '</b><br>Jarak: ' + distanceKm);
        }
        
        document.getElementById('trackingInfo').innerHTML = '<p style="color: #4ade80;"><i class="bi bi-check-circle"></i> Lokasi terkini</p>';
    }
    
    function init(id) {
        bookingId = id;
        document.addEventListener('DOMContentLoaded', function() {
            initTrackingMap();
            refreshInterval = setInterval(refreshTracking, 30000);
        });
    }

    window.BookingDetailTracking = { init: init };
    window.refreshTracking = refreshTracking;
})();