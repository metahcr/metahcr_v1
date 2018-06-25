/**
 * Created by pcmarks on 10/17/2014.
 */
/**
 * Provide a global place to store the index of the criterion that is being edited.
 * One index per type of entity being browsed. A value of undefined means that no
 * criterion is being edited for this entity.
 *
 * @type {{investigation: undefined, sample: undefined, organism: undefined, hydrocarbon_resource: undefined}}
 */

var editIndex = {
    'investigation': undefined,
    'sample': undefined,
    'organism': undefined
};

/**
 * endEditing of a search attribute row
 *
 * Called when it is necessary to save the criterion that is being edited. For instance, when
 * adding another browsing criterion. This function is called explicitly; that is, there
 * are no events that trigger a call here.
 *
 * Prior to returning, a validation of all the criterion fields is performed. If validated,
 * return true else return false, requiring some action by the user - cancel, for example.
 * Once validated, the editIndex value for this entity is set to undefined.
 *
 * @param entity
 * @returns {boolean}
 */
function endEditing(entity) {
    if (editIndex[entity] == undefined) {
        return true
    }
    var index = editIndex[entity];
    var filters = $('#' + entity + '-filters');
    if (filters.datagrid('validateRow', index)) {
        var current_row = filters.datagrid('getRows')[index];
        var ed = filters.datagrid('getEditor', {index: index, field: 'attribute_value'});
        var field_text = $(ed.target).combobox('getText');
        var field_value = $(ed.target).combobox('getValue');
        var type = field_value.split('|')[2];
        var value_value;
        current_row['attribute_text'] = field_text;
        ed = filters.datagrid('getEditor', {index: index, field: 'entity_value'});
        field_text = $(ed.target).combobox('getText');
        current_row['entity_text'] = field_text;
        ed = filters.datagrid('getEditor', {index: index, field: 'operator_value'});
        field_text = $(ed.target).combobox('getText');
        current_row['operator_text'] = field_text;
        ed = filters.datagrid('getEditor', {index: index, field: 'value_value'});
        field_text = $(ed.target).combobox('getText');
        current_row['value_text'] = field_text;
        if (type == 'T') {
            value_value = $(ed.target).textbox('getText');
        } else if (type == 'N') {
            value_value = $(ed.target).numberbox('getText');
        } else if (type == 'R') {
            value_value = field_text
        }
        ed = filters.datagrid('getEditor', {index: index, field: 'connector_value'});
        field_text = $(ed.target).combobox('getText');
        current_row['connector_text'] = field_text;
        filters.datagrid('endEdit', index);
        if (!current_row['value_value']) {
            current_row['value_value'] = value_value;
        }
        editIndex[entity] = undefined;
        return true;
    } else {
        $.messager.alert('Incomplete', 'Please enter all required fields.', 'info');
        return false;
    }
}

/**
 * OnClickInvestigationRow
 *
 * @param index
 * @param row
 */
onClickInvestigationRow = function (index, row) {
    onClickRow('investigation', index, row);
};

/**
 * onClickSampleRow
 *
 * @param index
 * @param row
 */
onClickSampleRow = function (index, row) {
    onClickRow('sample', index, row);
};

/**
 * onClickOrganismRow
 *
 * @param index
 * @param row
 */
onClickOrganismRow = function (index, row) {
    onClickRow('organism', index, row);
};

/**
 * onClickRow in the search area
 * @param entity
 * @param index
 * @param row
 */
onClickRow = function (entity, index, row) {
    if (editIndex[entity] != index) {
        if (endEditing(entity)) {
            editIndex[entity] = index;
            var filters = $('#' + entity + '-filters');
            filters.datagrid('selectRow', index).datagrid('beginEdit', index);
            //retrieve_filter_attributes(entity, {'label': row.entry_text, 'value': row.entity_value});
            var ed = filters.datagrid('getEditor', {index: index, field: 'attribute_value'});
            $(ed.target).combobox('setText', row.attribute_text);
            ed = filters.datagrid('getEditor', {index: index, field: 'operator_value'});
            $(ed.target).combobox('setText', row.operator_text);
            retrieve_filter_values(entity, {'text': row.attribute_text, 'value': row.attribute_value});
            ed = filters.datagrid('getEditor', {index: index, field: 'value_value'});
            $(ed.target).combobox('setText', row.value_text);
        } else {
            $('#' + entity + '-filters').datagrid('selectRow', editIndex[entity]);
        }
    }
};

