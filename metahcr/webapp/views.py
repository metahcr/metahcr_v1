"""
 Copyright (C) 2018 Shell Global Solutions International B.V.
"""

from collections import defaultdict
import json
from django.contrib import messages
from django.contrib.auth import authenticate

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
#from django.core.mail import send_mail
from django.db import models
from django.db.models import Q
from django.db.models.fields import IntegerField, DecimalField
from django.db.models.fields.related import ForeignKey
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.template.loader import render_to_string, get_template
from webapp.forms import build_sample_search_fields, build_investigation_search_fields, build_organism_search_fields, \
    build_hydrocarbon_resource_fields, build_environment_fields, \
    build_hydrocarbon_chemistry_fields, build_water_chemistry_fields, build_production_data_at_time_of_sampling_fields, \
    build_metabolism_type_fields
from webapp.forms import InvestigationForm, SampleForm, SingleGeneAnalysisForm, MetagenomeAnalysisForm
from webapp.forms import WaterChemistryForm, ProductionDataForm, EnvironmentDataForm, HydrocarbonChemistryForm
from webapp.forms import HydrocarbonResourceForm, MineralogyForm, CuratorDetailsForm, OrganismForm
from webapp.models import Investigation, HydrocarbonResource, Sample, Organism, Environment, WaterChemistry, \
    HydrocarbonChemistry, ProductionDataAtTimeOfSampling, SingleGeneAnalysis, SingleGeneResult, Mineralogy, \
    Attribute, MetagenomeAnalysis, MetagenomeResult, MetagenomeResultGene, BiologicalAnalysis, MetabolismType, \
    Country, UserProfile, CuratorDetails, Habitat
    # MetadataInfo
from metahcr import settings
from unicodecsv import UnicodeWriter

"""
This file represents the Controller part of a Django Web Application

All the views found in urls.py point to functions that are defined here with the exception of the upload function - its
views are handled in the upload_views.py file.

Privileged functions that require that the user be logged are annotated with @login_required
"""



def home(request):
    """
    Home. The "/" or "/dashboard" URLs

    Simply return the home page: Dashboard/index.html
    """
    user_profile = None
    if request.user.is_authenticated():
        user_profile = request.session.get('user_profile', None)
        # try:
        #     user_profile = UserProfile.objects.get(user=request.user)
        # except ObjectDoesNotExist:
        #     pass
    t = get_template('index.html')
    html = t.render(RequestContext(request,
                                   {'style': settings.VIEW_STYLE,
                                    'user_profile': user_profile
                                    }))
    return HttpResponse(html)

@login_required
def database(request):
    """
    The "/database" URL.

    Display the page which lists the databases that are available. The available databases
    are listed in the settings.py file.

    TODO: currently selecting a database has no effect. Only the first (default) database is
    used.

    :param request:
    :return:
    """
    databases = []
    for db_type, value in settings.DATABASES.items():
        databases.append({'name': value['NAME']})

    html = render_to_string('database.html', RequestContext(request,
                                   {'style': settings.VIEW_STYLE,
                                    'databases': databases}))
    return HttpResponse(html)



def about(request):
    html = render_to_string('about.html', RequestContext(request, {'style': settings.VIEW_STYLE}))
    return HttpResponse(html)


