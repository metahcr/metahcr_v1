from django.contrib import admin


from django.contrib import admin
from django.forms import ModelForm, ModelChoiceField
from django import forms

import models
from django.conf import settings

"""
Copyright (C) 2018 Shell Global Solutions International B.V.

Certain Django admin facility defaults are redefined here.
"""

#### Attribute

class AttributeForm(ModelForm):
    category = forms.ChoiceField(choices=settings.CATEGORY_CHOICES)
    attribute = forms.CharField()
    class Meta:
        model = models.Attribute
        fields = "__all__"


class AttributeAdmin(admin.ModelAdmin):
    form = AttributeForm


#### Organism
class OrganismForm(ModelForm):
    class Meta:
        model = models.Organism
        exclude = ('ncbi_taxon',)


class OrganismAdmin(admin.ModelAdmin):
    form = OrganismForm


#### Metadata
# class MetadataInfoForm(ModelForm):
    # """
    # Use this ModelForm and ModelAdmin to handle the Attribute data model.
    # """
    # category = forms.ModelChoiceField(
        # queryset=models.Attribute.objects.order_by('category',
                                                   # 'attribute').distinct('category', 'attribute'))
    # attribute = forms.CharField()
    # class Meta:
        # model = models.MetadataInfo
        # fields = "__all__"


# class MetadataInfoAdmin(admin.ModelAdmin):
    # form = MetadataInfoForm



#### Mineralogy
class MineralogyInline(admin.StackedInline):
    model = models.Mineralogy


class HydrocarbonResourceAdmin(admin.ModelAdmin):
    inlines = [
        MineralogyInline
    ]


#### SingleGeneResult
# class SingleGeneResultInline(admin.TabularInline):
#     model = models.SingleGeneResult

class SingleGeneAnalysisAdmin(admin.ModelAdmin):
    model = models.SingleGeneAnalysis
    def formfield_for_foreign_field(self, db_field, request, **kwargs):
        if db_field == 'type':
            kwargs['choices'] = (('HHHIII','HHIIII'),)
            return super(SingleGeneAnalysisAdmin,self).formfield_for_foreignkey(db_field, request, **kwargs)
    # inlines = [
    #     SingleGeneResultInline
    # ]

### Investigation
# class InvestigationInLine(admin.TabularInline):
#     model = models.Investigation
#
class InvestigationAdmin(admin.ModelAdmin):
    model = models.Investigation

# inlines = [HydrocarbonResourceInLine]
# fieldsets = (
#     (None, {
#         'fields': ('curator_details', ('status', 'availability'), 'reference',
#                    'hydrocarbon_resource')
#     }),
# )

# WaterChemistry
# class WaterChemistryForm(ModelForm):
#     sample = forms.ModelChoiceField(
#         queryset=models.Sample.objects.filter(~Q(id=models.WaterChemistry.sample))
#     )
#
# class WaterChemistryAdmin(admin.ModelAdmin):
#     form = WaterChemistryForm


class WaterChemistryInline(admin.StackedInline):
    model = models.WaterChemistry

#### HydrocarbonChemistry
class HydrocarbonChemistryInline(admin.StackedInline):
    model = models.HydrocarbonChemistry

#### ProductionDataAtTimeOfSampling
class ProductionDataAtTimeOfSamplingInline(admin.StackedInline):
    model = models.ProductionDataAtTimeOfSampling

#### Samples
class SamplesInLine(admin.StackedInline):
    """
    Override the default admin pages for Investigations. Allow maintenance of Samples inline
    """
    model = models.Sample

class SampleAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [
        WaterChemistryInline,
        HydrocarbonChemistryInline,
        ProductionDataAtTimeOfSamplingInline
    ]
    save_as = True


"""
The data models that can be administered.
"""
admin.site.register(models.Attribute, AttributeAdmin)
admin.site.register(models.HydrocarbonResource)
admin.site.register(models.MetabolismType)
admin.site.register(models.CuratorDetails)
#admin.site.register(models.MetadataInfo, MetadataInfoAdmin)
admin.site.register(models.MetagenomeAnalysis)
admin.site.register(models.Organism, OrganismAdmin)
admin.site.register(models.Investigation, InvestigationAdmin)
admin.site.register(models.Sample, SampleAdmin)
admin.site.register(models.Environment)
admin.site.register(models.SingleGeneAnalysis, SingleGeneAnalysisAdmin)
admin.site.register(models.UserProfile)
admin.site.register(models.Organization)
admin.site.register(models.MetaHCRDatabase)
admin.site.register(models.Mineralogy)
admin.site.register(models.WaterChemistry)
admin.site.register(models.HydrocarbonChemistry)

