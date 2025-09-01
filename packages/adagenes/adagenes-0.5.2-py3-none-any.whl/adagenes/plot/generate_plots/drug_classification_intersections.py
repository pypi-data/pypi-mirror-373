from upsetplot import generate_counts, generate_samples, UpSet
from upsetplot import plot, from_contents
import matplotlib.pyplot as plt
# TODO: ComplexUpset

def plot_evidence_database_intersections_upset(variant_data,
                                               variant, key='agg',
                                               databases=None, output_file=None, show_plot=True):
    """


    :param variant_data:
    :param variant:
    :param key:
    :param databases:
    :param output_file:
    :param show_plot:
    :return:
    """
    if databases is None:
        databases = config.get_config()["DEFAULT"]["ACTIVE_EVIDENCE_DATABASES"].split()

    plot_data = {}
    for result in variant_data[variant]["onkopus_aggregator"]["aggregated_evidence_data"]["exact_match"]:
        source = result['source']
        pmid = result['citation_id']
        if source not in plot_data:
                plot_data[source] = []
        if pmid not in plot_data[source]:
                plot_data[source].append(pmid)

    df = from_contents(plot_data)
    print("df shape ",df.shape)
    upset = UpSet(df, subset_size='count')
    #upset.style_subsets(present=['metakb', 'civic', 'oncokb'], facecolor="lightblue", label="in all DBs")
    upset.plot()

    #if output_file is not None:
    #    plt.savefig(output_file)

    if show_plot:
        plt.show()
    plt.close()

def plot_evidence_database_intersections_upset_drugs(variant_data,
                                               variant, key='agg',
                                               databases=None, output_file=None, show_plot=True):
    """


    :param variant_data:
    :param variant:
    :param key:
    :param databases:
    :param output_file:
    :param show_plot:
    :return:
    """
    if databases is None:
        databases = config.get_config()["DEFAULT"]["ACTIVE_EVIDENCE_DATABASES"].split()

    plot_data = {}
    for result in variant_data[variant]["onkopus_aggregator"]["merged_evidence_data"]["exact_match"]:
        source = result['source']
        pmid = result['drugs']
        if source not in plot_data:
                plot_data[source] = []
        if pmid not in plot_data[source]:
                plot_data[source].append(pmid)

    df = from_contents(plot_data)
    print("df shape ",df.shape)

    upset = UpSet(df, subset_size='count')
    #upset.style_subsets(present=['metakb', 'civic', 'oncokb'], facecolor="lightblue", label="in all DBs")
    upset.plot()

    #if output_file is not None:
    #    plt.savefig(output_file)

    if show_plot:
        plt.show()
    plt.close()