def login(request):
    """
    The "/login" URL

    If this is a GET request then display the login page: security/Login.html

    If this is a POST request, extract the username and password values from the
    form. Authenticate this user, using Django's admin/user facilities.

    If the login was the result of being redirected here because the user was
    not logged in then send control back to the original page that was asked for.
    Otherwise, show the home page: Dashboard/index.html

    :param request:
    :return:
    """
    databaselogin = False                           # Not an admin database login
    if request.method == 'POST':
        username = request.POST['_username']
        password = request.POST['_password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth_login(request, user)
                try:
                    user_profile = UserProfile.objects.get(user=request.user)
                    if password_expired(user_profile):
                        html = render_to_string('security/reset_password.html', RequestContext(request,{}))
                        return HttpResponse(html)
                    build_session_storage(request, user, user_profile)
                    if 'next' in request.GET:
                        next = request.GET['next']
                        return HttpResponseRedirect(next)
                    else:
                        return home(request)
                except ObjectDoesNotExist:
                    messages.warning(request, 'Your account does not have a User Profile. Please contact the site administrator.')
            else: \
                messages.warning(request, 'This user account is disabled. Please contact the site administrator.')
        else:
            messages.warning(request, "Your username and password didn't match. Please try again.")
        html = render_to_string('security/login.html', RequestContext(request,
                                       {'databaselogin': databaselogin}))
        return HttpResponse(html)
    else:
        html = render_to_string('security/login.html', RequestContext(request,
                                       {'databaselogin': databaselogin}))
    return HttpResponse(html)


def reset_password(request):
    if request.method == 'POST':
        current_password = request.POST['_current_password']
        new_password = request.POST['_new_password']
        if current_password == new_password:
            messages.warning(request, 'Old and new passwords must be different. Please re-enter them.')
            html = render_to_string('security/reset_password.html', RequestContext(request,{}))
        else:
            user_profile = UserProfile.objects.get(user=request.user)
            request.user.set_password(new_password)
            request.user.save()
            user_profile.reset_password = False
            user_profile.save()
            build_session_storage(request, request.user, user_profile)
            return home(request)
    else:
        html = render_to_string('security/reset_password.html', RequestContext(request,{}))
    return HttpResponse(html)


def build_session_storage(request, user, user_profile):
    request.session['username'] = user.username
    organization = user_profile.organization.name
    if user_profile.default_database:
        database = user_profile.default_database.description
    else:
        database = "Not available"
    request.session['user_profile'] = {"organization": organization, "database": database}
    build_column_headings(request, 'browse')
    return

def password_expired(user_profile):
    return user_profile.reset_password


def build_column_headings(request, page):
    entity_specs = [
        ('investigation',['name', 'description', 'comment']),
        ('sample',['name', 'description', 'comment'])]
    for entity_spec in entity_specs:
        contents = build_column_headings_for_entity(entity_spec[0], entity_spec[1])
        request.session[page + '_' + entity_spec[0]] = contents

def build_column_headings_for_entity(entity, columns):
    entity_model = models.get_model('webapp', entity)
    content = ''
    fields = entity_model._meta.fields
    for field in fields:
        field_name = field.name
        if field_name in columns:
            checked = "checked='checked'"
        else:
            checked = ''
        content += '\n<input type="checkbox" name="%s" value="%s" %s>%s<br>' % (field.name, field.name, checked, field.verbose_name)
    return content


def register(request):
    """
    TODO: Not implemented
    """
    if request.method == 'POST':
        username = request.POST['_username']
        password = request.POST['_password']
        password2 = request.POST['_password2']
        first_name = request.POST['_first_name']
        last_name = request.POST['_last_name']
        if password != password2:
            messages.warning(request, 'Passwords do not match')
            html = render_to_string('security/registration.html', RequestContext(request))
            return HttpResponse(html)
        user = authenticate(username=username, password=password)
        if user:
            messages.warning(request, 'This email address is already registered.')
            html = render_to_string('security/registration.html', RequestContext(request))
            return HttpResponse(html)
        else:
            new_user = User.objects.create_user(
                username,username,
                password,
                first_name=first_name,
                last_name=last_name)
            new_user.is_active = False
            new_user.save()

            messages.info(request, 'Thank you. We will contact you via email.')
            return render(request, 'index.html')
    else:
        html = render_to_string('security/registration.html', RequestContext(request))
    return HttpResponse(html)


def logout(request):
    """
    The "logout" URL.

    Logout the current user, using Django's authorization facilities, then
    show the home page.

    :param request:
    :return:
    """
    auth_logout(request)
    return redirect('home')

@login_required
def edit_source(request, source, id):
    if source == 'investigation':
        return edit_investigation(request, id)
    elif source == 'curator-details':
        return edit_curator_details(request, id)
    elif source == 'sample':
        return edit_sample(request, id)
    elif source == 'water-chemistry':
        return edit_water_chemistry(request, id)
    elif source == 'production-data':
        return edit_production_data(request, id)
    elif source == 'environment':
        return edit_environment(request, id)
    elif source == 'hydrocarbon-chemistry':
        return edit_hydrocarbon_chemistry(request, id)
    elif source == 'hydrocarbon-resource':
        return edit_hydrocarbon_resource(request, id)
    elif source == 'mineralogy':
        return edit_mineralogy(request, id)
    elif source == 'organism':
        return edit_organism(request, id)
    elif source == 'sga':
        return edit_sga(request, id)
    elif source == 'mga':
        return edit_mga(request, id)

@login_required
def edit_investigation(request, id):
    try:
        investigation = Investigation.objects.get(id=id)
    except Investigation.DoesNotExist:
        return render(request, 'edit/not_found.html', {'entity': 'Investigation'})

    if request.method == "POST":
        form = InvestigationForm(request.POST, instance=investigation)
        if form.is_valid():
            investigation = form.save(commit=False)
            investigation.save()
            return HttpResponse(status=204)
    else:
        form = InvestigationForm(instance=investigation)
    return render(request, 'edit/investigation.html', {'form': form, 'id': id})

@login_required
def edit_curator_details(request, id):
    try:
        curator_details = CuratorDetails.objects.get(id=id)
    except CuratorDetails.DoesNotExist:
        return render(request, 'edit/not_found.html', {'entity': 'Curator Details'})

    if request.method == "POST":
        form = CuratorDetailsForm(request.POST, instance=curator_details)
        if form.is_valid():
            curator_details = form.save(commit=False)
            curator_details.save()
            return HttpResponse(status=204)
    else:
        form = CuratorDetailsForm(instance=curator_details)

    return render(request, 'edit/curator_details.html', {'form': form, 'id': id})

@login_required
def edit_water_chemistry(request, sample_id):
    try:
        water_chemistry = WaterChemistry.objects.get(sample_id=sample_id)
    except WaterChemistry.DoesNotExist:
        return render(request, 'edit/not_found.html', {'entity': 'Water Chemistry'})
    if request.method == "POST":
        form = WaterChemistryForm(request.POST, instance=water_chemistry)
        if form.is_valid():
            water_chemistry = form.save(commit=False)
            water_chemistry.save()
            return HttpResponse(status=204)
    else:
        form = WaterChemistryForm(instance=water_chemistry)

    html = render(request, 'edit/water_chemistry.html', {'form': form, 'id': sample_id})
    return html

@login_required
def edit_production_data(request, sample_id):
    try:
        production_data = ProductionDataAtTimeOfSampling.objects.get(sample_id=sample_id)
    except ProductionDataAtTimeOfSampling.DoesNotExist:
        return render(request, 'edit/not_found.html', {'entity': 'Production Data At Time of Sampling'})
    if request.method == "POST":
        form = ProductionDataForm(request.POST, instance=production_data)
        if form.is_valid():
            production_data = form.save(commit=False)
            production_data.save()
            return HttpResponse(status=204)
    else:
        form = ProductionDataForm(instance=production_data)

    html = render(request, 'edit/production_data.html', {'form': form, 'id': sample_id})
    return html

@login_required
def edit_environment(request, sample_id):
    try:
        sample = Sample.objects.get(id=sample_id)
        environment = Environment.objects.get(id=sample.environment_id)
    except Environment.DoesNotExist:
        return render(request, 'edit/not_found.html', {'entity': 'Environment'})
    if request.method == "POST":
        form = EnvironmentDataForm(request.POST, instance=environment)
        if form.is_valid():
            environment = form.save(commit=False)
            environment.save()
            return HttpResponse(status=204)
    else:
        form = EnvironmentDataForm(instance=environment)

    html = render(request, 'edit/environment.html', {'form': form, 'id': sample_id})
    return html

@login_required
def edit_hydrocarbon_chemistry(request, sample_id):
    try:
        hydrocarbon_chemistry = HydrocarbonChemistry.objects.get(sample_id=sample_id)
    except HydrocarbonChemistry.DoesNotExist:
        return render(request, 'edit/not_found.html', {'entity': 'Hydrocarbon Chemistry'})
    if request.method == "POST":
        form = HydrocarbonChemistryForm(request.POST, instance=hydrocarbon_chemistry)
        if form.is_valid():
            hydrocarbon_chemistry = form.save(commit=False)
            hydrocarbon_chemistry.save()
            return HttpResponse(status=204)
    else:
        form = HydrocarbonChemistryForm(instance=hydrocarbon_chemistry)

    html = render(request, 'edit/hydrocarbon_chemistry.html', {'form': form, 'id': sample_id})
    return html


@login_required
def edit_hydrocarbon_resource(request, id):
    try:
        hydrocarbon_resource = HydrocarbonResource.objects.get(id=id)
    except HydrocarbonResource.DoesNotExist:
        return render(request, 'edit/not_found.html', {'entity': 'Hydrocarbon Resource'})

    if request.method == "POST":
        form = HydrocarbonResourceForm(request.POST, instance=hydrocarbon_resource)
        if form.is_valid():
            hydrocarbon_resource = form.save(commit=False)
            hydrocarbon_resource.save()
            return HttpResponse(status=204)
    else:
        form = HydrocarbonResourceForm(instance=hydrocarbon_resource)

    return render(request, 'edit/hydrocarbon_resource.html', {'form': form, 'id': id})


@login_required
def edit_mineralogy(request, id):
    try:
        mineralogy = Mineralogy.objects.get(hydrocarbon_resource_id=id)
    except Mineralogy.DoesNotExist:
        return render(request, 'edit/not_found.html', {'entity': 'Mineralogy'})

    if request.method == "POST":
        form = MineralogyForm(request.POST, instance=mineralogy)
        if form.is_valid():
            mineralogy = form.save(commit=False)
            mineralogy.save()
            return HttpResponse(status=204)
    else:
        form = MineralogyForm(instance=mineralogy)

    return render(request, 'edit/mineralogy.html', {'form': form, 'id': id})


@login_required
def edit_sample(request, id):
    try:
        sample = Sample.objects.get(id=id)
    except Sample.DoesNotExist:
        return render(request, 'edit/not_found.html', {'entity': 'Sample'})

    if request.method == "POST":
        form = SampleForm(request.POST, instance=sample)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.save()
            return HttpResponse(status=204)
    else:
        form = SampleForm(instance=sample)

    return render(request, 'edit/sample.html', {'form': form, 'id': id})

@login_required
def edit_sga(request, id):
    try:
        sga = SingleGeneAnalysis.objects.get(id=id)
    except SingleGeneAnalysis.DoesNotExist:
        return render(request, 'edit/not_found.html', {'entity': 'Single Gene Analysis'})

    if request.method == "POST":
        form = SingleGeneAnalysisForm(request.POST, instance=sga)
        if form.is_valid():
            sga = form.save(commit=False)
            sga.save()
            return HttpResponse(status=204)
    else:
        form = SingleGeneAnalysisForm(instance=sga)

    return render(request, 'edit/sga.html', {'form': form, 'id': id})

@login_required
def edit_mga(request, id):
    try:
        mga = MetagenomeAnalysis.objects.get(id=id)
    except MetagenomeAnalysis.DoesNotExist:
        return render(request, 'edit/not_found.html', {'entity': 'Metagenome Analysis'})

    if request.method == "POST":
        form = MetagenomeAnalysisForm(request.POST, instance=mga)
        if form.is_valid():
            mga = form.save(commit=False)
            mga.save()
            return HttpResponse(status=204)
    else:
        form = MetagenomeAnalysisForm(instance=mga)

    return render(request, 'edit/mga.html', {'form': form, 'id': id})

@login_required
def edit_organism(request, id):
    try:
        organism = Organism.objects.get(id=id)
    except Organism.DoesNotExist:
        return render(request, 'edit/not_found.html', {'entity': 'Organism'})

    if request.method == "POST":
        form = OrganismForm(request.POST, instance=organism)
        if form.is_valid():
            organism = form.save(commit=False)
            organism.save()
            return HttpResponse(status=204)
    else:
        form = OrganismForm(instance=organism)

    return render(request, 'edit/organism.html', {'form': form, 'id': id})

@login_required
def browse(request):
    """
    Browse MetaHCR's entities.

    :param request:
    :return:
    """
    parameters = settings.PARAMETERS
    user_profile = request.session['user_profile']
    html = render_to_string('browse.html',
                            RequestContext(request,
                                           {'style': settings.VIEW_STYLE,
                                            'user_profile': user_profile,
                                            'parameters': parameters}))
    return HttpResponse(html)


@login_required
def browse_investigations_page(request):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = int(request.GET.get('page', '1'))
    rows = int(request.GET.get('rows', '10'))
    sort_field = None
    if 'sort' in request.GET:
        sort_field = request.GET['sort']
        sort_order = request.GET['order']
        if sort_order == 'desc':
            sort_field = '-' + sort_field
    return_values = []

    # Any Filters present? If so, add them to the query
    filters_j = request.GET.get('filterRules','[]')
    filters = json.JSONDecoder().decode(filters_j)
    if len(filters) > 0:
        i = 1
        for filter in filters:
            field = filter['field']
            op = filter['op']
            if op == 'contains':
                op_suffix = '__icontains'
            elif op == 'equal':
                op_suffix = '__exact'
            value = filter['value']
            attribute = "%s%s" % (field, op_suffix,)
            kwargs = {attribute: value}
            aQ = Q(**kwargs)
            if i == 1:
                q = aQ
            else:
                q = q & aQ
            i += 1
        # Are we being asked to sort on a field?
        if sort_field:
            investigations = Investigation.objects.filter(q).order_by(sort_field)
        else:
            investigations = Investigation.objects.filter(q)
    else:
        # No filters specified
        # Are we being asked to sort on a field?
        if sort_field:
            investigations = Investigation.objects.order_by(sort_field)
        else:
            investigations = Investigation.objects.all().order_by('project_name')

    # Create a Paginator to nicely handle multi-page results
    paginator = Paginator(investigations, rows)
    try:
        investigation_results = paginator.page(page)
    except PageNotAnInteger:
        investigation_results = paginator.page(1)
    except EmptyPage:
        investigation_results = paginator.page(paginator.num_pages)

    total = paginator.count
    if total > 0:
        for investigation in investigation_results:
            return_values.append({
                'id': investigation.id,
                'project_name': investigation.project_name,
                'investigation_description': investigation.investigation_description
            })

    response = {'total': total, 'rows': return_values}
    serialized = json.JSONEncoder().encode(response)
    return HttpResponse(serialized, content_type='application/json')

@login_required
def browse_samples_page(request):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = int(request.GET['page'])
    rows = int(request.GET['rows'])
    sort_field = None
    if 'sort' in request.GET:
        sort_field = request.GET['sort']
        sort_order = request.GET['order']
        if sort_order == 'desc':
            sort_field = '-' + sort_field
    return_values = []
    # Any Filters present?
    filters_j = request.GET.get('filterRules','[]')
    filters = json.JSONDecoder().decode(filters_j)
    if len(filters) > 0:
        i = 1
        for filter in filters:
            field = filter['field']
            op = filter['op']
            if op == 'contains':
                op_suffix = '__icontains'
            elif op == 'equal':
                op_suffix = '__exact'
            value = filter['value']
            attribute = "%s%s" % (field, op_suffix,)
            kwargs = {attribute: value}
            aQ = Q(**kwargs)
            if i == 1:
                q = aQ
            else:
                q = q & aQ
            i += 1
        # Are we being asked to sort on a field?
        if sort_field:
            samples = Sample.objects.filter(q).order_by(sort_field)
        else:
            samples = Sample.objects.filter(q)
    else:
        # No filters.
        # Are we being asked to sort on a field?
        if sort_field:
            samples = Sample.objects.order_by(sort_field)
        else:
            samples = Sample.objects.all().order_by('source_mat_id')

    paginator = Paginator(samples, rows)
    try:
        sample_results = paginator.page(page)
    except PageNotAnInteger:
        sample_results = paginator.page(1)
    except EmptyPage:
        sample_results = paginator.page(paginator.num_pages)

    total = paginator.count
    if total > 0:
        for sample in sample_results:
            # Find out how many analyses have been performed - if any. The count determines whether the
            # sample line can be expanded (to see the analyses).
            analyses_count = BiologicalAnalysis.objects.filter(sample=sample).count()
            return_values.append({
                'id': sample.id,
                'source_mat_id': sample.source_mat_id,
                'samp_type': get_cv_value(sample.samp_type),
                'samp_subtype': get_cv_value(sample.samp_subtype),
                'samp_description': sample.samp_description,
                'samp_comment': sample.samp_comment,
                'analyses_count': analyses_count})

    response = {'total': total, 'rows': return_values}
    serialized = json.JSONEncoder().encode(response)
    return HttpResponse(serialized, content_type='application/json')

@login_required
def browse_analyses_page(request):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = int(request.GET['page'])
    page = int(request.GET['page'])
    rows = int(request.GET['rows'])
    sort_field = None
    if 'sort' in request.GET:
        sort_field = request.GET['sort']
        sort_order = request.GET['order']
        if sort_order == 'desc':
            sort_field = '-' + sort_field
    return_values = []
    # Any Filters present?
    filters_j = request.GET.get('filterRules','[]')
    filters = json.JSONDecoder().decode(filters_j)
    if len(filters) > 0:
        i = 1
        for filter in filters:
            field = filter['field']
            op = filter['op']
            if op == 'contains':
                op_suffix = '__icontains'
            elif op == 'equal':
                op_suffix = '__exact'
            value = filter['value']
            attribute = "%s%s" % (field, op_suffix,)
            kwargs = {attribute: value}
            aQ = Q(**kwargs)
            if i == 1:
                q = aQ
            else:
                q = q & aQ
            i += 1
        # Are we being asked to sort on a field?
        if sort_field:
            analyses = BiologicalAnalysis.objects.filter(q).order_by(sort_field)
        else:
            analyses = BiologicalAnalysis.objects.filter(q)
    else:
        # No filtering needed
        # Are we being asked to sort on a field?
        if sort_field:
            analyses = BiologicalAnalysis.objects.order_by(sort_field)
        else:
            analyses = BiologicalAnalysis.objects.all().order_by('type')

    paginator = Paginator(analyses, rows)
    try:
        analyses_results = paginator.page(page)
    except PageNotAnInteger:
        analyses_results = paginator.page(1)
    except EmptyPage:
        analyses_results = paginator.page(paginator.num_pages)

    total = paginator.count
    if total > 0:
        for analysis in analyses_results:
            try:
                target_gene = analysis.singlegeneanalysis.target_gene
            except:
                target_gene = ''

            if analysis.analysis_date:
                analysis_date = analysis.analysis_date.strftime('%Y/%m/%d')
            else:
                analysis_date = ''
            if analysis.upload_date:
                upload_date = analysis.upload_date.strftime('%Y/%m/%d')
            else:
                upload_date = ''
            return_values.append({
                'id': analysis.id,
                'type': get_cv_value(analysis.type),
                'samp_anal_name': analysis.samp_anal_name,
                'analysis_name': analysis.analysis_name,
                'sequencing_center': analysis.sequencing_center,
                'analysis_date': analysis_date,
                'upload_date': upload_date,
                'uploaded_by': analysis.uploaded_by
            })
    response = {'total': total, 'rows': return_values}
    serialized = json.JSONEncoder().encode(response)
    return HttpResponse(serialized, content_type='application/json')

def browse_sample_analyses_sub(request):
    id = request.GET['id']
    analyses = BiologicalAnalysis.objects.filter(sample_id=id)
    return_values = []
    for analysis in analyses:
        if analysis.analysis_date:
            analysis_date = analysis.analysis_date.strftime('%Y/%m/%d')
        else:
            analysis_date = ''
        if analysis.upload_date:
            upload_date = analysis.upload_date.strftime('%Y/%m/%d')
        else:
            upload_date = ''
        return_values.append({
            'id': analysis.id,
            'type': get_cv_value(analysis.type),
            'samp_anal_name': analysis.samp_anal_name,
            'analysis_name': analysis.analysis_name,
            'analysis_date': analysis_date,
            'upload_date': upload_date,
            'uploaded_by': analysis.uploaded_by,
            'sequencing_center': analysis.sequencing_center,
            'sequencing_method': analysis.seq_meth
        })
    total = len(analyses)
    response = {'total': total, 'rows': return_values}
    serialized = json.JSONEncoder().encode(response)
    return HttpResponse(serialized, content_type='application/json')


def browse_investigation_samples_sub(request):
    id = request.GET['id']
    investigation = Investigation.objects.select_related().get(id=id)
    samples = investigation.sample.all()
    return_values_dict = {}
    for sample in samples:
        # Find out how many analyses have been performed - if any. The count determines whether the
        # sample line can be expanded (to see the analyses).
        analyses_count = BiologicalAnalysis.objects.filter(sample=sample).count()
        return_values_dict[sample.id] = {
            'source_mat_id': sample.source_mat_id,
            'samp_description': sample.samp_description,
            'samp_subtype': get_cv_value(sample.samp_subtype),
            'samp_type': get_cv_value(sample.samp_type),
            'samp_comment': sample.samp_comment,
            'analyses_count': analyses_count
        }
        sorted_return_values_list = sorted(return_values_dict)
    return_values_list = []
    for key in sorted_return_values_list:
        return_values_list.append({
            'id': key,
            'source_mat_id': return_values_dict[key]['source_mat_id'],
            'samp_type': return_values_dict[key]['samp_type'],
            'samp_subtype': return_values_dict[key]['samp_subtype'],
            'samp_description': return_values_dict[key]['samp_description'],
            'samp_comment': return_values_dict[key]['samp_comment'],
            'analyses_count': return_values_dict[key]['analyses_count']
        })
    serialized = json.JSONEncoder().encode(return_values_list)
    return HttpResponse(serialized, content_type="application/json")

def browse_sample_analyses(request, id):
    # There should be at least one analysis
    analyses = BiologicalAnalysis.objects.filter(sample_id=id)
    return_values = []
    for analysis in analyses:
        if analysis.analysis_date:
            analysis_date = analysis.analysis_date.strftime('%Y/%m/%d')
        else:
            analysis_date = ''
        if analysis.upload_date:
            upload_date = analysis.upload_date.strftime('%Y/%m/%d')
        else:
            upload_date = ''
        return_values.append({
            'id': analysis.id,
            'samp_anal_name': analysis.samp_anal_name,
            'analysis_name': analysis.analysis_name,
            'type': get_cv_value(analysis.type),
            'analysis_date': analysis_date,
            'uploaded_by': analysis.uploaded_by,
            'upload_date': upload_date,
            'sequencing_center': analysis.sequencing_center,
            'seq_method': analysis.seq_meth
        })
    total = len(analyses)
    response = {'total': total, 'rows': return_values}
    serialized = json.JSONEncoder().encode(response)
    return HttpResponse(serialized, content_type='application/json')


def retrieve_filtered(group, source, filters_j):
    query = json.loads(filters_j)
    total = query['total']
    rows = query['rows']
    if total < 1:
        return HttpResponse('')
    q = Q()
    i = 1
    last_row = []
    for row in rows:
        entity_value = row['entity_value']
        # if entity_value == 'metabolismtype':
        #     entity_value = 'organism'
        attribute_value = row['attribute_value']
        operator_value = row['operator_value']
        value_value = row['value_value']
        category, attribute_field, field_type = attribute_value.split('|')
        if group != entity_value:
            if field_type == 'R':
                attribute_field = "%s__%s" % (category, attribute_field,)
            else:
                attribute_field = "%s__%s" % (entity_value, attribute_field,)
        operator_suffix = ''
        negation = False
        if operator_value == '=':
            operator_suffix = '__exact'
        elif operator_value == '!=':
            operator_suffix = '__exact'
            negation = True
        elif operator_value == '>':
            operator_suffix = '__gt'
        elif operator_value == '<':
            operator_suffix = '__lt'
        elif operator_value == '>=':
            operator_suffix = '__gte'
        elif operator_value == '<=':
            operator_suffix = '__lte'
        elif operator_value == 'contains':
            operator_suffix = '__icontains'
        attribute = "%s%s" % (attribute_field, operator_suffix)
        if field_type == 'CV' or field_type == 'N':
            value = float(value_value)
        else:
            value = value_value
        kwargs = {attribute: value}
        if negation:
            aQ = ~Q(**kwargs)
        else:
            aQ = Q(**kwargs)
        if i > 1:
            if last_row['connector_value'] == "and":
                q = q & aQ
            else:
                q = q | aQ
        else:
            q = aQ
        # print q
        i = i + 1
        last_row = row
    results = None
    if group == 'organism':
        if source == 'organism':
            results = Organism.objects.filter(q).order_by('id')

    return results

def organisms_results_filtered_page(request):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    return_values = []
    page = int(request.GET['page'])
    rows = int(request.GET['rows'])
    filters_j = request.GET.get('filters_j', None)
    if not filters_j:
        return HttpResponse('')
    # Returns a QuerySet that has not been evaluated yet.
    organisms = retrieve_filtered('organism', 'organism', filters_j)
    paginator = Paginator(organisms, rows)
    try:
        organism_results = paginator.page(page)
    except PageNotAnInteger:
        organism_results = paginator.page(1)
    except EmptyPage:
        organism_results = paginator.page(paginator.num_pages)
    total = paginator.count
    if total > 0:
        for organism in organism_results:
            sg_samples_count = Sample.objects.filter(biologicalanalysis__singlegeneanalysis__singlegeneresult__organism__id=organism.id).count()
            mg_samples_count = Sample.objects.filter(biologicalanalysis__metagenomeanalysis__metagenomeresult__organism__id=organism.id).count()
            if (sg_samples_count + mg_samples_count) > 0:
                samples_present = 'Y'
            else:
                samples_present = 'N'
            if not organism.risk:
                risk_value = ""
            else:
                risk_value = Attribute.objects.get(id=organism.risk_id).value
            return_values.append({
                'id': organism.id,
                'samples': samples_present,
                'superkingdom': organism.superkingdom,
                'phylum': organism.phylum,
                'class': organism.bio_class,
                'order': organism.bio_order,
                'family': organism.family,
                'genus': organism.genus,
                'species': organism.species,
                'strain': organism.strain,
                'metabolism_type': '/'.join([x['type'] for x in organism.metabolism_type.values()]),
                'risk': risk_value})
    response = {'total': total, 'rows': return_values}
    serialized = json.JSONEncoder().encode(response)
    return HttpResponse(serialized, content_type='application/json')

def organisms_results_page(request):
    response = None
    page = int(request.GET['page'])
    rows = int(request.GET['rows'])
    if 'id' in request.GET:
        id = int(request.GET['id'])
    else:
        id = None
    if 'source' in request.GET:
        source = request.GET['source']
    else:
        source = None
    if source == 'sga':
        (return_values, total) = organisms_sga_results_page(page, rows, id)
    elif source == 'mga':
        (return_values, total) = organisms_mga_results_page(page, rows, id)
    else:
        return HttpResponse('')
    response = {'total': total, 'rows': return_values}
    serialized = json.JSONEncoder().encode(response)
    return HttpResponse(serialized, content_type='application/json')

def organisms_sga_results_page(page, rows, analysis_id):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    return_values = []
    try:
        analysis = SingleGeneAnalysis.objects.get(id=analysis_id)
        try:
            single_gene_results = SingleGeneResult.objects.filter(single_gene_analysis=analysis).order_by('-score')
        except SingleGeneResult.DoesNotExist:
            single_gene_results = None
    except SingleGeneAnalysis.DoesNotExist:
        single_gene_results = None
    if not single_gene_results:
        response = {'total': 0, 'rows': return_values}
        serialized = json.JSONEncoder().encode(response)
        return HttpResponse(serialized, content_type='application/json')

    paginator = Paginator(single_gene_results, rows)
    try:
        sga_results = paginator.page(page)
    except PageNotAnInteger:
        sga_results = paginator.page(1)
    except EmptyPage:
        sga_results = paginator.page(paginator.num_pages)

    total = paginator.count
    if total > 0:
        for single_gene_result in sga_results:
            organisms = Organism.objects.filter(singlegeneresult=single_gene_result)
            for organism in organisms:
                if not organism.risk:
                    risk_value = ""
                else:
                    risk_value = Attribute.objects.get(id=organism.risk_id).value
                return_values.append({
                    'analysis_id': analysis_id,
                    'analysis_type': 'sga',
                    'id': organism.id,
                    'superkingdom': organism.superkingdom,
                    'phylum': organism.phylum,
                    'class': organism.bio_class,
                    'order': organism.bio_order,
                    'family': organism.family,
                    'genus': organism.genus,
                    'species': organism.species,
                    'strain': organism.strain,
                    'score': str(single_gene_result.score),
                    'gene_pc': '-',
                    'metabolism_type': '/'.join([x['type'] for x in organism.metabolism_type.values()]),
                    'risk': risk_value})
    return (return_values, total,)


def organisms_mga_results_page(page, rows, analysis_id):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    return_values = []
    try:
        analysis = MetagenomeAnalysis.objects.get(id=analysis_id)
        try:
            metagenome_results = MetagenomeResult.objects.filter(metagenome_analysis=analysis).order_by('-sequence_length_percent')
        except MetagenomeResult.DoesNotExist:
            metagenome_results = None
    except MetagenomeAnalysis.DoesNotExist:
        metagenome_results = None
    if not metagenome_results:
        response = {'total': 0, 'rows': return_values}
        serialized = json.JSONEncoder().encode(response)
        return HttpResponse(serialized, content_type='application/json')

    paginator = Paginator(metagenome_results, rows)
    try:
        mga_results = paginator.page(page)
    except PageNotAnInteger:
        mga_results = paginator.page(1)
    except EmptyPage:
        mga_results = paginator.page(paginator.num_pages)

    total = paginator.count
    if total > 0:
        for metagenome_result in mga_results:
            organisms = Organism.objects.filter(metagenomeresult=metagenome_result)
            for organism in organisms:
                if not organism.risk:
                    risk_value = ""
                else:
                    risk_value = Attribute.objects.get(id=organism.risk_id).value
                return_values.append({
                    'analysis_id': analysis_id,
                    'analysis_type': 'mga',
                    'id': organism.id,
                    'superkingdom': organism.superkingdom,
                    'phylum': organism.phylum,
                    'class': organism.bio_class,
                    'order': organism.bio_order,
                    'family': organism.family,
                    'genus': organism.genus,
                    'species': organism.species,
                    'strain': organism.strain,
                    'score': str(metagenome_result.sequence_length_percent),
                    'gene_pc': str(metagenome_result.protein_count_percent),
                    'metabolism_type': '/'.join([x['type'] for x in organism.metabolism_type.values()]),
                    'risk': risk_value})
    return (return_values, total,)

mga_search_function_fields = {'cog_id': 'cog_function',
                              'pfam_id': 'pfam_function',
                              'ec_number': 'enzyme_function',
                              'ko_id': 'ko_function'}
@login_required
def metagenome_analysis_genes_page(request):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = int(request.GET['page'])
    rows = int(request.GET['rows'])
    mga_id = int(request.GET['mga_id'])
    return_values = []
    # Any filters present?
    filters_j = request.GET.get('filterRules', None)
    if filters_j:
        filters = json.JSONDecoder().decode(filters_j)
        kwargs = {'metagenome_result__metagenome_analysis__id__exact': mga_id}
        q = Q(**kwargs)
        for filter in filters:
            field = filter['field']
            if field.startswith('organism'):
                field = 'metagenome_result__' + field
            # See if this protein id/function field
            function_field = mga_search_function_fields.get(field)
            if function_field:
                if not (filter['value']).isdigit():
                    field = function_field
            op = filter['op']
            if op == 'contains':
                op_suffix = '__icontains'
            value = filter['value']
            attribute = "%s%s" % (field, op_suffix,)
            kwargs = {attribute: value}
            aQ = Q(**kwargs)
            q = q & aQ
        metagenome_analysis_genes = MetagenomeResultGene.objects.filter(q).order_by('-scaffold_length', 'scaffold_id')
    else:
        metagenome_analysis_genes = MetagenomeResultGene.objects.filter(metagenome_result__metagenome_analysis__id=mga_id).order_by('-scaffold_length', 'scaffold_id')
    paginator = Paginator(metagenome_analysis_genes, rows)
    try:
        mga_gene_results = paginator.page(page)
    except PageNotAnInteger:
        mga_gene_results = paginator.page(1)
    except EmptyPage:
        mga_gene_results = paginator.page(paginator.num_pages)

    total = paginator.count
    if total > 0:
        mga_analysis = MetagenomeAnalysis.objects.get(id=mga_id)
        total_sequence_length = mga_analysis.total_sequence_length
        for mga_gene_result in mga_gene_results:
            organism = Organism.objects.get(metagenomeresult=mga_gene_result.metagenome_result)
            return_values.append({
                'gene_name': mga_gene_result.gene_name,
                'gene_symbol': mga_gene_result.gene_symbol,
                'scaffold_id': mga_gene_result.scaffold_id,
                'scaffold_length': mga_gene_result.scaffold_length,
                'cog_id': mga_gene_result.cog_id,
                'cog_function': mga_gene_result.cog_function,
                'pfam_id': mga_gene_result.pfam_id,
                'pfam_function': mga_gene_result.pfam_function,
                'tigrfam_id': mga_gene_result.tigrfam_id,
                'tigrfam_function': mga_gene_result.tigrfam_function,
                'ec_number': mga_gene_result.ec_number,
                'enzyme_function': mga_gene_result.enzyme_function,
                'ko_id': mga_gene_result.ko_id,
                'ko_function': mga_gene_result.ko_function,
                'organism__ncbi_taxon_id': organism.ncbi_taxon_id,
                'organism__superkingdom': organism.superkingdom,
                'organism__phylum': organism.phylum,
                'organism__bio_class': organism.bio_class,
                'organism__bio_order': organism.bio_order,
                'organism__family': organism.family,
                'organism__genus': organism.genus,
                'organism__species': organism.species,
                'organism__strain': organism.strain
            })
    response = {'total': total, 'rows': return_values}
    serialized = json.JSONEncoder().encode(response)
    return HttpResponse(serialized, content_type='application/json')

@login_required
def single_gene_analysis_organisms_page(request):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = int(request.GET['page'])
    rows = int(request.GET['rows'])
    sga_id = int(request.GET['sga_id'])
    return_values = []
    # Any filters present?
    filters_j = request.GET.get('filterRules', None)
    if filters_j:
        filters = json.JSONDecoder().decode(filters_j)
        kwargs = {'single_gene_analysis__id__exact': sga_id}
        q = Q(**kwargs)
        for filter in filters:
            field = filter['field']
            # if field.startswith('organism'):
            #     field = 'organism__' + field
            op = filter['op']
            if op == 'contains':
                op_suffix = '__icontains'
            elif op == 'equals':
                op_suffix = '__equals'
            value = filter['value']
            attribute = "%s%s" % (field, op_suffix,)
            kwargs = {attribute: value}
            aQ = Q(**kwargs)
            q = q & aQ
        single_gene_results = SingleGeneResult.objects.filter(q)
    else:
        single_gene_results = SingleGeneResult.objects.filter(single_gene_analysis__id=sga_id)
    paginator = Paginator(single_gene_results, rows)
    try:
        sga_results = paginator.page(page)
    except PageNotAnInteger:
        sga_results = paginator.page(1)
    except EmptyPage:
        sga_results = paginator.page(paginator.num_pages)

    total = paginator.count
    if total > 0:
        for sga_result in sga_results:
            organism = Organism.objects.get(singlegeneresult=sga_results)

            return_values.append({
                'organism__ncbi_taxon_id': organism.ncbi_taxon_id,
                'organism__superkingdom': organism.superkingdom,
                'organism__phylum': organism.phylum,
                'organism__bio_class': organism.bio_class,
                'organism__bio_order': organism.bio_order,
                'organism__family': organism.family,
                'organism__genus': organism.genus,
                'organism__species': organism.species,
                'organism__strain': organism.strain,
                'score': sga_result.score
            })
    response = {'total': total, 'rows': return_values}
    serialized = json.JSONEncoder().encode(response)
    return HttpResponse(serialized, content_type='application/json')


@login_required
def browse_sample_sgr_page(request):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = int(request.GET['page'])
    rows = int(request.GET['rows'])
    sga_id = int(request.GET['sga_id'])
    return_values = []
    # First see if there is an analysis with this id
    try:
        analysis = SingleGeneAnalysis.objects.get(id=sga_id)
    except:
        response = {'total': 0, 'rows': return_values}
        serialized = json.JSONEncoder().encode(response)
        return HttpResponse(serialized, content_type='application/json')

    sort_field = None
    if 'sort' in request.GET:
        sort_field = request.GET['sort']
        sort_order = request.GET['order']
        if sort_order == 'desc':
            sort_field = '-' + sort_field
    # Any Filters present?
    filters_j = request.GET.get('filterRules','[]')
    filters = json.JSONDecoder().decode(filters_j)
    q = None    # Query to be built
    if len(filters) > 0:
        i = 1
        for filter in filters:
            field = 'organism__' + filter['field']
            op = filter['op']
            if op == 'contains':
                op_suffix = '__icontains'
            elif op == 'equal':
                op_suffix = '__exact'
            else:
                print "ERROR: browse_sample_sgr_page unknown op: ", op
                continue
            value = filter['value']
            attribute = "%s%s" % (field, op_suffix,)
            kwargs = {attribute: value}
            aQ = Q(**kwargs)
            if i == 1:
                q = aQ
            else:
                q = q & aQ
            i += 1
        if sort_field:
            single_gene_results = SingleGeneResult.objects.filter(single_gene_analysis=analysis).filter(q).order_by(sort_field)
        else:
            single_gene_results = SingleGeneResult.objects.filter(single_gene_analysis=analysis).filter(q)
    else:
        if sort_field:
            single_gene_results = SingleGeneResult.objects.filter(single_gene_analysis=analysis).order_by(sort_field)
        else:
            single_gene_results = SingleGeneResult.objects.filter(single_gene_analysis=analysis).order_by('-score')

    if not single_gene_results:
        response = {'total': 0, 'rows': return_values}
        serialized = json.JSONEncoder().encode(response)
        return HttpResponse(serialized, content_type='application/json')

    paginator = Paginator(single_gene_results, rows)
    try:
        sga_results = paginator.page(page)
    except PageNotAnInteger:
        sga_results = paginator.page(1)
    except EmptyPage:
        sga_results = paginator.page(paginator.num_pages)

    total = paginator.count
    if total > 0:
        for single_gene_result in sga_results:
            organisms = Organism.objects.filter(singlegeneresult=single_gene_result)
            for organism in organisms:
                if not organism.risk:
                    risk_value = ""
                else:
                    risk_value = Attribute.objects.get(id=organism.risk_id).value
                return_values.append({
                    'id': organism.id,
                    'superkingdom': organism.superkingdom,
                    'phylum': organism.phylum,
                    'bio_class': organism.bio_class,
                    'bio_order': organism.bio_order,
                    'family': organism.family,
                    'genus': organism.genus,
                    'species': organism.species,
                    'strain': organism.strain,
                    'score': str(single_gene_result.score),
                    'metabolism_type': '/'.join([x['type'] for x in organism.metabolism_type.values()]),
                    'risk': risk_value})
    response = {'total': total, 'rows': return_values}
    serialized = json.JSONEncoder().encode(response)
    return HttpResponse(serialized, content_type='application/json')

@login_required
def browse_sample_mgr_page(request):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = int(request.GET['page'])
    rows = int(request.GET['rows'])
    mga_id = int(request.GET['mga_id'])
    return_values = []
    try:
        analysis = MetagenomeAnalysis.objects.get(id=mga_id)
        try:
            metagenome_results = MetagenomeResult.objects.filter(metagenome_analysis=analysis).order_by('-sequence_length')
        except ObjectDoesNotExist:
            metagenome_results = None
    except MetagenomeResult.DoesNotExist:
        metagenome_results = None
    if not metagenome_results:
        response = {'total': 0, 'rows': return_values}
        serialized = json.JSONEncoder().encode(response)
        return HttpResponse(serialized, content_type='application/json')

    paginator = Paginator(metagenome_results, rows)
    try:
        mga_results = paginator.page(page)
    except PageNotAnInteger:
        mga_results = paginator.page(1)
    except EmptyPage:
        mga_results = paginator.page(paginator.num_pages)

    total = paginator.count
    if total > 0:
        for mga_result in mga_results:
            if analysis.total_sequence_length != 0:
                sequence_length_percent = float(mga_result.sequence_length) / analysis.total_sequence_length
            else:
                sequence_length_percent = 0.0
            organisms = Organism.objects.filter(metagenomeresult=mga_result)
            for organism in organisms:
                return_values.append({
                    'id': mga_result.id,
                    'superkingdom': organism.superkingdom,
                    'phylum': organism.phylum,
                    'class': organism.bio_class,
                    'order': organism.bio_order,
                    'family': organism.family,
                    'genus': organism.genus,
                    'species': organism.species,
                    'seq_length_percent': str(sequence_length_percent),
                    'gene_count_percent': str(mga_result.protein_count_percent)
                    # 'strain': organism.strain,
                    # 'metabolism_type': '/'.join([x['type'] for x in organism.metabolism_type.values()]),
                    # 'gene_name': protein_result.gene_name,
                    # 'cog_function': protein_result.cog_function,
                    # 'pfam_function': protein_result.pfam_function,
                    # 'tigrfam_function': protein_result.tigrfam_function,
                    # 'enzyme_function': protein_result.enzyme_function,
                    # 'ko_function': protein_result.ko_function})
                })
    response = {'total': total, 'rows': return_values}
    serialized = json.JSONEncoder().encode(response)
    return HttpResponse(serialized, content_type='application/json')


@login_required
def browse_organisms_page(request):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = int(request.GET['page'])
    rows = int(request.GET['rows'])
    sort_field = None
    if 'sort' in request.GET:
        sort_field = request.GET['sort']
        sort_order = request.GET['order']
        if sort_order == 'desc':
            sort_field = '-' + sort_field
    return_values = []
    # Any Filters present?
    filters_j = request.GET.get('filterRules','[]')
    filters = json.JSONDecoder().decode(filters_j)
    q = None    # Query to be built
    if len(filters) > 0:
        i = 1
        for filter in filters:
            field = filter['field']
            op = filter['op']
            if op == 'contains':
                op_suffix = '__icontains'
            elif op == 'equal':
                op_suffix = '__exact'
            else:
                print "ERROR: browse_organisms_page unknown op: ", op
                continue
            value = filter['value']
            attribute = "%s%s" % (field, op_suffix,)
            kwargs = {attribute: value}
            aQ = Q(**kwargs)
            if i == 1:
                q = aQ
            else:
                q = q & aQ
            i += 1
        if sort_field:
            organisms = Organism.objects.filter(q).order_by(sort_field)
        else:
            organisms = Organism.objects.filter(q)
    else:
        if sort_field:
            organisms = Organism.objects.order_by(sort_field)
        else:
            organisms = Organism.objects.order_by('-superkingdom', 'subphylum', 'phylum', 'bio_class', 'bio_order',
                                                  'family', 'genus', 'species', 'strain')

    paginator = Paginator(organisms, rows)
    try:
        organism_results = paginator.page(page)
    except PageNotAnInteger:
        organism_results = paginator.page(1)
    except EmptyPage:
        organism_results = paginator.page(paginator.num_pages)

    #total = len(organisms)
    total = paginator.count
    if total > 0:
        for organism in organism_results:
            metabolism_type = organism.metabolism_type
            display_metabolism_type = '/'.join([x['type'] for x in metabolism_type.values()])
            if organism.ncbi_taxon_id == 32644:
                ncbi_taxon_id = 'Unclass.'
            else:
                ncbi_taxon_id = organism.ncbi_taxon_id
            if organism.risk:
                risk = organism.risk.value
            else:
                risk = ''
            return_values.append({
                'id': organism.id,
                'superkingdom': organism.superkingdom,
                'phylum': organism.phylum,
                'subphylum': organism.subphylum,
                'bio_class': organism.bio_class,
                'bio_order': organism.bio_order,
                'family': organism.family,
                'genus': organism.genus,
                'species': organism.species,
                'strain': organism.strain,
                'ncbi_taxon_id': ncbi_taxon_id,
                'metabolism_type': display_metabolism_type,
                'risk': risk})

    response = {'total': total, 'rows': return_values}
    serialized = json.JSONEncoder().encode(response)
    return HttpResponse(serialized, content_type='application/json')


@login_required
def browse_hydrocarbon_resources_page(request):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = int(request.GET['page'])
    rows = int(request.GET['rows'])
    sort_field = None
    if 'sort' in request.GET:
        sort_field = request.GET['sort']
        sort_order = request.GET['order']
        if sort_order == 'desc':
            sort_field = '-' + sort_field
    return_values = []
    # Any Filters present?
    filters_j = request.GET.get('filterRules','[]')
    filters = json.JSONDecoder().decode(filters_j)
    if len(filters) > 0:
        i = 1
        for filter in filters:
            field = filter['field']
            op = filter['op']
            if op == 'contains':
                op_suffix = '__icontains'
            elif op == 'equal':
                op_suffix = '__exact'
            value = filter['value']
            attribute = "%s%s" % (field, op_suffix,)
            kwargs = {attribute: value}
            aQ = Q(**kwargs)
            if i == 1:
                q = aQ
            else:
                q = q & aQ
            i += 1
        if sort_field:
            hcrs = HydrocarbonResource.objects.filter(q).order_by(sort_field)
        else:
            hcrs = HydrocarbonResource.objects.filter(q)
    else:
        if sort_field:
            hcrs = HydrocarbonResource.objects.order_by(sort_field)
        else:
            hcrs = HydrocarbonResource.objects.all()

    paginator = Paginator(hcrs, rows)
    try:
        hcr_results = paginator.page(page)
    except PageNotAnInteger:
        hcr_results = paginator.page(1)
    except EmptyPage:
        hcr_results = paginator.page(paginator.num_pages)

    total = paginator.count
    if total > 0:
        for hcr in hcr_results:
            # try:
            #     country = Attribute.objects.get(id=hcr.country_id).value
            # except Attribute.DoesNotExist:
            #     print "No Country Attribute for id: [%s]" % hcr.country_id
            #     country = ''
            return_values.append({
                'id': hcr.id,
                'hcr': get_cv_value(hcr.hcr),
                'hcr_abbrev': hcr.hcr_abbrev,
                'basin': hcr.basin,
                'field': hcr.field,
                'reservoir': hcr.reservoir})
    response = {'total': total, 'rows': return_values}
    serialized = json.JSONEncoder().encode(response)
    return HttpResponse(serialized, content_type='application/json')


@login_required
def export_analysis(request, source):
    id = request.GET.get('id', None)
    if not id:
        return None
    if source == 'metagenome_analysis_genes':
        mga_id = id
        entity_model = models.get_model('webapp', 'MetagenomeResultGene' )
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s-%s.tsv"' % (source, mga_id)
        # We use the Python UnicodeWriter to send to create and send the csv file back to the
        # requester.
        writer = UnicodeWriter(response, delimiter='\t')
        # Any filters present?
        filters_j = request.GET.get('filterRules', None)
        if filters_j:
            filters = json.JSONDecoder().decode(filters_j)
            kwargs = {'metagenome_result__metagenome_analysis__id__exact': mga_id}
            q = Q(**kwargs)
            for filter in filters:
                field = filter['field']
                if field.startswith('organism'):
                    field = 'metagenome_result__' + field
                # See if this protein id/function field
                function_field = mga_search_function_fields.get(field)
                if function_field:
                    if not (filter['value']).isdigit():
                        field = function_field
                op = filter['op']
                if op == 'contains':
                    op_suffix = '__icontains'
                value = filter['value']
                attribute = "%s%s" % (field, op_suffix,)
                kwargs = {attribute: value}
                aQ = Q(**kwargs)
                q = q & aQ
            items = MetagenomeResultGene.objects.filter(q).order_by('-scaffold_length', 'scaffold_id')
        else:
            items = MetagenomeResultGene.objects.filter(metagenome_result__metagenome_analysis__id=mga_id).order_by('-scaffold_length', 'scaffold_id')
    elif source == 'single_gene_analysis_organisms':
        sga_id = id
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s-%s.tsv"' % (source, sga_id)
        # We use the Python UnicodeWriter to send to create and send the csv file back to the
        # requester.
        writer = UnicodeWriter(response, delimiter='\t')
        # Any filters present?
        filters_j = request.GET.get('filterRules', None)
        if filters_j:
            filters = json.JSONDecoder().decode(filters_j)
            kwargs = {'single_gene_analysis__id__exact': sga_id}
            q = Q(**kwargs)
            for filter in filters:
                field = filter['field']
                # if field.startswith('organism'):
                #     field = 'organism__' + field
                op = filter['op']
                if op == 'contains':
                    op_suffix = '__icontains'
                elif op == 'equals':
                    op_suffix = '__equals'
                value = filter['value']
                attribute = "%s%s" % (field, op_suffix,)
                kwargs = {attribute: value}
                aQ = Q(**kwargs)
                q = q & aQ
            single_gene_results = SingleGeneResult.objects.filter(q)
        else:
            single_gene_results = SingleGeneResult.objects.filter(single_gene_analysis__id=sga_id)
        headers = ['ncbi_taxon_id', 'superkingdom', 'phulum', 'class', 'order', 'family', 'genus', 'species', 'strain',
                   'score', 'metabolism_type', 'threat']
        writer.writerow(headers)
        for single_gene_result in single_gene_results:
            organisms = Organism.objects.filter(singlegeneresult=single_gene_result)
            for organism in organisms:
                if not organism.risk:
                    threat = ""
                else:
                    threat = Attribute.objects.get(id=organism.risk_id).value
                row = [
                    organism.id,
                    organism.superkingdom,
                    organism.phylum,
                    organism.bio_class,
                    organism.bio_order,
                    organism.family,
                    organism.genus,
                    organism.species,
                    organism.strain,
                    str(single_gene_result.score),
                    '/'.join([x['type'] for x in organism.metabolism_type.values()]),
                    threat
                    ]
                writer.writerow(row)
        return response
    else:
        return None

    headers = []
    fields = entity_model._meta.fields
    for field in fields:
        headers.append(field.name)
    writer.writerow(headers)
    for item in items:
        row = []
        for field in fields:
            try:
                value = getattr(item, field.name)
            except ObjectDoesNotExist:
                value = ''
            if callable(value):
                value = value()
            row.append("%s" % value)
        writer.writerow(row)
    return response


@login_required
def export(request, source):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s.tsv"' % source
    # We use the Python UnicodeWriter to send to create and send the csv file back to the
    # requester.
    writer = UnicodeWriter(response, delimiter='\t')
    entity_model = models.get_model('webapp', source)
    # Any Filters present? If so, add them to the query
    filters_j = request.GET.get('filterRules','[]')
    filters = json.JSONDecoder().decode(filters_j)
    if len(filters) > 0:
        i = 1
        for filter in filters:
            field = filter['field']
            op = filter['op']
            if op == 'contains':
                op_suffix = '__icontains'
            elif op == 'equal':
                op_suffix = '__exact'
            value = filter['value']
            attribute = "%s%s" % (field, op_suffix,)
            kwargs = {attribute: value}
            aQ = Q(**kwargs)
            if i == 1:
                q = aQ
            else:
                q = q & aQ
            i += 1
        items = entity_model.objects.filter(q)
    else:
        # No filters specified
        items = entity_model.objects.all()
    headers = []
    fields = entity_model._meta.fields
    for field in fields:
        headers.append(field.name)
    writer.writerow(headers)
    for item in items:
        row = []
        for field in fields:
            try:
                value = getattr(item, field.name)
            except ObjectDoesNotExist:
                value = ''
            if callable(value):
                value = value()
            row.append("%s" % value)
        writer.writerow(row)
    return response



@login_required
def source_infosheet(request, source, id):
    html = ''
    suppress_query = request.GET.get('suppressed', 'false')
    if suppress_query == 'true':
        suppress_query = '_suppressed'
    else:
        suppress_query = ''
    if source == 'hydrocarbon_resource':
        mineralogy = None
        hcr = HydrocarbonResource.objects.get(id=id)
        field_names = HydrocarbonResource._meta.get_all_field_names()
        display_names = []
        for field_name in field_names:
            n = field_name.replace('_', ' ')
            n = n.capitalize()
            display_names.append([n, field_name])
        try:
            mineralogy = Mineralogy.objects.get(hydrocarbon_resource=hcr)
        except ObjectDoesNotExist:
            pass

        html = render_to_string('infosheet/hydrocarbon_resource'+suppress_query+'.html', RequestContext(request, {
            'style': settings.VIEW_STYLE,
            'hcr': hcr,
            'display_names': display_names,
            'mineralogy': mineralogy,
            'app.session.style': settings.VIEW_STYLE
        }))
    elif source == 'investigation':
        investigation = Investigation.objects.get(id=id)
        hydrocarbon_resource = None
        mineralogy = None

        # TODO: Handle multiple hydrocarbon resources in Infosheet
        # hydrocarbon_resources = HydrocarbonResource.objects.filter(investigation_id=investigation_id).order_by('id')[0]
        try:
            hydrocarbon_resource = HydrocarbonResource.objects.get(investigation=investigation)
        except ObjectDoesNotExist:
            pass

        if hydrocarbon_resource:
            try:
                mineralogy = Mineralogy.objects.get(hydrocarbon_resource=hydrocarbon_resource)
            except ObjectDoesNotExist:
                pass

        metadata_info = get_all_metadata_info()
        # samples = investigation.sample.all()
        html = render_to_string('infosheet/investigation'+suppress_query+'.html', RequestContext(request, {
            'investigation': investigation,
            'hydrocarbon_resource': hydrocarbon_resource,
            'mineralogy': mineralogy,
            # 'samples': samples,
            'metadata_info': metadata_info,
            'style': settings.VIEW_STYLE,
            'parameters': settings.PARAMETERS
        }))

    elif source == 'sample':
        html = source_sample_infosheet(request, id, None, None, suppress_query)

    elif source == 'sga':
        html = source_sample_infosheet(request, None, id, None, suppress_query)

    elif source == 'mga':
        html = source_sample_infosheet(request, None, None, id, suppress_query)

    elif source == 'organism':
        organism = Organism.objects.get(id=id)
        display_metabolism_type = '/'.join([x['type'] for x in organism.metabolism_type.values()])
        html = render_to_string('infosheet/organism'+suppress_query+'.html', RequestContext(request, {
            'style': settings.VIEW_STYLE,
            'organism': organism,
            'metabolism_type': display_metabolism_type,
            'app.session.style': settings.VIEW_STYLE
        }))

    elif source == 'organism_tree':
        from math import log10, trunc
        full_name = (request.GET['full_name']).split('^')
        level = int(id)
        level_no = trunc(log10(level))
        try:
            if level_no == 1:
                organism = Organism.objects.filter(superkingom=full_name[0], phylum=None, bio_class=None, bio_order=None, family=None, genus=None, species=None)[0]
            if level_no == 2:
                organism = Organism.objects.filter(superkingdom=full_name[0], phylum=full_name[1])[0]
            if level_no == 3:
                organism = Organism.objects.filter(superkingdom=full_name[0], phylum=full_name[1], bio_class=full_name[2])[0]
            if level_no == 4:
                organism = Organism.objects.filter(superkingdom=full_name[0], phylum=full_name[1], bio_class=full_name[2],
                                                bio_order=full_name[3])[0]
            if level_no == 5:
                organism = Organism.objects.filter(superkingdom=full_name[0], phylum=full_name[1], bio_class=full_name[2],
                                                bio_order=full_name[3], family=full_name[4])[0]
            if level_no == 6:
                organism = Organism.objects.filter(superkingdom=full_name[0], phylum=full_name[1], bio_class=full_name[2],
                                                bio_order=full_name[3], family=full_name[4], genus=full_name[5])[0]
            if level_no == 7:
                organism = Organism.objects.filter(superkingdom=full_name[0], phylum=full_name[1], bio_class=full_name[2],
                                                bio_order=full_name[3], family=full_name[4], genus=full_name[5], species=full_name[6])[0]
            display_metabolism_type = '/'.join([x['type'] for x in organism.metabolism_type.values()])
            html = render_to_string('infosheet/organism'+suppress_query+'.html', RequestContext(request, {
                'style': settings.VIEW_STYLE,
                'organism': organism,
                'metabolism_type': display_metabolism_type,
                'app.session.style': settings.VIEW_STYLE
            }))
        except Organism.DoesNotExist:
            pass


    return HttpResponse(html)

def source_sample_infosheet(request, sample_id, sga_id, mga_id, suppress_query):
    single_gene_analysis = None
    metagenome_analysis = None
    # If the request includes a sample id, use it to retrieve the sample data
    # if the request includes a Single Gene Analysis id, use it to retrieve the sample data
    # If the request includes a Metagenome Analysis id, use it to retrieve the sample data.
    if sample_id:
        sample = Sample.objects.get(id=sample_id)
    if sga_id:
        single_gene_analysis = SingleGeneAnalysis.objects.get(id=sga_id)
        sample = Sample.objects.get(id=single_gene_analysis.sample_id)
    if mga_id:
        metagenome_analysis = MetagenomeAnalysis.objects.get(id=mga_id)
        sample = Sample.objects.get(id=metagenome_analysis.sample_id)

    # Try and retrieve additional sample information. Not all extra
    # data exist for a given sample.
    try:
        environment = Environment.objects.get(id=sample.environment_id)
    except ObjectDoesNotExist:
        environment = None
    try:
        waterChemistry = WaterChemistry.objects.get(sample_id=sample.id)
    except ObjectDoesNotExist:
        waterChemistry = None
    try:
        hydrocarbonChemistry = HydrocarbonChemistry.objects.get(sample_id=sample.id)
    except ObjectDoesNotExist:
        hydrocarbonChemistry = None
    try:
        productionDataAtTimeOfSampling = ProductionDataAtTimeOfSampling.objects.get(sample_id=sample.id)
    except ObjectDoesNotExist:
        productionDataAtTimeOfSampling = None

    metadata_info = get_all_metadata_info()

    html = render_to_string('infosheet/sample'+suppress_query+'.html', RequestContext(request, {
        'style': settings.VIEW_STYLE,
        'environment': environment,
        'production_data_at_time_of_sampling': productionDataAtTimeOfSampling,
        'sample': sample,
        'water_chemistry': waterChemistry,
        'hc_chemistry': hydrocarbonChemistry,
        'sga': single_gene_analysis,
        'mga': metagenome_analysis,
        'metadata_info': metadata_info,
        'app.session.style': settings.VIEW_STYLE
    }))
    return html


def get_all_metadata_info():
    """
    Used by the infosheet function

    :return:  All the MetadataInfo records as a dictionary indexed by the category and attribute
                values
    """
    # metaData = MetadataInfo.objects.all()
    # metaDataInfo = defaultdict(defaultdict)
    # for item in metaData:
        # metaDataInfo[item.category][item.attribute] = item.info

    # return metaDataInfo
    return {}


@login_required
def search(request):
    """

    :param request:
    :return:
    """
    parameters = settings.PARAMETERS
    # sample_fields = build_sample_search_fields()['fields']
    # hcr_fields = build_hcr_search_fields()['fields']
    # investigation_fields = build_investigation_search_fields()['fields']
    # organism_fields = build_organism_search_fields()['fields']
    # html = render_to_string('search.html', RequestContext(request,
    #                                {'style': settings.VIEW_STYLE,
    #                                 'parameters': parameters,
    #                                 'hcr_fields': hcr_fields,
    #                                 'investigation_fields': investigation_fields,
    #                                 'sample_fields': sample_fields,
    #                                 'organism_fields': organism_fields}))
    user_profile = request.session['user_profile']
    html = render_to_string('search.html', RequestContext(request,
                                                          {'style': settings.VIEW_STYLE,
                                                           'user_profile': user_profile,
                                                           'parameters': parameters}))
    return HttpResponse(html)


def search_filtered(request, group, source):
    import urllib

    query_string = request.META['QUERY_STRING']
    query_decoded = urllib.unquote(query_string).decode('utf8')
    query = json.loads(query_decoded)
    total = query['total']
    rows = query['rows']
    if total < 1:
        return HttpResponse('')
    q = Q()
    i = 1
    last_row = []
    for row in rows:
        entity_value = row['entity_value']
        attribute_value = row['attribute_value']
        operator_value = row['operator_value']
        value_value = row['value_value']
        category, attribute_field, field_type = attribute_value.split('|')
        if group != entity_value:
            if field_type == 'R':
                attribute_field = "%s__%s" % (category, attribute_field,)  # Pulls in the related table name
            else:
                attribute_field = "%s__%s" % (entity_value, attribute_field,)
        operator_suffix = ''
        negation = False
        if operator_value == '=':
            operator_suffix = '__exact'
        elif operator_value == '!=':
            operator_suffix = '__exact'
            negation = True
        elif operator_value == '>':
            operator_suffix = '__gt'
        elif operator_value == '<':
            operator_suffix = '__lt'
        elif operator_value == '>=':
            operator_suffix = '__gte'
        elif operator_value == '<=':
            operator_suffix = '__lte'
        elif operator_value == 'contains':
            operator_suffix = '__icontains'
        attribute = "%s%s" % (attribute_field, operator_suffix)
        if field_type == 'CV' or field_type == 'N':
            value = float(value_value)
        else:
            value = value_value
        kwargs = {attribute: value}
        if negation:
            aQ = ~Q(**kwargs)
        else:
            aQ = Q(**kwargs)
        if i > 1:
            if last_row['connector_value'] == "and":
                q = q & aQ
            else:
                q = q | aQ
        else:
            q = aQ
        # print q
        i = i + 1
        last_row = row
    return_values = []
    if group == 'hydrocarbon_resource':
        hcrs = HydrocarbonResource.objects.filter(q).order_by('id')
        if source == 'hydrocarbon_resource':
            for hcr in hcrs:
                return_values.append({
                    'hcr_abbrev': hcr.hcr_abbrev,
                    'field': hcr.field}
                )
        else:
            for hcr in hcrs:
                return_values.append(
                    {'id': hcr.id, 'hcr_abbrev': hcr.hcr_abbrev, 'field': hcr.field, 'reservoir': hcr.reservoir})
    elif group == 'investigation':
        investigations = Investigation.objects.filter(q).order_by('id')
        for investigation in investigations:
            return_values.append({
                'id': investigation.id,
                'investigation_name': investigation.project_name,
                'investigation_description': investigation.investigation_description})
    elif group == 'sample':
        if source == 'sample':
            samples = Sample.objects.filter(q).order_by('id')
            for sample in samples:
                # Find out how many analyses have been performed - if any. The count determines whether the
                # sample line can be expanded (to see the analyses).
                analyses_count = BiologicalAnalysis.objects.filter(sample=sample).count()
                return_values.append({
                    'id': sample.id,
                    'source_mat_id': sample.source_mat_id,
                    'samp_description': sample.samp_description,
                    'samp_comment': sample.samp_comment,
                    'analyses_count': analyses_count})
            # sample_count = 1
            # for sample in samples:
            #     children = []
            #     c_count = 1
            #     single_gene_analyses = SingleGeneAnalysis.objects.filter(sample=sample);
            #     metagenome_analyses = MetagenomeAnalysis.objects.filter(sample=sample);
            #     for single_gene_analysis in single_gene_analyses:
            #         children.append({
            #             'id': '%s%s' % (sample_count, c_count),
            #             'name': 'SGA - %s' % c_count,
            #             'date': single_gene_analysis.analysis_date.strftime('%Y/%m/%d'),
            #             'type': 'sga',
            #             'sga_id': single_gene_analysis.id
            #         })
            #         c_count = c_count + 1
            #     for metagenome_analysis in metagenome_analyses:
            #         children.append({
            #             'id': '%s%s' % (sample_count, c_count),
            #             'name': 'MGA - %s' % c_count,
            #             'date': metagenome_analysis.analysis_date.strftime('%Y/%m/%d'),
            #             'type': 'mga',
            #             'mga_id': metagenome_analysis.id
            #         })
            #         c_count = c_count + 1
            #     return_values.append({
            #         'id': sample_count,
            #         'name': sample.name,
            #         'date': '',
            #         'type': 'sample',
            #         'sample_id': sample.id,
            #         'children': children
            #     })
            #     sample_count = sample_count + 1
    elif group == 'organism':
        if source == 'organism':
            organisms = Organism.objects.filter(q).order_by('id')
            for organism in organisms:
                if not organism.risk:
                    risk_value = ""
                else:
                    risk_value = Attribute.objects.get(id=organism.risk_id).value
                return_values.append({
                    'id': organism.id,
                    'superkingdom': organism.superkingdom,
                    'phylum': organism.phylum,
                    'class': organism.bio_class,
                    'order': organism.bio_order,
                    'family': organism.family,
                    'genus': organism.genus,
                    'species': organism.species,
                    'strain': organism.strain,
                    'metabolism_type': list(organism.metabolism_type.values_list('type')),
                    'risk': risk_value
                })

    serialized = json.JSONEncoder().encode(return_values)
    return HttpResponse(serialized, content_type="application/json")


def search_results_get(request, source, target):
    import urllib

    query_string = request.META['QUERY_STRING']
    query_decoded = urllib.unquote(query_string).decode('utf8')
    query = json.loads(query_decoded)
    source_ids = query['ids']
    if not source_ids:
        serialized = json.JSONEncoder().encode([])
        return HttpResponse(serialized, content_type="application/json")

    return_values_dict = {}

    # We need to handle a sample source for an organism target
    # if source == 'sample' and target == 'organism':
    #     # Retrieve and make an organism tree for the samples that have
    #     # Single Gene Analysis results
    #     return_values_list = retrieve_organism_tree(source_ids)
    # else:
    for source_id in source_ids:
        if source == 'investigation':
            if target == 'sample':
                investigation = Investigation.objects.select_related().get(id=source_id)
                samples = investigation.sample.all()
                for sample in samples:
                    # Find out how many analyses have been performed - if any. The count determines whether the
                    # sample line can be expanded (to see the analyses).
                    analyses_count = BiologicalAnalysis.objects.filter(sample=sample).count()
                    return_values_dict[sample.id] = {
                        'source_mat_id': sample.source_mat_id,
                        'samp_description': sample.samp_description,
                        'samp_comment': sample.samp_comment,
                        'analyses_count': analyses_count
                    }
        elif source == 'sample':
            if target == 'investigation':
                investigation = Investigation.objects.filter(sample=source_id)
                if investigation:
                    return_values_dict[investigation[0].id] = \
                        {'investigation_name': investigation[0].project_name,
                         'investigation_description': investigation[0].investigation_description}
        elif source == 'sga':
            if target == 'organism':
                single_gene_results = SingleGeneResult.objects.filter(single_gene_analysis__id=source_id).order_by('-score')
                return_values = []
                for single_gene_result in single_gene_results:
                    try:
                        organism = Organism.objects.get(singlegeneresult=single_gene_result)
                    except Organism.DoesNotExist:
                        continue
                    if not organism.risk:
                        risk_value = ""
                    else:
                        risk_value = Attribute.objects.get(id=organism.risk_id).value
                    return_values.append({
                        'id': organism.id,
                        'superkingdom': organism.superkingdom,
                        'phylum': organism.phylum,
                        'class': organism.bio_class,
                        'order': organism.bio_order,
                        'family': organism.family,
                        'genus': organism.genus,
                        'species': organism.species,
                        'strain': organism.strain,
                        'score': str(single_gene_result.score),
                        'metabolism_type': list(organism.metabolism_type.values_list('type')),
                        'risk': risk_value
                    })
                serialized = json.JSONEncoder().encode(return_values)
                return HttpResponse(serialized, content_type="application/json")
        elif source == 'mga':
            if target == 'organism':
                analysis = MetagenomeAnalysis.objects.get(id=source_id)
                metagenome_results = \
                    MetagenomeResult.objects.filter(metagenome_analysis__id=source_id).order_by('-sequence_length')
                return_values = []
                for metagenome_result in metagenome_results:
                    if analysis.total_sequence_length != 0:
                        sequence_length_percent = float(metagenome_result.sequence_length) / analysis.total_sequence_length
                    else:
                        sequence_length_percent = 0.0
                    try:
                        organism = Organism.objects.get(metagenomeresult=metagenome_result)
                    except Organism.DoesNotExist:
                        continue
                    if not organism.risk:
                        risk_value = ""
                    else:
                        risk_value = Attribute.objects.get(id=organism.risk_id).value
                    return_values.append({
                        'id': organism.id,
                        'superkingdom': organism.superkingdom,
                        'phylum': organism.phylum,
                        'class': organism.bio_class,
                        'order': organism.bio_order,
                        'family': organism.family,
                        'genus': organism.genus,
                        'species': organism.species,
                        'strain': organism.strain,
                        'score': str(sequence_length_percent),
                        # 'gene_cnt_pc': str(metagenome_result.protein_count_percent),
                        'metabolism_type': list(organism.metabolism_type.values_list('type')),
                        'risk': risk_value
                    })
                serialized = json.JSONEncoder().encode(return_values)
                return HttpResponse(serialized, content_type="application/json")
        elif source == 'organism_tree':
            # Target should be Samples
            if target == 'sample':
                # source_ids are strings of taxonomic names
                taxon_names = source_id.split('^')
                if len(taxon_names) == 0:
                    continue
                columns = ['', '', '', '', '', '', '']
                for i in range(len(taxon_names)):
                    columns[i] = taxon_names[i]
                single_gene_results = SingleGeneResult.objects.filter(
                    kingdom=columns[0], phylum=columns[1], class_field=columns[2],
                    bio_order=columns[3], family=columns[4], genus=columns[5], species=columns[6])
                for single_gene_result in single_gene_results:
                    sample = single_gene_result.single_gene_analysis.sample
                    return_values_dict[sample.id] = {'samp_name': sample.name}
        elif source == 'organism' or source == 'organism-in-analysis':
            if target == 'sample':
                sg_samples = Sample.objects.filter(biologicalanalysis__singlegeneanalysis__singlegeneresult__organism__id=source_id)
                mg_samples = Sample.objects.filter(biologicalanalysis__metagenomeanalysis__metagenomeresult__organism__id=source_id)
                analyses_count = len(sg_samples) + len(mg_samples)
                for sample in sg_samples:
                    return_values_dict[sample.id] = {
                        'source_mat_id': sample.source_mat_id,
                        'samp_description': sample.samp_description,
                        'samp_comment': sample.samp_comment,
                        'analyses_count': analyses_count
                    }
                for sample in mg_samples:
                    return_values_dict[sample.id] = {
                        'source_mat_id': sample.source_mat_id,
                        'samp_description': sample.samp_description,
                        'samp_comment': sample.samp_comment,
                        'analyses_count': analyses_count
                    }

        sorted_return_values_list = sorted(return_values_dict)
        return_values_list = []
        for key in sorted_return_values_list:
            if target == 'investigation':
                return_values_list.append({
                    'id': key,
                    'investigation_name': return_values_dict[key]['investigation_name'],
                    'investigation_description': return_values_dict[key]['investigation_description']
                })
            elif target == 'sample':
                return_values_list.append({
                    'id': key,
                    'source_mat_id': return_values_dict[key]['source_mat_id'],
                    'samp_description': return_values_dict[key]['samp_description'],
                    'samp_comment': return_values_dict[key]['samp_comment'],
                    'analyses_count': return_values_dict[key]['analyses_count']
                })
            else:
                return_values_list.append({'id': key, 'samp_name': return_values_dict[key]['samp_name']})
    serialized = json.JSONEncoder().encode(return_values_list)
    return HttpResponse(serialized, content_type="application/json")


def organism_family_infosheet(request, family):
    html = render_to_string('infosheet/organism_family.html', RequestContext(request,{'family': family}))
    return HttpResponse(html)


def organism_genus_infosheet(request, genus):
    html = render_to_string('infosheet/organism_genus.html', RequestContext(request, {'genus': genus}))
    return HttpResponse(html)


def prepare_organism_tree_entry(organism):
    entry = {}
    fields = Organism._meta.fields
    for field in fields:
        field_type = type(field)
        field_value = getattr(organism, field.name)
        if field_type is ForeignKey:
            if field.rel.to.__name__ is 'Attribute':
                if field_value:
                    field_value = field_value.value
            else:
                field_value = None
        elif field_type is IntegerField:
            field_value = str(field_value)
        elif field_type is DecimalField:
            field_value = str(field_value)
        entry[field.name] = field_value

    if organism.risk and organism.risk != 0:
        entry['risk'] = organism.risk.value
    else:
        entry['risk'] = ''
    entry['metabolism_type'] = list(organism.metabolism_type.values_list('type'))
    entry['habitats'] = list(organism.habitats.values_list('habitat'))
    entry['ncbi_taxon_id'] = organism.ncbi_taxon_id
    return entry

def organism_genus_tree(request, genus):
    id = request.GET.get('id', None)
    if id:
        return HttpResponse('')
    organisms = Organism.objects.filter(genus=genus)
    json_response = create_tree('genus', organisms)
    return HttpResponse(json_response, content_type="application/json")


def organism_family_tree(request, family):
    id = request.GET.get('id', None)
    if id:
        return HttpResponse('')
    organisms = Organism.objects.filter(family=family)
    json_response = create_tree('family', organisms)
    return HttpResponse(json_response, content_type="application/json")


def create_tree(tree_type, organisms):
    results = [{"id": "1", "name": "Kingdoms", 'risk': '',
                'attributes': {'level': 'top'},
                "children": []}]
    organism_fields = Organism._meta.fields
    empty_tree_entry = {field.name: '' for field in organism_fields}
    for organism in organisms:
        tree_entry = prepare_organism_tree_entry(organism)
        if organism.superkingdom:
            full_name = organism.superkingdom
            children = results[0]['children']
            new_child = True
            k_count = 0
            for child in children:
                if organism.superkingdom in child.values():
                    new_child = False
                    break
                k_count += 1
            if new_child:
                entry = empty_tree_entry.copy()
                entry['id'] = "1%s" % (k_count + 1)
                entry['name'] = organism.superkingdom
                entry['attributes'] =  {'level': 'kingdom', 'full_name': full_name}
                entry['state'] = 'open'
                children.append(entry)
            kingdoms = children
        else:
            continue
        if organism.phylum:
            full_name += '^' + organism.phylum
            if 'children' not in kingdoms[k_count]:
                entry = empty_tree_entry.copy()
                entry['id'] = "1%s1" % (k_count + 1)
                entry['name'] = organism.phylum
                entry['attributes'] =  {'level': 'phylum', 'full_name': full_name}
                entry['state'] = 'open'
                children = [entry]
                kingdoms[k_count]['children'] = children
                p_count = 0
            else:
                children = kingdoms[k_count]['children']
                new_child = True
                p_count = 0
                for child in children:
                    if organism.phylum in child.values():
                        new_child = False
                        break
                    p_count += 1
                if new_child:
                    entry = tree_entry.copy()
                    entry['id'] = "1%s%s" % (k_count + 1, p_count + 1)
                    entry['name'] = organism.phylum
                    entry['attributes'] =  {'level': 'phylum', 'full_name': full_name}
                    entry['state'] = 'open'
                    children.append(entry)
            phyla = children
        else:
            continue
        if organism.bio_class:
            full_name += '^' + organism.bio_class
            if 'children' not in phyla[p_count]:
                entry = empty_tree_entry.copy()
                entry['id'] = "1%s%s1" % (k_count + 1, p_count + 1)
                entry['name'] = organism.bio_class
                entry['attributes'] =  {'level': 'class', 'full_name': full_name}
                entry['state'] = 'open'
                children = [entry]
                phyla[p_count]['children'] = children
                c_count = 0
            else:
                children = phyla[p_count]['children']
                new_child = True
                c_count = 0
                for child in children:
                    if organism.bio_class in child.values():
                        new_child = False
                        break
                    c_count += 1
                if new_child:
                    entry = tree_entry.copy()
                    entry['id'] = "1%s%s%s" % (k_count + 1, p_count + 1, c_count + 1)
                    entry['name'] = organism.bio_class
                    entry['attributes'] =  {'level': 'class', 'full_name': full_name}
                    entry['state'] = 'open'
                    children.append(entry)
            classes = children
        else:
            continue
        if organism.bio_order:
            full_name += '^' + organism.bio_order
            if 'children' not in classes[c_count]:
                entry = empty_tree_entry.copy()
                entry['id'] = "1%s%s%s1" % (k_count + 1, p_count + 1, c_count + 1)
                entry['name'] = organism.bio_order
                entry['attributes'] =  {'level': 'order', 'full_name': full_name}
                entry['state'] = 'open'
                children = [entry]
                classes[c_count]['children'] = children
                o_count = 0
            else:
                children = classes[c_count]['children']
                new_child = True
                o_count = 0
                for child in children:
                    if organism.bio_order in child.values():
                        new_child = False
                        break
                    o_count += 1
                if new_child:
                    entry = tree_entry.copy()
                    entry['id'] = "1%s%s%s%s" % (k_count + 1, p_count + 1, c_count + 1, o_count + 1)
                    entry['name'] = organism.bio_order
                    entry['attributes'] =  {'level': 'order', 'full_name': full_name}
                    entry['state'] = 'open'
                    children.append(entry)
            orders = children
        else:
            continue
        if organism.family:
            full_name += '^' + organism.family
            if 'children' not in orders[o_count]:
                entry = tree_entry.copy()
                entry['id'] = "1%s%s%s%s1" % (k_count + 1, p_count + 1, c_count + 1, o_count + 1)
                entry['name'] = organism.family
                entry['attributes'] =  {'level': 'family', 'full_name': full_name}
                entry['state'] = 'open'
                children = [entry]
                orders[o_count]['children'] = children
                f_count = 0
            else:
                children = orders[o_count]['children']
                new_child = True
                f_count = 0
                for child in children:
                    if organism.family in child.values():
                        new_child = False
                        break
                    f_count += 1
                if new_child:
                    entry = tree_entry.copy()
                    entry['id'] = "1%s%s%s%s%s" % (k_count + 1, p_count + 1, c_count + 1, o_count + 1, f_count + 1)
                    entry['name'] = organism.family
                    entry['attributes'] =  {'level': 'family', 'full_name': full_name}
                    entry['state'] = 'open'
                    children.append(entry)
            families = children
        else:
            continue
        if organism.genus:
            full_name += '^' + organism.genus
            if 'children' not in families[f_count]:
                entry = tree_entry.copy()
                entry['id'] = "1%s%s%s%s%s1" % \
                              (k_count + 1, p_count + 1, c_count + 1, o_count + 1, f_count + 1)
                entry['name'] = organism.genus
                entry['attributes'] =  {'level': 'genus', 'full_name': full_name}
                if tree_type == 'family':
                    entry['state'] = 'closed'
                else:
                    entry['state'] = 'open'
                children = [entry]
                families[f_count]['children'] = children
                g_count = 0
            else:
                children = families[f_count]['children']
                new_child = True
                g_count = 0
                for child in children:
                    if organism.genus in child.values():
                        new_child = False
                        break
                    g_count += 1
                if new_child:
                    entry = tree_entry.copy()
                    entry['id'] = "1%s%s%s%s%s%s" % \
                                  (k_count + 1, p_count + 1, c_count + 1, o_count + 1, f_count + 1, g_count + 1)
                    entry['name'] = organism.genus
                    entry['attributes'] =  {'level': 'genus', 'full_name': full_name}
                    if tree_type == 'family':
                        entry['state'] = 'closed'
                    else:
                        entry['state'] = 'open'
                    children.append(entry)
            genera = children
        else:
            continue
        if organism.species:
            full_name += '^' + organism.species
            if 'children' not in genera[g_count]:
                entry = tree_entry.copy()
                entry['id'] = "1%s%s%s%s%s%s1" % \
                              (k_count + 1, p_count + 1, c_count + 1, o_count + 1, f_count + 1, g_count + 1)
                entry['name'] = organism.species
                entry['attributes'] =  {'level': 'species', 'full_name': full_name}
                entry['state'] = 'closed'
                children = [entry]
                genera[g_count]['children'] = children
                s_count = 0
            else:
                children = genera[g_count]['children']
                new_child = True
                s_count = 0
                for child in children:
                    if organism.species in child.values():
                        new_child = False
                        break
                    s_count += 1
                if new_child:
                    entry = tree_entry.copy()
                    entry['id'] = "1%s%s%s%s%s%s%s" % \
                                  (k_count + 1, p_count + 1, c_count + 1, o_count + 1, f_count + 1, g_count + 1, s_count + 1)
                    entry['name'] = organism.species
                    entry['attributes'] =  {'level': 'species', 'full_name': full_name}
                    entry['state'] = 'closed'
                    children.append(entry)
            species = children
        else:
            continue
        if organism.strain:
            full_name += '^' + organism.strain
            if 'children' not in species[s_count]:
                entry = tree_entry.copy()
                entry['id'] = "1%s%s%s%s%s%s%s1" % \
                              (k_count + 1, p_count + 1, c_count + 1, o_count + 1, f_count + 1, g_count + 1, s_count + 1)
                entry['name'] = organism.strain
                entry['attributes'] =  {'level': 'strain', 'full_name': full_name}
                entry['state'] = 'closed'
                children = [entry]
                species[s_count]['children'] = children
                st_count = 0
            else:
                children = species[s_count]['children']
                new_child = True
                s_count = 0
                for child in children:
                    if organism.strain in child.values():
                        new_child = False
                        break
                    s_count += 1
                if new_child:
                    entry = tree_entry.copy()
                    entry['id'] = "1%s%s%s%s%s%s%s%s" % \
                                  (k_count + 1, p_count + 1, c_count + 1, o_count + 1, f_count + 1, g_count + 1, s_count + 1, st_count + 1)
                    entry['name'] = organism.strain
                    entry['attributes'] =  {'level': 'strain', 'full_name': full_name}
                    entry['state'] = 'closed'
                    children.append(entry)
        else:
            continue

    serialized = json.JSONEncoder().encode(results)
    return serialized

###########################################################################################################
# Browsing Support
###########################################################################################################
def browse_columns(request, entity):
    columns = request.session['browse_'+entity]
    content = '<form>' + columns + '</form>'
    return HttpResponse(content)

# Get a Controlled Value value
def get_cv_value(cv_value):
    if cv_value:
        return cv_value.value
    return ""
###########################################################################################################
# Searching Support
###########################################################################################################

def search_entity_cv(request, group, entity):
    """
    For the search page/tabs retrieve all of the fields associated with the entity choice.

    :param request:
    :param group:
    :param entity:
    :return:
    """
    value_list = []
    if entity == 'investigation':
        fields = build_investigation_search_fields()['fields']
    elif entity == 'hydrocarbon_resource':
        fields = build_hydrocarbon_resource_fields()['fields']
    elif entity == 'sample':
        fields = build_sample_search_fields()['fields']
    elif entity == 'environment':
        fields = build_environment_fields()['fields']
    elif entity == 'hydrocarbonchemistry':
        fields = build_hydrocarbon_chemistry_fields()['fields']
    elif entity == 'waterchemistry':
        fields = build_water_chemistry_fields()['fields']
    elif entity == 'productiondataattimeofsampling':
        fields = build_production_data_at_time_of_sampling_fields()['fields']
    elif entity == 'organism':
        fields = build_organism_search_fields()['fields']
    elif entity == 'metabolismtype':
        fields  = build_metabolism_type_fields()['fields']
    # Sort the field list
    for field in fields:
        value_list.append({
            'value': "%s|%s|%s" % (field['category'], field['attribute'],field['type'],),
            'text': field['name']})
    serialized = json.JSONEncoder().encode(value_list)
    return HttpResponse(serialized, content_type="application/json")


@login_required
def search_attribute_r(request, table, column):
    """
    Attribute values are found in a "R"elation.

    :param request:
    :param table:    Table name
    :param column:   Table column name
    :return:
    """
    if table == 'metabolism_type':
        field_values = MetabolismType.objects.filter().values(column)
        value_list = []
        for field_value in field_values:
            value_list.append({'value': field_value[column], 'text': field_value[column]})
    elif table == 'environment__country':
        field_values = Country.objects.filter().values(column)
        value_list = []
        for field_value in field_values:
            value_list.append({'value': field_value[column], 'text': field_value[column]})
    elif table == 'organism__habitat':
        field_values = Habitat.objects.filter().values(column)
        value_list = []
        for field_value in field_values:
            value_list.append({'value': field_value[column], 'text': field_value[column]})

    serialized = json.JSONEncoder().encode(value_list)
    return HttpResponse(serialized, content_type="application/json")


# @login_required
def search_attribute_cv(request, category, attribute):
    """

    :param request:
    :param category:
    :param attribute:
    :return:
    """
    field_values = Attribute.objects.filter(category=category, attribute=attribute, deprecated=False).values('id', 'value')
    value_list = []
    for field_value in field_values:
        value_list.append({'value': field_value['id'], 'text': field_value['value']})
    serialized = json.JSONEncoder().encode(value_list)
    return HttpResponse(serialized, content_type="application/json")


def search_filtered_get_page(group, source, total, rows):

    if total < 1:
        return HttpResponse('')
    q = Q()
    i = 1
    last_row = []
    for row in rows:
        entity_value = row['entity_value']
        attribute_value = row['attribute_value']
        operator_value = row['operator_value']
        value_value = row['value_value']
        category, attribute_field, field_type = attribute_value.split('|')
        if group != entity_value:
            attribute_field = "%s__%s" % (entity_value, attribute_field,)
        operator_suffix = ''
        negation = False
        if operator_value == '=':
            operator_suffix = '__exact'
        elif operator_value == '!=':
            operator_suffix = '__exact'
            negation = True
        elif operator_value == '>':
            operator_suffix = '__gt'
        elif operator_value == '<':
            operator_suffix = '__lt'
        elif operator_value == '>=':
            operator_suffix = '__gte'
        elif operator_value == '<=':
            operator_suffix = '__lte'
        elif operator_value == 'contains':
            operator_suffix = '__icontains'
        attribute = "%s%s" % (attribute_field, operator_suffix)
        if field_type == 'CV' or field_type == 'N':
            value = float(value_value)
        elif field_type == 'D':
            date_time = value_value.split(' ')
            date_parts = date_time[0].split('/')
            value = '%s-%s-%s %s' % (date_parts[2], date_parts[0], date_parts[1], date_time[1],)
        else:
            value = value_value
        kwargs = {attribute: value}
        if negation:
            aQ = ~Q(**kwargs)
        else:
            aQ = Q(**kwargs)
        if i > 1:
            if last_row['connector_value'] == "and":
                q = q & aQ
            else:
                q = q | aQ
        else:
            q = aQ
        # print q
        i += 1
        last_row = row
    results = []
    if group == 'hydrocarbon_resource':
        results = HydrocarbonResource.objects.filter(q).order_by('id')
    elif group == 'investigation':
        results = Investigation.objects.filter(q).order_by('id')
    elif group == 'sample':
        results = Sample.objects.filter(q).order_by('id')
    elif group == 'organism':
        results = Organism.objects.filter(q).order_by('id')
    return results


def retrieve_organism_tree(source_ids):
    results = [{"id": "1", "text": "Kingdoms",
                'attributes': {'level': 'top'},
                "children": []}]
    # First get any Analyses
    analyses = SingleGeneAnalysis.objects.filter(sample__in=source_ids)
    # First get the results, if any
    sgrs = SingleGeneResult.objects.filter(single_gene_analysis__in=analyses)
    for sgr in sgrs:
        # Get the organisms associated with this result
        organisms = Organism.objects.filter(singlegeneresult = sgr)
        k_count = p_count = c_count = o_count = f_count = g_count = s_count = 0
        full_name = ''
        for organism in organisms:
            score = 0.0
            if sgr.score:
                score = float(sgr.score)
    # Now get the organisms for all these analyses and sort them
    # organisms = Organism.objects.filter(singlegeneresult__single_gene_analysis__sample__in = analyses)
    # organisms = SingleGeneResult.objects.filter(single_gene_analysis__in=analyses)\
    #      .order_by('superkingdom', 'phylum', 'bio_class', 'bio_order', 'family', 'genus', 'species')
    # k_count = p_count = c_count = o_count = f_count = g_count = s_count = 0
    # full_name = ''
    # for organism in organisms:
    #     score = 0.0
    #     if organism.score:
    #         score = float(organism.score)
            if organism.superkingdom:
                full_name = organism.superkingdom
                children = results[0]['children']
                new_child = True
                k_count = 0
                for child in children:
                    if organism.superkingdom in child.values():
                        new_child = False
                        break
                    k_count += 1
                if new_child:
                    id = "1%s" % (k_count + 1)
                    children.append({'id': id, 'text': organism.superkingdom,
                                     'attributes':
                                         {'level': 'kingdom',
                                          'full_name': full_name,
                                          'score': score},
                                     'state': 'closed'})
                kingdoms = children
            else:
                continue
            if organism.phylum:
                full_name += '^' + organism.phylum
                if 'children' not in kingdoms[k_count]:
                    id = "1%s1" % (k_count + 1)
                    children = [{'id': id, 'text': organism.phylum,
                                 'attributes':
                                     {'level': 'phylum',
                                      'full_name': full_name,
                                      'score': score},
                                 'state': 'closed'}]
                    kingdoms[k_count]['children'] = children
                    p_count = 0
                else:
                    children = kingdoms[k_count]['children']
                    new_child = True
                    p_count = 0
                    for child in children:
                        if organism.phylum in child.values():
                            new_child = False
                            break
                        p_count += 1
                    if new_child:
                        id = "1%s%s" % (k_count + 1, p_count + 1)
                        children.append({'id': id, 'text': organism.phylum,
                                         'attributes':
                                             {'level': 'phylum',
                                              'full_name': full_name,
                                              'score': score},
                                         'state': 'closed'})
                phyla = children
            else:
                continue
            if organism.bio_class:
                full_name += '^' + organism.bio_class
                if 'children' not in phyla[p_count]:
                    id = "1%s%s1" % (k_count + 1, p_count + 1)
                    children = [{'id': id,
                                 'text': organism.bio_class,
                                 'attributes':
                                     {'level': 'class',
                                      'full_name': full_name,
                                      'score': score},
                                 'state': 'closed'}]
                    phyla[p_count]['children'] = children
                    c_count = 0
                else:
                    children = phyla[p_count]['children']
                    new_child = True
                    c_count = 0
                    for child in children:
                        if organism.bio_class in child.values():
                            new_child = False
                            break
                        c_count += 1
                    if new_child:
                        id = "1%s%s%s" % (k_count + 1, p_count + 1, c_count + 1)
                        children.append({'id': id, 'text': organism.bio_class,
                                         'attributes':
                                             {'level': 'class',
                                              'full_name': full_name,
                                              'score': score},
                                         'state': 'closed'})
                classes = children
            else:
                continue
            if organism.bio_order:
                full_name += '^' + organism.bio_order
                if 'children' not in classes[c_count]:
                    id = "1%s%s%s1" % (k_count + 1, p_count + 1, c_count + 1)
                    children = [{'id': id, 'text': organism.bio_order,
                                 'attributes':
                                     {'level': 'order',
                                      'full_name': full_name,
                                      'score': score},
                                 'state': 'closed'}]
                    classes[c_count]['children'] = children
                    o_count = 0
                else:
                    children = classes[c_count]['children']
                    new_child = True
                    o_count = 0
                    for child in children:
                        if organism.bio_order in child.values():
                            new_child = False
                            break
                        o_count += 1
                    if new_child:
                        id = "1%s%s%s%s" % (k_count + 1, p_count + 1, c_count + 1, o_count + 1)
                        children.append({'id': id, 'text': organism.bio_order,
                                         'attributes':
                                             {'level': 'order',
                                              'full_name': full_name,
                                              'score': score},
                                         'state': 'closed'})
                orders = children
            else:
                continue
            if organism.family:
                full_name += '^' + organism.family
                if 'children' not in orders[o_count]:
                    id = "1%s%s%s%s1" % (k_count + 1, p_count + 1, c_count + 1, o_count + 1)
                    children = [{'id': id, 'text': organism.family,
                                 'attributes':
                                     {'level': 'family',
                                      'full_name': full_name,
                                      'score': score},
                                 'state': 'closed'}]
                    orders[o_count]['children'] = children
                    f_count = 0
                else:
                    children = orders[o_count]['children']
                    new_child = True
                    f_count = 0
                    for child in children:
                        if organism.family in child.values():
                            new_child = False
                            break
                        f_count += 1
                    if new_child:
                        id = "1%s%s%s%s%s" % (k_count + 1, p_count + 1, c_count + 1, o_count + 1, f_count + 1)
                        children.append({'id': id, 'text': organism.family,
                                         'attributes':
                                             {'level': 'family',
                                              'full_name': full_name,
                                              'score': score},
                                         'state': 'closed'})
                families = children
            else:
                continue
            if organism.genus:
                full_name += '^' + organism.genus
                if 'children' not in families[f_count]:
                    id = "1%s%s%s%s%s1" % \
                         (k_count + 1, p_count + 1, c_count + 1, o_count + 1, f_count + 1)
                    children = [{'id': id, 'text': organism.genus,
                                 'attributes':
                                     {'level': 'phylum',
                                      'full_name': full_name,
                                      'score': score},
                                 'state': 'closed'}]
                    families[f_count]['children'] = children
                    g_count = 0
                else:
                    children = families[f_count]['children']
                    new_child = True
                    g_count = 0
                    for child in children:
                        if organism.genus in child.values():
                            new_child = False
                            break
                        g_count += 1
                    if new_child:
                        id = "1%s%s%s%s%s%s" % \
                             (k_count + 1, p_count + 1, c_count + 1, o_count + 1, f_count + 1, g_count + 1)
                        children.append({'id': id, 'text': organism.genus,
                                         'attributes':
                                             {'level': 'genus',
                                              'full_name': full_name,
                                              'score': score},
                                         'state': 'closed'})
                genera = children
            else:
                continue
            if organism.species:
                full_name += '^' + organism.species
                if 'children' not in genera[g_count]:
                    id = "1%s%s%s%s%s%s1" % \
                         (k_count + 1, p_count + 1, c_count + 1, o_count + 1, f_count + 1, g_count + 1)
                    children = [{'id': id, 'text': organism.species,
                                 'attributes':
                                     {'level': 'species',
                                      'full_name': full_name,
                                      'score': score},
                                 'state': 'closed'}]
                    genera[g_count]['children'] = children
                    g_count = 0
                else:
                    children = genera[g_count]['children']
                    new_child = True
                    s_count = 0
                    for child in children:
                        if organism.species in child.values():
                            new_child = False
                            break
                        s_count += 1
                    if new_child:
                        id = "1%s%s%s%s%s%s%s" % \
                             (k_count + 1, p_count + 1, c_count + 1, o_count + 1, f_count + 1, g_count + 1, s_count + 1)
                        children.append({'id': id, 'text': organism.species,
                                         'attributes':
                                             {'level': 'species',
                                              'full_name': full_name,
                                              'score': score},
                                         'state': 'closed'})
            else:
                continue
    return results
