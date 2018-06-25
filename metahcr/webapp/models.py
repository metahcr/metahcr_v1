"""
Copyright (C) 2018 Shell Global Solutions International B.V.

The colletion of Models used by this Django app. Each model typically maps to one relational
table. Of note is the BiologicalAnalysis model and its subclasses: SingleGeneAnalysis 
and MetagenomeAnalysis. To reflect inheritance, the tables corresponding to the models
SingleGeneAnalysis and MetagenomeAnalysis each have an auto-generated column that points to 
a row in the BiologicalAnalysis table. 
"""
from __future__ import unicode_literals

from django.db import models


class Attribute(models.Model):
    """

    """
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=64)
    attribute = models.CharField(max_length=64)
    value = models.CharField(max_length=256)
    source_type = models.CharField(max_length=32)
    source_detail = models.CharField(max_length=128, blank=True, null=True )
    deprecated = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True )

    class Meta:
        db_table = 'attribute'
        ordering = ['category', 'attribute', 'value']

    def __unicode__(self):
        return "%s.%s => %s" % (self.category, self.attribute, self.value,)


class BiologicalAnalysis(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    analysis_name = models.CharField(max_length=64, blank=True)
    samp_anal_name = models.TextField(blank=True)
    type = models.ForeignKey(Attribute, null=True,  blank=True, related_name='biological_analysis_type',
                             limit_choices_to={'category': 'biological_analysis', 'attribute': 'type'})

    seq_meth = models.CharField(max_length=64,  blank=True)
    seq_quality_filtering_method = models.TextField(blank=True)
    mid_names = models.CharField(max_length=32,  blank=True)
    mid = models.TextField(blank=True)
    nucl_acid_ext = models.CharField(max_length=64,  blank=True)     # {PMID | DOI | URL}
    adapters = models.CharField(max_length=128,  blank=True)         # {dna},{dna}
    nucl_acid_amp = models.CharField(max_length=64,  blank=True)     # {PMID | DOI | URL}
    url = models.URLField(blank=True)
    reads_count = models.BigIntegerField( blank=True, null=True)
    seq_comment = models.TextField(blank=True )
    seq_reference =models.TextField(blank=True )
    seq_status_id = models.CharField(max_length=32,  blank=True)
    sequencing_center = models.CharField(max_length=128,  blank=True)
    taxonomic_group =models.CharField(max_length=64,  blank=True)
    analysis_date = models.DateTimeField(blank=True, null=True)
    upload_date = models.DateTimeField(blank=True, null=True )
    uploaded_by = models.CharField(max_length=64,  blank=True)

    sample = models.ForeignKey('Sample', on_delete=models.CASCADE)

    class Meta:
        db_table = 'biological_analysis'
        verbose_name_plural = 'biological analyses'

    def __unicode__(self):
        return "%s for Sample %s" % (self.analysis_name, self.sample,)


class SingleGeneAnalysis(BiologicalAnalysis):
    chimera_check = models.CharField(max_length=64, blank=True) # {text} {text}
    target_gene = models.ForeignKey(Attribute, null=True,  blank=True, related_name='single_gene_analysis_target_gene',
                                    limit_choices_to={'category': 'single_gene_analysis', 'attribute': 'target_gene'})
    target_subfragment = models.CharField(max_length=64, blank=True)  # {text}
    pcr_primers = models.CharField(max_length=128, blank=True) # FWD:{dna} REV:{dna}
    pcr_cond = models.CharField(max_length=64, blank=True)
    sop = models.CharField(max_length=256,  blank=True)
    nested_pcr_required = models.BooleanField( blank=True, default=False)

    class Meta:
        db_table = 'single_gene_analysis'
        verbose_name_plural = 'single gene analyses'

    def __unicode__(self):
        return "%s for Sample %s" % (self.analysis_name, self.sample,)


class SingleGeneResult(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    OTU_name = models.CharField(max_length=64, blank=True, null=True )
    counts = models.IntegerField( blank=True, null=True)
    organism = models.ForeignKey('Organism', blank=True)
    name = models.CharField(max_length=32, blank=True)
    repseq = models.CharField(max_length=32, blank=True)
    seq = models.TextField(blank=True)
    score = models.DecimalField( max_digits=8, decimal_places=2, blank=True)
    abundance = models.IntegerField( blank=True, null=True)

    single_gene_analysis = models.ForeignKey('SingleGeneAnalysis', blank=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'single_gene_result'

    def __unicode__(self):
        return "%s" % self.single_gene_analysis


class MetagenomeAnalysis(BiologicalAnalysis):
    assembly = models.CharField(max_length=256, blank=True)
    annot_source = models.TextField(blank=True )
    assembly_name = models.TextField(blank=True )
    assembly_size = models.IntegerField(blank=True, null=True )
    contig_count = models.IntegerField(blank=True, null=True )
    gene_count = models.IntegerField(blank=True, null=True )
    library_method = models.CharField(max_length=32, blank=True)
    library_size = models.IntegerField(blank=True, null=True)
    vector = models.CharField(max_length=64, blank=True )
    total_sequence_length = models.IntegerField(blank=True, null=True)
    total_gene_count = models.IntegerField(blank=True, null=True)
    class Meta:
        db_table = 'metagenome_analysis'
        verbose_name_plural = 'metagenome analyses'

    def __unicode__(self):
        return "%s for Sample %s" % (self.analysis_name, self.sample,)


class MetagenomeResult(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    scaffold_id = models.CharField(max_length=22, blank=True)
    sequence_length = models.IntegerField(blank=True, null=True)
    gene_count = models.IntegerField(blank=True, null=True)
    lineage_percentage = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)

    metagenome_analysis = models.ForeignKey('MetagenomeAnalysis', blank=True, on_delete=models.CASCADE)
    organism = models.ForeignKey('Organism', blank=True)

    class Meta:
        db_table = 'metagenome_result'

    def __unicode__(self):
        return "%s" % self.id


class MetagenomeResultGene(models.Model):
    gene_id = models.CharField(max_length=45, blank=True)
    gene_name = models.CharField(max_length=148, blank=True)
    gene_symbol = models.ForeignKey(Attribute, null=True,  blank=True,
                                    related_name='metagenome_result_gene_gene_symbol',
                                    limit_choices_to={'category': 'metagenome_result_gene',
                                                      'attribute': 'gene_symbol'})
    taxon_id = models.CharField( blank=True, max_length=128)
    assembled = models.CharField(max_length=19, blank=True)
    locus_type = models.ForeignKey(Attribute, null=True,  blank=True,
                                   related_name='metagenome_result_gene_locus_type',
                                   limit_choices_to={'category': 'metagenome_result_gene',
                                                     'attribute': 'locus_type'})
    start_coord = models.IntegerField( blank=True, null=True)
    end_coord = models.IntegerField( blank=True, null=True)
    gene_length = models.IntegerField( blank=True, null=True)
    strand = models.CharField(max_length=11, blank=True)
    scaffold_id = models.CharField(max_length=22, blank=True)
    scaffold_length = models.IntegerField( blank=True, null=True)
    scaffold_gc_content = models.DecimalField( max_digits=9, decimal_places=2, blank=True, null=True)
    scaffold_read_depth = models.IntegerField( blank=True, null=True)
    no_of_genes_on_scaffold = models.IntegerField( blank=True, null=True)
    cog_id = models.CharField(max_length=35, blank=True)
    cog_function = models.CharField(max_length=188, blank=True)
    pfam_id = models.CharField(max_length=63, blank=True)
    pfam_function = models.CharField(max_length=201, blank=True)
    tigrfam_id = models.CharField(max_length=16, blank=True)
    tigrfam_function = models.CharField(max_length=16, blank=True)
    ec_number = models.CharField(max_length=22, blank=True)
    enzyme_function = models.CharField(max_length=124, blank=True)
    ko_id = models.CharField(max_length=19, blank=True)
    ko_function = models.CharField(max_length=132, blank=True)

    metagenome_result = models.ForeignKey('MetagenomeResult', blank=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'metagenome_result_gene'
        ordering = ['id']
        verbose_name_plural = 'metagenome gene results'
    def __unicode__(self):
        return "%s" % self.gene_id


class Country(models.Model):
    iso = models.CharField(max_length=2, blank=True)
    name = models.CharField(max_length=64, blank=True)
    printable_name = models.CharField(max_length=256, blank=True)
    iso3 = models.CharField(max_length=3, blank=True, null=True )
    numcode = models.IntegerField( blank=True, null=True)

    class Meta:
        db_table = 'country'
        ordering = ['printable_name']
        verbose_name_plural = 'countries'

    def __unicode__(self):
        return "%s" % self.printable_name


class Organization(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    address1 = models.CharField(max_length=64,  blank=True)
    address2 = models.CharField(max_length=64,  blank=True)
    postcode = models.CharField(max_length=32,  blank=True)
    country = models.ForeignKey(Country,  blank=True, null=True)
    contact_name = models.CharField(max_length=64, blank=True, null=True )
    contact_email = models.CharField(max_length=64, blank=True, null=True )

    class Meta:
        db_table = 'organization'
        ordering = ['name']
        verbose_name_plural = 'organizations'

    def __unicode__(self):
        return "%s" % self.name


class MetaHCRDatabase(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128,  blank=True)
    creation_date = models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    version = models.CharField(max_length=10, blank=True, null=True )

    organization = models.ForeignKey(Organization,  blank=True)

    class Meta:
        db_table = 'metahcr_database'
        ordering = ['organization']
        verbose_name_plural = 'MetaHCR databases'
    def __unicode__(self):
        return "%s of %s" % (self.name, self.organization,)

from django.contrib.auth.models import User


class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User)   ## This is Django's Auth User
    organization = models.ForeignKey(Organization,  blank=True)
    default_database = models.ForeignKey(MetaHCRDatabase,  blank=True)
    reset_password = models.BooleanField(default=True)
    date_of_password = models.DateTimeField(blank=True)

    class Meta:
        db_table = 'user_profile'
        verbose_name_plural = 'user profiles'
    def __unicode__(self):
        return "%s %s" % (self.user.first_name, self.user.last_name,)


class CuratorDetails(models.Model):
    id = models.AutoField(primary_key=True)
    curator_firstname = models.CharField(max_length=32)
    curator_lastname = models.CharField(max_length=64)
    curator_email = models.CharField(max_length=64)
    curator_comment = models.TextField(blank=True)

    curator_affiliation = models.ForeignKey(Organization, blank=True, null=True)

    class Meta:
        db_table = 'curator_details'
        ordering = ['curator_lastname', 'curator_firstname']
        verbose_name_plural = "curator details"

    def __unicode__(self):
        return "%s, %s" % (self.curator_lastname, self.curator_firstname,)


class HydrocarbonChemistry(models.Model):
    id = models.AutoField(primary_key=True)
    api = models.FloatField(blank=True,default=0.0)
    tan = models.FloatField(blank=True,default=0.0)
    viscosity = models.FloatField(blank=True,default=0.0)
    saturates_pc = models.FloatField(blank=True,default=0.0)
    aromatics_pc = models.FloatField(blank=True,default=0.0)
    resins_pc = models.FloatField(blank=True,default=0.0)
    asphaltenes_pc = models.FloatField(blank=True,default=0.0)
    methane_pc = models.FloatField(blank=True,default=0.0)
    naph_pc = models.FloatField(blank=True,default=0.0)
    olef_pc = models.FloatField(blank=True,default=0.0)
    paraf_pc = models.FloatField(blank=True,default=0.0)
    wax_pc = models.FloatField(blank=True,default=0.0)
    c12_c19 = models.FloatField(blank=True,default=0.0)
    c20_c35 = models.FloatField(blank=True,default=0.0)
    c2_c6 = models.FloatField(blank=True,default=0.0)
    c36plus = models.FloatField(blank=True,default=0.0)
    c7_c11 = models.FloatField(blank=True,default=0.0)
    mah_pc = models.FloatField(blank=True,default=0.0)
    pah_pc = models.FloatField(blank=True,default=0.0)
    polysufides_pc = models.FloatField(blank=True,default=0.0)
    sg_oil_phase = models.FloatField(blank=True,default=0.0)
    hc_analysis_date = models.DateTimeField(blank=True, null=True)
    hc_comment = models.TextField(blank=True)
    hc_reference = models.TextField(blank=True)

    sample = models.ForeignKey('Sample', unique=True,  blank=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'hydrocarbon_chemistry'
        ordering = ['id']
        verbose_name_plural = "hydrocarbon chemistries"

    def __unicode__(self):
        return "Sample: %s" % self.sample

        
class Mineralogy(models.Model):
    id = models.AutoField(primary_key=True)
    anhydrite = models.FloatField(blank=True, default=0.0)
    carbonate = models.FloatField(blank=True, default=0.0)
    carbonate_cement = models.FloatField(blank=True, default=0.0)
    clay = models.FloatField(blank=True, default=0.0)
    dolomite = models.FloatField(blank=True, default=0.0)
    feldspar = models.FloatField(blank=True, default=0.0)
    mica = models.FloatField(blank=True, default=0.0)
    mineralogy_analysis_date = models.DateTimeField(blank=True, null=True)
    minearlogy_comment = models.TextField(blank=True, null=True )
    mineralogy_reference = models.TextField(blank=True)
    quartz = models.FloatField(blank=True, default=0.0)
    siderite =models.FloatField(blank=True,default=0.0)
    hematite = models.FloatField(blank=True,default=0.0)
    chlorite = models.FloatField(blank=True, default=0.0)
    illite = models.FloatField(blank=True, default=0.0)
    magnetite = models.FloatField(blank=True, default=0.0)
    smectite = models.FloatField(blank=True, default=0.0)

    hydrocarbon_resource = models.ForeignKey('HydrocarbonResource', unique=True, null=True, blank=True)

    class Meta:
        db_table = 'mineralogy'
        ordering = ['id']
        verbose_name_plural = 'mineralogies'

    def __unicode__(self):
        return "%s" % self.hydrocarbon_resource


class MetabolismType(models.Model):
    type = models.CharField(max_length=64, primary_key=True)
    description = models.CharField(max_length=128, blank=True, null=True )

    class Meta:
        db_table = 'metabolism_type'
        verbose_name_plural = 'metabolism types'

    def __unicode__(self):
        return "%s" % self.type

class Habitat(models.Model):
    habitat = models.CharField(max_length=64, primary_key=True)
    description = models.CharField(max_length=128, blank=True, null=True )

    class Meta:
        db_table = 'habitat'
        verbose_name_plural = 'organism habitats'

    def __unicode__(self):
        return "%s" % self.habitat

class NucleicAcidSequenceSource(models.Model):
    id = models.AutoField(primary_key=True)
    samp_mat_process = models.TextField(blank=True)
    samp_size = models.FloatField(blank=True,default=0.0)
    source_mat_id = models.CharField(max_length=128)        # See Sample.source_mat_id
    rel_to_oxygen = models.ForeignKey(Attribute, null=True,  blank=True, related_name='nucleic_acid_sequence_source_rel_to_oxygen',
                                      limit_choices_to={'category': 'nucleic_acid_sequence_source', 'attribute': 'rel_to_oxygen'})
    samp_collect_device = models.TextField(blank=True)

    sample = models.ForeignKey('Sample',  blank=True, unique=True, on_delete=models.CASCADE)
    class Meta:
        db_table = 'nucleic_acid_sequence_source'
        verbose_name = 'nucleic acid sequence sources'

    def __unicode__(self):
        return "%s" % self.id

class Organism(models.Model):
    id = models.AutoField(primary_key=True)
    superkingdom = models.CharField(max_length=32, blank=True)
    phylum = models.CharField(max_length=128, blank=True)
    subphylum = models.CharField(max_length=128, blank=True)
    bio_class = models.CharField(max_length=128, blank=True)    # Can't clash with Python keyword
    bio_order = models.CharField(max_length=128, blank=True)
    family = models.CharField(max_length=128, blank=True)
    genus = models.CharField(max_length=128, blank=True)
    species = models.CharField(max_length=128, blank=True)
    strain = models.CharField(max_length=32, blank=True)
    ncbi_taxon_id = models.IntegerField( blank=True, null=True)
    metabolism_type = models.ManyToManyField(MetabolismType)
    description = models.CharField(max_length=256, blank=True)
    risk = models.ForeignKey(Attribute, null=True,  blank=True, related_name='organism_risk',
                             limit_choices_to={'category': 'organism', 'attribute': 'risk'})
    grow_postgate = models.ForeignKey(Attribute, null=True,  blank=True, related_name='organism_grow_postgate',
                                      limit_choices_to={'category': 'organism', 'attribute': 'grow_postgate'})
    temperature_range = models.ForeignKey(Attribute, null=True,  blank=True, related_name='organism_temperature_range',
                                          limit_choices_to={'category': 'organism', 'attribute': 'temperature_range'})
    oxygen_requirement = models.ForeignKey(Attribute, null=True,  blank=True, related_name='organism_oxygen_requirement',
                                           limit_choices_to={'category': 'organism', 'attribute': 'oxygen_requirement'})
    cell_shape = models.ForeignKey(Attribute, null=True,  blank=True, related_name='organism_cell_shape',
                                   limit_choices_to={'category': 'organism', 'attribute': 'cell_shape'})
    motility = models.ForeignKey(Attribute, null=True,  blank=True, related_name='organism_motility',
                                 limit_choices_to={'category': 'organism', 'attribute': 'motility'})
    sporulation = models.ForeignKey(Attribute, null=True,  blank=True, related_name='organism_sporulation',
                                    limit_choices_to={'category': 'organism', 'attribute': 'sporulation'})
    salinity = models.ForeignKey(Attribute, null=True,  blank=True, related_name='organism_salinity',
                                 limit_choices_to={'category': 'organism', 'attribute': 'salinity'})
    cell_arrangement = models.ForeignKey(Attribute, null=True,  blank=True, related_name='organism_cell_arrangement',
                                         limit_choices_to={'category': 'organism', 'attribute': 'cell_arrangement'})
    colour = models.ForeignKey(Attribute, null=True,  blank=True, related_name='organism_colour',
                               limit_choices_to={'category': 'organism', 'attribute': 'colour'})
    gram_staining = models.ForeignKey(Attribute, null=True,  blank=True, related_name='organism_gram_staining',
                                      limit_choices_to={'category': 'organism', 'attribute': 'gram_staining'})
    disease = models.ForeignKey(Attribute, null=True,  blank=True, related_name='organism_disease',
                                limit_choices_to={'category': 'organism', 'attribute': 'disease'})
    habitats = models.ManyToManyField(Habitat)
    # habitat = models.ForeignKey(Attribute, null=True,  blank=True, related_name='organism_habitat',
    #                             limit_choices_to={'category': 'organism', 'attribute': 'habitat'})
    metabolism = models.ForeignKey(Attribute, null=True,  blank=True, related_name='organism_metabolism',
                                   limit_choices_to={'category': 'organism', 'attribute': 'metabolism'})
    phenotype = models.ForeignKey(Attribute, null=True,  blank=True, related_name='organism_phenotype',
                                  limit_choices_to={'category': 'organism', 'attribute': 'phenotype'})
    energy_source = models.ForeignKey(Attribute, null=True,  blank=True, related_name='organism_energy_source',
                                      limit_choices_to={'category': 'organism', 'attribute': 'energy_source'})
    biotic_relationship = models.ForeignKey(Attribute, null=True,  blank=True,
                                            related_name='organism_biotic_relationship',
                                            limit_choices_to={'category': 'organism',
                                                              'attribute': 'biotic_relationship'})
    a_16s_sequence = models.TextField(blank=True)
    accession_no_cultured = models.CharField(max_length=64, blank=True)
    accession_no_uncultured = models.CharField(max_length=64, blank=True)
    ss_rdb_id = models.CharField(max_length=32, blank=True)
    temperature_min = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True)
    temperature_max = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True)
    temperature_opt_c = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True)
    ph_min = models.DecimalField( max_digits=4, decimal_places=2, blank=True, null=True)
    ph_max = models.DecimalField( max_digits=4, decimal_places=2, blank=True, null=True)
    ph_opt = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True)
    cell_diameter = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True)
    cell_length = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True)
    comment = models.TextField(blank=True)
    clone = models.CharField(max_length=64, blank=True)
    closest_cultured_relative = models.CharField(max_length=64, blank=True)
    closest_relative = models.CharField(max_length=128, blank=True)
    max_salinity_tds = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True)
    min_salinity_tds = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True)
    opt_salinity_tds = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True)
    true_tds_or_tds_equiv = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True)
    ncbi_ref_seq = models.CharField(max_length=64, blank=True)
    reference = models.CharField(max_length=64, blank=True)
    relative_abundance = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True)
    similarity = models.CharField(max_length=64, blank=True)
    similarity_clos_cul = models.CharField(max_length=64, blank=True)
    # The following fields were added as a result of loading JGI/GOLD organism information
    gold_project_id = models.IntegerField(blank=True, null=True )
    genus_synonyms = models.CharField(max_length=128, blank=True, null=True )
    species_synonyms = models.CharField(max_length=128, blank=True, null=True )
    culture_collection_id = models.CharField(max_length=64, blank=True, null=True )
    ecosystem = models.ForeignKey(Attribute, null=True,  blank=True,
                                  related_name='organism_ecosystem',
                                  limit_choices_to={'category': 'organism',
                                                    'attribute': 'ecosystem'})
    ecosystem_category = models.ForeignKey(Attribute, null=True,  blank=True,
                                           related_name='organism_ecosystem_category',
                                           limit_choices_to={'category': 'organism',
                                                             'attribute': 'ecosystem_category'})
    ecosystem_type = models.ForeignKey(Attribute, null=True,  blank=True,
                                       related_name='organism_ecosystem_type',
                                       limit_choices_to={'category': 'organism',
                                                         'attribute': 'ecosystem_type'})
    ecosystem_subtype = models.ForeignKey(Attribute, null=True,  blank=True,
                                          related_name='organism_ecosystem_subtype',
                                          limit_choices_to={'category': 'organism',
                                                            'attribute': 'ecosystem_subtype'})
    specific_ecosystem = models.ForeignKey(Attribute, null=True,  blank=True,
                                           related_name='organism_specific_ecosystem',
                                           limit_choices_to={'category': 'organism',
                                                             'attribute': 'specific_ecosystem'})
    data_source = models.ForeignKey(Attribute, null=True,  blank=True,
                                    related_name='organism_data_source',
                                    limit_choices_to={'category': 'organism',
                                                      'attribute': 'data_source'})
    contaminant = models.ForeignKey(Attribute, null=True,  blank=True,
                                    related_name='organism_contaminant',
                                    limit_choices_to={'category': 'organism',
                                                      'attribute': 'contaminant'})

    class Meta:
        db_table = 'organism'
        ordering = ['superkingdom', 'subphylum', 'phylum', 'bio_class', 'bio_order',
                    'family', 'genus', 'species', 'strain']

    def __unicode__(self):
        if self.genus:
            return "%s %s" % (self.genus, self.species,)
        if self.strain:
            return "Strain: %s" % self.strain
        return "Family: %s" % self.family


