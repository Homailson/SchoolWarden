$(document).ready(function () {
    function formatState(state) {
        if (!state.id) {
            return state.text;
        }
        var $state = $(
            '<span><input type="checkbox" style="margin-right: 8px;" />' + state.text + '</span>'
        );
        return $state;
    }

    function formatSelection(state) {
        return state.text;
    }



    $('#student-search').select2({
        templateResult: formatState,
        templateSelection: formatSelection,
        closeOnSelect: false,
        allowClear: true,
        placeholder: "Selecione os alunos",
    }).on('select2:select', function (e) {
        var data = e.params.data;
        var option = $(this).find('option[value="' + data.id + '"]');
        option.prop('selected', true);
        $(this).trigger('change');
    }).on('select2:unselect', function (e) {
        var data = e.params.data;
        var option = $(this).find('option[value="' + data.id + '"]');
        option.prop('selected', false);
        $(this).trigger('change');
    });

    $('#subjects').select2({
        templateResult: formatState,
        templateSelection: formatSelection,
        closeOnSelect: false,
        allowClear: true,
        placeholder: "Selecione as disciplinas",
    }).on('select2:select', function (e) {
        var data = e.params.data;
        var option = $(this).find('option[value="' + data.id + '"]');
        option.prop('selected', true);
        $(this).trigger('change');
    }).on('select2:unselect', function (e) {
        var data = e.params.data;
        var option = $(this).find('option[value="' + data.id + '"]');
        option.prop('selected', false);
        $(this).trigger('change');
    });

    $('#classes').select2({
        templateResult: formatState,
        templateSelection: formatSelection,
        closeOnSelect: false,
        allowClear: true,
        placeholder: "Selecione as turmas",
    }).on('select2:select', function (e) {
        var data = e.params.data;
        var option = $(this).find('option[value="' + data.id + '"]');
        option.prop('selected', true);
        $(this).trigger('change');
    }).on('select2:unselect', function (e) {
        var data = e.params.data;
        var option = $(this).find('option[value="' + data.id + '"]');
        option.prop('selected', false);
        $(this).trigger('change');
    });
});
