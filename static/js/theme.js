// ===== Gestion du thème Dark/Light Mode =====

document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    
    if (!themeToggle) {
        console.error('Bouton theme-toggle non trouvé !');
        return;
    }
    
    // Récupérer le thème sauvegardé (par défaut: dark)
    let currentTheme = localStorage.getItem('festy-theme') || 'dark';
    
    // Fonction pour appliquer le thème
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        document.body.setAttribute('data-theme', theme);
        
        // Mettre à jour le texte du bouton
        if (theme === 'dark') {
            themeToggle.textContent = 'Mode Jour';
        } else {
            themeToggle.textContent = 'Mode Nuit';
        }
        
        console.log('Thème appliqué:', theme);
    }
    
    // Appliquer le thème au chargement
    applyTheme(currentTheme);
    
    // Écouter le clic sur le bouton
    themeToggle.addEventListener('click', function() {
        // Basculer le thème
        currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        // Sauvegarder dans localStorage
        localStorage.setItem('festy-theme', currentTheme);
        
        // Appliquer le nouveau thème
        applyTheme(currentTheme);
        
        // Appeler la fonction de mise à jour des graphiques si elle existe
        if (typeof updateChartColors === 'function') {
            updateChartColors();
        }
        
        console.log('Nouveau thème:', currentTheme);
    });
    
    console.log('Script theme.js chargé et bouton attaché');
});
