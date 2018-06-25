/**
 * Created by pcmarks on 11/2/2015.
 */




/**
 * Set up the datagrid that will display all of the organisms associated with a
 * single gene analysis
 *
 * @param id   single gene analysis id
 */
prepare_sga_organism_datagrid = function(id) {
    sga_org_dg = $('#single_gene_analysis_organisms').datagrid(
        {queryParams: {sga_id: id}});
    var metabolism_type_choices = get_r_values('metabolism_type', 'type');
    var risk_choices = get_cv_values('organism', 'risk');

    sga_org_dg.datagrid('enableFilter',[
        {field: 'metabolism_type', type: 'combobox',
            options:{
                data: metabolism_type_choices,
                editable: false,
                onChange: function(value){
                    if (value == ''){
                        sga_org_dg.datagrid('removeFilterRule', 'metabolism_type')
                    } else if(typeof value !== 'undefined') {
                        sga_org_dg.datagrid('addFilterRule', {
                            field: 'metabolism_type',
                            op: 'equal',
                            value: value
                        });
                    }
                    sga_org_dg.datagrid('doFilter');
                }
            }
        },
        {field: 'risk', type: 'combobox', width: 10,
            options:{
                data: risk_choices,
                editable: false,
                onChange: function(value){
                    if (value == ''){
                        sga_org_dg.datagrid('removeFilterRule', 'risk')
                    } else if(typeof value !== 'undefined') {
                        sga_org_dg.datagrid('addFilterRule', {
                            field: 'risk',
                            op: 'equal',
                            value: value
                        });
                    }
                    sga_org_dg.datagrid('doFilter');
                }
            }
        }
    ]);

};

/**
 * Fetch the infosheet portion of the browsing page. Retrieval is based on the result's 'id' field.
 * Note that the 'id' field may be hidden. This call is triggered by clicking on a
 * browsing row. It uses the accordion behavior. Once the html is loaded, open it.
 *
 * @param source  - 'investigation', 'sample', etc.
 * @param index   - which row in the results table
 * @param data    - the data in the results table row. Only use the 'id' field
 */
retrieve_infosheet2 = function(source, index, data) {
    var infosheets = $('#infosheets-accordion');
    if (source == 'sample') {
        clear_infosheets(infosheets);
        $('#sga-sample-chosen').text('You have chosen Sample ' + data['id'] + ', ' +
            data['samp_name'] + ' - ' + data['samp_description'])
        $('#mga-sample-chosen').text('You have chosen Sample ' + data['id'] + ', ' +
            data['samp_name'] + ' - ' + data['samp_description'])
        infosheets.accordion('add', {
            title: 'Sample',
            selected: false,
            content: "<div id='sample'></div>"
        });
        $('#sample').load('/source-infosheet/sample/' + data['id'], function() {
            infosheets.accordion('select', 'Sample');
            $('#sample-info-accordion').accordion('select', 'Metadata');
        });
    } else if (source == 'sample-sga') {
        clear_infosheets(infosheets);
        infosheets.accordion('add', {
            title: 'Sample',
            selected: false,
            content: "<div id='sample'></div>"
        });
        $('#sample').load('/source-infosheet/sga/' + data['id'], function() {
            infosheets.accordion('select', 'Sample');
            prepare_sga_organism_datagrid(data['id']);
            $('#sample-info-accordion').accordion('select', 1);
        });
    } else if (source == 'sample-mga') {
        clear_infosheets(infosheets);
        infosheets.accordion('add', {
            title: 'Sample',
            selected: false,
            content: "<div id='sample'></div>"
        });
        $('#sample').load('/source-infosheet/mga/' + data['id'], function() {
            infosheets.accordion('select', 'Sample');
            $('#metagenomeresultgene-results').datagrid(
                {queryParams: {mga_id: data['id']}}
            );
            $('#metagenomeresultgene-results').datagrid('enableFilter');
            $('#sample-info-accordion').accordion('select', 2);
            $('#sample-info-accordion').accordion('select', 3);
        });
    }
};

sga_submit_form = function() {
    var formData = new FormData($('#sga-upload-form')[0]);
    $.ajax({
        url: "/sga_upload",
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        type: 'POST',
        success: function(data) {
            $('#sga-analysis').html(data);
        }
    });
};

/**
 *
 * @param sample_count
 */
sga_upload_samples = function(number_of_samples) {
    var sga_sample_names = $('#sga-sample-names').datalist('getData');
    $('#sga-loading-image').show();
    $('#sga-analysis').load('/sga_upload/samples',
            function() {
                //$.messager.alert('Upload Finished', 'Upload completed.', 'info');
                // Reload the analyses results and sample lists
                $('#sga-loading-image').hide();
                $('#analyses-results').datagrid('reload');
                $('#sample-results').datagrid('reload');
            });
};

sga_download_log = function() {
    $.get('/sga_upload/log_file');
};

