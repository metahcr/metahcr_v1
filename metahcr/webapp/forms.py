# -*- coding: latin-1 -*-
__author__ = 'pcmarks'

"""
Copyright (C) 2018 Shell Global Solutions International B.V.

These functions supply values for the drop-down menus in the search pages. They can be generated from the Django
application/model information.

Type:
    CV = Controlled Vocabulary (Attribute)
    N  = Numeric
    R  = Relation - follow the field value to its table entry value
    T  = Text

The type will affect what operators are made available for the search fields.


"""
from django import forms
from django.contrib import admin

from webapp.models import Investigation, Sample, SingleGeneAnalysis, MetagenomeAnalysis
from webapp.models import WaterChemistry, ProductionDataAtTimeOfSampling, Environment, HydrocarbonChemistry
from webapp.models import HydrocarbonResource, Mineralogy, CuratorDetails, Organism


class InvestigationForm(forms.ModelForm):
    class Meta:
        model = Investigation
        fields = '__all__'

class CuratorDetailsForm(forms.ModelForm):
    class Meta:
        model = CuratorDetails
        fields = '__all__'

class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = '__all__'

class WaterChemistryForm(forms.ModelForm):
    class Meta:
        model = WaterChemistry
        fields = '__all__'

class ProductionDataForm(forms.ModelForm):
    class Meta:
        model = ProductionDataAtTimeOfSampling
        fields = '__all__'

class EnvironmentDataForm(forms.ModelForm):
    class Meta:
        model = Environment
        fields = '__all__'

class HydrocarbonChemistryForm(forms.ModelForm):
    class Meta:
        model = HydrocarbonChemistry
        fields = '__all__'

class HydrocarbonResourceForm(forms.ModelForm):
    class Meta:
        model = HydrocarbonResource
        fields = '__all__'

class MineralogyForm(forms.ModelForm):
    class Meta:
        model = Mineralogy
        fields = '__all__'

class SingleGeneAnalysisForm(forms.ModelForm):
    class Meta:
        model = SingleGeneAnalysis
        fields = '__all__'

class MetagenomeAnalysisForm(forms.ModelForm):
    class Meta:
        model = MetagenomeAnalysis
        fields = '__all__'

class OrganismForm(forms.ModelForm):
    class Meta:
        model = Organism
        fields = '__all__'


def build_metabolism_type_fields():
    tmp_array = []
    tmp_array.append({'category': 'metabolism_type',
                      'attribute': 'type',
                      'name': 'Type',
                      'type': 'R',                  # Relation
                      'unit': ''})
    return {"fields": tmp_array}

def build_country_fields():
    tmp_array = []
    tmp_array.append({'category': 'country',
                      'attribute': 'printable_name',
                      'name': 'Name',
                      'type': 'R',
                      'unit': ''})

    return {"fields": tmp_array}

def build_hydrocarbon_resource_fields():
    tmp_array = []

    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'basin',
                      'name': 'Basin',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'comment',
                      'name': 'Comment',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'depos_env',
                      'name': 'Depos Env',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'drive_mech',
                      'name': 'Drive Mech',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'field',
                      'name': 'Field',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'formation',
                      'name': 'Formation',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'hc_produced',
                      'name': 'Hc Produced',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'hcr',
                      'name': 'Hcr',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'hcr_abbrev',
                      'name': 'Hcr Abbrev',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'hcr_fw_salinity',
                      'name': 'Hcr Fw Salinity',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'hcr_geol_age',
                      'name': 'Hcr Geol Age',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'hcr_hc_satur_pc',
                      'name': 'Hcr Hc Satur Pc',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'hcr_pressure',
                      'name': 'Hcr Pressure',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'hcr_temp_hi',
                      'name': 'Hcr Temp Hi',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'hcr_temp_lo',
                      'name': 'Hcr Temp Lo',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'lithology',
                      'name': 'Lithology',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'owc_tvdss',
                      'name': 'Owc Tvdss',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'permeability',
                      'name': 'Permeability',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'porosity',
                      'name': 'Porosity',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'reference',
                      'name': 'Reference',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'reservoir',
                      'name': 'Reservoir',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'salinity_today',
                      'name': 'Salinity Today',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'sr_dep_env',
                      'name': 'Sr Dep Env',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'sr_geol_age',
                      'name': 'Sr Geol Age',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'sr_kerog_type',
                      'name': 'Sr Kerog Type',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'sr_lithology',
                      'name': 'Sr Lithology',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'tvdss_of_hcr_pressure',
                      'name': 'Tvdss Of Hcr Pressure',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'tvdss_of_hcr_temp',
                      'name': 'Tvdss Of Hcr Temp',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_resource',
                      'attribute': 'unique_resource_name',
                      'name': 'Unique Resource Name',
                      'type': 'T',
                      'unit': ''})


    return {'fields': tmp_array}

