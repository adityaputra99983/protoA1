(function() {
    document.addEventListener('DOMContentLoaded', function() {
        var map = L.map('searchMap').setView([-2.5, 118], 5);
        
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        fetch('/api/artists/')
            .then(function(response) { return response.json(); })
            .then(function(data) {
                var artists = data.artists || data || [];
                artists.forEach(function(artist) {
                    if (artist.latitude && artist.longitude) {
                        var icon = L.divIcon({
                            className: 'custom-marker',
                            html: '<div style="background: linear-gradient(135deg, #6B21A8, #2563EB); width: 30px; height: 30px; border-radius: 50%; border: 2px solid white; display: flex; align-items: center; justify-content: center; color: white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"><i class="bi bi-brush" style="font-size: 12px;"></i></div>',
                            iconSize: [30, 30],
                            iconAnchor: [15, 15]
                        });
                        L.marker([artist.latitude, artist.longitude], {icon: icon})
                            .addTo(map)
                            .bindPopup('<b style="color: #6B21A8;">' + artist.name + '</b><br>' + artist.city);
                    }
                });
            })
            .catch(function() {
                console.error('Failed to load artists');
            });
    });
})();