class ProductionDataAtTimeOfSampling(models.Model):
    id = models.AutoField(primary_key=True)
    prod_start_date = models.DateTimeField(blank=True, null=True)
    prod_rate = models.FloatField(blank=True, default=0.0)
    water_production_rate = models.FloatField(blank=True, default=0.0)
    water_cut = models.FloatField(blank=True, default=0.0)
    iwf = models.FloatField(blank=True, default=0.0)
    add_recov_method = models.ForeignKey(Attribute, null=True,  blank=True,
                                         related_name='production_data_at_time_of_sampling_add_recov_method',
                                         limit_choices_to={'category': 'production_data_at_time_of_sampling',
                                                           'attribute': 'add_recov_method'})
    iw_bt_date_well = models.DateTimeField(blank=True, null=True)
    biocide = models.TextField( blank=True)
    biocide_admin_method = models.TextField( blank=True)
    chem_treatment = models.TextField( blank=True)
    chem_treatment_method = models.TextField( blank=True)
    samp_loc_corr_rate = models.FloatField(blank=True, default=0.0)
    gas_rate = models.FloatField(blank=True, default=0.0)
    oil_rate = models.FloatField(blank=True, default=0.0)
    comment = models.TextField(blank=True)
    reference = models.TextField(blank=True)
    pw_per_day = models.FloatField(blank=True, default=0.0)
    prod_conn_to_injctr = models.BooleanField( blank=True, default=False)
    gas_oil_ratio = models.FloatField(blank=True,default=0.0)
    salinity = models.ForeignKey(Attribute, null=True,  blank=True,
                                 related_name='production_data_at_time_of_sampling_pd_salinity',
                                 limit_choices_to={'category': 'production_data_at_time_of_sampling',
                                                   'attribute': 'pd_salinity'})
    operator = models.TextField(blank=True)

    sample = models.ForeignKey('Sample',  blank=True, unique=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'production_data_at_time_of_sampling'
        ordering = ['id']

    def __unicode__(self):
        return "Sample: %s" % self.sample



class HydrocarbonResource(models.Model):
    id = models.AutoField(primary_key=True)
    hcr_abbrev = models.CharField(max_length=32, blank=True)
    hcr = models.ForeignKey(Attribute, null=True,
                            related_name='hydrocarbon_resource_hcr',
                            limit_choices_to={'category': 'hydrocarbon_resource',
                                              'attribute': 'hcr'})
    hc_produced = models.ForeignKey(Attribute, null=True,
                                    related_name='hydrocarbon_resource_hc_produced',
                                    limit_choices_to={'category': 'hydrocarbon_resource',
                                                      'attribute': 'hc_produced'})
    basin = models.CharField(max_length=64)
    field = models.CharField(max_length=40, blank=True)
    reservoir = models.CharField(max_length=59, blank=True)
    hcr_temp_lo = models.FloatField(blank=True, default=0.0)
    hcr_temp_hi = models.FloatField(blank=True, default=0.0)
    tvdss_of_hcr_temp = models.FloatField(blank=True, default=0.0)
    hcr_pressure = models.FloatField(blank=True, default=0.0)
    tvdss_of_hcr_pressure = models.FloatField(blank=True, default=0.0)
    permeability = models.FloatField(blank=True, default=0.0)
    porosity = models.FloatField(blank=True, default=0.0)
    lithology = models.ForeignKey(Attribute, null=True,  blank=True,
                                  related_name='hydrocarbon_resource_lithology',
                                  limit_choices_to={'category': 'hydrocarbon_resource',
                                                    'attribute': 'lithology'})
    depos_env = models.ForeignKey(Attribute, null=True,  blank=True,
                                  related_name='hydrocarbon_resource_depos_env',
                                  limit_choices_to={'category': 'hydrocarbon_resource',
                                                    'attribute': 'depos_env'})
    hcr_geol_age = models.ForeignKey(Attribute, null=True,  blank=True,
                                     related_name='hydrocarbon_resource_hcr_geol_age',
                                     limit_choices_to={'category': 'hydrocarbon_resource',
                                                       'attribute': 'hcr_geol_age'})
    owc_tvdss = models.FloatField(blank=True,default=0.0)
    hcr_fw_salinity = models.FloatField(blank=True,default=0.0)
    sr_kerog_type = models.ForeignKey(Attribute, null=True,  blank=True,
                                      related_name='hydrocarbon_resource_sr_kerog_type',
                                      limit_choices_to={'category': 'hydrocarbon_resource',
                                                        'attribute': 'sr_kerog_type'})
    sr_lithology = models.ForeignKey(Attribute, null=True,  blank=True,
                                     related_name='hydrocarbon_resource_sr_lithology',
                                     limit_choices_to={'category': 'hydrocarbon_resource',
                                                       'attribute': 'sr_lithology'})
    sr_dep_env = models.ForeignKey(Attribute, null=True,  blank=True,
                                   related_name='hydrocarbon_resource_sr_dep_env',
                                   limit_choices_to={'category': 'hydrocarbon_resource',
                                                     'attribute': 'sr_dep_env'})
    sr_geol_age = models.ForeignKey(Attribute, null=True,  blank=True,
                                    related_name='hydrocarbon_resource_sr_geol_age',
                                    limit_choices_to={'category': 'hydrocarbon_resource',
                                                      'attribute': 'sr_geol_age'})
    hcr_hc_satur_pc = models.FloatField(blank=True,default=0.0)
    drive_mech  = models.ForeignKey(Attribute, null=True,  blank=True,
                                    related_name='hydrocarbon_resource_drive_mech',
                                    limit_choices_to={'category': 'hydrocarbon_resource',
                                                      'attribute': 'drive_mech'})
    unique_resource_name = models.CharField(max_length=128, blank=True)
    comment = models.TextField(blank=True)
    reference = models.CharField(max_length=64, blank=True)
    salinity_today = models.ForeignKey(Attribute, null=True,  blank=True,
                                       related_name='hydrocarbon_rc_salinity',
                                       limit_choices_to={'category': 'hydrocarbon_resource',
                                                         'attribute': 'salinity_today'})
    formation = models.CharField(max_length=64, blank=True)
    class Meta:
        db_table = 'hydrocarbon_resource'
        ordering = ['id']
        verbose_name_plural = 'hydrocarbon resources'

    def __unicode__(self):
        return "%s %s %s %s" % (self.hcr_abbrev, self.basin, self.field, self.reservoir,)

class Investigation(models.Model):
    """
    In the original database this was known as a Project
    """
    id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=192)
    experimental_factor = models.ForeignKey(Attribute, null=True, blank=True, related_name='investigation_experimental_factor',
                                            limit_choices_to={'category': 'investigation', 'attribute': 'experimental_factor'})
    investigation_type = models.ForeignKey(Attribute, null=True, blank=True, related_name='investigation_investigation_type',
                                           limit_choices_to={'category': 'investigation', 'attribute': 'investigation_type'})
    submitted_to_insdc = models.BooleanField(blank=True, default=False)
    availability = models.ForeignKey(Attribute, null=True,  blank=True, related_name='investigation_availability',
                                     limit_choices_to={'category': 'investigation', 'attribute': 'availability'})
    completion_date = models.DateTimeField(blank=True, null=True)
    contact_id = models.CharField(blank=True, max_length=128)
    gold_project_id = models.CharField(max_length=64, blank=True)
    investigation_start_date = models.DateTimeField(blank=True, null=True)
    keywords = models.TextField(blank=True)
    ncbi_project_id = models.CharField(max_length=64, blank=True)
    investigation_comment = models.TextField(blank=True)
    investigation_description = models.TextField(blank=True)
    investigation_reference = models.TextField(blank=True)
    investigation_status = models.ForeignKey(Attribute, null=True,  blank=True, related_name='investigation_investigation_status',
                                             limit_choices_to={'category': 'investigation', 'attribute': 'investigation_status'})
    investigation_publication = models.CharField(max_length=128, blank=True)
    quality = models.ForeignKey(Attribute, null=True,  blank=True, related_name='investigation_quality',
                                limit_choices_to={'category': 'investigation', 'attribute': 'investigation_quality'})
    purpose = models.TextField(blank=True)
    env_package = models.ForeignKey(Attribute, null=True,  blank=True, related_name='investigation_env_package',
                                    limit_choices_to={'category': 'investigation', 'attribute': 'env_package'})

    curator_details = models.ManyToManyField(CuratorDetails,  blank=True)
    sample = models.ManyToManyField('Sample')
    hydrocarbon_resource = models.ManyToManyField(HydrocarbonResource)

    class Meta:
        db_table = 'investigation'
        ordering = ['project_name']

    def __unicode__(self):
        return "%s" % self.project_name[0:60]


