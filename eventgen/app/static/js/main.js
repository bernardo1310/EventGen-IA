/* EventGen AI - main.js */

(function () {
    'use strict';

    // Loading overlay for the optimization form
    const optimizeForm = document.getElementById('optimizeForm');
    if (optimizeForm) {
        optimizeForm.addEventListener('submit', function () {
            showLoadingOverlay();
        });
    }

    function showLoadingOverlay() {
        let overlay = document.getElementById('loadingOverlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loadingOverlay';
            overlay.innerHTML = `
                <div class="loading-box">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Processando...</span>
                    </div>
                    <p>Executando Algoritmo Genético...<br>
                    <span class="text-muted" style="font-size:0.78rem;">Isso pode levar alguns segundos.</span></p>
                </div>`;
            document.body.appendChild(overlay);
        }
        overlay.classList.add('active');
    }

    // Auto-dismiss alerts after 5 seconds
    document.querySelectorAll('.alert.alert-success').forEach(function (el) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
            bsAlert.close();
        }, 5000);
    });

})();
