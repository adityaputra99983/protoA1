(function() {
    function requestLocationAndSearch() {
        document.getElementById('searchLocationStatus').innerHTML = '<span class="loading-spinner" style="width: 16px; height: 16px; border-width: 2px;"></span> Mendeteksi lokasi...';
        
        if (window.TED && TED.getLocation) {
            TED.getLocation(function(location) {
                var url = '/artists/?lat=' + location.lat + '&lng=' + location.lng;
                window.location.href = url;
            }, function(error) {
                document.getElementById('searchLocationStatus').innerHTML = '<span style="color: #f87171;"><i class="bi bi-x-circle"></i> Gagal mendeteksi lokasi</span>';
            });
        } else {
            document.getElementById('searchLocationStatus').innerHTML = '<span style="color: #f87171;"><i class="bi bi-x-circle"></i> TED not available</span>';
        }
    }

    window.ArtistsPage = {
        requestLocationAndSearch: requestLocationAndSearch
    };
})();