class Sample(models.Model):
    id = models.AutoField(primary_key=True)
    source_mat_id = models.CharField(max_length=128)    # Cannot be blank or null
    samp_well_name = models.TextField(blank=True)
    win = models.TextField(blank=True)
    samp_type = models.ForeignKey(Attribute, null=True,  blank=True, related_name='sample_samp_type',
                                  limit_choices_to={'category': 'sample', 'attribute': 'samp_type'})
    samp_subtype = models.ForeignKey(Attribute, null=True,  blank=True,
                                     related_name='sample_samp_subtype',
                                     limit_choices_to={'category': 'sample', 'attribute': 'samp_subtype'})
    samp_location_point = models.ForeignKey(Attribute, null=True,  blank=True,
                                            related_name='sample_samp_location_point',
                                            limit_choices_to={'category': 'sample',
                                                              'attribute': 'samp_location_point'})
    temp = models.FloatField(blank=True,default=0.0)
    pressure = models.FloatField(blank=True,default=0.0)
    samp_tvdss = models.FloatField(blank=True, default=0.0,
                                   help_text="Depth of the sample i.e. the vertical distance between the sea level and the sampled position in "
                                             "the subsurface. Depth can be reported as an interval for subsurface samples e.g. 1325.75-1362.25 m")
    samp_md = models.FloatField(blank=True,default=0.0)
    elev = models.FloatField(blank=True,default=0.0)
    oxy_stat_sample = models.FloatField(blank=True,default=0.0)
    samp_preserv = models.CharField(max_length=32, blank=True)
    samp_transport_cond_duration = models.CharField(max_length=32, blank=True)
    samp_transport_cond_temp = models.FloatField(blank=True, default=9.0)
    samp_store_temp = models.FloatField(blank=True,default=0.0)
    samp_store_dur = models.FloatField(blank=True,default=0.0)
    samp_store_loc = models.CharField(max_length=64, blank=True)
    samp_vwa_dna_extr = models.FloatField(blank=True,default=0.0)
    organism_count = models.CharField(max_length=64, blank=True)
    organism_count_qpcr_info = models.CharField(max_length=64, blank=True)
    misc_param = models.CharField(max_length=32, blank=True)
    additional_info = models.TextField(blank=True)
    rc_distance_from_hc_water_contact = models.FloatField(blank=True,default=0.0)
    samp_comment = models.TextField(blank=True)
    samp_description = models.TextField(blank=True)
    samp_location_comment = models.TextField(blank=True)
    samp_location_reference = models.TextField(blank=True)
    samp_location_reservoir_name = models.TextField(blank=True)
    samp_name = models.TextField(blank=True)
    samp_name_alias = models.TextField(blank=True)
    material_provider = models.ForeignKey(Attribute, null=True,  blank=True, related_name='sample_material_provider',
                                          limit_choices_to={'category': 'sample', 'attribute': 'material_provider'})
    material_internal_external = models.ForeignKey(Attribute, null=True,  blank=True, related_name='sample_material_internal_external',
                                                   limit_choices_to={'category': 'sample', 'attribute': 'material_internal_external'})
    material_type = models.ForeignKey(Attribute, null=True,  blank=True, related_name='sample_material_type',
                                      limit_choices_to={'category': 'sample', 'attribute': 'sample_material_type'})
    surface_sampling_location = models.ForeignKey(Attribute, null=True,  blank=True,
                                                  related_name='sample_surface_sampling_location',
                                                  limit_choices_to={'category': 'sample',
                                                                    'attribute': 'surface_sampling_location'})
    well_type_classification = models.ForeignKey(Attribute, null=True,  blank=True,
                                                 related_name='sample_well_type_classification',
                                                 limit_choices_to={'category': 'sample',
                                                                   'attribute': 'well_type_classification'})
    environment = models.ForeignKey('Environment',  blank=True, null=True)

    class Meta:
        db_table = 'sample'
        ordering = ['id']

    def __unicode__(self):
        return "Id: %s Name: %s" % (self.id, self.source_mat_id,)