def build_production_data_at_time_of_sampling_fields():
    tmp_array = []

    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'add_recov_method',
                      'name': 'Add Recov Method',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'biocide',
                      'name': 'Biocide',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'biocide_admin_method',
                      'name': 'Biocide Admin Method',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'chem_treatment',
                      'name': 'Chem Treatment',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'chem_treatment_method',
                      'name': 'Chem Treatment Method',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'comment',
                      'name': 'Comment',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'gas_oil_ratio',
                      'name': 'Gas Oil Ratio',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'gas_rate',
                      'name': 'Gas Rate',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'iwf',
                      'name': 'Iwf',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'oil_rate',
                      'name': 'Oil Rate',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'operator',
                      'name': 'Operator',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'prod_conn_to_injctr',
                      'name': 'Prod Conn To Injctr',
                      'type': 'B',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'prod_rate',
                      'name': 'Prod Rate',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'pw_per_day',
                      'name': 'Pw Per Day',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'reference',
                      'name': 'Reference',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'pd_salinity',
                      'name': 'Salinity',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'samp_loc_corr_rate',
                      'name': 'Samp Loc Corr Rate',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'water_cut',
                      'name': 'Water Cut',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'production_data_at_time_of_sampling',
                      'attribute': 'water_production_rate',
                      'name': 'Water Production Rate',
                      'type': 'N',
                      'unit': ''})

    return {'fields': tmp_array}

def build_environment_fields():
    tmp_array = []

    tmp_array.append({'category': 'environment',
                      'attribute': 'alt_elev',
                      'name': 'Alt Elev',
                      'type': 'N',
                      'unit': ''})

    tmp_array.append({'category': 'environment__country',   # We need the 'country' table name to follow the link
                      'attribute': 'printable_name',
                      'name': 'Country Name',
                      'type': 'R',
                      'unit': ''})

    tmp_array.append({'category': 'environment',
                      'attribute': 'depth',
                      'name': 'Depth',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'environment',
                      'attribute': 'env_biome',
                      'name': 'Env Biome',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'environment',
                      'attribute': 'env_feature',
                      'name': 'Env Feature',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'environment',
                      'attribute': 'env_material',
                      'name': 'Env Material',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'environment',
                      'attribute': 'latitude',
                      'name': 'Latitude',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'environment',
                      'attribute': 'longitude',
                      'name': 'Longitude',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'environment',
                      'attribute': 'region',
                      'name': 'Region',
                      'type': 'T',
                      'unit': ''})

    return {'fields': tmp_array}

def build_hydrocarbon_chemistry_fields():
    tmp_array = []
    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'api',
                      'name': 'Api',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'aromatics_pc',
                      'name': 'Aromatics Pc',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'asphaltenes_pc',
                      'name': 'Asphaltenes Pc',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'c12_c19',
                      'name': 'C12 C19',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'c2_c6',
                      'name': 'C2 C6',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'c20_c35',
                      'name': 'C20 C35',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'c36plus',
                      'name': 'C36Plus',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'c7_c11',
                      'name': 'C7 C11',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'hc_comment',
                      'name': 'Hc Comment',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'hc_reference',
                      'name': 'Hc Reference',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'mah_pc',
                      'name': 'Mah Pc',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'methane_pc',
                      'name': 'Methane Pc',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'naph_pc',
                      'name': 'Naph Pc',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'olef_pc',
                      'name': 'Olef Pc',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'pah_pc',
                      'name': 'Pah Pc',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'paraf_pc',
                      'name': 'Paraf Pc',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'polysufides_pc',
                      'name': 'Polysufides Pc',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'resins_pc',
                      'name': 'Resins Pc',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'saturates_pc',
                      'name': 'Saturates Pc',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'sg_oil_phase',
                      'name': 'Sg Oil Phase',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'tan',
                      'name': 'Tan',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'viscosity',
                      'name': 'Viscosity',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'hydrocarbon_chemistry',
                      'attribute': 'wax_pc',
                      'name': 'Wax Pc',
                      'type': 'N',
                      'unit': ''})


    return {'fields': tmp_array}

