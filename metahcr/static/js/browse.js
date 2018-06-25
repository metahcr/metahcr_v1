/**
 * Created by pcmarks on 1/5/2015.
 *
 * The functions in this file are responsible for the display  and control of all HTML on the Browse page of MetaHCR
 *
 * The browse template page is organized as follows:
 *
 *  1. A Tab browsing area
 *      Tab: Investigations
 *      Tab: Samples
 *      Tab: Analyses
 *      Tab: Organisms
 *      Tab: Hydrocarbon Resources
 *  2. An Infosheet Accordion - the accordion is dynamically created depending on what is selected in the Browsing area
 *  3. A window div that is used to create the Google Map popup window when a user selects a location.
 *
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
    var pager = sga_org_dg.datagrid('getPager');
    pager.pagination({
        buttons: [{iconCls: 'icon-save', text: "Download",
            handler: function(){browse_results_export('single_gene_analysis_organisms', id);} }]
    });

};

/**
 * Fetch the infosheet portion of the browsing page. Retrieval is based on the result's 'id' field.
 * Note that the 'id' field may be hidden. This call is triggered by clicking on a
 * browsing row. It uses the accordion behavior. Once the html is loaded, open it.
 *
 * Values for the source parameter:
 *          'investigation'
 *          'investigation-sample'
 *          'investigation-sample-sga'
 *          'investigation-sample-mga'
 *          'sample'
 *          'sample-sga'
 *          'sample-mga'
 *          'organism'
 *          'hydrocarbon_resource'
 *
 * @param source  - 'investigation', 'sample', etc.
 * @param index   - which row in the results table
 * @param data    - the data in the results table row. Only use the 'id' field
 */
retrieve_infosheet2 = function(source, index, data) {
    retrieve_infosheet(source, index, data, true);
};

retrieve_infosheet_full = function(source, index, data) {
    retrieve_infosheet(source, index, data, false);
};

