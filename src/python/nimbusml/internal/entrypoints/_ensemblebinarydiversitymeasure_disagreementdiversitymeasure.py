# - Generated by tools/entrypoint_compiler.py: do not edit by hand
"""
DisagreementDiversityMeasure
"""


from ..utils.entrypoints import Component


def disagreement_diversity_measure(
        **params):
    """
    **Description**
        None

    """

    entrypoint_name = 'DisagreementDiversityMeasure'
    settings = {}

    component = Component(
        name=entrypoint_name,
        settings=settings,
        kind='EnsembleBinaryDiversityMeasure')
    return component