/**
 * addFilter
 *
 * @param entity
 */
addFilter = function (entity) {
    if (endEditing(entity)) {
        var filters = $('#' + entity + '-filters');
        filters.datagrid('appendRow', {});
        editIndex[entity] = filters.datagrid('getRows').length - 1;
        filters.datagrid('selectRow', editIndex[entity]).datagrid('beginEdit', editIndex[entity]);
    }
};

/**
 * removeFilter
 *
 * @param entity
 */
removeFilter = function (entity) {
    if (editIndex[entity] == undefined) {
        return
    }
    var filters = $('#' + entity + '-filters');
    filters.datagrid('cancelEdit', editIndex[entity]).datagrid('deleteRow', editIndex[entity]);
    editIndex[entity] = undefined;
};

/**
 * rejectFilter
 *
 * @param entity
 */
rejectFilter = function (entity) {
    $("#" + entity + "-filters").datagrid('rejectChanges');
    editIndex[entity] = undefined;
};

/**
 * retrieve_filter_attributes
 *
 * @param group
 * @param selection
 */
retrieve_filter_attributes = function (group, selection) {
    var filters = $("#" + group + "-filters");
    var entity = selection.value;
    var url = '/search/entity-cv/' + group + '/' + entity;
    $.ajax({
        url: url,
        success: function (data) {
            var ed = filters.datagrid('getEditor', {index: editIndex[group], field: 'attribute_value'});
            $(ed.target).combobox('clear');
            $(ed.target).combobox('loadData', data);
            ed = filters.datagrid('getEditor', {index: editIndex[group], field: 'operator_value'});
            $(ed.target).combobox('clear');
            ed = filters.datagrid('getEditor', {index: editIndex[group], field: 'value_value'});
            $(ed.target).combobox('clear')
        },
        error: function () {
            alert("failure 4");
        }
    })
};

/**
 * retrieve_filter_values
 *
 * @param source
 * @param selection
 */
retrieve_filter_values = function (source, selection) {
    var url;
    var filters = $('#' + source + '-filters');
    var value_ed = filters.datagrid('getEditor', {index: editIndex[source], field: 'value_value'});
    var operator_ed = filters.datagrid('getEditor', {index: editIndex[source], field: 'operator_value'});
    var connector_ed = filters.datagrid('getEditor', {index: editIndex[source], field: 'connector_value'});
    var category = selection.value.split('|')[0];
    var attribute = selection.value.split('|')[1];
    var type = selection.value.split('|')[2];
    if (type == 'N') {
        $(operator_ed.target).combobox('clear');
        $(operator_ed.target).combobox('loadData',
            [
                {text: '=', value: '=', selected: true},
                {text: '!=', value: '!='},
                {text: '<', value: '<'},
                {text: '>', value: '>'},
                {text: '<=', value: '<='},
                {text: '>=', value: '>='}
            ]);
        $(value_ed.target).numberbox({precision: 4, width: 'auto'});
        $(value_ed.target).numberbox('clear');
        filters.datagrid('autoSizeColumn', 'value_value');
    } else if (type == 'T') {
        $(operator_ed.target).combobox('clear');
        $(operator_ed.target).combobox('loadData',
            [
                {text: 'is', value: '=', selected: true},
                {text: 'is not', value: '!='},
                {text: 'contains', value: 'contains'}
            ]);
        $(value_ed.target).textbox();
        $(value_ed.target).textbox('clear');
        filters.datagrid('autoSizeColumn', 'value_value');
        } else if (type == 'CV') {
        url = '/search/attribute-cv/' + category + '/' + attribute;
        // Did not use easyui url loading facility because it issues a POST and there is no form
        // associated with this action, hence no CSRF token
        $.ajax({
            url: url,
            async: false,
            cache: true,
            success: function (data) {
                $(operator_ed.target).combobox('clear');
                $(operator_ed.target).combobox('loadData',
                    [
                        {text: 'is', value: '=', selected: true},
                        {text: 'is not', value: '!='}
                    ]);
                $(value_ed.target).combobox({width: 'auto'});
                filters.datagrid('autoSizeColumn', 'value_value');
                $(value_ed.target).combobox('clear');
                $(value_ed.target).combobox('loadData', data);
            },
            error: function () {
                alert("failure 3");
            }
        });
    } else if (type == 'R') {
        url = '/search/attribute-r/' + category + '/' + attribute;
        // Did not use easyui url loading facility because it issues a POST and there is no form
        // associated with this action, hence no CSRF token
        $.ajax({
            url: url,
            async: false,
            cache: true,
            success: function (data) {
                $(operator_ed.target).combobox('clear');
                $(operator_ed.target).combobox('loadData',
                    [
                        {text: 'is', value: '=', selected: true},
                        {text: 'is not', value: '!='}
                    ]);
                $(value_ed.target).combobox({width: 'auto'});
                filters.datagrid('autoSizeColumn', 'value_value');
                $(value_ed.target).combobox('clear');
                $(value_ed.target).combobox('loadData', data);
            },
            error: function () {
                alert("failure 3");
            }
        });
    }
    $(connector_ed.target).combobox('select', 'and');
};

