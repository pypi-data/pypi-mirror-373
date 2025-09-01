"""
SIMPApy: A package for normalized single sample Integrated Multiomics Pathway Analysis.

This package provides tools for running Gene Set Enrichment Analysis (GSEA) on
multi-omics data (RNA-seq, DNA methylation, and copy number variation) in single samples and
integrating the results to identify consistently enriched pathways.

The package includes the following modules:
- core: Contains the main functions for running sopa and sopa_population.
- ranking: Contains functions for calculating ranking and mean signed deviation.
- simpa: Contains the main functions for running SIMPA.
- visualize: Contains functions for creating interactive plots of from SIMPA results.
"""
from .core import _sopa, sopa, load_sopa
from .ranking import calculate_ranking, _calculate_msd
from .SIMPA import _simpa, simpa, load_simpa
from .preprocess import _extract_tag_genes, _create_aggregated_dataframes, process_multiomics_data
from .visualize import _create_traces, create_interactive_plot
from .analyze import group_diffs, plot_volcano, calculate_correlation, plot_correlation_scatterplot

__version__ = "0.1.6"
__all__ = [
    "calculate_ranking",
    "sopa",
    "load_sopa",
    "simpa",
    "load_simpa",
    "process_multiomics_data",
    "create_interactive_plot",
    "group_diffs",
    "plot_volcano",
    "calculate_correlation",
    "plot_correlation_scatterplot"
]