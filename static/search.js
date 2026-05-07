(function() {
    var map;

    document.addEventListener('DOMContentLoaded', function() {
        var mapEl = document.getElementById('searchMap');
        if (!mapEl) return;
        
        // Check Leaflet
        if (typeof L === 'undefined') {
            console.error('Leaflet not loaded');
            return;
        }
        
        // Create map
        map = L.map('searchMap').setView([-2.5, 118], 5);
        
        // Add tiles
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }).addTo(map);
        
        console.log('Search map initialized');
        
        // Load artists
        loadArtists();
    });

    function loadArtists() {
        fetch('/api/artists/')
            .then(function(r) { return r.json(); })
            .then(function(result) {
                var artists = result.artists || [];
                displayArtists(artists);
            })
            .catch(function(err) {
                console.error('Error:', err);
                // Try embedded
                var el = document.getElementById('embedded-artists');
                if (el) {
                    try {
                        displayArtists(JSON.parse(el.textContent));
                    } catch(e) {}
                }
            });
    }

    function displayArtists(artists) {
        if (!map || !artists || artists.length === 0) return;
        
        var bounds = [];
        
        artists.forEach(function(artist) {
            var lat = parseFloat(artist.latitude);
            var lng = parseFloat(artist.longitude);
            
            if (isNaN(lat) || isNaN(lng)) return;
            
            bounds.push([lat, lng]);
            
            var icon = L.divIcon({
                html: '<div style="background:linear-gradient(135deg,#6B21A8,#2563EB);width:30px;height:30px;border-radius:50%;border:2px solid #fff;display:flex;align-items:center;justify-content:center;color:#fff;font-size:14px;">✒️</div>',
                className: '',
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            });
            
            L.marker([lat, lng], {icon: icon})
                .addTo(map)
                .bindPopup('<b style="color:#6B21A8;">' + (artist.name || 'Artist') + '</b><br>' + (artist.city || ''));
        });
        
        if (bounds.length > 0) {
            map.fitBounds(bounds, {padding: [30, 30]});
        }
    }
})();