def build_water_chemistry_fields():
    tmp_array = []

    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'additional_carbon_source',
                      'name': 'Additional Carbon Source',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'alkalinity',
                      'name': 'Alkalinity',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'aluminum',
                      'name': 'Aluminum',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'ammonium',
                      'name': 'Ammonium',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'barium',
                      'name': 'Barium',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'benzene',
                      'name': 'Benzene',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'bicarbonate',
                      'name': 'Bicarbonate',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'boron',
                      'name': 'Boron',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'bromide',
                      'name': 'Bromide',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'calcium',
                      'name': 'Calcium',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'carbonate',
                      'name': 'Carbonate',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'chloride',
                      'name': 'Chloride',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'cobalt',
                      'name': 'Cobalt',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'conductivity',
                      'name': 'Conductivity',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'density',
                      'name': 'Density',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'diss_carb_dioxide',
                      'name': 'Diss Carb Dioxide',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'diss_inorg_carb',
                      'name': 'Diss Inorg Carb',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'diss_inorg_phosp',
                      'name': 'Diss Inorg Phosp',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'diss_iron',
                      'name': 'Diss Iron',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'diss_org_carb',
                      'name': 'Diss Org Carb',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'diss_oxygen',
                      'name': 'Diss Oxygen',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'ethylbenzene',
                      'name': 'Ethylbenzene',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'fluorine',
                      'name': 'Fluorine',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'h2po4',
                      'name': 'H2Po4',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'hydroxide',
                      'name': 'Hydroxide',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'lithium',
                      'name': 'Lithium',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'magnesium',
                      'name': 'Magnesium',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'manganese',
                      'name': 'Manganese',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'molybdenum',
                      'name': 'Molybdenum',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'napthenic_acids',
                      'name': 'Napthenic Acids',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'nickel',
                      'name': 'Nickel',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'nitrate',
                      'name': 'Nitrate',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'nitrite',
                      'name': 'Nitrite',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'ph',
                      'name': 'Ph',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'potassium',
                      'name': 'Potassium',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'resistivity',
                      'name': 'Resistivity',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'samp_salinity',
                      'name': 'Samp Salinity',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'sg_aqueous_phase',
                      'name': 'Sg Aqueous Phase',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'silicon',
                      'name': 'Silicon',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'sodium',
                      'name': 'Sodium',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'strontium',
                      'name': 'Strontium',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'sulfate',
                      'name': 'Sulfate',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'sulfate_fw',
                      'name': 'Sulfate Fw',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'sulfide',
                      'name': 'Sulfide',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'suspend_solids',
                      'name': 'Suspend Solids',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'thiosulfate',
                      'name': 'Thiosulfate',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'toluene',
                      'name': 'Toluene',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'tot_iron',
                      'name': 'Tot Iron',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'tot_nitro',
                      'name': 'Tot Nitro',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'tot_phosp',
                      'name': 'Tot Phosp',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'tot_sulfur',
                      'name': 'Tot Sulfur',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'vfa',
                      'name': 'Vfa',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'vfa_acetate',
                      'name': 'Vfa Acetate',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'vfa_butyrate',
                      'name': 'Vfa Butyrate',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'vfa_formate',
                      'name': 'Vfa Formate',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'vfa_fw',
                      'name': 'Vfa Fw',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'vfa_proprionate',
                      'name': 'Vfa Proprionate',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'wc_comment',
                      'name': 'Wc Comment',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'wc_reference',
                      'name': 'Wc Reference',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'water_chemistry',
                      'attribute': 'xylene',
                      'name': 'Xylene',
                      'type': 'N',
                      'unit': ''})

    return {'fields': tmp_array}

