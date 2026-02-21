/**
 * DComite Web - JavaScript principal
 * Gestion des modals AJAX, recherche table, confirmation suppression
 */

// Charger un contenu HTML dans le modal generique
async function loadModal(url) {
    var container = document.getElementById('modalContent');
    container.innerHTML = '<div class="modal-body text-center py-5"><div class="spinner-border text-primary"></div></div>';

    var modalEl = document.getElementById('detailModal');
    var modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();

    try {
        var response = await fetch(url);
        container.innerHTML = await response.text();
    } catch (err) {
        container.innerHTML = '<div class="modal-body"><div class="alert alert-danger">Erreur de chargement</div></div>';
    }
}

// Confirmation et suppression via POST
function confirmDelete(url, message) {
    if (confirm(message || 'Etes-vous sur de vouloir supprimer cet element ?')) {
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = url;
        document.body.appendChild(form);
        form.submit();
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function () {

    // Rendre les lignes de tableau cliquables
    document.querySelectorAll('.clickable-row').forEach(function (row) {
        row.addEventListener('click', function (e) {
            // Ne pas declencher si clic sur un bouton ou lien dans la ligne
            if (e.target.closest('a, button')) return;
            var url = this.dataset.detailUrl;
            if (url) loadModal(url);
        });
    });

    // Recherche client-side dans le tableau
    var searchInput = document.getElementById('tableSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            var query = this.value.toLowerCase();
            var rows = document.querySelectorAll('#dataTable tbody tr');
            var visibleCount = 0;

            rows.forEach(function (row) {
                var text = row.textContent.toLowerCase();
                var match = text.indexOf(query) !== -1;
                row.classList.toggle('hidden-row', !match);
                if (match) visibleCount++;
            });

            // Mettre a jour le compteur de lignes
            var counter = document.getElementById('rowCount');
            if (counter) counter.textContent = visibleCount;
        });
    }

    // Auto-dismiss des flash messages apres 5 secondes
    document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });
});
