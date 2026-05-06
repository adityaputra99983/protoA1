(function() {
    window.TED = {
        getLocation: function(callback, errorCallback) {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    TED.userLocation = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };
                    if (callback) callback(TED.userLocation);
                }, function(error) {
                    if (errorCallback) errorCallback(error);
                }, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 60000
                });
            } else {
                if (errorCallback) errorCallback({message: 'Geolocation tidak didukung'});
            }
        },
        
        getAddressFromLatLng: function(lat, lng, callback) {
            fetch('https://nominatim.openstreetmap.org/reverse?format=json&lat=' + lat + '&lon=' + lng, {
                headers: {'User-Agent': 'TED-App/1.0'}
            })
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (callback) callback(data.display_name || 'Alamat tidak ditemukan');
                })
                .catch(function() {
                    if (callback) callback('Alamat tidak ditemukan');
                });
        }
    };

    function toggleMobileMenu() {
        document.getElementById('mobileSlideMenu').classList.toggle('active');
        document.getElementById('mobileOverlay').classList.toggle('active');
        document.querySelector('.mobile-menu-toggle').classList.toggle('active');
    }

    function closeMobileMenu() {
        document.getElementById('mobileSlideMenu').classList.remove('active');
        document.getElementById('mobileOverlay').classList.remove('active');
        document.querySelector('.mobile-menu-toggle').classList.remove('active');
    }

    window.toggleMobileMenu = toggleMobileMenu;
    window.closeMobileMenu = closeMobileMenu;

    document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('.menu-link').forEach(function(link) {
            link.addEventListener('click', closeMobileMenu);
        });
    });

    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/service-worker.js?v=40')
            .then(function(reg) { 
                console.log('SW registered', reg.scope); 
            })
            .catch(function(err) { 
                console.log('SW registration failed', err); 
            });
    }

    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
})();