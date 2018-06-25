"""
 Copyright (C) 2018 Shell Global Solutions International B.V.
"""

from django.conf.urls import patterns, include, url

# Django uses autodiscover() to generate code and pages to support model instance maintenance
# This maintenance function is only available to authorized users.
from django.contrib import admin
from django.contrib.auth.decorators import login_required

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

from webapp import views, upload_views

# Below are all of the urls that this application recognizes. Most url also have a "name" which
# can be used within html pages instead of hard-wired urls, eg: {% url browse_investigations_page %}
urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),
    url(r'^upload$', upload_views.upload, name='upload'),
    url(r'^about$', views.about, name='about'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^reset_password', views.reset_password, name='reset_password'),
    url(r'^admin/logout/', views.logout, name="logout"),
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^register$', views.register, name='register'),
    url(r'^edit/(?P<source>[\w\-]+)/(?P<id>\d+)$', views.edit_source, name='edit_source'),
    url(r'^edit/sample/(?P<id>\d+)$', views.edit_sample, name='edit_sample'),
    url(r'^edit/sample-sga/(?P<id>\d+)$', views.edit_sga, name='edit_sga'),
    url(r'^edit/sample-mga/(?P<id>\d+)$', views.edit_mga, name='edit_sga'),
    url(r'^export/(?P<source>\w+)$', views.export, name='export'),
    url(r'^export-analysis/(?P<source>\w+)$', views.export_analysis, name='export_analysis'),
    url(r'^browse/investigations-page$', views.browse_investigations_page, name='browse_investigations_page'),
    url(r'^browse/samples-page$', views.browse_samples_page, name='browse_samples_page'),
    url(r'^browse/analyses-page$', views.browse_analyses_page, name='browse_analyses_page'),
    url(r'^browse/organisms-page$', views.browse_organisms_page, name='browse_organisms_page'),
    url(r'^browse/hydrocarbon-resources-page$', views.browse_hydrocarbon_resources_page, name='browse_hydrocarbon_resources_page'),
    url(r'^browse/sample-sgr-page$', views.browse_sample_sgr_page, name='browse_sample_sgr_pages'),
    url(r'^browse/sample-mgr-page$', views.browse_sample_mgr_page, name='browse_sample_mgr_pages'),
    url(r'^browse/sample-analyses/(?P<id>\d+)$', views.browse_sample_analyses, name='browse_sample_analyses'),
    url(r'^browse/sample-analyses$', views.browse_sample_analyses_sub, name='browse_sample_anlyses'),
    url(r'^browse/investigation-samples$', views.browse_investigation_samples_sub, name='browse_investigation_samples'),
    url(r'^browse/columns/(?P<entity>\w*)$', views.browse_columns, name='browse_columns'),
    url(r'^browse/', views.browse, name='browse'),
    url(r'^search/attribute-cv/(?P<category>\w*)/(?P<attribute>\w*)$', views.search_attribute_cv,
        name='search_attribute_cv'),
    url(r'^search/attribute-r/(?P<table>\w*)/(?P<column>\w*)$', views.search_attribute_r,
        name='search_attribute_r'),
    url(r'^search/entity-cv/(?P<group>\w+)/(?P<entity>\w+)$', views.search_entity_cv, name='search_entity_cv'),
    url(r'^search/filtered/(?P<group>\w+)/(?P<source>\w+)$', views.search_filtered, name='search_filtered'),
    url(r'^search-results-get/(?P<source>\w+)/(?P<target>\w+)/$', views.search_results_get,
        name='search_results_get'),
    url(r'^search$', views.search, name='search'),
    url(r'^organism/genus/(?P<genus>\w+)$', views.organism_genus_tree, name='organism_genus_tree'),
    url(r'^organism-genus-infosheet/(?P<genus>\w+)$', views.organism_genus_infosheet, name='organism_genus_infosheet'),
    url(r'^organism/family/(?P<family>\w+)$', views.organism_family_tree, name='organism_family_tree'),
    url(r'^organism-family-infosheet/(?P<family>\w+)$', views.organism_family_infosheet, name='organism_family_infosheet'),
    url(r'^source-infosheet/(?P<source>\w*)/(?P<id>\d+)$', views.source_infosheet, name='source_infosheet'),
    url(r'^organism-results-page$', views.organisms_results_page, name='organism_results_pages'),
    url(r'^organism-results-filtered-pages', views.organisms_results_filtered_page, name='organism_results_filtered_pages'),
    url(r'^metagenome_analysis_genes_pages', views.metagenome_analysis_genes_page, name='metagenome_analysis_genes_pages'),
    url(r'^single_gene_analysis_organisms_pages', views.single_gene_analysis_organisms_page, name='single_gene_analysis_organisms_pages'),
    url(r'^sga_upload/samples$', upload_views.sga_upload_samples, name='sga_upload_samples'),
    url(r'^sga_upload/log_file/(?P<log_filename>[\w .\-]+)$', upload_views.sga_upload_log_file, name='sga_upload_log_file'),
    # url(r'^sga_upload/sample/(?P<sample_name>\w+)$', upload_views.sga_upload_sample, name='sga_upload_sample'),
    url(r'^sga_upload', upload_views.sga_upload, name='sga_upload'),
    url(r'^mga_upload/sample/(?P<sample_id>\d+)$', upload_views.mga_upload_sample, name='mga_upload_sample'),
    url(r'^mga_upload/log_file/(?P<log_filename>[\w .\-]+)$', upload_views.mga_upload_log_file, name='mga_upload_log_file'),
    url(r'^mga_upload', upload_views.mga_upload, name='mga_upload'),
    url(r'^upload_maint/delete/(?P<id>\d+)$', upload_views.analysis_delete, name='analysis_delete'),
    url(r'^upload_maint/log_file/(?P<id>\d+)$', upload_views.analysis_log_file, name='analysis_log_file'),
)

# Uncomment the following to use the Django Debug Toolbar
# from django.conf import settings
# from django.conf.urls import include, url
# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#                       url(r'^__debug__/', include(debug_toolbar.urls)),
#                   ] + urlpatterns
