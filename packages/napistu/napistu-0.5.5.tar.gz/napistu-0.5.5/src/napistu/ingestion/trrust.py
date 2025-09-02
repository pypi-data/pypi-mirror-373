from __future__ import annotations

import os
import warnings
from itertools import chain

import pandas as pd

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
    from fs import open_fs

from napistu import identifiers
from napistu import sbml_dfs_core
from napistu import source
from napistu import utils
from napistu.constants import BQB
from napistu.constants import IDENTIFIERS
from napistu.constants import MINI_SBO_FROM_NAME
from napistu.constants import SBOTERM_NAMES
from napistu.constants import SBML_DFS
from napistu.ingestion.constants import LATIN_SPECIES_NAMES
from napistu.ingestion.constants import INTERACTION_EDGELIST_DEFS
from napistu.ingestion.constants import TRRUST_COMPARTMENT_NUCLEOPLASM
from napistu.ingestion.constants import TRRUST_COMPARTMENT_NUCLEOPLASM_GO_ID
from napistu.ingestion.constants import TRRUST_SYMBOL
from napistu.ingestion.constants import TRRUST_UNIPROT
from napistu.ingestion.constants import TRRUST_UNIPROT_ID
from napistu.ingestion.constants import TTRUST_URL_RAW_DATA_HUMAN
from napistu.ingestion.constants import TRRUST_SIGNS
from napistu.rpy2 import callr


def download_trrust(target_uri: str) -> None:
    """Downloads trrust to the target uri

    Args:
        target_uri (str): target url

    Returns:
        None
    """
    utils.download_wget(TTRUST_URL_RAW_DATA_HUMAN, target_uri)

    return None


def convert_trrust_to_sbml_dfs(
    trrust_uri: str,
) -> sbml_dfs_core.SBML_dfs:
    """Ingests trrust to sbml dfs

    Args:
        trrust_uri (str): trrust uri

    Returns:
        sbml_dfs
    """
    # Read trrust raw data
    trrust_edgelist = _read_trrust(trrust_uri)

    # Get uniprot to symbol mapping
    uniprot_2_symbol = _get_uniprot_2_symbol_mapping()

    # Start building new sbml dfs
    # Per convention unaggregated models receive an empty source
    interaction_source = source.Source(init=True)

    # Summarize edges

    edge_summaries_df = (
        trrust_edgelist.groupby(["from", "to"], as_index=True)
        .apply(_summarize_trrust_pairs)
        .reset_index(drop=False)
    )

    # define distinct species
    species_df = (
        pd.DataFrame(
            {
                SBML_DFS.S_NAME: list(
                    {*edge_summaries_df["from"], *edge_summaries_df["to"]}
                )
            }
        )
        .merge(
            uniprot_2_symbol.rename({TRRUST_SYMBOL: SBML_DFS.S_NAME}, axis=1),
            how="left",
        )
        .set_index(SBML_DFS.S_NAME)
    )

    # create Identifiers objects for all species with uniprot IDs
    species_w_ids = species_df[~species_df[TRRUST_UNIPROT_ID].isnull()].sort_index()
    species_w_ids["url"] = [
        identifiers.create_uri_url(ontology=TRRUST_UNIPROT, identifier=x)
        for x in species_w_ids[TRRUST_UNIPROT_ID]
    ]

    # create a series where each row is a gene with 1+ uniprot ids and the value is an
    # identifiers objects with all uniprot ids
    species_w_ids_series = pd.Series(
        [
            identifiers.Identifiers(
                [
                    identifiers.format_uri(uri=x, biological_qualifier_type=BQB.IS)
                    for x in species_w_ids.loc[[ind]][IDENTIFIERS.URL].tolist()
                ]
            )
            for ind in species_w_ids.index.unique()
        ],
        index=species_w_ids.index.unique(),
    ).rename(SBML_DFS.S_IDENTIFIERS)

    # just retain s_name and s_Identifiers
    # this just needs a source object which will be added later
    species_df = (
        species_df.reset_index()
        .drop(TRRUST_UNIPROT_ID, axis=1)
        .drop_duplicates()
        .merge(
            species_w_ids_series,
            how="left",
            left_on=SBML_DFS.S_NAME,
            right_index=True,
        )
        .reset_index(drop=True)
    )
    # stub genes with missing IDs
    species_df[SBML_DFS.S_IDENTIFIERS] = species_df[SBML_DFS.S_IDENTIFIERS].fillna(  # type: ignore
        value=identifiers.Identifiers([])
    )

    # define distinct compartments
    compartments_df = pd.DataFrame(
        {
            SBML_DFS.C_NAME: TRRUST_COMPARTMENT_NUCLEOPLASM,
            SBML_DFS.C_IDENTIFIERS: identifiers.Identifiers(
                [
                    identifiers.format_uri(
                        uri=identifiers.create_uri_url(
                            ontology="go",
                            identifier=TRRUST_COMPARTMENT_NUCLEOPLASM_GO_ID,
                        ),
                        biological_qualifier_type="BQB_IS",
                    )
                ]
            ),
        },
        index=[0],
    )

    gene_gene_identifier_edgelist = edge_summaries_df.rename(
        {
            "from": INTERACTION_EDGELIST_DEFS.UPSTREAM_NAME,
            "to": INTERACTION_EDGELIST_DEFS.DOWNSTREAM_NAME,
        },
        axis=1,
    ).assign(
        upstream_compartment=TRRUST_COMPARTMENT_NUCLEOPLASM,
        downstream_compartment=TRRUST_COMPARTMENT_NUCLEOPLASM,
    )
    gene_gene_identifier_edgelist[SBML_DFS.R_NAME] = [
        f"{x} {y} of {z}"
        for x, y, z in zip(
            gene_gene_identifier_edgelist[INTERACTION_EDGELIST_DEFS.UPSTREAM_NAME],
            gene_gene_identifier_edgelist["sign"],
            gene_gene_identifier_edgelist[INTERACTION_EDGELIST_DEFS.DOWNSTREAM_NAME],
        )
    ]

    # convert relationships to SBO terms
    interaction_edgelist = gene_gene_identifier_edgelist.replace(
        {"sign": MINI_SBO_FROM_NAME}
    ).rename({"sign": INTERACTION_EDGELIST_DEFS.SBO_TERM_UPSTREAM}, axis=1)

    # format pubmed identifiers of interactions
    interaction_edgelist[SBML_DFS.R_IDENTIFIERS] = [
        _format_pubmed_for_interactions(x) for x in interaction_edgelist["reference"]
    ]

    # directionality: by default, set r_isreversible to False for TRRUST data
    interaction_edgelist[SBML_DFS.R_ISREVERSIBLE] = False

    # reduce to essential variables
    interaction_edgelist = interaction_edgelist[
        [
            INTERACTION_EDGELIST_DEFS.UPSTREAM_NAME,
            INTERACTION_EDGELIST_DEFS.DOWNSTREAM_NAME,
            INTERACTION_EDGELIST_DEFS.UPSTREAM_COMPARTMENT,
            INTERACTION_EDGELIST_DEFS.DOWNSTREAM_COMPARTMENT,
            SBML_DFS.R_NAME,
            INTERACTION_EDGELIST_DEFS.UPSTREAM_SBO_TERM,
            SBML_DFS.R_IDENTIFIERS,
            SBML_DFS.R_ISREVERSIBLE,
        ]
    ]

    # Build sbml dfs
    sbml_dfs = sbml_dfs_core.sbml_dfs_from_edgelist(
        interaction_edgelist=interaction_edgelist,
        species_df=species_df,
        compartments_df=compartments_df,
        interaction_source=interaction_source,
    )
    sbml_dfs.validate()
    return sbml_dfs