retrieve_infosheet = function(source, index, data, suppressed) {
    var infosheets = $('#infosheets-accordion');
    if (source == 'investigation') {
        clear_infosheets(infosheets);
        infosheets.accordion('add', {
            title: 'Investigation',
            selected: false,
            tools:[
                {iconCls: 'icon-eye', handler:function(){retrieve_infosheet(source, index, data, !suppressed)}}
            ],
            content: "<div id='investigation'></div>"
        });
        // var panel = infosheets.accordion('getPanel', 'Investigation');
        // panel.panel({tools:[{iconCls: 'icon-add', handler:function(){alert('new')}}]});

        $('#investigation').load('/source-infosheet/investigation/' + data['id'] +'?suppressed=' + suppressed, function () {
            infosheets.accordion('select', 'Investigation');
        })
    } else if (source == 'investigation-sample') {
        infosheets.accordion('unselect', 'Investigation');
        clear_infosheets_from(infosheets, 0);
        if (!infosheets.accordion('getPanel', 'Sample')) {
            infosheets.accordion('add', {
                title: 'Sample',
                selected: false,
                tools:[
                    {iconCls: 'icon-eye', handler:function(){retrieve_infosheet(source, index, data, !suppressed)}}
                ],
                content: "<div id='sample'></div>"
            });
        }
        $('#sample').load('/source-infosheet/sample/' + data['id'] + '?suppressed=' + suppressed, function() {
            infosheets.accordion('select', 'Sample');
            $('#sample-info-accordion').accordion('select', 'Metadata');
        });
    } else if (source == 'investigation-sample-sga') {
        clear_infosheets_from(infosheets, 0);
        if (!infosheets.accordion('getPanel', 'Sample')) {
            infosheets.accordion('add', {
                title: 'Sample',
                selected: false,
                tools:[
                    {iconCls: 'icon-eye', handler:function(){retrieve_infosheet(source, index, data, !suppressed)}}
                ],
                content: "<div id='sample'></div>"
            });
        }
        $('#sample').load('/source-infosheet/sga/' + data['id'] + '?suppressed=' + suppressed, function() {
            infosheets.accordion('select', 'Sample');
            prepare_sga_organism_datagrid(data['id']);
            $('#sample-info-accordion').accordion('select', 1);
        });
    } else if (source == 'investigation-sample-mga') {
        clear_infosheets(infosheets, 0);
        if (!infosheets.accordion('getPanel', 'Sample')) {
            infosheets.accordion('add', {
                title: 'Sample',
                selected: false,
                tools:[
                    {iconCls: 'icon-eye', handler:function(){retrieve_infosheet(source, index, data, !suppressed)}}
                ],
                content: "<div id='sample'></div>"
            });
        }
        $('#sample').load('/source-infosheet/mga/' + data['id'] + '?suppressed=' + suppressed, function() {
            infosheets.accordion('select', 'Sample');
            var mga_dg = $('#metagenome_analysis_genes');
            mga_dg.datagrid(
                {queryParams: {mga_id: data['id']}}
            );
            mga_dg.datagrid('enableFilter');
            // Add a download button to the pagination line
            var pager = mga_dg.datagrid('getPager');
            pager.pagination({
                buttons: [{iconCls: 'icon-save', text: "Download",
                    handler: function(){browse_results_export('metagenome_analysis_genes', data['id']);} }]
            });
            $('#sample-info-accordion').accordion('select', 2);
            $('#sample-info-accordion').accordion('select', 3);
        });
    } else if (source == 'sample') {
        clear_infosheets(infosheets);
        infosheets.accordion('add', {
            title: 'Sample',
            selected: false,
            tools:[
                {iconCls: 'icon-eye', handler:function(){retrieve_infosheet(source, index, data, !suppressed)}}
            ],
            content: "<div id='sample'></div>"
        });
        $('#sample').load('/source-infosheet/sample/' + data['id'] + '?suppressed=' + suppressed, function() {
            infosheets.accordion('select', 'Sample');
            $('#sample-info-accordion').accordion('select', 'Metadata');
        });
    } else if (source == 'sample-sga') {
        clear_infosheets(infosheets);
        infosheets.accordion('add', {
            title: 'Sample',
            selected: false,
            tools:[
                {iconCls: 'icon-eye', handler:function(){retrieve_infosheet(source, index, data, !suppressed)}}
            ],
            content: "<div id='sample'></div>"
        });
        $('#sample').load('/source-infosheet/sga/' + data['id'] + '?suppressed=' + suppressed, function() {
            infosheets.accordion('select', 'Sample');
            prepare_sga_organism_datagrid(data['id']);
            $('#sample-info-accordion').accordion('select', 1);
        });
    } else if (source == 'sample-mga') {
        clear_infosheets(infosheets);
        infosheets.accordion('add', {
            title: 'Sample',
            selected: false,
            tools:[
                {iconCls: 'icon-eye', handler:function(){retrieve_infosheet(source, index, data, !suppressed)}}
            ],
            content: "<div id='sample'></div>"
        });
        $('#sample').load('/source-infosheet/mga/' + data['id'] + '?suppressed=' + suppressed, function() {
            infosheets.accordion('select', 'Sample');
            var mga_dg = $('#metagenome_analysis_genes');
            mga_dg.datagrid(
                {queryParams: {mga_id: data['id']}}
            );
            mga_dg.datagrid('enableFilter');
            // Add a download button to the pagination line
            var pager = mga_dg.datagrid('getPager');
            pager.pagination({
                buttons: [{iconCls: 'icon-save', text: "Download",
                    handler: function(){browse_results_export('metagenome_analysis_genes', data['id']);} }]
            });
            $('#sample-info-accordion').accordion('select', 2);
            $('#sample-info-accordion').accordion('select', 3);
        });
    } else if (source == 'organism') {
        clear_infosheets(infosheets);
        infosheets.accordion('add', {
            title: 'Organism',
            selected: false,
            tools:[{iconCls: 'icon-eye', handler:function(){retrieve_infosheet(source, index, data, !suppressed)}}],
            content: "<div id='organism'></div>"
        });
        $('#organism').load('/source-infosheet/organism/' + data['id'] + '?suppressed=' + suppressed, function() {
            infosheets.accordion('select', 'Organism');
        });
    } else if (source == 'hydrocarbon_resource') {
        clear_infosheets(infosheets);
        infosheets.accordion('add', {
            title: 'Hydrocarbon Resource',
            selected: false,
            tools:[
                {iconCls: 'icon-eye', handler:function(){retrieve_infosheet(source, index, data, !suppressed)}}
            ],
            content: "<div id='hydrocarbon-resource'></div>"
        });
        $('#hydrocarbon-resource').load('/source-infosheet/hydrocarbon_resource/' + data['id'] + '?suppressed=' + suppressed,
            function() {
            infosheets.accordion('select', 'Hydrocarbon Resource');
        });
    }
};

