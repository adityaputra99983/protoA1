(function() {
    var map;
    var userMarker;
    var watchId = null;

    function initMap() {
        map = L.map('map').setView([-2.5, 118], 5);
        
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        loadArtistsMarkers();
        startLocationWatch();
    }

    function loadArtistsMarkers() {
        fetch('/api/artists/')
            .then(function(response) { return response.json(); })
            .then(function(data) {
                var artists = data.artists || data || [];
                artists.forEach(function(artist) {
                    if (artist.latitude && artist.longitude) {
                        var icon = L.divIcon({
                            className: 'custom-marker',
                            html: '<div style="background: linear-gradient(135deg, #6B21A8, #2563EB); width: 36px; height: 36px; border-radius: 50%; border: 3px solid white; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.4);"><i class="bi bi-brush" style="font-size: 16px;"></i></div>',
                            iconSize: [36, 36],
                            iconAnchor: [18, 36],
                            popupAnchor: [0, -36]
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
    }

    function startLocationWatch() {
        var statusEl = document.getElementById('locationStatus');
        if (statusEl) {
            statusEl.innerHTML = '<span class="loading-spinner" style="width:16px;height:16px;border-width:2px;"></span> Mencari lokasi...';
        }
        
        if (navigator.geolocation) {
            watchId = navigator.geolocation.watchPosition(function(position) {
                var lat = position.coords.latitude;
                var lng = position.coords.longitude;
                var accuracy = position.coords.accuracy;
                
                var statusEl = document.getElementById('locationStatus');
                if (statusEl) {
                    statusEl.innerHTML = '<span style="color: #4ade80;"><i class="bi bi-geo-alt-fill"></i> Lokasi real-time aktif</span>';
                }
                
                map.setView([lat, lng], 14);
                
                if (userMarker) {
                    userMarker.setLatLng([lat, lng]);
                } else {
                    var userIcon = L.divIcon({
                        className: 'user-marker',
                        html: '<div style="background: #3B82F6; width: 24px; height: 24px; border-radius: 50%; border: 4px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.4);"></div>',
                        iconSize: [24, 24],
                        iconAnchor: [12, 12]
                    });
                    userMarker = L.marker([lat, lng], {icon: userIcon})
                        .addTo(map)
                        .bindPopup('<b style="color: #3B82F6;">Lokasi Anda</b><br>Akurasi: ' + Math.round(accuracy) + 'm')
                        .openPopup();
                }
            }, function(error) {
                var statusEl = document.getElementById('locationStatus');
                if (statusEl) {
                    statusEl.innerHTML = '<span style="color: #f87171;"><i class="bi bi-x-circle"></i> Gagal: ' + error.message + '</span>';
                }
            }, {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            });
        } else {
            var statusEl = document.getElementById('locationStatus');
            if (statusEl) {
                statusEl.innerHTML = '<span style="color: #f87171;"><i class="bi bi-x-circle"></i> Geolocation tidak didukung</span>';
            }
        }
    }

    function stopLocationWatch() {
        if (watchId !== null) {
            navigator.geolocation.clearWatch(watchId);
            watchId = null;
        }
    }

    function requestLocation() {
        startLocationWatch();
    }

    window.HomeMap = {
        initMap: initMap,
        requestLocation: requestLocation,
        startLocationWatch: startLocationWatch,
        stopLocationWatch: stopLocationWatch
    };

    document.addEventListener('DOMContentLoaded', initMap);
})();