def _read_trrust(trrust_uri: str) -> pd.DataFrame:
    """Read trrust csv

    Args:
        trrust_uri (str): uri to the trrust csv

    Returns:
        pd.DataFrame: Data Frame
    """
    base_path = os.path.dirname(trrust_uri)
    file_name = os.path.basename(trrust_uri)
    with open_fs(base_path) as base_fs:
        with base_fs.open(file_name) as f:
            trrust_edgelist = pd.read_csv(
                f, sep="\t", names=["from", "to", "sign", "reference"]
            ).drop_duplicates()
    return trrust_edgelist


def _summarize_trrust_pairs(pair_data: pd.DataFrame) -> pd.Series:
    """Summarize a TF->target relationship based on the sign and source of the interaction."""

    signs = set(pair_data["sign"].tolist())
    if (TRRUST_SIGNS.ACTIVATION in signs) and (TRRUST_SIGNS.REPRESSION in signs):
        sign = SBOTERM_NAMES.MODIFIER
    elif TRRUST_SIGNS.ACTIVATION in signs:
        sign = SBOTERM_NAMES.STIMULATOR
    elif TRRUST_SIGNS.REPRESSION in signs:
        sign = SBOTERM_NAMES.INHIBITOR
    else:
        sign = SBOTERM_NAMES.MODIFIER

    refs = set(chain(*[x.split(";") for x in pair_data["reference"]]))
    return pd.Series({"sign": sign, "reference": refs})


def _get_uniprot_2_symbol_mapping() -> pd.DataFrame:
    """Create a mapping from Uniprot IDs to human gene symbols."""

    entrez_2_symbol = callr.r_dataframe_to_pandas(
        callr.bioconductor_org_r_function(
            TRRUST_SYMBOL.upper(), species=LATIN_SPECIES_NAMES.HOMO_SAPIENS
        )
    )
    # only look at symbol which uniquely map to a single gene
    symbol_counts = entrez_2_symbol.value_counts(TRRUST_SYMBOL)
    unique_symbols = symbol_counts[symbol_counts == 1].index.tolist()
    entrez_2_symbol = entrez_2_symbol[
        entrez_2_symbol[TRRUST_SYMBOL].isin(unique_symbols)
    ]

    # one entrez -> multiple uniprot IDs is okay
    entrez_2_uniprot = callr.r_dataframe_to_pandas(
        callr.bioconductor_org_r_function(
            TRRUST_UNIPROT.upper(), species=LATIN_SPECIES_NAMES.HOMO_SAPIENS
        )
    )

    uniprot_2_symbol = entrez_2_symbol.merge(entrez_2_uniprot).drop("gene_id", axis=1)
    return uniprot_2_symbol


def _format_pubmed_for_interactions(pubmed_set):
    """Format a set of pubmed ids as an Identifiers object."""

    ids = list()
    for p in pubmed_set:
        # some pubmed IDs are bogus
        url = identifiers.create_uri_url(ontology="pubmed", identifier=p, strict=False)
        if url is not None:
            valid_url = identifiers.format_uri(
                uri=url, biological_qualifier_type=BQB.IS_DESCRIBED_BY
            )

            ids.append(valid_url)

    return identifiers.Identifiers(ids)