/**
 * Make a request to download, as a csv file, data appearing in a datagrid. E.g., Samples, Organisms, etc.
 * @param source
 */
browse_export= function(source) {
    var filters = $("#" + source + "-results").datagrid('options').filterRules;
    var filters_j = JSON.stringify(filters);
    window.location="/export/" + source + '?filterRules=' + filters_j;
};

/**
 * Make a request to download, as a csv file, Metagenome or Single Gene Results
 *
 * @param source
 * @param id
 */
browse_results_export= function(source, id) {
    var filters = $("#" + source).datagrid('options').filterRules;
    var filters_j = JSON.stringify(filters);
    window.location="/export-analysis/" + source + '?id=' + id + '&filterRules=' + filters_j;
};



/**
 * Open an edit dialog window on an infosheet (metadata).
 *
 * @param source
 * @param index
 * @param data
 * @param suppressed
 */
var edit_save = {
    source: null,
    index: null,
    data: null,
    suppressed: null
};
edit_infosheet = function(source, index, data, suppressed) {
    var address = '/edit/' + source + '/' + data['id'];
    $('#infosheet-dialog').dialog({
        modal: true,
        resizable: true,
        title: 'Editing ' + source + ' with id ' + data['id'],
        height: 800,
        width: 800,
        closed: true,
        href: address,
        onBeforeClose: function(){edit_infosheet_closing();},
        toolbar: '#dlg-buttons'
    });
    var idl = $('#infosheet-dialog');
    idl.dialog('open');
};
edit_infosheet_save = function(source) {
    $('#' + source + '_edit_form').submit();
    $('#infosheet-dialog').dialog('clear');
    $('#infosheet-dialog').dialog('close');
//    retrieve_infosheet(source, index, data, suppressed);
};

edit_infosheet_closing = function() {
    $('#infosheet-dialog').dialog('clear');
    return true
}
edit_infosheet_cancel = function() {
    $('#infosheet-dialog').dialog('clear');
    $('#infosheet-dialog').dialog('close');
};