searchOrganismsWithFilters = function (filters_j) {
    $("#organism-results").datagrid({
        queryParams: {filters_j: filters_j}
    })
};
/**
 * searchFilters
 *
 * @param source
 */
searchFilters = function (source) {
    if (!endEditing(source)) {
        return;
    }
    var filters = $("#" + source + "-filters").datagrid('getData');
    var filters_j = JSON.stringify(filters);
    var display_source;
    if (source == "organism") {
        searchOrganismsWithFilters(filters_j);
        display_source = source.charAt(0).toUpperCase() + source.slice(1);
        $("#" + source + "-results-panel").panel('setTitle', display_source + "s From Search");
        $('#outer-accordion').accordion('select', 'Search Results');
        $("#organisms-accordion").accordion('select', 0);
        return;
    }
    var url = "search/filtered/" + source + '/' + source;
    $.ajax({
        url: url,
        data: filters_j,
        dataType: 'json',
        success: function (data) {
            display_source = source.charAt(0).toUpperCase() + source.slice(1);
            if (source != "organism") {
                $("#" + source + "-results-panel").panel('setTitle', display_source + "s From Search")
            }
            if (data.length == 0) {
                $.messager.alert('No Results', 'No matching ' + display_source + 's found.', 'info');
            } else {
                $('#outer-accordion').accordion('select', 'Search Results');
                if (source == 'organism') {
                    $("#organisms-accordion").accordion('select', 0)
                }
                $("#" + source + "-results").datagrid('loadData', data)
            }
        }
    });

};

/**
 *
 */
$('#investigation-results').datagrid({
    onClickRow: function (index, rowValue) {
        retrieve_infosheet2('investigation', index, rowValue);
    }
});

/*
 Can be a Sample, Single Gene Analysis or Metagenome Analysis entry.  Indicated by a 'type' value.
 */