mga_submit_form = function() {
    if (!$('#id_scaffold_file').val() || !$('#id_gene_function_file').val() || !$('#id_rna_file').val()) {
        $.messager.alert('Missing Files', 'You must supply three files.', 'warning');
        return false;
    }
    //$('#mga-upload-form').ajaxStart(function() {
    //    $('#mga-loading-image').show();
    //});
    //$('#mga-upload-form').ajaxStop(function() {
    //    $('#mga-loading-image').hide();
    //});
    var formData = new FormData($('#mga-upload-form')[0]);
    $.ajax({
        url: "/mga_upload",
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        type: 'POST',
        success: function(data) {
            $('#mga-loading-image').hide();
            $('#mga-analysis').html(data);
            // Reload the analyses results and sample lists
            $('#sample-results').datagrid('reload');
            $('#analyses-results').datagrid('reload');
        }
    });
};

/**
 * mga_upload_analysis
 *
 * Begin the uploading of a metagenome analysis but only if a sample has been selected in
 * the sample list.
 *
 */
mga_upload_analysis = function() {
    var sample_selected = $('#sample-results').datagrid('getSelected');
    if (!sample_selected) {
        $.messager.alert('No Selection', 'Please select a sample first.', 'info');
    } else {
        var sample_name = sample_selected.samp_name;
        var sample_id = sample_selected.id;
        var message = 'Upload a metagenome analysis to the sample ' + sample_name;
        $.messager.confirm('Confirm', message,
            function(r) {
                if (r) {
                    $('#mga-loading-image').show();
                    $('#mga-analysis').load(
                        '/mga_upload/sample/' + sample_id,
                        function() {
                            //$.messager.alert('All Done.', 'Loading has completed', 'info');
                            $('#mga-loading-image').hide();
                            $('#sample-results').datagrid('reload');
                            $('#analyses-results').datagrid('reload');
                        }
                    );
                }
            }
        );
    }
};

/**
 * analysis_delete()
 *
 * Delete the Biological Analysis that the user has selected from the analyses list.
 *
 */
analysis_delete = function() {
    var infosheets = $('#infosheets-accordion');
    var analysis_selected = $('#analyses-results').datagrid('getSelected');
    if (!analysis_selected) {
        $.messager.alert('No Selection', 'Please select an analysis.', 'info');
    } else {
        var analysis_name = analysis_selected.analysis_name;
        var upload_date = analysis_selected.upload_date;
        var message = 'Are you sure that you want to delete the analysis named ' +
            analysis_name +
            ' uploaded on ' +
                upload_date +
                '?';
        $.messager.confirm('Confirm', message,
            function (r) {
                if (r) {
                    $.get('/upload_maint/delete/' + analysis_selected.id,
                    function(data) {
                        $.messager.alert('Analysis Deleted', 'The analysis was deleted', 'info');
                        $('#analyses-results').datagrid('reload');
                        $('#sample-results').datagrid('reload');
                        clear_infosheets(infosheets);
                    });
                }
            }
        )
    }
};
/**
 * analysis_log_download()
 *
 * Download the log file that is associated with the the Biologicial Analysis that the user has selected
 * in the analysis list.
 *
 */
analysis_log_download = function() {
    var infosheets = $('#infosheets-accordion');
    var analysis_selected = $('#analyses-results').datagrid('getSelected');
    if (!analysis_selected) {
        $.messager.alert('No Selection', 'Please select an analysis.', 'info');
    } else {
        //$.get('/upload_maint/log_file/' + analysis_selected.id);
        $("#downloadFrame").remove();
        $('body').append('<iframe id="downloadFrame" style="display:none"></iframe>');
        $("#downloadFrame").attr('src', '/upload_maint/log_file/' + analysis_selected.id);
    }
};

