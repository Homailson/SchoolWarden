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
        language: "pt-BR"
    });

    // Atualiza o input hidden com o ID do aluno selecionado
    $('#student-search').on('change', function () {
        var studentId = $(this).val();
        $('input[name="student"]').val(studentId).trigger('change');
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
