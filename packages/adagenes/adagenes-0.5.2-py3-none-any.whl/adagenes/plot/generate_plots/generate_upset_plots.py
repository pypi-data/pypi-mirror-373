import traceback

from upsetplot import generate_counts, generate_samples, UpSet, from_memberships
from upsetplot import plot, from_contents
import matplotlib.pyplot as plt
# TODO: ComplexUpset

def plot_evidence_database_intersections_upset(variant_data,
                                               key='agg',
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

    plot_data = {}
    for variant in variant_data.keys():
        if "onkopus_aggregator" in variant_data[variant].keys():
            for result in variant_data[variant]["onkopus_aggregator"]["merged_match_types_data"]:
                source = result['source']
                pmid = result['citation_id']
                if source not in plot_data:
                        plot_data[source] = []
                if pmid not in plot_data[source]:
                        plot_data[source].append(pmid)

    try:
        df = from_contents(plot_data)
        print("df shape ",df.shape)
        upset = UpSet(df, subset_size='count')
        #upset.style_subsets(present=['metakb', 'civic', 'oncokb'], facecolor="lightblue", label="in all DBs")
        upset.plot()
    except:
        print(traceback.format_exc())

    #if output_file is not None:
    #    plt.savefig(output_file)

    if show_plot:
        plt.show()
    plt.close()


def plot_evidence_database_intersections_upset_drugs(patient_data,
                                               key='agg',
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

    plot_data = {}
    for pid in patient_data:
        for var in patient_data[pid].keys():
            for drug_name in patient_data[pid][var]["onkopus_aggregator"]["agg"].keys():
                result = patient_data[pid][var]["onkopus_aggregator"]["agg"][drug_name]
                print("result ",result)
                try:
                    #source = result['sources']
                    #pmid = result['drugs']
                    pmid = pid
                    if drug_name not in plot_data:
                            plot_data[drug_name] = []
                    if pmid not in plot_data[drug_name]:
                            plot_data[drug_name].append(pmid)
                except:
                    print(traceback.format_exc())

    print("plot data ",plot_data)
    df = from_contents(plot_data)
    print("df shape ",df.shape)
    print(df)

    upset = UpSet(df, subset_size='count')
    #upset.style_subsets(present=['metakb', 'civic', 'oncokb'], facecolor="lightblue", label="in all DBs")
    upset.plot()

    #if output_file is not None:
    #    plt.savefig(output_file)

    if show_plot:
        plt.show()
    plt.close()

def plot_evidence_database_intersections_upset_drug_classes(patient_data,
                                               key='agg',
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

    plot_data = {}
    for pid in patient_data:
        for var in patient_data[pid].keys():
            for drug_name in patient_data[pid][var]["onkopus_aggregator"]["agg"].keys():
                result = patient_data[pid][var]["onkopus_aggregator"]["agg"][drug_name]
                #print("result ",result)
                try:
                    #source = result['sources']
                    #pmid = result['drugs']
                    pmid = pid
                    if drug_name not in plot_data:
                            plot_data[drug_name] = []
                    if pmid not in plot_data[drug_name]:
                            plot_data[drug_name].append(pmid)
                except:
                    print(traceback.format_exc())

    #print("plot data ",plot_data)
    df = from_contents(plot_data)
    #print("df shape ",df.shape)
    print(df)

    upset = UpSet(df, subset_size='count')

    #upset.style_subsets(present=['metakb', 'civic', 'oncokb'], facecolor="lightblue", label="in all DBs")
    upset.plot()

    #if output_file is not None:
    #    plt.savefig(output_file)

    if show_plot:
        plt.show()
    plt.close()
