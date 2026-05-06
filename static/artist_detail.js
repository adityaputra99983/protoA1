(function() {
    document.addEventListener('DOMContentLoaded', function() {
        var mapEl = document.getElementById('artistMap');
        var lat = parseFloat(mapEl.dataset.lat || '-2.5');
        var lng = parseFloat(mapEl.dataset.lng || '118');
        var name = mapEl.dataset.name || '';
        var address = mapEl.dataset.address || '';
        var city = mapEl.dataset.city || '';
        var studio = mapEl.dataset.studio || '';

        var map = L.map('artistMap').setView([lat, lng], 15);

        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        var icon = L.divIcon({
            className: 'custom-marker',
            html: '<div style="background: linear-gradient(135deg, #6B21A8, #2563EB); width: 36px; height: 36px; border-radius: 50%; border: 3px solid white; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.4);"><i class="bi bi-brush" style="font-size: 16px;"></i></div>',
            iconSize: [36, 36],
            iconAnchor: [18, 36],
            popupAnchor: [0, -36]
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