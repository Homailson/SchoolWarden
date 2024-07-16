// Controlador do menu de configurações
$(document).ready(function () {
    $('.config-nav-link').click(function (e) {
        e.preventDefault();
        var url = $(this).data('url');
        $('#main-content').load(url);
    });
});


// ativador da classe do menu dropdown de configurações
function toggleMenu() {
    const navFlexColumn = document.getElementById('nav-list');
    if (navFlexColumn.classList.contains('active')) {
        navFlexColumn.classList.remove('active');
    } else {
        navFlexColumn.classList.add('active');
    }
}