class Environment(models.Model):
    id = models.AutoField(primary_key=True)
    collection_date = models.DateTimeField(blank=True, null=True)
    latitude = models.FloatField(blank=True, default=0.0)
    longitude = models.FloatField(blank=True, default=0.0)
    # country_iso = models.CharField(max_length=2, blank=True)
    country = models.ForeignKey(Country,  blank=True, null=True)
    region = models.CharField(max_length=255, blank=True)
    alt_elev = models.FloatField(blank=True,default=0.0)
    depth = models.FloatField(blank=True,default=0.0)
    env_biome = models.ForeignKey(Attribute, null=True, blank=True,
                                  related_name='environment_env_biome',
                                  limit_choices_to={'category': 'environment',
                                                    'attribute': 'env_biome'})
    env_feature = models.ForeignKey(Attribute, null=True, blank=True,
                                    related_name='environment_env_feature',
                                    limit_choices_to={'category': 'environment',
                                                      'attribute': 'env_feature'})
    env_material = models.ForeignKey(Attribute, null=True, blank=True,
                                     related_name='environment_env_material',
                                     limit_choices_to={'category': 'environment',
                                                       'attribute': 'env_material'})

    class Meta:
        db_table = 'environment'
        verbose_name_plural = 'environments'

    def __unicode__(self):
        return "%s %s" % (self.country.iso, self.region)


