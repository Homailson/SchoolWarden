$(document).ready(function () {
    // Configuração do Select2 para o campo de busca de alunos
    $('#student-search').select2({
        ajax: {
            url: window.STUDENT_SEARCH_URL,
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term
                };
            },
            processResults: function (data) {
                return {
                    results: data
                };
            }
        },
        minimumInputLength: 1,
        language: "pt-BR",
        closeOnSelect: false, // Permite múltiplas seleções sem fechar o dropdown
        placeholder: "pesquisar", // Define o placeholder
        allowClear: true, // Permite limpar a seleção
        multiple: true // Permite seleção múltipla
    });

    // Atualiza o input hidden com os IDs dos alunos selecionados
    $('#student-search').on('change', function () {
        var selectedStudents = $(this).val(); // Array com os IDs dos alunos selecionados
        $('input[name="student"]').val(selectedStudents.join(',')).trigger('change'); // Converte o array para uma string separada por vírgulas
    });

    // Configuração do Select2 para o campo de classificação
    $('#classification').select2({
        placeholder: "Selecione um tipo"
    });
    $('#teacher').select2({
        placeholder: "Selecione um professor(a)"
    });
    $('#classe').select2({
        placeholder: "Selecione uma turma"
    });
    $('#subject').select2({
        placeholder: "Selecione uma disciplina"
    });
    $('#subjects').select2({
        placeholder: "Selecione as disciplinas",
        multiple: true
    });
    $('#filterStatus').select2({
    });
});
