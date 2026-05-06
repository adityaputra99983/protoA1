(function() {
    var trackingInterval;
    var currentLat, currentLng;

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

    function startLocationTracking() {
        document.getElementById('locationStatus').innerHTML = '<div class="loading-spinner mx-auto"></div> Mendeteksi lokasi...';
        
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                currentLat = position.coords.latitude;
                currentLng = position.coords.longitude;
                
                document.getElementById('currentLat').value = currentLat;
                document.getElementById('currentLng').value = currentLng;
                document.getElementById('locationStatus').innerHTML = 
                    '<span style="color: #4ade80;"><i class="bi bi-check-circle"></i> Lokasi aktif - Mengirim setiap 10 detik</span>';
                
                sendLocation();
                trackingInterval = setInterval(sendLocation, 10000);
            }, function(error) {
                document.getElementById('locationStatus').innerHTML = 
                    '<span style="color: #f87171;"><i class="bi bi-x-circle"></i> Gagal mendeteksi lokasi</span>';
            }, {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            });
        } else {
            document.getElementById('locationStatus').innerHTML = 
                '<span style="color: #f87171;"><i class="bi bi-x-circle"></i> Geolocation tidak didukung</span>';
        }
    }

    function sendLocation() {
        if (!currentLat || !currentLng) return;
        
        fetch('/api/artist/location/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                latitude: currentLat,
                longitude: currentLng
            })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            console.log('Location sent:', data);
        })
        .catch(function() {
            console.error('Failed to send location');
        });
    }

    window.ArtistDashboard = {
        startLocationTracking: startLocationTracking,
        sendLocation: sendLocation
    };

    navigator.geolocation.watchPosition(function(position) {
        currentLat = position.coords.latitude;
        currentLng = position.coords.longitude;
    });
})();