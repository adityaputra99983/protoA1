(function() {
    var myLat, myLng;

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function initMap() {
        var mapEl = document.getElementById('trackingMap');
        var userLat = parseFloat(mapEl.dataset.userLat || '0');
        var userLng = parseFloat(mapEl.dataset.userLng || '0');
        
        if (userLat && userLng) {
            var map = L.map('trackingMap').setView([userLat, userLng], 15);
            
            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);
            
            var userIcon = L.divIcon({
                className: 'user-marker',
                html: '<div style="background: #3B82F6; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>',
                iconSize: [20, 20],
                iconAnchor: [10, 10]
            });
            L.marker([userLat, userLng], {icon: userIcon}).addTo(map).bindPopup('<b style="color: #3B82F6;">Lokasi Pelanggan</b>');
        } else {
            var map = L.map('trackingMap').setView([-2.5, 118], 5);
            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);
            
            document.getElementById('locationStatus').innerHTML = '<span style="color: #f87171;"><i class="bi bi-exclamation-circle"></i> Lokasi pelanggan tidak tersedia</span>';
        }
    }

    function sendMyLocation() {
        document.getElementById('locationStatus').innerHTML = '<div class="loading-spinner mx-auto"></div>';
        
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                myLat = position.coords.latitude;
                myLng = position.coords.longitude;
                
                fetch('/api/artist/location/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        latitude: myLat,
                        longitude: myLng
                    })
                })
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    document.getElementById('locationStatus').innerHTML = '<span style="color: #4ade80;"><i class="bi bi-check-circle"></i> Lokasi terkirim!</span>';
                });
            }, function(error) {
                document.getElementById('locationStatus').innerHTML = '<span style="color: #f87171;"><i class="bi bi-x-circle"></i> Gagal</span>';
            });
        }
    }

    window.ArtistBookingDetail = {
        initMap: initMap,
        sendMyLocation: sendMyLocation
    };

    document.addEventListener('DOMContentLoaded', function() {
        initMap();
    });
})();