$('#sample-results').datagrid({
    onClickRow: function (index, rowValue) {
        retrieve_infosheet2('sample', index, rowValue);
    },
    view: detailview,
    detailFormatter: function (index, row) {
        // Need id sample id to distinguish one set of analyses from another
        var id = row['id'];
        return '<div style="padding:2px;"><table id="sample-analyses-' + id + '" class="ddv"></table></div>';
    },
    onExpandRow: function (index, row) {
        var ddv = $(this).datagrid('getRowDetail', index).find('table.ddv');
        ddv.datagrid({
            url: '/browse/sample-analyses/' + row['id'],
            method: 'get',
            fitColumns: true,
            loadMsg: '',
            height: 'auto',
            singleSelect: true,
            onClickRow: function (index, rowValue) {
                var type = rowValue.type;
                if (type == 'Single Gene') {
                    retrieve_infosheet2('sga', index, rowValue);
                } else if (type == 'Metagenome') {
                    retrieve_infosheet2('mga', index, rowValue)
                }
            },
            columns: [[
                {field: 'id', title: 'Id'},
                {field: 'type', title: 'Type'},
                {field: 'samp_anal_name', title: 'Analysis Name'},
                {field: 'analysis_date', title: 'Analysis Date'},
                {field: 'uploaded_by', title: 'Uploaded by'},
                {field: 'upload_date', title: 'Upload Date'},
                {field: 'sequencing_center', title: 'Sequencing Center'},
                {field: 'seq_method', title: 'Sequencing Method'}
            ]],
            onResize: function () {
                $('#sample-results').datagrid('fixDetailRowHeight', index);
            },
            onLoadSuccess: function () {
                setTimeout(function () {
                    $('#sample-results').datagrid('fixDetailRowHeight', index);
                }, 0);
            }
        });
        $('#sample-results').datagrid('fixDetailRowHeight', index);
    },
    onLoadSuccess: function (data) {
        for (var i = 0; i < data.rows.length; i++) {
            if (data.rows[i].analyses_count == 0) {
                $(this).datagrid('getExpander', i).hide();
            }
        }
    }
});

var organism_results_dg = $('#organism-results').datagrid({
    columns: [[
        {field: 'id', title: 'ID',
            styler: function(value, row, index) {
                if (row['samples'] == 'Y'){
                    return 'background-color: #95B8E7;';
                }
            }
        },
        {field: 'family', title: 'Family'},
        {field: 'genus', title: 'Genus'}
    ]],
    view: detailview,
    detailFormatter: function (index, row) {
        var row1 = '<tr>' + prepare_cell('Superkingdom', row['superkingdom']) + prepare_cell('Phylum', row.phylum) + '</tr>';
        var row2 = '<tr>' + prepare_cell('Class', row.class) + prepare_cell('Order', row.order) + '</tr>';
        var row3 = '<tr>' + prepare_cell('Metab. Type', row.metabolism_type) + prepare_cell('Threat', row.risk) + '</tr>';
        var row4 = '<tr>' + prepare_cell('Species', row.species) + prepare_cell('Strain', row.strain) + '</tr>';
        var table = '<table border="0" style="width:100%">' + row1 + row2 + row4 + row3 + '</table>';
        return '<div class="ddv" style="padding:5px 0">' + table + '</div>';
    },
    onClickRow: function (index, rowValue) {
        retrieve_infosheet2('organism', index, rowValue);
    }
});

$('#organism-results-in-analysis').datagrid({
    onClickRow: function(index, rowValue) {
        retrieve_infosheet2('organism', index, rowValue);
    },
    view: detailview,
    detailFormatter: function (index, row) {
        var row1 = '<tr>' + prepare_cell('Superkingdom', row.superkingdom) + prepare_cell('Phylum', row.phylum) + '</tr>';
        var row2 = '<tr>' + prepare_cell('Class', row.class) + prepare_cell('Order', row.order) + '</tr>';
        var row3 = '<tr>' + prepare_cell('Metab. Type', row.metabolism_type) + prepare_cell('Threat', row.risk) + '</tr>';
        var row4 = '<tr>' + prepare_cell('Species', row.species) + prepare_cell('Strain', row.strain) + '</tr>';
        var table = '<table border="0" style="width:100%">' + row1 + row2 + row4 + row3 + '</table>';
        return '<div class="ddv" style="padding:5px 0">' + table + '</div>';
    },
    onExpandRow: function (index, row) {
        $('#organism-results').datagrid('fixDetailRowHeight', index);
    }
});

/**
 *
 * @param label
 * @param value
 * @returns {string|*}
 */
prepare_cell = function (label, value) {
    cell = '<td style="font-weight: bold">' +
        label +
        ':</td><td>' +
        value + '</td>';
    return cell
};

/**
 * Show all the "metadata" associated with many of the MetaHCR entities: Investigations, Samples
 * and Organisms.
 * This function can be called from both the Browse and Search pages.
 * @param source
 * @param index
 * @param data
 */
