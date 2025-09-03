import argparse


cdb_usage = '''
============ cdb example commands ============

BioSAK cdb -i Cdb.csv -o Cdb_reformatted.txt

==============================================
'''


def cdb(args):

    Cdb_file            = args['i']
    bin_cluster_file    = args['o']

    cluster_to_bin_dict = {}
    obtained_clusters = set()
    for each_bin in open(Cdb_file):
        if not each_bin.startswith('genome,'):
            each_bin_split = each_bin.strip().split(',')
            bin_id = each_bin_split[0]
            secondary_cluster = each_bin_split[-1]
            obtained_clusters.add(secondary_cluster)
            if secondary_cluster not in cluster_to_bin_dict:
                cluster_to_bin_dict[secondary_cluster] = [bin_id]
            else:
                cluster_to_bin_dict[secondary_cluster].append(bin_id)

    obtained_clusters_list = sorted([i for i in obtained_clusters])

    bin_cluster_file_handle = open(bin_cluster_file, 'w')
    for j in obtained_clusters_list:
        bin_cluster_file_handle.write('cluster_%s\t%s\n' % (j, '\t'.join(cluster_to_bin_dict[j])))
    bin_cluster_file_handle.close()


if __name__ == '__main__':
    cdb_parser = argparse.ArgumentParser(usage=cdb_usage)
    cdb_parser.add_argument('-i',  required=True, help='input file, Cdb.csv')
    cdb_parser.add_argument('-o',  required=True, help='output table')
    args = vars(cdb_parser.parse_args())
    cdb(args)

