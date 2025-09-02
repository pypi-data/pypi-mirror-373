from nr_vocabularies.customfields import HintCF, NonPreferredLabelsCF, RelatedURICF

NR_VOCABULARIES_CF = [
    RelatedURICF("relatedURI"),
    HintCF("hint"),
    NonPreferredLabelsCF("nonpreferredLabels"),
]