retrieve_infosheet2 = function(source, index, data) {
    retrieve_infosheet(source, index, data, true);
};

retrieve_infosheet = function (source, index, data, suppressed) {
    var url = '/source-infosheet/' + source + '/' + data['id'];
    if (source == "sample" || source == 'investigation' || source == 'organism') {
        url += '?suppressed=' + suppressed;
    }
    $("#infosheet").load(url, function () {
        // Remove the suppression icon from  the third accordion panel ('Infosheet').
        var investigation_panel =  $('#outer-accordion').accordion('getPanel', 2);
        investigation_panel.panel(
            {tools: []});
        $('#outer-accordion').accordion('select', 'Infosheet');
        /*
         If the request is for a Single Gene Analysis or Metagenome Analysis, the Sample that it is associated with
         has been loaded into the page and can be shown. Now we need to load the Analysis Metadata and the Analysis
         Results.
         */
        var sample_info_accordion = $('#sample-info-accordion');
        sample_info_accordion.accordion('unselect', 1);
        sample_info_accordion.accordion('unselect', 2);
        sample_info_accordion.accordion('unselect', 3);
        if (source == 'sga') {
            var sga_organisms = $('#single_gene_analysis_organisms');
            sga_organisms.datagrid(
                {queryParams: {sga_id: data['id']}}
            );
            sga_organisms.datagrid('enableFilter');
            sample_info_accordion.accordion('select', 1)
        } else if (source == 'mga') {
            var mga_genes = $('#metagenomeresultgene-results');
            mga_genes.datagrid(
                {queryParams: {mga_id: data['id']}}
            );
            mga_genes.datagrid('enableFilter');
            sample_info_accordion.accordion('select', 2);
            sample_info_accordion.accordion('select', 3);
        } else if (source == 'sample') {
            // get the first accordion panel ('Metadata') and add suppression icon.
            var sample_panel = sample_info_accordion.accordion('getPanel', 0);
            sample_panel.panel(
                {tools: [{iconCls: 'icon-eye',
                    handler: function(){retrieve_infosheet(source, index, data, !suppressed);}}]});
            sample_info_accordion.accordion('select', 0);
        } else if (source == 'investigation') {
            // get the third outer accordion panel ('Infosheet') and add suppression icon.
            var infosheet_panel =  $('#outer-accordion').accordion('getPanel', 2);
            infosheet_panel.panel(
                {tools: [{iconCls: 'icon-eye',
                    handler: function(){retrieve_infosheet(source, index, data, !suppressed);}}]});
            $('#outer-accordion').accordion('select', 'Infosheet');
        } else if (source == 'organism') {
            // get the third outer accordion panel ('Infosheet') and add suppression icon.
            var infosheet_panel =  $('#outer-accordion').accordion('getPanel', 2);
            infosheet_panel.panel(
                {tools: [{iconCls: 'icon-eye',
                    handler: function(){retrieve_infosheet(source, index, data, !suppressed);}}]});
            $('#outer-accordion').accordion('select', 'Infosheet');
        }
    });
};

/**
 * getLinkedData - get the data associated with one of the results:
 *      investigations -> samples
 *      samples -> investigations or organisms
 *      organisms -> samples
 *
 * @param source
 * @param target
 * @returns {boolean}
 */
