(function() {
    document.addEventListener('DOMContentLoaded', function() {
        var mapEl = document.getElementById('artistMap');
        var latStr = mapEl.dataset.lat;
        var lngStr = mapEl.dataset.lng;
        
        // Handle "None" from Django or empty string
        var lat = (latStr && latStr !== 'None') ? parseFloat(latStr) : -6.2088;
        var lng = (lngStr && lngStr !== 'None') ? parseFloat(lngStr) : 106.8456;
        
        if (isNaN(lat)) lat = -6.2088;
        if (isNaN(lng)) lng = 106.8456;

        var map = L.map('artistMap', {
            zoomControl: false,
            attributionControl: true
        }).setView([lat, lng], 15);

        L.control.zoom({ position: 'topright' }).addTo(map);

        // GOOGLE MAPS TILE LAYER
        L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
            attribution: '&copy; Google Maps',
            maxZoom: 20
        }).addTo(map);

        window.addEventListener('resize', function() {
            setTimeout(function() { map.invalidateSize(); }, 250);
        });

        var icon = L.divIcon({
            html: `
                <div class="artist-pin-wrapper" style="display:flex; flex-direction:column; align-items:center;">
                    <div style="width:40px; height:40px; background:linear-gradient(135deg, #A855F7, #2563EB); border-radius:50%; border:2px solid white; display:flex; align-items:center; justify-content:center; color:white; z-index:2; box-shadow:0 4px 10px rgba(0,0,0,0.5);">
                        <i class="bi bi-brush" style="font-size: 18px;"></i>
                    </div>
                    <div style="width:0; height:0; border-left:10px solid transparent; border-right:10px solid transparent; border-top:12px solid #2563EB; margin-top:-5px; z-index:1;"></div>
                </div>
            `,
            className: '',
            iconSize: [40, 52],
            iconAnchor: [20, 52],
            popupAnchor: [0, -52]
        });

        var popupContent = '<b style="color: #6B21A8;">' + name + '</b>';
        if (address) popupContent += '<br><small>' + address + '</small>';
        if (city) popupContent += '<br><small><i class="bi bi-geo-alt"></i> ' + city + '</small>';
        if (studio) popupContent += '<br><small><i class="bi bi-building"></i> ' + studio + '</small>';

        L.marker([lat, lng], {icon: icon})
            .addTo(map)
            .bindPopup(popupContent)
            .openPopup();
    });
})();