$(document).ready(function () {
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

    $('#student-search').on('change', function () {
        var studentId = $(this).val();
        $('input[name="student"]').val(studentId).trigger('change');
    });
});