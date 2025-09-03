"""
This module contains a list of all the available system tags, separated by the context in which they can be used.
Some functions in the SDK might require you to pass one or more tag IDs as arguments, for any system level tag you can simply use one of the entries
from this file like so:
```python
from enpi_api.l2.tags import CollectionTags
id_of_system_tag_called_name = CollectionTags.Name
```
The available contexts are:
- [Collection](#CollectionTags)
- [Clone](#CloneTags)
- [Sequence](#SequenceTags)
- [CloneContextual](#CloneContextualTags)
- [File](#FileTags)
"""
from enpi_api.l2.types.tag import TagId


class CollectionTags:
    pass
    Age = TagId(2001)
    """
    **Display name**: Age

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    AlignmentStringency = TagId(2002)
    """
    **Display name**: Alignment Stringency

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    AnalysisType = TagId(2003)
    """
    **Display name**: Analysis Type

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    AppCodename = TagId(2004)
    """
    **Display name**: App Codename

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    AppVersion = TagId(2005)
    """
    **Display name**: App Version

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    CampaignId = TagId(2080)
    """
    **Display name**: Campaign ID

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    Chemistry = TagId(2006)
    """
    **Display name**: Chemistry

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Complexity = TagId(2083)
    """
    **Display name**: Complexity

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    DataSpace = TagId(2009)
    """
    **Display name**: Data Space

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    DatabaseName = TagId(2008)
    """
    **Display name**: Database Name

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    DateImported = TagId(2010)
    """
    **Display name**: Date Imported

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Diagnosis = TagId(2011)
    """
    **Display name**: Diagnosis

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    EarlyAccess = TagId(2012)
    """
    **Display name**: Early Access

    **Data type**: `enpi_api.l2.types.tag.TagDataType.BOOLEAN`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    EstimatedNumberOfCells = TagId(2013)
    """
    **Display name**: Estimated Number of Cells

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Ethnicity = TagId(2014)
    """
    **Display name**: Ethnicity

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    FastaHeader = TagId(2016)
    """
    **Display name**: FASTA Header

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    FamilyId = TagId(2015)
    """
    **Display name**: Family Id

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    FileFormat = TagId(2017)
    """
    **Display name**: File Format

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    FractionReadsInCells = TagId(2019)
    """
    **Display name**: Fraction Reads in Cells

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    InputFilename1 = TagId(2022)
    """
    **Display name**: Input Filename 1

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    InputFilename2 = TagId(2023)
    """
    **Display name**: Input Filename 2

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Intervention = TagId(2024)
    """
    **Display name**: Intervention

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    MeanReadPairsPerCell = TagId(2028)
    """
    **Display name**: Mean Read Pairs per Cell

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    MeanUsedReadPairsPerCell = TagId(2029)
    """
    **Display name**: Mean Used Read Pairs per Cell

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    MedianIghUmIsPerCell = TagId(2030)
    """
    **Display name**: Median IGH UMIs per Cell

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    MedianIgkUmIsPerCell = TagId(2031)
    """
    **Display name**: Median IGK UMIs per Cell

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    MedianIglUmIsPerCell = TagId(2032)
    """
    **Display name**: Median IGL UMIs per Cell

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    MedianTraUmIsPerCell = TagId(2033)
    """
    **Display name**: Median TRA UMIs per Cell

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    MedianTrbUmIsPerCell = TagId(2034)
    """
    **Display name**: Median TRB UMIs per Cell

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Name = TagId(2035)
    """
    **Display name**: Name

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE_NON_DELETABLE`
    """
    NumberOfClones = TagId(2036)
    """
    **Display name**: Number Of Clones

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    NumberOfReadPairs = TagId(2037)
    """
    **Display name**: Number of Read Pairs

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    NumberOfShortReadsSkipped = TagId(2038)
    """
    **Display name**: Number of Short Reads Skipped

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Organism = TagId(2040)
    """
    **Display name**: Organism

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    PipelineVersion = TagId(2041)
    """
    **Display name**: Pipeline Version

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    PlateId = TagId(2082)
    """
    **Display name**: Plate ID

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    ProjectId = TagId(2081)
    """
    **Display name**: Project ID

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    Protocol = TagId(2044)
    """
    **Display name**: Protocol

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    Q30BasesInBarcode = TagId(2045)
    """
    **Display name**: Q30 Bases in Barcode

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Q30BasesInRnaRead1 = TagId(2046)
    """
    **Display name**: Q30 Bases in RNA Read 1

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Q30BasesInRnaRead2 = TagId(2047)
    """
    **Display name**: Q30 Bases in RNA Read 2

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Q30BasesInUmi = TagId(2048)
    """
    **Display name**: Q30 Bases in UMI

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    QualityFilter = TagId(2049)
    """
    **Display name**: Quality Filter

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Race = TagId(2050)
    """
    **Display name**: Race

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    ReadsMappedToAnyVDJGene = TagId(2053)
    """
    **Display name**: Reads Mapped to Any V(D)J Gene

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ReadsMappedToIgh = TagId(2054)
    """
    **Display name**: Reads Mapped to IGH

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ReadsMappedToIgk = TagId(2055)
    """
    **Display name**: Reads Mapped to IGK

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ReadsMappedToIgl = TagId(2056)
    """
    **Display name**: Reads Mapped to IGL

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ReadsMappedToTra = TagId(2057)
    """
    **Display name**: Reads Mapped to TRA

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ReadsMappedToTrb = TagId(2058)
    """
    **Display name**: Reads Mapped to TRB

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Receptor = TagId(2084)
    """
    **Display name**: Receptor

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Reference = TagId(2060)
    """
    **Display name**: Reference

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    RegionOfInterest = TagId(2062)
    """
    **Display name**: Region of Interest

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    SampleDescription = TagId(2065)
    """
    **Display name**: Sample Description

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    SampleId = TagId(2066)
    """
    **Display name**: Sample ID

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    SequenceStructure = TagId(2068)
    """
    **Display name**: Sequence Structure

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    SequencingPlatform = TagId(2069)
    """
    **Display name**: Sequencing Platform

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    Sex = TagId(2070)
    """
    **Display name**: Sex

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    Software = TagId(2072)
    """
    **Display name**: Software

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    StudyId = TagId(2073)
    """
    **Display name**: Study Id

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    SubjectId = TagId(2074)
    """
    **Display name**: Subject Id

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    Tissue = TagId(2076)
    """
    **Display name**: Tissue

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    VDJReference = TagId(2079)
    """
    **Display name**: V(D)J Reference

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ValidBarcodes = TagId(2078)
    """
    **Display name**: Valid Barcodes

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """


class CloneTags:
    pass
    TenXBarcode = TagId(1001)
    """
    **Display name**: 10X Barcode

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    Affinity = TagId(1002)
    """
    **Display name**: Affinity

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    AnimalIdString = TagId(1003)
    """
    **Display name**: Animal ID String

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    AsnDeamidationCount = TagId(1009)
    """
    **Display name**: Asn Deamidation Count

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    AsnDeamidationScore = TagId(1010)
    """
    **Display name**: Asn Deamidation Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    AspIsomerisationCount = TagId(1011)
    """
    **Display name**: Asp isomerisation Count

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    AspIsomerisationScore = TagId(1012)
    """
    **Display name**: Asp isomerisation Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    BarcodeAminoAcids = TagId(1014)
    """
    **Display name**: Barcode Amino Acids

    **Data type**: `enpi_api.l2.types.tag.TagDataType.AMINO_ACID_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    BarcodeAminoAcidsLength = TagId(1015)
    """
    **Display name**: Barcode Amino Acids Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    BarcodeAverageQuality = TagId(1016)
    """
    **Display name**: Barcode Average Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    BarcodeNucleotides = TagId(1017)
    """
    **Display name**: Barcode Nucleotides

    **Data type**: `enpi_api.l2.types.tag.TagDataType.NUCLEOTIDE_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    BarcodeNucleotidesLength = TagId(1018)
    """
    **Display name**: Barcode Nucleotides Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    BarcodeQuality = TagId(1019)
    """
    **Display name**: Barcode Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.QUALITY_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cd11CCd18BindingCount = TagId(1020)
    """
    **Display name**: CD11c/CD18 Binding Count

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cd11CCd18BindingScore = TagId(1021)
    """
    **Display name**: CD11c/CD18 Binding Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    CloneCount = TagId(1077)
    """
    **Display name**: Clone Count

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    CloneIdString = TagId(1022)
    """
    **Display name**: Clone Id String

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    CloneQualityString = TagId(1023)
    """
    **Display name**: Clone Quality String

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ClonotypeId = TagId(1024)
    """
    **Display name**: Clonotype Id

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    FragmentationCount = TagId(1027)
    """
    **Display name**: Fragmentation Count

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    FragmentationScore = TagId(1028)
    """
    **Display name**: Fragmentation Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    IntegrinBindingCount = TagId(1030)
    """
    **Display name**: Integrin Binding Count

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    IntegrinBindingScore = TagId(1031)
    """
    **Display name**: Integrin Binding Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Isotype = TagId(1032)
    """
    **Display name**: Isotype

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    LysineGlycationCount = TagId(1033)
    """
    **Display name**: Lysine Glycation Count

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    LysineGlycationScore = TagId(1034)
    """
    **Display name**: Lysine Glycation Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    MetOxidationCount = TagId(1053)
    """
    **Display name**: Met Oxidation Count

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    MetOxidationScore = TagId(1054)
    """
    **Display name**: Met Oxidation Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    NLinkedGlycosylationCount = TagId(1057)
    """
    **Display name**: N-linked Glycosylation Count

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    NLinkedGlycosylationScore = TagId(1058)
    """
    **Display name**: N-linked Glycosylation Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    NTerminalGlutamateCount = TagId(1059)
    """
    **Display name**: N-terminal Glutamate Count

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    NTerminalGlutamateScore = TagId(1060)
    """
    **Display name**: N-terminal Glutamate Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    SequenceLiabilityCount = TagId(1064)
    """
    **Display name**: Sequence Liability Count

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    SequenceLiabilityScore = TagId(1065)
    """
    **Display name**: Sequence Liability Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    TapPatchesOfNegativeChargeMetricPncScore = TagId(1066)
    """
    **Display name**: TAP Patches of Negative Charge Metric (PNC) Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    TapPatchesOfPositiveChargeMetricPpcScore = TagId(1067)
    """
    **Display name**: TAP Patches of Positive Charge Metric (PPC) Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    TapPatchesOfSurfaceHydrophobicityPshScore = TagId(1068)
    """
    **Display name**: TAP Patches of Surface Hydrophobicity (PSH) Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    TapScore = TagId(1069)
    """
    **Display name**: TAP Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    TapStructuralFvChargeSymmetryParameterSFvCspScore = TagId(1070)
    """
    **Display name**: TAP Structural Fv Charge Symmetry Parameter (SFvCSP) Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    TapTotalCdrLength = TagId(1071)
    """
    **Display name**: TAP Total CDR Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    TrpOxidationCount = TagId(1072)
    """
    **Display name**: Trp Oxidation Count

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    TrpOxidationScore = TagId(1073)
    """
    **Display name**: Trp Oxidation Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    UnpairedCysCount = TagId(1074)
    """
    **Display name**: Unpaired Cys Count

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    UnpairedCysScore = TagId(1075)
    """
    **Display name**: Unpaired Cys Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """


class SequenceTags:
    pass
    CCall = TagId(2)
    """
    **Display name**: C Call

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    CCigar = TagId(3)
    """
    **Display name**: C Cigar

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    CEnd = TagId(36)
    """
    **Display name**: C End

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    CGene = TagId(37)
    """
    **Display name**: C Gene

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    CScore = TagId(46)
    """
    **Display name**: C Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    CStart = TagId(49)
    """
    **Display name**: C Start

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr1AminoAcids = TagId(4)
    """
    **Display name**: CDR1 Amino Acids

    **Data type**: `enpi_api.l2.types.tag.TagDataType.AMINO_ACID_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr1AminoAcidsLength = TagId(5)
    """
    **Display name**: CDR1 Amino Acids Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr1AverageQuality = TagId(6)
    """
    **Display name**: CDR1 Average Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr1Nucleotides = TagId(8)
    """
    **Display name**: CDR1 Nucleotides

    **Data type**: `enpi_api.l2.types.tag.TagDataType.NUCLEOTIDE_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr1NucleotidesLength = TagId(9)
    """
    **Display name**: CDR1 Nucleotides Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr1Quality = TagId(12)
    """
    **Display name**: CDR1 Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.QUALITY_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr2AminoAcids = TagId(14)
    """
    **Display name**: CDR2 Amino Acids

    **Data type**: `enpi_api.l2.types.tag.TagDataType.AMINO_ACID_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr2AminoAcidsLength = TagId(15)
    """
    **Display name**: CDR2 Amino Acids Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr2AverageQuality = TagId(16)
    """
    **Display name**: CDR2 Average Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr2Nucleotides = TagId(18)
    """
    **Display name**: CDR2 Nucleotides

    **Data type**: `enpi_api.l2.types.tag.TagDataType.NUCLEOTIDE_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr2NucleotidesLength = TagId(19)
    """
    **Display name**: CDR2 Nucleotides Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr2Quality = TagId(22)
    """
    **Display name**: CDR2 Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.QUALITY_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr3AminoAcids = TagId(24)
    """
    **Display name**: CDR3 Amino Acids

    **Data type**: `enpi_api.l2.types.tag.TagDataType.AMINO_ACID_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr3AminoAcidsLength = TagId(25)
    """
    **Display name**: CDR3 Amino Acids Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr3AverageQuality = TagId(26)
    """
    **Display name**: CDR3 Average Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr3End = TagId(27)
    """
    **Display name**: CDR3 End

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr3InFrame = TagId(28)
    """
    **Display name**: CDR3 In Frame

    **Data type**: `enpi_api.l2.types.tag.TagDataType.BOOLEAN`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr3Nucleotides = TagId(29)
    """
    **Display name**: CDR3 Nucleotides

    **Data type**: `enpi_api.l2.types.tag.TagDataType.NUCLEOTIDE_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr3NucleotidesLength = TagId(30)
    """
    **Display name**: CDR3 Nucleotides Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr3Quality = TagId(33)
    """
    **Display name**: CDR3 Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.QUALITY_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr3Start = TagId(34)
    """
    **Display name**: CDR3 Start

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Cdr3StopCodon = TagId(35)
    """
    **Display name**: CDR3 Stop Codon

    **Data type**: `enpi_api.l2.types.tag.TagDataType.BOOLEAN`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Chain = TagId(38)
    """
    **Display name**: Chain

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ChainQualityNumber = TagId(40)
    """
    **Display name**: Chain Quality Number

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ContigId = TagId(41)
    """
    **Display name**: Contig Id

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    CreatedAt = TagId(42)
    """
    **Display name**: Created At

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    CreatedBy = TagId(43)
    """
    **Display name**: Created By

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    DCall = TagId(52)
    """
    **Display name**: D Call

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    DCigar = TagId(53)
    """
    **Display name**: D Cigar

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    DEnd = TagId(54)
    """
    **Display name**: D End

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    DGene = TagId(55)
    """
    **Display name**: D Gene

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    DIdentityDecimal = TagId(177)
    """
    **Display name**: D Identity Decimal

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    DScore = TagId(59)
    """
    **Display name**: D Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    DStart = TagId(62)
    """
    **Display name**: D Start

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ErrorCorrection = TagId(63)
    """
    **Display name**: Error Correction

    **Data type**: `enpi_api.l2.types.tag.TagDataType.BOOLEAN`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr1AminoAcids = TagId(64)
    """
    **Display name**: FR1 Amino Acids

    **Data type**: `enpi_api.l2.types.tag.TagDataType.AMINO_ACID_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr1AminoAcidsLength = TagId(65)
    """
    **Display name**: FR1 Amino Acids Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr1AverageQuality = TagId(66)
    """
    **Display name**: FR1 Average Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr1Nucleotides = TagId(67)
    """
    **Display name**: FR1 Nucleotides

    **Data type**: `enpi_api.l2.types.tag.TagDataType.NUCLEOTIDE_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr1NucleotidesLength = TagId(68)
    """
    **Display name**: FR1 Nucleotides Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr1Quality = TagId(71)
    """
    **Display name**: FR1 Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.QUALITY_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr2AminoAcids = TagId(72)
    """
    **Display name**: FR2 Amino Acids

    **Data type**: `enpi_api.l2.types.tag.TagDataType.AMINO_ACID_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr2AminoAcidsLength = TagId(73)
    """
    **Display name**: FR2 Amino Acids Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr2AverageQuality = TagId(74)
    """
    **Display name**: FR2 Average Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr2Nucleotides = TagId(75)
    """
    **Display name**: FR2 Nucleotides

    **Data type**: `enpi_api.l2.types.tag.TagDataType.NUCLEOTIDE_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr2NucleotidesLength = TagId(76)
    """
    **Display name**: FR2 Nucleotides Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr2Quality = TagId(79)
    """
    **Display name**: FR2 Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.QUALITY_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr3AminoAcids = TagId(80)
    """
    **Display name**: FR3 Amino Acids

    **Data type**: `enpi_api.l2.types.tag.TagDataType.AMINO_ACID_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr3AminoAcidsLength = TagId(81)
    """
    **Display name**: FR3 Amino Acids Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr3AverageQuality = TagId(82)
    """
    **Display name**: FR3 Average Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr3Nucleotides = TagId(83)
    """
    **Display name**: FR3 Nucleotides

    **Data type**: `enpi_api.l2.types.tag.TagDataType.NUCLEOTIDE_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr3NucleotidesLength = TagId(84)
    """
    **Display name**: FR3 Nucleotides Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr3Quality = TagId(87)
    """
    **Display name**: FR3 Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.QUALITY_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr4AminoAcids = TagId(88)
    """
    **Display name**: FR4 Amino Acids

    **Data type**: `enpi_api.l2.types.tag.TagDataType.AMINO_ACID_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr4AminoAcidsLength = TagId(89)
    """
    **Display name**: FR4 Amino Acids Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr4AverageQuality = TagId(90)
    """
    **Display name**: FR4 Average Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr4Nucleotides = TagId(91)
    """
    **Display name**: FR4 Nucleotides

    **Data type**: `enpi_api.l2.types.tag.TagDataType.NUCLEOTIDE_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr4NucleotidesLength = TagId(92)
    """
    **Display name**: FR4 Nucleotides Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Fr4Quality = TagId(95)
    """
    **Display name**: FR4 Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.QUALITY_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    FullLength = TagId(96)
    """
    **Display name**: Full Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.BOOLEAN`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    FullSequenceAminoAcids = TagId(97)
    """
    **Display name**: Full Sequence Amino Acids

    **Data type**: `enpi_api.l2.types.tag.TagDataType.AMINO_ACID_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    FullSequenceAminoAcidsLength = TagId(98)
    """
    **Display name**: Full Sequence Amino Acids Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    FullSequenceAverageQuality = TagId(99)
    """
    **Display name**: Full Sequence Average Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    FullSequenceNucleotides = TagId(100)
    """
    **Display name**: Full Sequence Nucleotides

    **Data type**: `enpi_api.l2.types.tag.TagDataType.NUCLEOTIDE_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    FullSequenceNucleotidesLength = TagId(101)
    """
    **Display name**: Full Sequence Nucleotides Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    GermlineAligned = TagId(103)
    """
    **Display name**: Germline Aligned

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    HighConfidence = TagId(104)
    """
    **Display name**: High Confidence

    **Data type**: `enpi_api.l2.types.tag.TagDataType.BOOLEAN`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    InputFilename = TagId(105)
    """
    **Display name**: Input Filename

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    JCall = TagId(106)
    """
    **Display name**: J Call

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    JCigar = TagId(107)
    """
    **Display name**: J Cigar

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    JEnd = TagId(109)
    """
    **Display name**: J End

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    JGene = TagId(110)
    """
    **Display name**: J Gene

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    JGeneComplete = TagId(111)
    """
    **Display name**: J Gene Complete

    **Data type**: `enpi_api.l2.types.tag.TagDataType.BOOLEAN`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    JGeneMutations = TagId(112)
    """
    **Display name**: J Gene Mutations

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    JGeneShm = TagId(113)
    """
    **Display name**: J Gene SHM

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    JIdentityDecimal = TagId(178)
    """
    **Display name**: J Identity Decimal

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    JScore = TagId(117)
    """
    **Display name**: J Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    JStart = TagId(120)
    """
    **Display name**: J Start

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    MutatedAminoAcid = TagId(180)
    """
    **Display name**: Mutated Amino Acid

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    MutatedPosition = TagId(179)
    """
    **Display name**: Mutated Position

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    NumberOfAminoAcidMutations = TagId(181)
    """
    **Display name**: Number of Amino Acid Mutations

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Productive = TagId(128)
    """
    **Display name**: Productive

    **Data type**: `enpi_api.l2.types.tag.TagDataType.BOOLEAN`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ReadCount = TagId(129)
    """
    **Display name**: Read Count

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ReceptorAminoAcids = TagId(130)
    """
    **Display name**: Receptor Amino Acids

    **Data type**: `enpi_api.l2.types.tag.TagDataType.AMINO_ACID_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ReceptorAminoAcidsLength = TagId(131)
    """
    **Display name**: Receptor Amino Acids Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ReceptorAverageQuality = TagId(132)
    """
    **Display name**: Receptor Average Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ReceptorComplete = TagId(133)
    """
    **Display name**: Receptor Complete

    **Data type**: `enpi_api.l2.types.tag.TagDataType.BOOLEAN`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ReceptorInFrame = TagId(134)
    """
    **Display name**: Receptor In Frame

    **Data type**: `enpi_api.l2.types.tag.TagDataType.BOOLEAN`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ReceptorNucleotides = TagId(135)
    """
    **Display name**: Receptor Nucleotides

    **Data type**: `enpi_api.l2.types.tag.TagDataType.NUCLEOTIDE_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ReceptorNucleotidesLength = TagId(136)
    """
    **Display name**: Receptor Nucleotides Length

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ReceptorProductive = TagId(139)
    """
    **Display name**: Receptor Productive

    **Data type**: `enpi_api.l2.types.tag.TagDataType.BOOLEAN`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ReceptorQuality = TagId(140)
    """
    **Display name**: Receptor Quality

    **Data type**: `enpi_api.l2.types.tag.TagDataType.QUALITY_SEQUENCE`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    ReceptorStopCodon = TagId(141)
    """
    **Display name**: Receptor Stop Codon

    **Data type**: `enpi_api.l2.types.tag.TagDataType.BOOLEAN`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    SequenceAligned = TagId(143)
    """
    **Display name**: Sequence Aligned

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    SequenceCount = TagId(144)
    """
    **Display name**: Sequence Count

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    SequenceFrequency = TagId(145)
    """
    **Display name**: Sequence Frequency

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    SequenceHeader = TagId(146)
    """
    **Display name**: Sequence Header

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    SequenceIdString = TagId(147)
    """
    **Display name**: Sequence Id String

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    TaxonId = TagId(149)
    """
    **Display name**: Taxon Id

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    VJGeneMutations = TagId(160)
    """
    **Display name**: V & J Gene Mutations

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    VJGeneShm = TagId(161)
    """
    **Display name**: V & J Gene SHM

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    VCall = TagId(150)
    """
    **Display name**: V Call

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    VCigar = TagId(151)
    """
    **Display name**: V Cigar

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    VEnd = TagId(153)
    """
    **Display name**: V End

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    VGene = TagId(154)
    """
    **Display name**: V Gene

    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    VGeneComplete = TagId(155)
    """
    **Display name**: V Gene Complete

    **Data type**: `enpi_api.l2.types.tag.TagDataType.BOOLEAN`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    VGeneMutations = TagId(156)
    """
    **Display name**: V Gene Mutations

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    VGeneShm = TagId(157)
    """
    **Display name**: V Gene SHM

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    VIdentityDecimal = TagId(158)
    """
    **Display name**: V Identity Decimal

    **Data type**: `enpi_api.l2.types.tag.TagDataType.DECIMAL`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    VScore = TagId(164)
    """
    **Display name**: V Score

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    VStart = TagId(169)
    """
    **Display name**: V Start

    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """


class CloneContextualTags:
    pass


class FileTags:
    pass
    CampaignId = TagId(200009)
    """
    **Display name**: Campaign ID
    
    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    DataSpace = TagId(200005)
    """
    **Display name**: Data Space
    
    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    FilePath = TagId(200006)
    """
    **Display name**: File Path
    
    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Filename = TagId(200002)
    """
    **Display name**: Filename
    
    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Organism = TagId(200003)
    """
    **Display name**: Organism
    
    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    PlateId = TagId(200011)
    """
    **Display name**: Plate ID
    
    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    ProjectId = TagId(200010)
    """
    **Display name**: Project ID
    
    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    ReadCount = TagId(200004)
    """
    **Display name**: Read Count
    
    **Data type**: `enpi_api.l2.types.tag.TagDataType.INTEGER`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Receptor = TagId(200001)
    """
    **Display name**: Receptor
    
    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    Reference = TagId(200008)
    """
    **Display name**: Reference
    
    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
    SampleId = TagId(200012)
    """
    **Display name**: Sample ID
    
    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.MUTABLE`
    """
    Source = TagId(200007)
    """
    **Display name**: Source
    
    **Data type**: `enpi_api.l2.types.tag.TagDataType.TEXT`
    
    **Access type**: `enpi_api.l2.types.tag.TagAccessType.IMMUTABLE`
    """