def build_investigation_search_fields():
    tmp_array = []

    tmp_array.append({'category': 'investigation',
                      'attribute': 'availability',
                      'name': 'Availability',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'investigation',
                      'attribute': 'contact_id',
                      'name': 'Contact Id',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'investigation',
                      'attribute': 'env_package',
                      'name': 'Env Package',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'investigation',
                      'attribute': 'experimental_factor',
                      'name': 'Experimental Factor',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'investigation',
                      'attribute': 'gold_project_id',
                      'name': 'Gold Project Id',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'investigation',
                      'attribute': 'investigation_comment',
                      'name': 'Investigation Comment',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'investigation',
                      'attribute': 'investigation_description',
                      'name': 'Investigation Description',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'investigation',
                      'attribute': 'investigation_publication',
                      'name': 'Investigation Publication',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'investigation',
                      'attribute': 'investigation_reference',
                      'name': 'Investigation Reference',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'investigation',
                      'attribute': 'investigation_status',
                      'name': 'Investigation Status',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'investigation',
                      'attribute': 'investigation_type',
                      'name': 'Investigation Type',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'investigation',
                      'attribute': 'keywords',
                      'name': 'Keywords',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'investigation',
                      'attribute': 'ncbi_project_id',
                      'name': 'Ncbi Project Id',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'investigation',
                      'attribute': 'project_name',
                      'name': 'Project Name',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'investigation',
                      'attribute': 'purpose',
                      'name': 'Purpose',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'investigation',
                      'attribute': 'investigation_quality',
                      'name': 'Quality',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'investigation',
                      'attribute': 'submitted_to_insdc',
                      'name': 'Submitted To Insdc',
                      'type': 'B',
                      'unit': ''})
    return {'fields': tmp_array}


def build_sample_search_fields():
    tmp_array = []

    tmp_array.append({'category': 'sample',
                      'attribute': 'additional_info',
                      'name': 'Additional Info',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'elev',
                      'name': 'Elev',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'material_internal_external',
                      'name': 'Material Internal External',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'material_provider',
                      'name': 'Material Provider',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'sample_material_type',
                      'name': 'Material Type',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'misc_param',
                      'name': 'Misc Param',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'organism_count',
                      'name': 'Organism Count',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'organism_count_qpcr_info',
                      'name': 'Organism Count Qpcr Info',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'oxy_stat_sample',
                      'name': 'Oxy Stat Sample',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'pressure',
                      'name': 'Pressure',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'rc_distance_from_hc_water_contact',
                      'name': 'Rc Distance From Hc Water Contact',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_comment',
                      'name': 'Samp Comment',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_description',
                      'name': 'Samp Description',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_location_comment',
                      'name': 'Samp Location Comment',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_location_point',
                      'name': 'Samp Location Point',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_location_reference',
                      'name': 'Samp Location Reference',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_location_reservoir_name',
                      'name': 'Samp Location Reservoir Name',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_md',
                      'name': 'Samp Md',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_name',
                      'name': 'Samp Name',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_name_alias',
                      'name': 'Samp Name Alias',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_preserv',
                      'name': 'Samp Preserv',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_store_dur',
                      'name': 'Samp Store Dur',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_store_loc',
                      'name': 'Samp Store Loc',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_store_temp',
                      'name': 'Samp Store Temp',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_subtype',
                      'name': 'Samp Subtype',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_transport_cond_duration',
                      'name': 'Samp Transport Cond Duration',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_transport_cond_temp',
                      'name': 'Samp Transport Cond Temp',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_tvdss',
                      'name': 'Samp Tvdss',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_type',
                      'name': 'Samp Type',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_vwa_dna_extr',
                      'name': 'Samp Vwa Dna Extr',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'samp_well_name',
                      'name': 'Samp Well Name',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'source_mat_id',
                      'name': 'Source Mat Id',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'surface_sampling_location',
                      'name': 'Surface Sampling Location',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'temp',
                      'name': 'Temp',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'well_type_classification',
                      'name': 'Well Type Classification',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'sample',
                      'attribute': 'win',
                      'name': 'Win',
                      'type': 'T',
                      'unit': ''})

    return {'fields': tmp_array}