class WaterChemistry(models.Model):
    id = models.AutoField(primary_key=True)
    ph = models.FloatField(blank=True,default=0.0)
    samp_salinity = models.FloatField(blank=True,default=0.0)
    alkalinity = models.FloatField(blank=True,default=0.0)
    sulfate = models.FloatField(blank=True,default=0.0)
    sulfide = models.FloatField(blank=True,default=0.0)
    tot_sulfur = models.FloatField(blank=True,default=0.0)
    nitrate = models.FloatField(blank=True,default=0.0)
    nitrite = models.FloatField(blank=True,default=0.0)
    ammonium = models.FloatField(blank=True,default=0.0)
    tot_nitro = models.FloatField(blank=True,default=0.0)
    diss_iron = models.FloatField(blank=True,default=0.0)
    sodium = models.FloatField(blank=True,default=0.0)
    potassium = models.FloatField(blank=True,default=0.0)
    magnesium = models.FloatField(blank=True,default=0.0)
    calcium = models.FloatField(blank=True,default=0.0)
    tot_iron = models.FloatField(blank=True,default=0.0)
    diss_org_carb = models.FloatField(blank=True,default=0.0)
    diss_inorg_carb = models.FloatField(blank=True,default=0.0)
    diss_inorg_phosp = models.FloatField(blank=True,default=0.0)
    tot_phosp = models.FloatField(blank=True,default=0.0)
    suspend_solids = models.FloatField(blank=True,default=0.0)
    density = models.FloatField(blank=True,default=0.0)
    diss_carb_dioxide = models.FloatField(blank=True,default=0.0)
    diss_oxygen = models.FloatField(blank=True,default=0.0)
    vfa = models.FloatField(blank=True,default=0.0)
    benzene = models.FloatField(blank=True,default=0.0)
    toluene = models.FloatField(blank=True,default=0.0)
    ethylbenzene = models.FloatField(blank=True,default=0.0)
    xylene = models.FloatField(blank=True,default=0.0)
    sulfate_fw = models.FloatField(blank=True,default=0.0)
    vfa_fw = models.FloatField(blank=True,default=0.0)
    vfa_acetate = models.FloatField(blank=True,default=0.0)
    additional_carbon_source = models.FloatField(blank=True,default=0.0)
    aluminum = models.FloatField(blank=True,default=0.0)
    barium = models.FloatField(blank=True,default=0.0)
    bicarbonate = models.FloatField(blank=True,default=0.0)
    boron = models.FloatField(blank=True,default=0.0)
    bromide = models.FloatField(blank=True,default=0.0)
    vfa_butyrate = models.FloatField(blank=True,default=0.0)
    carbonate = models.FloatField(blank=True,default=0.0)
    chloride = models.FloatField(blank=True,default=0.0)
    cobalt = models.FloatField(blank=True,default=0.0)
    conductivity = models.FloatField(blank=True,default=0.0)
    fluorine  = models.FloatField(blank=True,default=0.0)
    vfa_formate = models.FloatField(blank=True,default=0.0)
    h2po4 = models.FloatField(blank=True,default=0.0)
    hydroxide = models.FloatField(blank=True,default=0.0)
    lithium = models.FloatField(blank=True,default=0.0)
    manganese = models.FloatField(blank=True,default=0.0)
    molybdenum = models.FloatField(blank=True,default=0.0)
    napthenic_acids = models.FloatField(blank=True,default=0.0)
    nickel = models.FloatField(blank=True,default=0.0)
    vfa_proprionate = models.FloatField(blank=True,default=0.0)
    resistivity = models.FloatField(blank=True,default=0.0)
    silicon = models.FloatField(blank=True,default=0.0)
    sg_aqueous_phase = models.FloatField(blank=True,default=0.0)
    strontium = models.FloatField(blank=True,default=0.0)
    thiosulfate = models.FloatField(blank=True,default=0.0)
    wc_analysis_date = models.DateTimeField(blank=True, null=True)
    wc_comment = models.TextField(blank=True)
    wc_reference = models.TextField(blank=True)

    sample = models.ForeignKey('Sample',  blank=True, unique=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'water_chemistry'
        ordering = ['id']
        verbose_name_plural = "water chemistries"

    def __unicode__(self):
        return "Sample: %s" % self.sample
