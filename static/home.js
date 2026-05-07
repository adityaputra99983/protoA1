(function() {
    var map;
    var userMarker = null;

    function initMap() {
        var mapEl = document.getElementById('map');
        if (!mapEl) {
            console.log('Map element not found');
            return;
        }
        
        // Check Leaflet
        if (typeof L === 'undefined') {
            console.error('Leaflet not loaded');
            document.getElementById('locationStatus').innerHTML = '<span style="color:#f87171;">Map library gagal load</span>';
            return;
        }
        
        // Create map
        map = L.map('map', {
            zoomControl: true,
            attributionControl: true
        }).setView([-2.5, 118], 5);
        
        // Add tiles
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }).addTo(map);
        
        console.log('Map initialized');
        
        // Load from API
        loadArtistsFromAPI();
        
        // Get user location
        getUserLocation();
    }

    function loadArtistsFromAPI() {
        fetch('/api/artists/')
            .then(function(response) {
                return response.json();
            })
            .then(function(result) {
                console.log('API Response:', result);
                var artists = result.artists || [];
                displayArtists(artists);
            })
            .catch(function(err) {
                console.error('API Error:', err);
                // Try embedded data
                var embeddedEl = document.getElementById('embedded-artists');
                if (embeddedEl) {
                    try {
                        var artists = JSON.parse(embeddedEl.textContent);
                        displayArtists(artists);
                    } catch(e) {}
                }
            });
    }

    function displayArtists(artists) {
        if (!map || !artists || artists.length === 0) {
            console.log('No artists to display');
            document.getElementById('locationStatus').innerHTML = '<span style="color:#f87171;">Tidak ada data seniman</span>';
            return;
        }
        
        console.log('Displaying', artists.length, 'artists');
        
        var bounds = [];
        
        artists.forEach(function(artist) {
            var lat = parseFloat(artist.latitude);
            var lng = parseFloat(artist.longitude);
            
            if (isNaN(lat) || isNaN(lng)) return;
            
            bounds.push([lat, lng]);
            
            // Create marker icon
            var icon = L.divIcon({
                html: '<div style="background:linear-gradient(135deg,#6B21A8,#2563EB);width:40px;height:40px;border-radius:50%;border:3px solid #fff;display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;box-shadow:0 4px 10px rgba(0,0,0,0.4);">✒️</div>',
                className: '',
                iconSize: [40, 40],
                iconAnchor: [20, 40]
            });
            
            L.marker([lat, lng], {icon: icon})
                .addTo(map)
                .bindPopup('<b style="color:#6B21A8;">' + (artist.name || 'Artist') + '</b><br><span style="color:#666;">' + (artist.city || '') + '</span>');
        });
        
        if (bounds.length > 0) {
            map.fitBounds(bounds, {padding: [50, 50]});
        }
        
        console.log('Displayed', artists.length, 'markers');
    }

    function getUserLocation() {
        if (!navigator.geolocation) {
            console.log('Geolocation not supported');
            return;
        }
        
        document.getElementById('locationStatus').innerHTML = '<span style="color:#fbbf24;">🔄 Mencari lokasi...</span>';
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                var lat = position.coords.latitude;
                var lng = position.coords.longitude;
                console.log('User location:', lat, lng);
                
                // User marker
                var userIcon = L.divIcon({
                    html: '<div style="background:#3B82F6;width:28px;height:28px;border-radius:50%;border:4px solid #fff;box-shadow:0 2px 10px rgba(0,0,0,0.5);"></div>',
                    className: '',
                    iconSize: [28, 28],
                    iconAnchor: [14, 14]
                });
                
                userMarker = L.marker([lat, lng], {icon: userIcon})
                    .addTo(map)
                    .bindPopup('<b style="color:#3B82F6;">📍 Lokasi Anda</b>')
                    .openPopup();
                
                // Center on user
                map.setView([lat, lng], 12);
                
                document.getElementById('locationStatus').innerHTML = 
                    '<span style="color:#4ade80;">● Lokasi real-time aktif</span>';
                
            },
            function(error) {
                var msg = 'Lokasi tidak tersedia';
                if (error.code === 1) msg = 'Izin lokasi ditolak';
                document.getElementById('locationStatus').innerHTML = 
                    '<span style="color:#f87171;">● ' + msg + '</span>';
            },
            { enableHighAccuracy: true, timeout: 15000 }
        );
    }

    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(initMap, 300);
    });
})();