def build_organism_search_fields():
    tmp_array = []
    tmp_array.append({'category': 'organism',
                      'attribute': 'a_16s_sequence',
                      'name': 'A 16S Sequence',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'accession_no_cultured',
                      'name': 'Accession No Cultured',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'accession_no_uncultured',
                      'name': 'Accession No Uncultured',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'bio_class',
                      'name': 'Bio Class',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'bio_order',
                      'name': 'Bio Order',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'biotic_relationship',
                      'name': 'Biotic Relationship',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'cell_arrangement',
                      'name': 'Cell Arrangement',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'cell_diameter',
                      'name': 'Cell Diameter',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'cell_length',
                      'name': 'Cell Length',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'cell_shape',
                      'name': 'Cell Shape',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'clone',
                      'name': 'Clone',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'closest_cultured_relative',
                      'name': 'Closest Cultured Relative',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'closest_relative',
                      'name': 'Closest Relative',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'colour',
                      'name': 'Colour',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'comment',
                      'name': 'Comment',
                      'type': 'T',
                      'unit': ''})

    tmp_array.append({'category': 'organism',
                      'attribute': 'contaminant',
                      'name': 'Contaminant',
                      'type': 'CV',
                      'unit': ''})

    tmp_array.append({'category': 'organism',
                      'attribute': 'culture_collection_id',
                      'name': 'Culture Collection Id',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'data_source',
                      'name': 'Data Source',
                      'type': 'CV',
                      'unit': ''})

    tmp_array.append({'category': 'organism',
                      'attribute': 'description',
                      'name': 'Description',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'disease',
                      'name': 'Disease',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'ecosystem',
                      'name': 'Ecosystem',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'ecosystem_category',
                      'name': 'Ecosystem Category',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'ecosystem_subtype',
                      'name': 'Ecosystem Subtype',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'ecosystem_type',
                      'name': 'Ecosystem Type',
                      'type': 'CV',
                      'unit': ''})

    tmp_array.append({'category': 'organism',
                      'attribute': 'energy_source',
                      'name': 'Energy Source',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'family',
                      'name': 'Family',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'genus',
                      'name': 'Genus',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'genus_synonyms',
                      'name': 'Genus Synonyms',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'gold_project_id',
                      'name': 'Gold Project Id',
                      'type': 'N',
                      'unit': ''})

    tmp_array.append({'category': 'organism',
                      'attribute': 'gram_staining',
                      'name': 'Gram Staining',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'grow_postgate',
                      'name': 'Grow Postgate',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism__habitat',   # We need the 'habitat' table name to follow the link
                      'attribute': 'habitat',
                      'name': 'Habitat',
                      'type': 'R',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'max_salinity_tds',
                      'name': 'Max Salinity Tds',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'metabolism',
                      'name': 'Metabolism',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'min_salinity_tds',
                      'name': 'Min Salinity Tds',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'motility',
                      'name': 'Motility',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'ncbi_ref_seq',
                      'name': 'Ncbi Ref Seq',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'ncbi_taxon_id',
                      'name': 'Ncbi Taxon Id',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'opt_salinity_tds',
                      'name': 'Opt Salinity Tds',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'oxygen_requirement',
                      'name': 'Oxygen Requirement',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'ph_max',
                      'name': 'Ph Max',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'ph_min',
                      'name': 'Ph Min',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'ph_opt',
                      'name': 'Ph Opt',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'phenotype',
                      'name': 'Phenotype',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'phylum',
                      'name': 'Phylum',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'reference',
                      'name': 'Reference',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'relative_abundance',
                      'name': 'Relative Abundance',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'risk',
                      'name': 'Risk',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'salinity',
                      'name': 'Salinity',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'similarity',
                      'name': 'Similarity',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'similarity_clos_cul',
                      'name': 'Similarity Clos Cul',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'species',
                      'name': 'Species',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'species_synonyms',
                      'name': 'Species Synonyms',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'specific_ecosystem',
                      'name': 'Specific Ecosystem',
                      'type': 'CV',
                      'unit': ''})

    tmp_array.append({'category': 'organism',
                      'attribute': 'sporulation',
                      'name': 'Sporulation',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'ss_rdb_id',
                      'name': 'Ss Rdb Id',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'strain',
                      'name': 'Strain',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'subphylum',
                      'name': 'Subphylum',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'superkingdom',
                      'name': 'Superkingdom',
                      'type': 'T',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'temperature_max',
                      'name': 'Temperature Max',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'temperature_min',
                      'name': 'Temperature Min',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'temperature_opt_c',
                      'name': 'Temperature Opt C',
                      'type': 'N',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'temperature_range',
                      'name': 'Temperature Range',
                      'type': 'CV',
                      'unit': ''})


    tmp_array.append({'category': 'organism',
                      'attribute': 'true_tds_or_tds_equiv',
                      'name': 'True Tds Or Tds Equiv',
                      'type': 'N',
                      'unit': ''})


    return {'fields': tmp_array}