$(document).ready(function() {
    var sample_dg;
    var sample_dg_conf;
    sample_dg_conf = {
        options: {
            url: 'browse/samples-page',
            method: 'get',
            striped: true,
            pagination: true,
            fitColumns: true,
            pageSize: 20,
            singleSelect: true,
            remoteFilter: true,
            queryParms: {source: 'sample'},
            idField: 'id',
            columns: [[
                {field: 'id', hidden: true},
                {field: 'source_mat_id', title: 'Source Mat. ID', width: 200, sortable: true},
                {field: 'samp_type', title: 'Type', width: 80, sortable: true},
                {field: 'samp_subtype', title: 'Sub Type', width: 80, sortable: true},
                {field: 'samp_description', title: 'Description', width: 300, sortable: true},
                {field: 'samp_comment', title: 'Comment', width: 320, sortable: true}
            ]],
            onLoadSuccess: function(data) {
                for (var i = 0; i <data.rows.length; i++) {
                    if (data.rows[i].analyses_count == 0) {
                        $(this).datagrid('getExpander', i).hide();
                    }
                }
            },
            onClickRow: function (index, rowValue) {
                retrieve_infosheet2('sample', index, rowValue);
            },
            onExpandRow: function(index, rowValue) {
                sample_dg.datagrid('selectRow', index);
                retrieve_infosheet2('sample', index, rowValue);
            }
        },
        subgrid: {
            options: {
                url: 'browse/sample-analyses',
                method: 'get',
                foreignField: 'id',
                fitColumns: true,
                loadMsg: '',
                singleSelect: true,
                height: 'auto',
                columns: [[
                    {field: 'id', title: 'ID'},
                    {field: 'type', title: 'Type'},
                    {field: 'samp_anal_name', title: 'Analysis Name'},
                    {field: 'analysis_date', title: 'Analysis Date'},
                    {field: 'upload_date', title: 'Upload Date'},
                    {field: 'uploaded_by', title: 'Uploaded By'},
                    {field: 'sequencing_center', title: 'Sequencing Center'}
                ]],
                onClickRow: function(index, rowValue) {
                    var type = rowValue.type;
                    if (type == 'Single Gene') {
                        retrieve_infosheet2('sample-sga', index, rowValue);
                    } else if (type == 'Metagenome') {
                        retrieve_infosheet2('sample-mga', index, rowValue)
                    }

                }
            }
        }
    };

    /*
     Build the Samples datagrid based on the configuration defined above.
     */
    sample_dg = $('#sample-results').datagrid('subgrid', sample_dg_conf);


    /*
     Add the ability to do filter searches in the Sample datagrid
     */
    var samp_type_choices = get_cv_values('sample', 'samp_type');
    var samp_subtype_choices = get_cv_values('sample', 'samp_subtype');

    sample_dg.datagrid('enableFilter',[
        {field: 'samp_type', type: 'combobox',
            options:{
                data: samp_type_choices,
                editable: false,
                onChange: function(value){
                    if (value == ''){
                        sample_dg.datagrid('removeFilterRule', 'samp_type')
                    } else if(typeof value !== 'undefined') {
                        sample_dg.datagrid('addFilterRule', {
                            field: 'samp_type',
                            op: 'equal',
                            value: value
                        });
                    }
                    sample_dg.datagrid('doFilter');
                }
            }
        },
        {field: 'samp_subtype', type: 'combobox',
            options:{
                data: samp_subtype_choices,
                editable: false,
                onChange: function(value){
                    if (value == ''){
                        sample_dg.datagrid('removeFilterRule', 'samp_subtype')
                    } else if(typeof value !== 'undefined') {
                        sample_dg.datagrid('addFilterRule', {
                            field: 'samp_subtype',
                            op: 'equal',
                            value: value
                        });
                    }
                    sample_dg.datagrid('doFilter');
                }
            }
        }
    ]);

    /*
     Build the Analyses datagrid
     */
    var analyses_dg = $('#analyses-results').datagrid({
        url: 'browse/analyses-page',
        method: 'get',
        striped: true,
        pagination: true,
        fitColumns: true,
        pageSize: 10,
        singleSelect: true,
        remoteFilter: true,
        queryParms: {source: 'biological_analysis'},
        idField: 'id',
        columns: [[
            {field: 'id', hidden: true},
            {field: 'type', title: 'Type', sortable: true},
            {field: 'samp_anal_name', title: 'Analysis Name', sortable: true},
            {field: 'upload_date', title: 'Upload Date', sortable: true},
            {field: 'uploaded_by', title: 'Uploaded By', sortable: true},
            {field: 'sequencing_center', title: 'Sequencing Center', sortable: true},
            {field: 'analysis_date', title: 'Analysis Date', sortable: true}
        ]],
        onClickRow: function (index, rowValue) {
            var type = rowValue.type;
            if (type == 'Single Gene') {
                retrieve_infosheet2('sample-sga', index, rowValue);
            } else if (type == 'Metagenome') {
                retrieve_infosheet2('sample-mga', index, rowValue)
            }
        },
        toolbar:[{
            text: 'Delete',
            iconCls: 'icon-delete',
            handler: function(){analysis_delete();}},
            {
            text: 'Download Log File',
            iconCls: 'tree-file',
            handler: function(){analysis_log_download();}}
        ]
    });

    var analysis_type_choices = get_cv_values('biological_analysis', 'type');

    /*
     Add the ability to do filter searches in the Analyses datagrid
     */
    analyses_dg.datagrid('enableFilter', [
        {field: 'type', type: 'combobox',
            options:{
                data: analysis_type_choices,
                editable: false,
                onChange: function(value){
                    if (value == ''){
                        analyses_dg.datagrid('removeFilterRule', 'type')
                    } else if(typeof value !== 'undefined') {
                        analyses_dg.datagrid('addFilterRule', {
                            field: 'type',
                            op: 'equal',
                            value: value
                        });
                    }
                    analyses_dg.datagrid('doFilter');
                }
            }
        }
    ]);


});