'''
Active Sequence Predictor
Main file
'''

import argparse
import sys
from util import ReadSequence
from util import Tokenize
from util import ModelPrep
from util import BuildModel
from util import TopicCalculator
import pandas as pd
from util import ActiveTopicFinder
from util import format_topics_sentences


def ActiveSeqPredictor(selection_model, seq_list, round_list, corpus, corpus_list, pos_rn):
    topic_distribution = TopicCalculator(selection_model, round_list, corpus_list)
    active_topic_list = ActiveTopicFinder(topic_distribution)
    results = []
    if active_topic_list == []:
        return results
    print('Finding active sequences in the sequencing data of the last selection round provided...')
    last_round_topic_df = format_topics_sentences(selection_model, corpus_list[pos_rn], seq_list[pos_rn])
    count = 0
    for i in active_topic_list:
        temp_topic = last_round_topic_df[last_round_topic_df['dominant_topic']==float(i)][['confidence', 'sequence']].copy()
        count += len(temp_topic)
        results.append(temp_topic)
    print('{} active sequence(s) were found!'.format(count))
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, help='folder path to the sequencing data')
    parser.add_argument('-k', '--token_size', type=int, default=8, help='token size to parse DNA/RNA squences (default is 8)')
    parser.add_argument('-rn', '--round_number', type=int, default=-1, help='round number of selection pool to predict active sequences (default is the latest round of the input)')
    parser.add_argument('-tn', '--num_topics', type=int, default=10, help='number of topics in the topic model (default is 10)')
    args = parser.parse_args()
    seq_list, round_list = ReadSequence(path = args.path)
    if (seq_list==[]) or (round_list==[]):
        print('No sequencing data found in the folder path provided!')
        sys.exit(0)
    if (len(round_list) == 1):
        print('At least 2 rounds of seqeuncing data are required for this algorithm!')
        sys.exit(0)
    if args.round_number != -1:
        try:
            pos_rn = round_list.index(args.round_number)
        except:
            print('The input of round_number is not in the sequence data!')
            sys.exit(0)
    else:
        pos_rn = round_list.index(max(round_list))
    token_seq_list = Tokenize(seq_list, token_size = args.token_size)
    id2word, corpus, corpus_list = ModelPrep(token_seq_list)
    selection_model = BuildModel(corpus, id2word, num_topics = args.num_topics)
    results = ActiveSeqPredictor(selection_model, seq_list, round_list, corpus, corpus_list, pos_rn)
    try:
        for i in range(len(results)):
            results[i].to_csv(args.path+'/active_sequence_cluster_{}.csv'.format(i+1))
        print('Active sequences were saved in csv files under path: '+args.path)
    except:
        sys.exit(0)