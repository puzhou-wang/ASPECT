'''
Active Sequence Predictor
Utility file    
'''

import pandas as pd
import os
import itertools
import gensim
import gensim.corpora as corpora
import numpy as np


#read all the sequencing data from folder path
#return a list of lsit (seq_list) and a list of round numbers (round_list)
def ReadSequence(path):
    print('Reading all the sequence files in the path:', path)
    round_list = []
    seq_list = []
    try:
        for file in os.listdir(path):
            if file.endswith('.csv') & file.startswith('round'):
                round_list.append(int(file[5:-4]))
                seq_df = pd.read_csv(path+'/'+file)
                seq_list.append(seq_df.sequence.values.tolist())
        print('Read {} file(s) from the path: {}'.format(len(round_list), path))
    except:
        return(seq_list, round_list)
    return(seq_list, round_list)

def Tokenize(seq_list, token_size):
    token_seq_list = []
    print('Tokenizing all the sequences...')
    for round_seq in seq_list: #each round of sequence list
        token_seq = []
        for single_seq in round_seq: #each sequence in the sequence list
            temp = []
            for i in range(len(single_seq)+1-token_size):
                temp.append(single_seq[i:i+token_size])
            token_seq.append(temp)
        token_seq_list.append(token_seq)
    print('Tokenizing done!')
    return(token_seq_list)
    
def ModelPrep(token_seq_list):
    print('Generating corpus for topic model...')
    corpus_total = list(itertools.chain.from_iterable(token_seq_list))
    id2word = corpora.Dictionary(corpus_total)
    corpus = [id2word.doc2bow(text) for text in corpus_total]
    corpus_list = []
    for token_seq in token_seq_list:
        temp_corpus = [id2word.doc2bow(text) for text in token_seq]
        corpus_list.append(temp_corpus)
    print('Corpus ready!')
    return(id2word, corpus, corpus_list)

def BuildModel(corpus, id2word, num_topics):
    print('Building selection model from the sequencing data...')
    selection_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                                id2word=id2word,
                                                num_topics=num_topics,
                                                random_state=100,
                                                update_every=5,
                                                chunksize=1000,
                                                passes=2,
                                                alpha='auto')
    print('Selection model ready!')
    return(selection_model)

#calculate topic distribution per selection round
def TopicCalculator(selection_model, round_list, corpus_list):
    print('Calculating topic distributions through selection rounds...')
    topic_sum_dict = {}
    for i in range(len(corpus_list)):
        get_document_topics = [selection_model.get_document_topics(item, minimum_probability=0) for item in corpus_list[i]]
        round_array = np.asarray(get_document_topics, dtype=np.float)
        round_mean = round_array.mean(axis=0)
        temp_list = round_mean[:,1].tolist()
        temp_list.insert(0, round_list[i])
        topic_sum_dict['round{0}'.format(round_list[i])] = temp_list
    topic_distribution = pd.DataFrame(data=topic_sum_dict)
    print('Topic distributions ready!')
    return(topic_distribution)

#calculate the correlation of topic probability and round number
def ActiveTopicFinder(topic_distribution):
    print('Finding topics representing active sequences...')
    topic_corr = topic_distribution.corrwith(topic_distribution.iloc[0], axis=1)
    active_topic_list = []
    for i in range(1, len(topic_corr)):
        if topic_corr[i] > 0.9:
            active_topic_list.append(i-1)
    print('{} cluster(s) of active sequences found!'.format(len(active_topic_list)))
    return(active_topic_list)

#find the most representative documents for each topic            
def format_topics_sentences(selection_model, corpus, seq_list):
    # Init output
    sent_topics_df = pd.DataFrame()

    # Get main topic in each document
    for i, row in enumerate(selection_model[corpus]):
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        # Get the Dominant topic, Perc Contribution and Keywords for each document
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:  # => dominant topic
                sent_topics_df = sent_topics_df.append(pd.Series([int(topic_num), round(prop_topic,4)]), ignore_index=True)
            else:
                break
    # Add original text to the end of the output
    contents = pd.Series(seq_list)
    sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
    sent_topics_df.columns = ['dominant_topic', 'confidence', 'sequence']
    sent_topics_df.index += 1
    sent_topics_df.index.names = ['seq_num']
    return(sent_topics_df)    
