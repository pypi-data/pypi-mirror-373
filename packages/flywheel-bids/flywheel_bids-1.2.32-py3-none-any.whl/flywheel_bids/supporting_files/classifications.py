import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

classifications = {
    "anat": {
        "T1w": {"Measurement": "T1", "Intent": "Structural"},
        "T2w": {"Measurement": "T2", "Intent": "Structural"},
        "T1rho": {"Custom": "T1rho"},
        "T1map": {
            "Measurement": "T1",
            "Intent": "Structural",
            "Features": "Quantitative",
        },
        "T2map": {
            "Measurement": "T2",
            "Intent": "Structural",
            "Features": "Quantitative",
        },
        "T2star": {"Measurement": "T2*", "Intent": "Structural"},
        "FLAIR": {"Custom": "FLAIR"},
        "FLASH": {"Custom": "FLASH"},
        "PD": {"Measurement": "PD", "Intent": "Structural"},
        "PDmap": {"Custom": "PD-Map"},
        "PDT2": {"Measurement": ["PD", "T2"], "Intent": "Structural"},
        "inplaneT1": {
            "Measurement": "T1",
            "Intent": "Structural",
            "Features": "In-Plane",
        },
        "inplaneT2": {
            "Measurement": "T2",
            "Intent": "Structural",
            "Features": "In-Plane",
        },
        "angio": {"Custom": "Angio"},
        "defacemask": {"Custom": "Defacemask"},
        "SWImagandphase": {"Custom": "SWI"},
    },
    "func": {
        "bold": {"Intent": "Functional"},
        "events": {"Intent": "Functional"},
        "sbref": {"Intent": "Functional"},
        "stim": {"Intent": "Functional", "Custom": "Stim"},
        "physio": {"Intent": "Functional", "Custom": "Physio"},
    },
    "beh": {
        "events": {"Custom": "Behavioral"},
        "stim": {"Custom": "Stim"},
        "physio": {"Custom": "Physio"},
    },
    "dwi": {
        "dwi": {"Measurement": "Diffusion", "Intent": "Structural"},
        "sbref": {"Measurement": "Diffusion", "Intent": "Structural"},
    },
    "fmap": {
        "phasediff": {"Measurement": "B0", "Intent": "Fieldmap"},
        "magnitude1": {"Measurement": "B0", "Intent": "Fieldmap"},
        "magnitude2": {"Measurement": "B0", "Intent": "Fieldmap"},
        "phase1": {"Measurement": "B0", "Intent": "Fieldmap"},
        "phase2": {"Measurement": "B0", "Intent": "Fieldmap"},
        "magnitude": {"Measurement": "B0", "Intent": "Fieldmap"},
        "fieldmap": {"Measurement": "B0", "Intent": "Fieldmap"},
        "epi": {"Measurement": "B0", "Intent": "Fieldmap"},
        "m0scan": {"Measurement": "B0", "Intent": "Fieldmap"},
    },
    "perf": {
        "asl": {"Measurement": "Perfusion"},
        "m0scan": {"Measurement": "Perfusion", "Intent": "Fieldmap"},
        "stim": {"Measurement": "Perfusion", "Custom": "Stim"},
        "physio": {"Measurement": "Perfusion", "Custom": "Physio"},
        "aslcontext": {"Measurement": "Perfusion", "Custom": "Context"},
        "asllabeling": {"Measurement": "Perfusion", "Intent": "Screenshot"},
    },
}


def determine_modality(parent_dir_name: str):
    """Determine which modality a file belongs to based on the parent directory's name.

    Args:
        parent_dir_name (str): folder or filename containing matching
                        information for BIDS classification.

    Returns:
        BIDS format modality folder name
    """
    for bids_folder, classificaton_dict in classifications.items():
        for k in classificaton_dict.keys():
            if k.lower() in parent_dir_name.lower():
                return bids_folder
    log.error(
        f"Could not match modality in classification table with {parent_dir_name}"
    )


def search_classifications(bids_folder: str, search_name: str):
    """Robust search on a filename to determine classifications.

    Args:
        bids_folder (str): modality folder, e.g., 'anat','perf'
        search_name (str): filename containing matching
                        information for BIDS classification.

    Returns:
        filetype with classification entries
    """
    matches = []
    for k in classifications[bids_folder].keys():
        if k.lower() in search_name.lower():
            matches.append(k)

    if matches:
        # In cases of multiple matches, choose the longest match
        return classifications[bids_folder][max(matches, key=len)]
    else:
        log.error(
            f"Did not find info in the classification table under {bids_folder} for {search_name}"
        )
