(function() {
    var savedLocation = null;

    function getCurrentLocation() {
        document.getElementById('locationStatus').innerHTML = '<span class="loading-spinner" style="width: 20px; height: 20px; border-width: 2px;"></span> Mendeteksi lokasi...';
        
        if (window.TED && TED.getLocation) {
            TED.getLocation(function(location) {
                savedLocation = location;
                document.getElementById('userLat').value = location.lat;
                document.getElementById('userLng').value = location.lng;
                document.getElementById('locationStatus').innerHTML = '<span style="color: #4ade80;"><i class="bi bi-check-circle"></i> Lokasi terdeteksi</span>';
                
                if (TED.getAddressFromLatLng) {
                    TED.getAddressFromLatLng(location.lat, location.lng, function(address) {
                        document.getElementById('addressField').value = address;
                    });
                }
            }, function(error) {
                document.getElementById('locationStatus').innerHTML = '<span style="color: #f87171;"><i class="bi bi-x-circle"></i> Gagal mendeteksi</span>';
            });
        } else {
            document.getElementById('locationStatus').innerHTML = '<span style="color: #f87171;"><i class="bi bi-x-circle"></i> TED not available</span>';
        }
    }

    function initDatePicker() {
        var dateInput = document.querySelector('input[type="date"]');
        if (dateInput) {
            var today = new Date();
            var tomorrow = new Date(today);
            tomorrow.setDate(tomorrow.getDate() + 1);
            dateInput.min = tomorrow.toISOString().split('T')[0];
        }
    }

    window.BookArtist = {
        getCurrentLocation: getCurrentLocation
    };

    document.addEventListener('DOMContentLoaded', function() {
        initDatePicker();
    });
})();