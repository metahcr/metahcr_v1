"""
 Copyright (C) 2018 Shell Global Solutions International B.V.
"""

__author__ = 'pcmarks'

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files import File

from metahcr import settings

from upload_forms import SGAForm, MGAForm
from django.core.exceptions import ObjectDoesNotExist
from webapp.models import Sample, Attribute, Organism, BiologicalAnalysis
from webapp.models import SingleGeneAnalysis, SingleGeneResult
from webapp.models import MetagenomeAnalysis, MetagenomeResultGene, MetagenomeResult
from webapp.models import UserProfile

import csv
import os
import sys

from Bio import Entrez
from os import path
from datetime import datetime
import logging

LOOKUP_TAXONOMY_RETRIES = 5  # Entrez number of retries on taxonomy id lookup before giving up

MESSAGE_TEXTS = [
    "=== MESSAGE LEGEND:",
    "I01: Creating new sample record for sample.",
    "I02: Creating new single gene analysis record for sample.",
    "I03: Created a new organism record.",
    "W01: Organism lookup returned multiple Organisms.",
    "W02: No organism data associated with scaffold id.",
    "W03: No metagenome result record for Gene Func scaffold.",
    "W04: No metagenome result record for RNA scaffold.",
    "W05: No taxonomy id found for sample and and taxonomy.",
    "W06: IO Error on taxonomy lookup retries.",
    "W07: No Analysis record found for samp_name.",
    "W08: Multiple SGA's for samp_name.",
    "W09: DB Error while retrieving samp_name.",
    "====",
    ""
]

## Get some useful Attribute values from the database
# Not Available Predefined ("n/a") attribute id value.
n_a = Attribute(category='all', attribute='all', value='n/a')
single_gene_analysis_type = Attribute.objects.get(category='biological_analysis', attribute='type', value='Single Gene')
metagenome_analysis_type = Attribute.objects.get(category='biological_analysis', attribute='type', value='Metagenome')
data_source = Attribute.objects.get(category='organism', attribute='data_source', value='SILVA/GREENGENES')
jgi_data_source = Attribute.objects.get(category='organism', attribute='data_source', value='JGI')

# Create an "Unknown" organism if doesn't exist. Used when there are no organism data associated with a scaffold.
try:
    unknown_organism = Organism.objects.get(superkingdom='Unknown')
except Organism.DoesNotExist:
    unknown_organism = Organism(superkingdom='Unknown')
    unknown_organism.data_source = jgi_data_source
    unknown_organism.save()


@login_required
def upload(request):
    user_profile = request.session['user_profile']

    request.session['sga_upload_filename'] = None
    request.session['sga_upload_log_filename'] = None
    request.session['sga_upload_samples'] = None
    request.session['mga_upload_scaffold_filename'] = None
    request.session['mga_upload_gene_function_filename'] = None
    request.session['mga_upload_rna_filename'] = None
    request.session['mga_upload_log_filename'] = None
    request.session['mga_upload_sample'] = None
    request.session['sga_mga_upload_datetime'] = None
    databases = []
    for db_type, value in settings.DATABASES.items():
        databases.append({'name': value['NAME']})
    sga_form = SGAForm()
    mga_form = MGAForm()
    html = render_to_string('upload.html', RequestContext(request,
                                                          {'style': settings.VIEW_STYLE,
                                                           'database': databases,
                                                           'user_profile': user_profile,
                                                           'sga_form': sga_form,
                                                           'sga_upload_file': None,
                                                           'sample_names': None,
                                                           'sga_upload_log_filename': None,
                                                           'mga_form': mga_form,
                                                           'sample_name': None,
                                                           'mga_upload_log_filename': None
                                                           }))
    return HttpResponse(html)