$(document).ready(function() {

    $('#browse-menu-button').linkbutton('select');

    //var browse_tabs;
    //browse_tabs = $('#browse-tabs').tabs({
    //    onSelect: function(title, index) {
    //        var infosheets = $('#infosheets-accordion');
    //        clear_infosheets(infosheets);
    //        switch (index) {
    //            case 0:
    //                investigation_dg.datagrid();
    //                investigation_dg.datagrid('enableFilter');
    //                break;
    //            case 1:
    //                sample_dg.datagrid('subgrid', sample_dg_conf);
    //                sample_dg.datagrid('enableFilter');
    //                break;
    //            case 2:
    //                organism_dg.datagrid();
    //                organism_dg.datagrid('enableFilter');
    //                break;
    //            case 3:
    //                hr_dg.datagrid();
    //                hr_dg.datagrid('enableFilter');
    //        }
    //    }
    //});

    /*
    Build an Investigation datagrid configuration. Investigations have a subgrid of Samples. And Samples have
    a subgrid of Analyses.
     */
    var investigation_dg;
    var investigation_dg_conf;
    investigation_dg_conf = {
        options: {
            url: 'investigations-page',
            method: 'get',
            striped: true,
            pagination: true,
            fitColumns: true,
            pageSize: 10,
            singleSelect: true,
            remoteFilter: true,
            queryParms: {source: 'investigation'},
            idField: 'id',
            columns:[[
                {field: 'id', hidden: true},
                {field: 'project_name', title: 'Name', width: 120, sortable: true},
                {field: 'investigation_description', title: 'Description', width: 580, sortable: true},
            ]],
            onClickRow: function (index, rowValue) {
                retrieve_infosheet2('investigation', index, rowValue);
            },
            onExpandRow: function(index, rowValue) {
                investigation_dg.datagrid('selectRow', index);
                retrieve_infosheet2('investigation', index, rowValue);
            }
        },
        subgrid: {
            options: {
                url: 'investigation-samples',
                method: 'get',
                foreignField: 'id',
                fitColumns: true,
                loadMsg: '',
                singleSelect: true,
                height: 'auto',
                columns: [[
                    {field: 'id', hidden: true},
                    {field: 'source_mat_id', title: 'Source Mat ID', width: 100, sortable: true},
                    {field: 'samp_type', title: 'Type', width: 60, sortable: true},
                    {field: 'samp_subtype', title: 'Subtype', width: 60, sortable: true},
                    {field: 'samp_description', title: 'Description', width: 400, sortable: true},
                    {field: 'samp_comment', title: 'Comment', width: 400, sortable: true}
                ]],
                // Here we determine if any of the investigations have samples. If not, hide the expander button/icon.
                onLoadSuccess: function(data) {
                    for (var i = 0; i <data.rows.length; i++) {
                        if (data.rows[i].analyses_count == 0) {
                            $(this).datagrid('getExpander', i).hide();
                        }
                    }
                },
                onClickRow: function (index, rowValue) {
                    retrieve_infosheet2('investigation-sample', index, rowValue);
                },
                onExpandRow: function(index, rowValue) {
                    $(this).datagrid('selectRow', index);
                    retrieve_infosheet2('investigation-sample', index, rowValue);
                }
            },
            subgrid: {
                options: {
                    url: 'sample-analyses',
                    method: 'get',
                    foreignField: 'id',
                    fitColumns: true,
                    loadMsg: '',
                    singleSelect: true,
                    height: 'auto',
                    columns: [[
                        {field: 'id', title: 'ID'},
                        {field: 'samp_anal_name', title: 'Sample Analysis Name'},
                        {field: 'analysis_name', title: 'Analysis Name'},
                        {field: 'type', title: 'Type'},
                        {field: 'analysis_date', title: 'Analysis Date'},
                        {field: 'upload_date', title: 'Upload Date'},
                        {field: 'uploaded_by', title: 'Uploaded By'},
                        {field: 'sequencing_center', title: 'Sequencing Center'}
                    ]],
                    onClickRow: function(index, rowValue) {
                        var type = rowValue.type;
                        if (type == 'Single Gene') {
                            retrieve_infosheet2('investigation-sample-sga', index, rowValue);
                        } else if (type == 'Metagenome') {
                            retrieve_infosheet2('investigation-sample-mga', index, rowValue)
                        }

                    }
                }
            }
        }
    };

    /*
     Build an Investigations datagrid based on the datagrid configuration defined above
     */
    investigation_dg = $('#investigation-results').datagrid('subgrid', investigation_dg_conf);

    /*
    The following code effectively builds and adds a filter combo box for any field of type
    Controlled Vocabulary (CV) so that filtering can be done with these CV values.
     */
    var investigation_type_choices = get_cv_values('investigation', 'investigation_type');
    var experimental_factor_choices = get_cv_values('investigation', 'experimental_factor');
    var investigation_status_choices = get_cv_values('investigation', 'investigation_status');

    investigation_dg.datagrid('enableFilter',[
        {field: 'investigation_type', type: 'combobox',
            options:{
                data: investigation_type_choices,
                editable: false,
                onChange: function(value){
                    if (value == ''){
                        investigation_dg.datagrid('removeFilterRule', 'investigation_type')
                    } else if(typeof value !== 'undefined') {
                        investigation_dg.datagrid('addFilterRule', {
                            field: 'investigation_type',
                            op: 'equal',
                            value: value
                        });
                    }
                    investigation_dg.datagrid('doFilter');
                }
            }
        },
        {field: 'experimental_factor', type: 'combobox',
            options:{
                data: experimental_factor_choices,
                editable: false,
                onChange: function(value){
                    if (value == ''){
                        investigation_dg.datagrid('removeFilterRule', 'experimental_factor')
                    } else if(typeof value !== 'undefined') {
                        investigation_dg.datagrid('addFilterRule', {
                            field: 'experimental_factor',
                            op: 'equal',
                            value: value
                        });
                    }
                    investigation_dg.datagrid('doFilter');
                }
            }
        },
        {field: 'investigation_status', type: 'combobox',
            options:{
                data: investigation_status_choices,
                editable: false,
                onChange: function(value){
                    if (value == ''){
                        investigation_dg.datagrid('removeFilterRule', 'investigation_status')
                    } else if(typeof value !== 'undefined') {
                        investigation_dg.datagrid('addFilterRule', {
                            field: 'investigation_status',
                            op: 'equal',
                            value: value
                        });
                    }
                    investigation_dg.datagrid('doFilter');
                }
            }
        }
    ]);

    /*
    Add a Download button at the bottom to download the entire datagrid.
     */
    investigation_dg.datagrid('getPager').pagination({
        buttons: [{iconCls: 'icon-save', text: "Download", handler: function(){browse_export('investigation');} }]
    });

    /*
    Build a datagrid configuration for Samples. This datagrid has a subgrid for displaying Analyses associate
    with a Sample
     */
    var sample_dg;
    var sample_dg_conf;
    sample_dg_conf = {
        options: {
            url: 'samples-page',
            method: 'get',
            striped: true,
            pagination: true,
            fitColumns: true,
            pageSize: 10,
            singleSelect: true,
            remoteFilter: true,
            queryParms: {source: 'sample'},
            idField: 'id',
            columns: [[
                {field: 'id', hidden: true},
                {field: 'source_mat_id', title: 'Source Mat ID', width: 100, sortable: true},
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
                url: 'sample-analyses',
                method: 'get',
                foreignField: 'id',
                fitColumns: true,
                loadMsg: '',
                singleSelect: true,
                height: 'auto',
                columns: [[
                    {field: 'id', title: 'ID'},
                    {field: 'type', title: 'Type'},
                    {field: 'samp_anal_name', title: 'Sample Analysis Name'},
                    {field: 'analysis_name', title: 'Analysis Name'},
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

    /*
     Add a Download button at the bottom to download the entire datagrid.
     */
    sample_dg.datagrid('getPager').pagination({
        buttons: [{iconCls: 'icon-save', text: "Download", handler: function(){browse_export('sample');} }]
    });

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
    var analyses_dg = $('#biologicalanalysis-results').datagrid({
        url: 'analyses-page',
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
            {field: 'samp_anal_name', title: 'Sample Analysis Name', sortable: true},
            {field: 'analysis_name', title: 'Analysis Name'},
            {field: 'sequencing_center', title: 'Sequencing Center', sortable: true},
            {field: 'analysis_date', title: 'Analysis Date', sortable: true},
            {field: 'upload_date', title: 'Upload Date', sortable: true},
            {field: 'uploaded_by', title: 'Uploaded By', sortable: true}
        ]],
        onClickRow: function (index, rowValue) {
            var type = rowValue.type;
            if (type == 'Single Gene') {
                retrieve_infosheet2('sample-sga', index, rowValue);
            } else if (type == 'Metagenome') {
                retrieve_infosheet2('sample-mga', index, rowValue)
            }
        }
    });

    var analysis_type_choices = get_cv_values('biological_analysis', 'type');

    /*
     Add a Download button at the bottom to download the entire datagrid.
     */
    analyses_dg.datagrid('getPager').pagination({
        buttons: [{iconCls: 'icon-save', text: "Download", handler: function(){browse_export('biologicalanalysis');} }]
    });

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

    /*
    Build the Organisms datagrid
     */
    var organism_dg = $('#organism-results').datagrid({
        url: 'organisms-page',
        method: 'get',
        striped: true,
        pagination: true,
        fitColumns: true,
        pageSize: 10,
        singleSelect: true,
        remoteFilter: true,
        queryParms: {source: 'organism'},
        idField: 'id',
        columns: [[
            {field: 'id', hidden: true},
            {field: 'superkingdom', title: 'Superkingdom', sortable: true},
            {field: 'phylum', title: 'Phylum', sortable: true},
            {field: 'subphylum', title: 'Subphylum', sortable: true},
            {field: 'bio_class', title: 'Class', sortable: true},
            {field: 'bio_order', title: 'Order', sortable: true},
            {field: 'family', title: 'Family', sortable: true},
            {field: 'genus', title: 'Genus', sortable: true},
            {field: 'species', title: 'Species', sortable: true},
            {field: 'strain', title: 'Strain', sortable: true},
            {field: 'ncbi_taxon_id', title: 'NCBI Taxon. ID', sortable: true,
                formatter: function(value, row, index){
                    if (value) {
                        return '<a href=\'http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=' + value + '\'target=\'_blank\'>' + value + '</a>';
                    } else { return '';}
                }
            },
            {field: 'metabolism_type', title: 'Metabolism Type', sortable: true},
            {field: 'risk', title: 'Threat', sortable: true}
        ]],
        //onBeforeLoad: function(param) {
        //    var tab = $('#browse-tabs').tabs('getSelected');
        //    var index = $('#browse-tabs').tabs('getTabIndex', tab);
        //    return index == 2;
        //},
        onClickRow: function (index, rowValue) {
            retrieve_infosheet2('organism', index, rowValue);
        }
    });

    var metabolism_type_choices = get_r_values('metabolism_type', 'type');
    var risk_choices = get_cv_values('organism', 'risk');

    /*
     Add a Download button at the bottom to download the entire datagrid.
     */
    organism_dg.datagrid('getPager').pagination({
        buttons: [{iconCls: 'icon-save', text: "Download", handler: function(){browse_export('organism');} }]
    });

    /*
    Add the ability to do filter searches in the Organisms datagrid columns.
     */
    organism_dg.datagrid('enableFilter',[
        {field: 'metabolism_type', type: 'combobox',
            options:{
                data: metabolism_type_choices,
                editable: false,
                onChange: function(value){
                    if (value == ''){
                        organism_dg.datagrid('removeFilterRule', 'metabolism_type')
                    } else if(typeof value !== 'undefined') {
                        organism_dg.datagrid('addFilterRule', {
                            field: 'metabolism_type',
                            op: 'equal',
                            value: value
                        });
                    }
                    organism_dg.datagrid('doFilter');
                }
            }
        },
        {field: 'risk', type: 'combobox', width: 10,
            options:{
                data: risk_choices,
                editable: false,
                onChange: function(value){
                    if (value == ''){
                        organism_dg.datagrid('removeFilterRule', 'risk')
                    } else if(typeof value !== 'undefined') {
                        organism_dg.datagrid('addFilterRule', {
                            field: 'risk',
                            op: 'equal',
                            value: value
                        });
                    }
                    organism_dg.datagrid('doFilter');
                }
            }
        }
    ]);

    /*
    Build the Hydrocarbon Resources datagrid
     */
    var hr_dg = $('#hydrocarbonresource-results').datagrid({
        url: 'hydrocarbon-resources-page',
        method: 'get',
        striped: true,
        pagination: true,
        fitColumns: true,
        pageSize: 10,
        singleSelect: true,
        remoteFilter: true,
        queryParms: {source: 'hydrocarbon_resource'},
        idField: 'id',
        columns: [[
            {field: 'hcr_abbrev', title: 'Abbrev.', sortable: true},
            {field: 'hcr', title: 'HCR', sortable: true },
            {field: 'basin', title: 'Basin Name', sortable: true},
            {field: 'field', title: 'Field Name', sortable: true},
            {field: 'reservoir', title: 'Reservoir', sortable: true},
            {field: 'id', hidden: true}
        ]],
        // Dont load anything until the tab for this datagrid has been selected.
        //onBeforeLoad: function(param) {
        //    var tab = $('#browse-tabs').tabs('getSelected');
        //    var index = $('#browse-tabs').tabs('getTabIndex', tab);
        //    return index == 3;
        //},
        onClickRow: function (index, rowValue) {
            retrieve_infosheet2('hydrocarbon_resource', index, rowValue);
        }
    });

    /*
     Add a Download button at the bottom to download the entire datagrid.
     */
    hr_dg.datagrid('getPager').pagination({
        buttons: [{iconCls: 'icon-save', text: "Download", handler: function(){browse_export('hydrocarbonresource');} }]
    });

    /*
    Add the ability to do filter searches in the Hydrocarbon Resources datagrid columns
     */
    var hcr_choices = get_cv_values('hydrocarbon_resource', 'hcr');
    hr_dg.datagrid('enableFilter',[
        {field: 'hcr', type: 'combobox',
            options: {
                data: hcr_choices,
                editable: false,
                onChange: function(value) {
                    if (value == ''){
                        hr_dg.datagrid('removeFilterRule', 'hcr')
                    } else if (typeof value != 'undefined') {
                        hr_dg.datagrid('addFilterRule', {
                            field: 'hcr',
                            op: 'equal',
                            value: value
                        })
                    }
                    hr_dg.datagrid('doFilter');
                }
            }
        }
    ]);
});   // $(document).ready()

