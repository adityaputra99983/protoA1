(function() {
    var map = null;
    var userMarker = null;
    var artistMarker = null;
    var bookingId = null;

    function hideLoading() {
        var el = document.getElementById('mapLoading');
        if (el) el.style.display = 'none';
    }

    function initTrackingMap() {
        var mapEl = document.getElementById('trackingMap');
        if (!mapEl) return;

        var userLat = parseFloat(mapEl.dataset.userLat);
        var userLng = parseFloat(mapEl.dataset.userLng);

        var centerLat = (!isNaN(userLat) && userLat !== 0) ? userLat : -6.2088;
        var centerLng = (!isNaN(userLng) && userLng !== 0) ? userLng : 106.8456;

        if (typeof L === 'undefined') {
            hideLoading();
            var loadEl = document.getElementById('mapLoading');
            if (loadEl) loadEl.innerHTML = '<p style="color:#f87171; padding:20px; text-align:center;"><i class="bi bi-exclamation-triangle"></i> Peta tidak tersedia</p>';
            return;
        }

        // Sembunyikan spinner sebelum inisialisasi peta
        hideLoading();

        map = L.map('trackingMap', {
            zoomControl: false,
            attributionControl: true
        }).setView([centerLat, centerLng], 14);

        L.control.zoom({ position: 'topright' }).addTo(map);

        // GOOGLE MAPS TILES - 100% reliable, never blocked locally
        L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
            attribution: '&copy; Google Maps',
            maxZoom: 20
        }).addTo(map);

        // Fix tiles on container resize
        setTimeout(function() { map.invalidateSize(); }, 300);
        setTimeout(function() { map.invalidateSize(); }, 1000);
        window.addEventListener('resize', function() {
            setTimeout(function() { if (map) map.invalidateSize(); }, 250);
        });

        // Marker lokasi user (biru)
        if (!isNaN(userLat) && !isNaN(userLng) && userLat !== 0 && userLng !== 0) {
            var userIcon = L.divIcon({
                className: '',
                html: '<div style="background:#3B82F6;width:28px;height:28px;border-radius:50%;border:3px solid white;box-shadow:0 2px 10px rgba(59,130,246,0.6);display:flex;align-items:center;justify-content:center;"><i class="bi bi-person-fill" style="color:white;font-size:14px;"></i></div>',
                iconSize: [28, 28],
                iconAnchor: [14, 14]
            });
            userMarker = L.marker([userLat, userLng], { icon: userIcon })
                .addTo(map)
                .bindPopup('<b style="color:#3B82F6;">📍 Lokasi Anda</b>');
        }

        refreshTracking();
    }

    function refreshTracking() {
        if (!bookingId) return;

        var btn = document.getElementById('refreshBtn');
        if (btn) {
            btn.innerHTML = '<span style="display:inline-block;width:14px;height:14px;border:2px solid #fff;border-top-color:transparent;border-radius:50%;animation:spin .6s linear infinite;margin-right:6px;vertical-align:middle;"></span> Memuat...';
            btn.disabled = true;
        }

        fetch('/api/booking/' + bookingId + '/track/')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                updateTrackingInfo(data);
                if (btn) { btn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh'; btn.disabled = false; }
            })
            .catch(function() {
                var infoEl = document.getElementById('trackingInfo');
                if (infoEl) infoEl.innerHTML = '<p style="color:#f87171;"><i class="bi bi-exclamation-triangle"></i> Gagal memuat lokasi</p>';
                if (btn) { btn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh'; btn.disabled = false; }
            });
    }

    function updateTrackingInfo(data) {
        if (!data) return;

        var distanceKm = (data.distance_km != null) ? parseFloat(data.distance_km).toFixed(1) + ' km' : '-';

        var statusMsg = '';
        if (data.status === 'on_the_way')      statusMsg = '🚗 Seniman dalam perjalanan — Jarak: ' + distanceKm;
        else if (data.status === 'arrived')    statusMsg = '✅ Seniman sudah tiba!';
        else if (data.status === 'confirmed')  statusMsg = '⏳ Menunggu seniman memulai perjalanan';
        else if (data.status === 'pending')    statusMsg = '🕐 Menunggu konfirmasi seniman';
        else if (data.status === 'completed')  statusMsg = '🎉 Sesi tattoo selesai!';
        else statusMsg = 'Status: ' + (data.status_display || data.status || '-');

        var statusTextEl = document.getElementById('statusText');
        var trackingStatusEl = document.getElementById('trackingStatus');
        if (statusTextEl) statusTextEl.textContent = statusMsg;
        if (trackingStatusEl) trackingStatusEl.style.display = 'block';

        var infoEl = document.getElementById('trackingInfo');
        if (infoEl) infoEl.innerHTML = '<p style="color:#4ade80;"><i class="bi bi-check-circle-fill"></i> Lokasi terkini berhasil dimuat</p>';

        if (data.artist_lat && data.artist_lng && map) {
            var latlng = [parseFloat(data.artist_lat), parseFloat(data.artist_lng)];
            if (artistMarker) {
                artistMarker.setLatLng(latlng);
            } else {
                var artistIcon = L.divIcon({
                    className: '',
                    html: '<div style="display:flex;flex-direction:column;align-items:center;"><div style="background:linear-gradient(135deg,#A855F7,#2563EB);width:40px;height:40px;border-radius:50%;border:2px solid white;display:flex;align-items:center;justify-content:center;color:white;box-shadow:0 4px 14px rgba(168,85,247,0.5);"><i class="bi bi-brush" style="font-size:18px;"></i></div><div style="width:0;height:0;border-left:10px solid transparent;border-right:10px solid transparent;border-top:12px solid #2563EB;margin-top:-4px;"></div></div>',
                    iconSize: [40, 52],
                    iconAnchor: [20, 52],
                    popupAnchor: [0, -52]
                });
                artistMarker = L.marker(latlng, { icon: artistIcon })
                    .addTo(map)
                    .bindPopup('<b style="color:#A855F7;">🎨 ' + (data.artist_name || 'Seniman') + '</b><br><small>Jarak: ' + distanceKm + '</small>');
            }

            if (userMarker) {
                map.fitBounds(L.latLngBounds([latlng, userMarker.getLatLng()]), { padding: [40, 40] });
            } else {
                map.setView(latlng, 14);
            }
        }
    }

    function init(id) {
        bookingId = id;
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                initTrackingMap();
                setInterval(refreshTracking, 30000);
            });
        } else {
            initTrackingMap();
            setInterval(refreshTracking, 30000);
        }
    }

    window.BookingDetailTracking = { init: init };
    window.refreshTracking = refreshTracking;
})();