getLinkedData = function (source, target) {
    var u_target = target.charAt(0).toUpperCase() + target.slice(1);
    var idList = [];
    var name = '';
    var selected_row = null;
    var value;
    var url;

    if (source == 'sample' && target == 'organism') {
        // Need to have an analysis selected in order to retrieve its organisms data
        // The analyses datagrid has to have been initialized before it can be checked for a selection
        var analyses_datagrids = $('table[id^="sample-analyses"]');
        if (analyses_datagrids) {
            for (var i = 0; i < analyses_datagrids.length; i++) {
                var analyses_datagrid = analyses_datagrids[i];
                if (analyses_datagrid.classList.contains('datagrid-f')) {
                    selected_row = $(analyses_datagrid).datagrid('getSelected');
                    if (selected_row) break;
                }
            }
        }
        if (!selected_row) {
            $.messager.alert('Info', 'Please select an analysis to get its organisms.', 'info');
            return false;
        }
        var type = selected_row['type'];
        if (type == 'Single Gene') source = 'sga';
        if (type == 'Metagenome') source = 'mga';
        idList = [selected_row['id']];
        // Unselect this analysis selection so that there is no conflict with other analysis selections from
        // other samples in this result panel.
        $(analyses_datagrid).datagrid('unselectAll');
    } else if (source == 'sample' && target == 'investigation') {
        selected_row = $('#sample-results').datagrid('getSelected');
        if (!selected_row) return false;
        idList = [selected_row['id']];
        name = [selected_row['source_mat_id']];
    } else if (source == 'investigation' && target == 'sample') {
        selected_row = $('#investigation-results').datagrid('getSelected');
        if (!selected_row) return false;
        idList = [selected_row['id']];
        name = [selected_row['investigation_name']];
    } else if (source == 'organism') {
        selected_row = $('#organism-results').datagrid('getSelected');
        if (!selected_row) {
            $.messager.alert('Info', 'Please select an organism.', 'info');
            return false;
        }
        idList = [selected_row['id']];
        name = 'species ' + selected_row['species'];
    } else if (source == 'organism-in-analysis' && (target == 'genus' || target == 'family')) {
        selected_row = $('#organism-results-in-analysis').datagrid('getSelected');
        if (!selected_row) {
            $.messager.alert('Info', 'Please select an organism.', 'info');
            return false;
        }
        // Get the selected Organism's family or genus value
        value = [selected_row[target]];
        if (value == "") {
            $.messager.alert('No ' + target, 'Organism does not have a value for its '+target);
            return false;
        }
        url = 'organism-'+target+'-infosheet/' + value;
        $("#infosheet").load(url, function() {
            $("#outer-accordion").accordion('select', 'Infosheet');
        });
    } else if (source == 'organism-results' && (target == 'genus' || target == 'family')) {
        selected_row = $('#organism-results').datagrid('getSelected');
        if (!selected_row) {
            $.messager.alert('Info', 'Please select an organism.', 'info');
            return false;
        }
        // Get the selected Organism's family or genus value
        value = [selected_row[target]];
        if (value == "") {
            $.messager.alert('No ' + target, 'Organism does not have a value for its '+target);
            return false;
        }
        url = 'organism-'+target+'-infosheet/' + value;
        $("#infosheet").load(url, function() {
            $("#outer-accordion").accordion('select', 'Infosheet');
        });
    }
    if ((source == 'sga' || source == 'mga') && target == 'organism') {
        var organisms_accordion = $("#organisms-accordion");
        organisms_accordion.accordion('getPanel', 1).panel('setTitle', 'From Sample Analysis Id: ' + idList[0]);
        organisms_accordion.accordion('select', 1);
        $("#organism-results-in-analysis").datagrid({
            queryParams: {source: source, id: idList[0]}
        })

    } else if (!((source == 'organism-in-analysis') ||
                 (source == 'organism-results'))) {
        url = "search-results-get/" + source + "/" + target;
        var idList_j = JSON.stringify({"ids": idList});
        $.ajax({
            url: url,
            async: false,
            data: idList_j,
            dataType: 'json',
            success: function (data) {
                if (data.length == 0) {
                    $.messager.alert('Nothing found', 'No ' + target + 's found.', 'info');
                    name = '';
                }
                if (target == 'organism') {
                    // The source must be a Sample
                    var organisms_accordion = $('#organisms-accordion');
                    organisms_accordion.accordion('getPanel', 1).panel('setTitle', 'From Sample Analysis Id: ' + idList[0]);
                    organisms_accordion.accordion('select', 1);
                    $("#organism-results-in-analyis").datagrid()
                } else {
                    $('#' + target + '-results-panel').panel('setTitle', u_target + 's for ' + source + ' ' + name);
                    $('#' + target + '-results').datagrid('loadData', data);
                }
            },
            error: function (xhr, status, err) {
                $.messager.alert('Retrieval Error', err.toString(), 'error');
            }
        });
    }
};
