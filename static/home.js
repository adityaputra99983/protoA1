(function() {
    var map;
    var userMarker = null;
    var markersLayer = L.layerGroup();
    var allArtists = [];
    
    var statusEl = document.getElementById('mapStatus');
    var locStatusEl = document.getElementById('locationStatus');
    var artistListEl = document.getElementById('artistList');

    function initMap() {
        var mapEl = document.getElementById('map');
        if (!mapEl) return;
        if (mapEl._leaflet_id) return;

        // Inisialisasi Map
        map = L.map('map', {
            zoomControl: false,
            attributionControl: true
        }).setView([-6.2088, 106.8456], 12);

        L.control.zoom({ position: 'topright' }).addTo(map);

        // GOOGLE MAPS TILE LAYER - 100% Reliable, Fast, Never blocked
        L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
            attribution: '&copy; Google Maps',
            maxZoom: 20
        }).addTo(map);

        markersLayer.addTo(map);

        setTimeout(function() { map.invalidateSize(); }, 500);

        window.addEventListener('resize', function() {
            setTimeout(function() {
                if(map) map.invalidateSize();
            }, 250);
        });

        loadArtistsFromAPI();
        getUserLocation();
    }

    function loadArtistsFromAPI() {
        var apiUrl = '/api/artists/';
        
        fetch(apiUrl)
            .then(res => res.json())
            .then(data => {
                allArtists = data.artists || [];
                
                if (allArtists.length > 0) {
                    if (statusEl) statusEl.innerHTML = '✅ Sekitar Anda: ' + allArtists.length + ' Seniman';
                    displayArtistMarkers(allArtists);
                    displayArtistList(allArtists);
                } else {
                    if (statusEl) statusEl.innerHTML = 'Tidak ada seniman ditemukan di sekitar Anda.';
                }
            })
            .catch(err => {
                console.error('API Error:', err);
                if (statusEl) statusEl.innerHTML = '⚠️ Gagal memuat data seniman dari API';
            });
    }

    function displayArtistMarkers(artists) {
        if (!map) return;
        markersLayer.clearLayers();
        var bounds = [];

        artists.forEach((artist, index) => {
            // Fallback coordinate magic mapping to spread them across Jakarta if missing
            var lat = parseFloat(artist.latitude);
            var lng = parseFloat(artist.longitude);
            if (isNaN(lat) || isNaN(lng)) {
                // Generate a dummy location around Jakarta so they still show up!
                lat = -6.2088 + (Math.random() * 0.1 - 0.05);
                lng = 106.8456 + (Math.random() * 0.1 - 0.05);
            }

            bounds.push([lat, lng]);

            var pinIcon = L.divIcon({
                html: `
                    <div class="artist-pin-wrapper" style="display:flex; flex-direction:column; align-items:center;">
                        <div style="width:36px; height:36px; background:linear-gradient(135deg, #A855F7, #2563EB); border-radius:50%; border:2px solid white; display:flex; align-items:center; justify-content:center; color:white; z-index:2; box-shadow:0 4px 10px rgba(0,0,0,0.5);">
                            <i class="bi bi-brush"></i>
                        </div>
                        <div style="width:0; height:0; border-left:8px solid transparent; border-right:8px solid transparent; border-top:10px solid #2563EB; margin-top:-4px; z-index:1;"></div>
                    </div>
                `,
                className: '',
                iconSize: [36, 46],
                iconAnchor: [18, 46]
            });

            var popupContent = `
                <div style="color:#333; padding:5px; text-align:center;">
                    <h6 style="color:#6B21A8; margin:0 0 5px; font-weight:700;">${artist.nickname || artist.name}</h6>
                    <p style="margin:0 0 8px; font-size:0.8rem;">📍 ${artist.city}</p>
                    <a href="/artist/${artist.id}/" class="btn btn-sm w-100 mt-2" style="background:#A855F7; color:white; font-size:12px; font-weight:600; border-radius:8px;">PESAN SEKARANG</a>
                </div>
            `;

            L.marker([lat, lng], {icon: pinIcon}).addTo(markersLayer).bindPopup(popupContent);
        });

        if (bounds.length > 0) {
            map.fitBounds(bounds, {padding: [50, 50]});
        }
    }

    function displayArtistList(artists) {
        if (!artistListEl) return;
        var html = '';
        artists.forEach(a => {
            html += `
                <a href="/artist/${a.id}/" class="text-decoration-none">
                    <div class="artist-list-item" style="background:#0f172a; padding:12px; border-radius:12px; border:1px solid rgba(168, 85, 247, 0.2);">
                        <div class="d-flex justify-content-between align-items-center">
                            <strong style="color:white; font-size:14px;">${a.nickname || a.name}</strong>
                            <span style="color:#FBBF24; font-size:12px;">★ ${a.rating || '0'}</span>
                        </div>
                        <div class="mt-1" style="color:rgba(255,255,255,0.6); font-size:12px;">
                            <i class="bi bi-geo-alt"></i> ${a.city}
                        </div>
                        <div class="mt-2 text-center" style="font-size:11px; background:#A855F7; color:white; padding:4px; border-radius:8px; font-weight:bold;">
                            Lihat Profil
                        </div>
                    </div>
                </a>
            `;
        });
        artistListEl.innerHTML = html;
    }

    function getUserLocation() {
        if (!navigator.geolocation) return;
        
        navigator.geolocation.getCurrentPosition(
            pos => {
                var lat = pos.coords.latitude;
                var lng = pos.coords.longitude;
                
                var userIcon = L.divIcon({
                    html: '<div style="width:20px;height:20px;background:#3b82f6;border-radius:50%;border:3px solid white;box-shadow:0 0 10px rgba(59,130,246,0.8);"></div>',
                    className: '',
                    iconSize: [20, 20],
                    iconAnchor: [10, 10]
                });

                if (userMarker) map.removeLayer(userMarker);
                userMarker = L.marker([lat, lng], {icon: userIcon, zIndexOffset: 1000}).addTo(map);
                
                if (locStatusEl) locStatusEl.innerHTML = '<span style="color:#4ade80;">● GPS Aktif</span>';
            },
            () => {
                if (locStatusEl) locStatusEl.innerHTML = '<span style="color:#f87171;">● GPS Timeout/Ditolak</span>';
            }
        );
    }

    window.centerOnUser = function() {
        if (userMarker) {
            map.setView(userMarker.getLatLng(), 15);
        } else {
            alert('Lokasi GPS belum tersedia');
        }
    };

    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(initMap, 500);
    });
})();