########################################################################################################################
#  Single Gene Analysis Uploading
########################################################################################################################
def sga_upload_log_file(request, log_filename):
    log_file = default_storage.open(log_filename)
    response = HttpResponse(log_file, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="%s"' % log_filename
    return response


@login_required
def sga_upload(request):
    # See if this is a POST request
    if request.method == 'POST':
        sga_form = SGAForm(request.POST, request.FILES)
        if sga_form.is_bound:
            # Open up the otu L6 file as a CSV (tab-delimited) file
            # Get the sample names and show them to the user
            username = request.user.get_username()
            upload_datetime = timezone.now()
            request.session['sga_mga_upload_datetime'] = upload_datetime.isoformat()
            upload_datetime_str = upload_datetime.strftime('%Y_%m_%d_%H_%M_%S_%Z')
            l6_file = request.FILES['l6_upload_file']
            request.session['sga_upload_filename'] = l6_file.name
            log_filename = 'sga_' + username + '_' +upload_datetime_str + '.log'
            request.session['sga_upload_log_filename'] = log_filename
            otu_table_reader = csv.DictReader(l6_file, delimiter='\t')
            sample_names = otu_table_reader.fieldnames[1:]
            request.session['sga_upload_samples'] = sample_names

            # Save the Single Gene Analysis file in default storage (e.g., Amazon S3)
            default_storage.save(l6_file.name, l6_file)

            html = render_to_string('upload_sga.html',
                                    RequestContext(request,
                                                   {'style': settings.VIEW_STYLE,
                                                    'sga_form': sga_form.as_table(),
                                                    'sga_upload_file': l6_file,
                                                    'sample_names': sample_names,
                                                    'sga_upload_log_filename': None}))
            return HttpResponse(html)
        else:
            return HttpResponseRedirect("/upload")
    else:
        return HttpResponseRedirect('/upload')


@login_required

def sga_upload_samples(request):
    l6_filename = request.session['sga_upload_filename']
    upload_datetime = parse_datetime(request.session['sga_mga_upload_datetime'])
    username = request.user.get_username()
    request.session['sample_count'] = 0
    sga_form = SGAForm()
    if l6_filename:

        # Set up logging to be written to a local file
        # Write upload info and message legend to the log file
        log_filename = request.session['sga_upload_log_filename']
        log_directory = settings.MEDIA_ROOT
        handler = logging.FileHandler(path.join(log_directory, log_filename),mode='w')
        handler.setLevel(logging.INFO)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.info("SGA Upload started at %s (local time) by user %s" % (str(datetime.now()), username,))
        logger.info("Upload file: %s" % l6_filename)
        # Write out the message legend
        for line in MESSAGE_TEXTS:
            logger.info(line)

        # Perform the reading and loading of Single Gene Analysis data
        sga_read_file(l6_filename, upload_datetime, username)

        # Close up the logging file
        # Read it and then upload and save it to default_storage (e.g., Amazon S3)
        # Finally, delete the local logging file
        logger.info("SGA Upload finished at %s (local time) by user %s" % (str(datetime.now()), username,))
        handler.flush()
        handler.close()
        logfile = open(handler.baseFilename)
        django_logfile = File(logfile)
        django_logfile.open()
        logfile_contents = logfile.read()
        default_storage.save(log_filename, ContentFile(logfile_contents))
        logfile.close()
        os.remove(handler.baseFilename)

        request.session['sga_upload_filename'] = None
        request.session['sga_upload_samples'] = None
        html = render_to_string('upload_sga.html',
                                RequestContext(request,
                                               {'style': settings.VIEW_STYLE,
                                                'sga_form': sga_form.as_table(),
                                                'sga_upload_file': None,
                                                'sample_names': None,
                                                'sga_upload_log_filename': log_filename}))
        return HttpResponse(html)

    return HttpResponseRedirect("upload")


def sga_read_file(otu_filename, upload_datetime, username):
    # otu_file = open(otu_filename)
    otu_file = default_storage.open(otu_filename)
    otu_table_reader = csv.DictReader(otu_file, delimiter='\t')
    samp_names = otu_table_reader.fieldnames[1:]
    for samp_name in samp_names:
        build_sgas(otu_table_reader, upload_datetime, samp_name, username)
        otu_file.close()
        # otu_file = open(otu_filename)
        otu_file = default_storage.open(otu_filename)
        otu_table_reader = csv.DictReader(otu_file, delimiter='\t')   # Skip the header line (sample names)
    otu_file.close()
    return


def build_sgas(otu_table_reader, upload_datetime, samp_name, username):
    # First, there needs to be a single gene analysis record associated with this samp_name
    # If one doesn't exist - note this as an error.
    # Save the single gene analysis record - to be used when constructing the results table entries
    analyses = {}
    analysis_count = 0
    saved_count = 0
    not_saved_count = 0
    skipped_count = 0
    logger = logging.getLogger()
    try:
        single_gene_analyses = SingleGeneAnalysis.objects.filter(analysis_name=samp_name)
        if len(single_gene_analyses) == 0:
            logger.warning("W07: %s" % samp_name)
            return
        if len(single_gene_analyses) > 1:
            logger.warning("W08: %s" % samp_name)
            return
        single_gene_analysis = single_gene_analyses[0]
    except:
        e = sys.exc_info()[0]
        logger.warning("W09: %s - error: %s" % (samp_name, e,))
        return

    # Update some fields in the analysis record.
    single_gene_analysis.upload_date = upload_datetime
    single_gene_analysis.uploaded_by = username
    single_gene_analysis.save()
    single_gene_analysis = SingleGeneAnalysis.objects.get(pk=single_gene_analysis.pk)

    analyses[samp_name] = single_gene_analysis

    # Second, read every row in the OTU results spreadsheet
    # For each row in the spreadsheet construct a SingleGeneResult and save it to the database
    for row in otu_table_reader:
        # Split the taxonomy into its constituent parts
        taxon = row['#OTU ID']
        bio_classes = taxon.split(';')
        kingdom = phylum = tax_class = order = family = genus = species = ""
        for index, bio_class in enumerate(bio_classes):
            abbrev = bio_class[0:5]
            bio_name = bio_class[5:]
            # Ignore all Eukaryota results
            if index == 0 and bio_name == 'Eukaryota':
                skipped_count += 1
                continue
            if bio_name == 'Other':
                bio_name = ''
            if abbrev == 'D_0__':
                kingdom = bio_name
            elif abbrev == 'D_1__':
                phylum = bio_name
            elif abbrev == 'D_2__':
                tax_class = bio_name
            elif abbrev == 'D_3__':
                order = bio_name
            elif abbrev == 'D_4__':
                family = bio_name
            elif abbrev == 'D_5__':
                genus = bio_name
            elif abbrev == 'D_6__':
                species = bio_name
            elif abbrev == 'Oth' or abbrev == 'Unc':
                if index == 0:
                    kingdom = bio_class
                elif index == 1:
                    phylum = bio_class
                elif index == 2:
                    tax_class = bio_class
                elif index == 3:
                    order = bio_class
                elif index == 4:
                    family = bio_class
                elif index == 5:
                    genus = bio_class
                elif index == 6:
                    species = bio_class

        score = row[samp_name]
        fscore = float(score)
        if fscore == 0.0:
            not_saved_count += 1
        else:
            single_gene_result = SingleGeneResult(single_gene_analysis=analyses[samp_name])
            single_gene_result.score = fscore * 100.0
            # single_gene_result.save()
            saved_count += 1
            # Retrieve an organism
            # Add it to the set of organisms for this result
            if kingdom:
                strain = ''
                organisms = Organism.objects.filter(superkingdom=kingdom, phylum=phylum, bio_class=tax_class,
                                                    bio_order=order, family=family, genus=genus, species=species,
                                                    strain=strain)
                if len(organisms) > 1:
                    logger.warning(
                        "W01: Sample: %s ([%s]) for K: %s P: %s C: %s O: %s F: %s G: %s S: %s" %
                        (samp_name, len(organisms), kingdom, phylum, tax_class, order, family, genus, species,))
                    continue
                elif len(organisms) == 0:
                    organism = Organism(superkingdom=kingdom, phylum=phylum, bio_class=tax_class,
                                        bio_order=order, family=family, genus=genus, species=species)
                    taxonomy_id = lookup_taxonomy_id(samp_name, kingdom, phylum, tax_class, order, family, genus,
                                                     species)
                    organism.ncbi_taxon_id = taxonomy_id
                    organism.data_source = data_source
                    organism.save()

                else:
                    organism = organisms[0]
                single_gene_result.organism = organism
                single_gene_result.save()
                analysis_count += 1

    logger.info("Sample: %s - single gene analyses written: %s" % (samp_name, analysis_count,))
    logger.info("Sample: %s - single gene results written: %s " % (samp_name, saved_count,), )
    logger.info("Sample: %s - single gene results zero values: %s" % (samp_name, not_saved_count,))
    logger.info("Sample: %s - single gene results skipped: %s" % (samp_name, skipped_count,))
    return


########################################################################################################################
#  Metagenome Analysis Uploading
########################################################################################################################
"""
Metagenomic Uploading Processing Steps:
    * Get the Sample record - if none exists, create one
    * Create an MetagenomeAnalysis(BiologicialAnalysis) record
    * Open and read the 'scaffold' csv file.
    * Create a organism_id => MetagenomeResult dictionary
    * Create a scaffold-id => MetagenomeResult dictionary
    * For each row:
        * Extract the organism name
        * If no organism data set organism name (super kingdom) to "Unknown"
        * Lookup its NCBI taxonomy id
        * Find or create an Organism record
        * Lookup organism in lookup dict. organism => metagenome result
            * If not found, create MetagenomeResult with organism
            * dict[organism] => metagenome_result.id
        * Extract the scaffold
        * Add scaffold => MetagenomeResult to dict
        * Add sequence length, gene count to dictionary entry
    * For each value in organism_id => metagenomeresult dict.
        * get metagenome result record
        * comput sequence and gene count percentages
        * update metagenome record
    * Open the "geneFuncStatsList" csv file
    * For each row:
        * Extract scaffold.
        * get metagenomeresult record from scaffold => metegenome result dictionary
        * Create metagenomeresultgene record with metagenomeresult
    * Open the "RNAGene" csv file
    * For each row:
        * Extract scaffold.
        * get metagenomeresult record from scaffold => metegenome result dictionary
        * Create metagenomeresultgene record with metagenomeresult
"""

@login_required
def mga_upload(request):
    # See if this is a POST request
    if request.method == 'POST':
        mga_form = MGAForm(request.POST, request.FILES)
        if mga_form.is_bound:
            scaffold_file = request.FILES['scaffold_file']
            gene_function_file = request.FILES['gene_function_file']
            rna_file = request.FILES['rna_file']

            # Save all of the Metagenome files to default storage (e.g., Amazon S3)
            default_storage.save(scaffold_file.name, scaffold_file)
            default_storage.save(gene_function_file.name, gene_function_file)
            default_storage.save(rna_file.name, rna_file)

            request.session['mga_upload_scaffold_filename'] = scaffold_file.name
            request.session['mga_upload_gene_function_filename'] = gene_function_file.name
            request.session['mga_upload_rna_filename'] = rna_file.name
            request.session['mga_upload_log_filename'] = None
            request.session['mga_upload_sample'] = None

            request.session['mga_upload_log_filename'] = None
            html = render_to_string('upload_mga.html',
                                    RequestContext(request,
                                                   {'style': settings.VIEW_STYLE,
                                                    'mga_form': mga_form.as_table(),
                                                    'mga_upload_scaffold_filename': scaffold_file.name,
                                                    'mga_upload_gene_function_filename': gene_function_file.name,
                                                    'mga_upload_rna_filename': rna_file.name,
                                                    'sample_name': None,
                                                    'mga_upload_log_filename': None}))
            return HttpResponse(html)
        else:
            return HttpResponseRedirect("/upload")
    else:
        return HttpResponseRedirect('/upload')


def mga_upload_log_file(request, log_filename):
    log_file = default_storage.open(log_filename)
    response = HttpResponse(log_file, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="%s"' % log_filename
    return response


def mga_upload_sample(request, sample_id):
    mga_form = MGAForm()
    upload_datetime = timezone.now()
    request.session['sga_mga_upload_datetime'] = upload_datetime.isoformat()
    username = request.user.get_username()
    scaffold_filename = request.session['mga_upload_scaffold_filename']
    gene_function_filename = request.session['mga_upload_gene_function_filename']
    rna_filename = request.session['mga_upload_rna_filename']
    upload_datetime_str = timezone.now().strftime('%Y_%m_%d_%H_%M_%S_%Z')

    # Set up logging to be written to a local file
    # Write upload info and message legend to the log file
    log_filename = 'mga_' + username + '_' + upload_datetime_str + '.log'
    request.session['mga_upload_log_filename'] = log_filename
    log_directory = settings.MEDIA_ROOT
    handler = logging.FileHandler(path.join(log_directory, log_filename),mode='w')
    handler.setLevel(logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.info("MGA Upload at %s by user %s" % (upload_datetime, username))
    logger.info("Upload Files: Scaffold: %s Gene Function: %s RNA: %s" %
                (scaffold_filename, gene_function_filename, rna_filename))
    # Write out the message legend
    for line in MESSAGE_TEXTS:
        logger.info(line)

    # Perform the reading and loading of the Metagenomic Data
    mga_read_files(scaffold_filename, gene_function_filename, rna_filename, sample_id, upload_datetime, username)

    # Close up the logging file
    # Read it and then upload and save it to default_storage (e.g., Amazon S3)
    # Finally, delete the local logging file
    handler.flush()
    handler.close()
    logfile = open(handler.baseFilename)
    django_logfile = File(logfile)
    django_logfile.open()
    logfile_contents = logfile.read()
    default_storage.save(log_filename, ContentFile(logfile_contents))
    logfile.close()
    os.remove(handler.baseFilename)

    request.session['mga_upload_scaffold_filename'] = None
    request.session['mga_upload_gene_function_filename'] = None
    request.session['mga_upload_rna_filename'] = None
    html = render_to_string('upload_mga.html',
                            RequestContext(request,
                                           {'style': settings.VIEW_STYLE,
                                            'mga_form': mga_form.as_table(),
                                            'mga_upload_scaffold_filename': None,
                                            'mga_upload_gene_function_filename': None,
                                            'mga_upload_rna_filename': None,
                                            'mga_upload_log_filename': log_filename}))
    return HttpResponse(html)


def mga_read_files(scaffold_filename, gene_function_filename, rna_filename, sample_id, upload_datetime, username):
    logger = logging.getLogger()
    try:
        sample = Sample.objects.get(id=sample_id)
    except Sample.DoesNotExist:
        logger.error("Unable to find sample id = %s" % sample_id)
        return "ERROR"

    # Assemble a sample analysis name
    samp_anal_name = "%s.METGNM.U" % sample.source_mat_id

    # Create a new Metagenome Analysis (Biological Analysis) record
    mg_analysis = MetagenomeAnalysis(sample=sample,
                                     type=metagenome_analysis_type,
                                     samp_anal_name=samp_anal_name,
                                     upload_date=upload_datetime,
                                     uploaded_by=username)
    mg_analysis.save()

    # Intermediate storage dictionaries
    organism_mgr_dict = {}
    scaffold_mgr_dict = {}

    # Counters
    scaffolds = 0
    unknown_organisms = 0
    organisms = 0
    protein_genes = 0
    rna_genes = 0
    total_sequence_length = 0
    total_gene_count = 0

    with default_storage.open(scaffold_filename) as csvfile:
        logger.info("Starting with scaffold file %s" % scaffold_filename)
        reader = csv.DictReader(csvfile, delimiter='\t')
        for line in reader:
            scaffolds += 1
            scaffold_id = line['Scaffold ID'].split(' ')
            scaffold = scaffold_id[2]
            lineage_percentage = line['Lineage Percentage']
            if lineage_percentage == '':
                logger.warning("W02: %s" % scaffold_id)
                unknown_organisms += 1
                organism = unknown_organism
            else:
                organism = lookup_organism(sample.samp_name, line)
            gene_count = int(line['Gene Count'])
            sequence_length = int(line['Sequence Length (bp)'])
            # bin_id = line['Bin ID']
            total_gene_count += gene_count
            total_sequence_length += sequence_length
            [mg_result_id, org_sequence_length, org_gene_count] = organism_mgr_dict.get(organism.id, [None, 0, 0])
            if not mg_result_id:
                mg_result = MetagenomeResult(sequence_length_percent=0.0,
                                             protein_count_percent=0.0,
                                             organism=organism,
                                             metagenome_analysis=mg_analysis)
                mg_result.save()
                mg_result_id = mg_result.id
                organism_mgr_dict[organism.id] = [mg_result_id, sequence_length, gene_count]
                # organism_mgr_dict[organism.id] = [mg_result_id, sequence_length, gene_count, bin_id]
                organisms += 1
            else:
                organism_mgr_dict[organism.id] = [mg_result_id,
                                                  org_sequence_length + sequence_length,
                                                  org_gene_count + gene_count]
            scaffold_mgr_dict[scaffold] = mg_result_id

    # Loop through all of the metagenome results, calculating percentages
    for organism_id, [mg_result_id, org_sequence_length, org_gene_count] in organism_mgr_dict.items():
        sequence_length_percentage = (org_sequence_length / total_sequence_length) * 100.0
        gene_percentage = (org_gene_count / total_gene_count) * 100.0
        mg_result = MetagenomeResult.objects.get(id=mg_result_id)
        mg_result.protein_count_percent = gene_percentage
        mg_result.sequence_length_percent = sequence_length_percentage
        mg_result.save()
    logger.info("Finished with scaffold file.")
    # Open up the protein file and, using the scaffold, create a gene result record pointing to the
    # mg result record (organism)
    with default_storage.open(gene_function_filename) as csvfile:
        logger.info("Starting with gene func file %s" % gene_function_filename)
        reader = csv.DictReader(csvfile, delimiter='\t')
        for line in reader:
            scaffold = line['Scaffold']
            mg_result_id = scaffold_mgr_dict.get(scaffold)
            if not mg_result_id:
                logger.warning("W03: %s" % scaffold)
                continue
            mg_result_gene = process_gene_function(line, mg_result_id)
            mg_result_gene.save()
            protein_genes += 1

    logger.info("Finished with gene func file.")
    # Open up the RNA file and, using the scaffold, create a gene result record pointing to the
    # mg result record (organism)
    with default_storage.open(rna_filename) as csvfile:
        logger.info("Starting with rna file %s." % rna_filename)
        reader = csv.DictReader(csvfile, delimiter='\t')
        for line in reader:
            scaffold = line['Scaffold ID']
            mg_result_id = scaffold_mgr_dict.get(scaffold)
            if not mg_result_id:
                logger.warning("W04: %s" % scaffold)
                continue
            mg_result_gene = process_rna(line, mg_result_id)
            mg_result_gene.save()
            rna_genes += 1
    logger.info("Finished with rna file.")
    logger.info("Number of scaffolds: %s" % scaffolds)
    logger.info("Number of unknown organisms: %s" % unknown_organisms)
    logger.info("Number of organisms: %s" % organisms)
    logger.info("Number of protein genes: %s" % protein_genes)
    logger.info("Number of rna genes: %s" % rna_genes)
    return


########################################################################################################################
#  Uploading Support
########################################################################################################################
def lookup_taxonomy_id(sample_name, kingdom, phylum, tax_class, bio_order, family, genus, species):
    logger = logging.getLogger()
    if family is None:
        family = ""
    if genus is None:
        genus = ""
    if species is None:
        species = ""
    if species == 'sp.':
        species = ''
    Entrez.email = settings.ENTREZ_EMAIL
    handle = Entrez.esearch(db="Taxonomy",
                            term="%s %s %s %s %s %s %s" % (
                                kingdom, phylum, tax_class, bio_order, family, genus, species,))
    result = Entrez.read(handle)
    handle.close()
    count = int(result['Count'])
    if count == 0:
        logger.warning("W05: Sample: %s - K: %s P: %s C: %s O: %s F: %s G: %s S: %s" %
                        (sample_name, kingdom, phylum, tax_class, bio_order, family, genus, species,))
        return 0
    return result['IdList'][0]


def lookup_organism(sample_name, scaffold_line):
    domain = scaffold_line['Lineage Domain']
    phylum = scaffold_line['Lineage Phylum']
    bio_class = scaffold_line['Lineage Class']
    order = scaffold_line['Lineage Order']
    family = scaffold_line['Lineage Family']
    genus = scaffold_line['Lineage Genus']
    species = scaffold_line['Lineage Species']

    logger = logging.getLogger()
    # See if this organism is in the Database - Note that we do not try to match on strain because there is no strain
    # value.
    try:
        organism = Organism.objects.get(superkingdom=domain, phylum=phylum, bio_class=bio_class,
                                        bio_order=order, family=family, genus=genus, species=species,
                                        strain='')
        return organism
    except Organism.DoesNotExist:
        pass
    except Organism.MultipleObjectsReturned:
        pass
    # Could not find this organism in DB; we need to create an Organism record
    organism = Organism(superkingdom=domain, phylum=phylum, bio_class=bio_class, bio_order=order, family=family,
                        genus=genus, species=species, strain='')
    logger.info("I03: %s" % organism)
    organism.data_source = jgi_data_source
    organism.save()
    # see if it has a taxonomy id. The Entrez website does cause network errors so retry.
    retries = 1
    taxon_id = None
    while retries < LOOKUP_TAXONOMY_RETRIES:
        try:
            taxon_id = lookup_taxonomy_id(sample_name, domain, phylum, bio_class, order, family, genus, species)
            break
        except IOError:
            logger.warning("W06: %s" % retries)
            retries += 1
    if taxon_id:
        organism.ncbi_taxon_id = taxon_id
        organism.data_source = jgi_data_source
        organism.save()
    return organism


def process_gene_function(line, metagenome_result_id):
    mg_result_gene = MetagenomeResultGene(
        metagenome_result=MetagenomeResult.objects.get(id=metagenome_result_id),
        gene_id=line['Gene ID'],
        gene_name=(line['Gene Name'])[:148],
        taxon_id=line['Taxon ID'],
        assembled=line['Assembled?'],
        locus_type=get_attribute('protein_metagenom_result', 'locus_type', line['Locus Type']),
        start_coord=int(line['Start Coord']),
        end_coord=int(line['End Coord']),
        gene_length=int(line['Gene Length']),
        strand=line['Strand'],
        scaffold_id=line['Scaffold'],
        scaffold_length=int(line['Scaffold Length']),
        scaffold_gc_content=float(line['Scaffold GC']),
        scaffold_read_depth=int(line['Scaffold Depth']),
        no_of_genes_on_scaffold=int(line['# of Genes on Scaffold']),
        cog_id=line['COG ID'],
        cog_function=(line['COG Function'])[:188],
        pfam_id=line['Pfam ID'],
        pfam_function=(line['Pfam Function'])[:201],
        tigrfam_id=line['TIGRfam ID'],
        tigrfam_function=(line['TIGRfam Function'])[:16],
        ec_number=line['EC Number'],
        enzyme_function=(line['Enzyme Function'])[:124],
        ko_id=line['KO ID'],
        ko_function=(line['KO Function'])[:132]
    )
    return mg_result_gene


def process_rna(line, metagenome_result_id):
    start_coord = int(((line['Coordinates']).split('..'))[0])
    gene_length = int(line['Length'])
    end_coord = start_coord + gene_length - 1
    mg_result_gene = MetagenomeResultGene(metagenome_result=MetagenomeResult.objects.get(
        id=metagenome_result_id),
        gene_id=line['Gene ID'],
        gene_name=line['Gene Product Name'],
        locus_type=get_attribute('metagenome_gene_result', 'locus_type', line['Locus Type']),
        start_coord=start_coord,
        end_coord=end_coord,
        gene_length=gene_length,
        scaffold_id=line['Scaffold ID'],
        scaffold_length=int(line['Scaffold Length']),
        scaffold_gc_content=float(line['Scaffold GC Content']),
        scaffold_read_depth=int(line['Scaffold Read Depth'])
    )
    return mg_result_gene


def get_attribute(category, attribute, value):
    try:
        attribute = Attribute(category=category, attribute=attribute, value=value)
    except:
        attribute = n_a
    return attribute


########################################################################################################################
#  Analysis Maintenance
########################################################################################################################

def analysis_delete(request, id):
    """
    Delete the biological analysis (single gene or metagenome) and all of its results.
    The delete of the BiologicalAnalysis record will trigger a SQL cascaded delete of all records
    that have this analysis as a foreign key.

    :param request:
    :param id:   The id of the BiologicalAnalysis
    :return:
    """
    analysis = BiologicalAnalysis.objects.get(id=id)
    analysis.delete()
    return HttpResponse('')

def analysis_log_file(request, id):
    """
    Download the analysis log file associated with this analysis id.

    :param request:
    :param id:  The id of the BiologicalAnalysis
    :return:
    """
    analysis = BiologicalAnalysis.objects.get(id=id)
    upload_datetime = analysis.upload_date
    username = analysis.uploaded_by
    if analysis.type == single_gene_analysis_type:
        log_filename = 'sga_' + username + '_' + upload_datetime.strftime('%Y_%m_%d_%H_%M_%S_%Z') + '.log'
    elif analysis.type == metagenome_analysis_type:
        log_filename = 'mga_' + username + '_' + upload_datetime.strftime('%Y_%m_%d_%H_%M_%S_%Z') + '.log'
    else:
        return HttpResponse('')
    log_file = default_storage.open(log_filename)
    response = HttpResponse(log_file, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="%s"' % log_filename
    return response