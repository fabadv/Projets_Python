document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const villeInput = document.getElementById('villeInput');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorContainer = document.getElementById('errorContainer');
    const resultsContainer = document.getElementById('resultsContainer');
    const emptyState = document.getElementById('emptyState');

    let map = null;
    let markers = [];

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const ville = villeInput.value.trim();

        if (!ville) {
            showError('Veuillez entrer le nom d\'une ville');
            return;
        }

        await searchDieselPrices(ville);
    });

    async function searchDieselPrices(ville) {
        // Afficher le spinner
        loadingSpinner.classList.remove('hidden');
        errorContainer.classList.add('hidden');
        resultsContainer.classList.add('hidden');
        emptyState.classList.add('hidden');

        try {
            const response = await fetch(`/api/prix/${encodeURIComponent(ville)}`);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erreur lors de la recherche');
            }

            const data = await response.json();
            displayResults(data);
        } catch (error) {
            showError(error.message);
        } finally {
            loadingSpinner.classList.add('hidden');
        }
    }

    function displayResults(data) {
        const { ville, stations } = data;

        document.getElementById('resultsTitle').textContent = 
            `Résultats pour ${ville} (${stations.length} station${stations.length > 1 ? 's' : ''})`;

        const stationsList = document.getElementById('stationsList');
        stationsList.innerHTML = '';

        stations.forEach((station, index) => {
            const stationCard = createStationCard(station, index);
            stationsList.appendChild(stationCard);
        });

        // Afficher le conteneur de résultats
        resultsContainer.classList.remove('hidden');
        emptyState.classList.add('hidden');

        // Initialiser la carte après que le DOM soit rendu
        setTimeout(() => {
            initializeMap(stations);
        }, 100);
    }

    function initializeMap(stations) {
        const mapContainer = document.getElementById('mapContainer');
        
        // Vérifier que le conteneur existe et est visible
        if (!mapContainer) {
            console.error('Map container not found');
            return;
        }

        // Détruire la carte existante si elle existe
        if (map) {
            map.remove();
            markers = [];
        }

        // Créer une nouvelle carte avec Leaflet
        map = L.map(mapContainer, {
            preferCanvas: true
        }).setView([48.8566, 2.3522], 12);

        // Invalider la taille pour s'assurer que Leaflet recalcule
        setTimeout(() => {
            if (map) {
                map.invalidateSize();
            }
        }, 100);

        // Utiliser Stamen Toner Lite (gratuit, performant, sans problème CORS)
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19,
            minZoom: 5,
            crossOrigin: true
        }).addTo(map);

        // Créer un groupe pour adapter la vue
        const markerGroup = L.featureGroup();

        // Ajouter les marqueurs
        stations.forEach((station) => {
            if (station.latitude && station.longitude) {
                try {
                    // Créer une icône personnalisée
                    const customIcon = L.icon({
                        iconUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iNDgiIHZpZXdCb3g9IjAgMCAzMiA0OCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTYgNDhjLTUgMC0xNi05LTE2LTMyQzAgNy4yIDcuMiAwIDE2IDAgYzguOCAwIDE2IDcuMiAxNiAxNiAwIDIzLTExIDMyLTE2IDMyeiIgZmlsbD0iI0ZGNkIzNSIvPjwvc3ZnPg==',
                        iconSize: [32, 48],
                        iconAnchor: [16, 48],
                        popupAnchor: [0, -48],
                        shadowSize: [41, 41],
                        shadowAnchor: [13, 41]
                    });

                    const marker = L.marker([station.latitude, station.longitude], {
                        icon: customIcon,
                        title: station.nom
                    });

                    // Créer le popup
                    const popupContent = createPopupContent(station);
                    marker.bindPopup(popupContent);

                    marker.addTo(map);
                    markerGroup.addLayer(marker);
                    markers.push(marker);
                } catch (e) {
                    console.error('Error creating marker:', e);
                }
            }
        });

        // Adapter la vue à tous les marqueurs
        if (markers.length > 0) {
            try {
                const bounds = markerGroup.getBounds();
                if (bounds.isValid()) {
                    map.fitBounds(bounds, { padding: [50, 50], maxZoom: 16, duration: 800 });
                }
            } catch (e) {
                console.error('Error fitting bounds:', e);
            }
        }
    }

    function createPopupContent(station) {
        const formatPrice = (price) => {
            return price !== null && price !== undefined && price !== 'N/A' 
                ? typeof price === 'number' ? price.toFixed(3) : price
                : 'N/A';
        };

        const diesel = formatPrice(station.prix_diesel);
        const sp95 = formatPrice(station.prix_sp95);
        const sp98 = formatPrice(station.prix_sp98);

        return `
            <div class="map-popup">
                <strong>${station.nom}</strong><br>
                <small>${station.adresse}</small><br>
                <hr style="margin: 8px 0;">
                <strong style="color: #FF6B35;">⛽ Diesel: ${diesel}€/L</strong><br>
                <small>SP95: ${sp95}€/L</small><br>
                <small>SP98: ${sp98}€/L</small>
            </div>
        `;
    }

    function createStationCard(station, index) {
        const card = document.createElement('div');
        card.className = 'station-card';
        card.style.animationDelay = `${index * 0.1}s`;

        const formatPrice = (price) => {
            return price !== null && price !== undefined && price !== 'N/A' 
                ? typeof price === 'number' ? price.toFixed(3) : price
                : 'N/A';
        };

        const formatDate = (dateStr) => {
            if (!dateStr) return 'N/A';
            try {
                return new Date(dateStr).toLocaleDateString('fr-FR', {
                    year: '2-digit',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } catch (e) {
                return dateStr;
            }
        };

        const services = Array.isArray(station.services) && station.services.length > 0
            ? `<div class="services"><strong>Services:</strong> ${station.services.join(', ')}</div>`
            : '';

        // Construire la grille de prix avec les carburants disponibles
        let pricesHTML = '';
        const fuels = [
            { name: 'Diesel', key: 'prix_diesel', dateKey: 'derniere_maj_diesel' },
            { name: 'SP95', key: 'prix_sp95', dateKey: 'derniere_maj_sp95' },
            { name: 'SP98', key: 'prix_sp98' },
            { name: 'E85', key: 'prix_e85' },
            { name: 'E10', key: 'prix_e10' },
            { name: 'GPLc', key: 'prix_gplc' }
        ];

        for (const fuel of fuels) {
            const price = station[fuel.key];
            if (price !== null && price !== undefined) {
                const dateStr = station[fuel.dateKey] ? ` (${formatDate(station[fuel.dateKey])})` : '';
                pricesHTML += `
                    <div class="price-card">
                        <div class="price-label">${fuel.name}</div>
                        <div class="price-value">${formatPrice(price)}</div>
                        <div class="price-date">${fuel.dateKey ? dateStr : ''}</div>
                    </div>
                `;
            }
        }

        card.innerHTML = `
            <div class="station-name">${station.nom}</div>
            <div class="station-address">${station.adresse}</div>
            <div class="prices-grid">
                ${pricesHTML}
            </div>
            ${services}
        `;

        return card;
    }

    function showError(message) {
        errorContainer.textContent = message;
        errorContainer.classList.remove('hidden');
        resultsContainer.classList.add('hidden');
        emptyState.classList.add('hidden');
    }
});
