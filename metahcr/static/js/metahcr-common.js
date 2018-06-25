/**
 * Created by pcmarks on 1/13/2016.
 */

/**
 * Common javascript functions used in MetaHCR:
 *
 *      clear_infosheets()
 *      get_cv_values()
 *      get_r_values()
 *
 */

/**
 * clear_infosheets unselects and then removes all of the panels in the infosheets-accordion.
 * @param infosheets
 */
clear_infosheets = function(infosheets) {
    infosheets.accordion('unselect', 0);
    var no_of_panels = infosheets.accordion('panels').length;
    for (var i = 0; i < no_of_panels; i++) {
        infosheets.accordion('remove', 0);
    }
};

clear_infosheets_from = function(infosheets, panel_no) {
    infosheets.accordion('unselect', panel_no);
    var no_of_panels = infosheets.accordion('panels').length;
    for (var i = panel_no + 1; i < no_of_panels; i++) {
        infosheets.accordion('remove', i);
    }
};

/**
 * get_cv_values is used to retrieve the displayable strings associated with the Controlled
 * Vocabulary (cv) numerical values used in the MetaHCR data base.
 *
 * @param category - "samples", "investigations", etc
 * @param attribute
 * @returns {*[]}
 */
get_cv_values = function(category, attribute) {
    var cv_data_list = [{value: '', text: 'All'}];
    var url = '/search/attribute-cv/' + category + '/' + attribute;
    $.ajax({
        url: url,
        async: false,
        cache: true,
        success: function(data) {cv_data_list = cv_data_list.concat(data);},
        error: function() {
            alert('failure: cv retrieval');
        }
    });
    return cv_data_list;
};

/**
 * get_r_values is used to retrieve the all the displayable strings associated with a table to table
 * relation. For instance, metabolism_type strings are in the metabolism_type table that is
 * pointed to from other tables. The MetaHCR field type is "R"
 *
 * @param table - "metabolism_type"
 * @param column - e.g., "type"
 * @returns {*[]}  - a list of strings
 */
get_r_values = function(table, column) {
    var r_data_list = [{value: '', text: 'All'}];
    var url = '/search/attribute-r/' + table + '/' + column;
    $.ajax({
        url: url,
        async: false,
        cache: true,
        success: function(data) {r_data_list = r_data_list.concat(data);},
        error: function() {
            alert('failure: r retrieval for table: '+table+' column: '+column);
        }
    });
    return r_data_list;
};
