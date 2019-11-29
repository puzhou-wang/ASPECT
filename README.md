# ASPECT (Active Sequence PrEdiCTor)

## Overview

In vitro selection is the experiment process by which random sequences of DNA or RNA are examined in parallel to identify those particular sequences (i.e., active sequences) that have a desired function. In vitro selection is widely used for the identification of novel binding and catalytic activity. Even though the initial sequence throughput of in vitro selection is normally ~10^14, the number of eventually identified active sequences is usually on the order of 10^1. Such dramatic difference between the throughputs of input and output for selection experiments is largely attributed to the lack of sequence-function relationship. In other words, it is not possible to screen each sequence for its activity, albeit state-of-the-art sequencing technology allows us to discover more than 10^6 sequences per run.

In this repository, an LDA-based algorithmic method, ASPECT, is developed to allow prediction of active sequences without sequence-activity information.

## Requirements

The following repositories are required.  

1. `pandas`:

   ```bash
   pip install pandas
   ```

2. `gensim`:

   ```bash
   pip install gensim
   ```


## Usage

**To run ASPECT**

```bash
python predictor.py [-h] [-t TOKEN_SIZE] [-n NUM_TOPICS] path
```

positional arguments:

​	path         folder path to the sequencing data

optional arguments:

​	-h, --help		show this help message and exit

​	-k TOKEN_SIZE, --token_size TOKEN_SIZE		token size to parse DNA/RNA squences (default is 8)

​	-rn ROUND_NUMBER, --round_number ROUND_NUMBER            round number of selection pool to predict active sequences (default is the latest round of the input)

​	-tn NUM_TOPICS, --num_topics NUM_TOPICS		number of topics in the topic model (default is 10)

**Input**

The path in the above command should be a folder path containing all the sequencing data for a selection experiment. In this folder, each round of sequencing data will be stored in a `csv` file named as "**round<u>X</u>.csv**", where **<u>X</u>** stands for the round number. To run the active sequence predictor, at least two rounds of sequencing data will be needed.

In each csv file, sequencing data should be stored with column name "sequence".

**Output**

ASPECT will output all predicted active sequences found in the `last` round csv file, separated by different cluster number. Each csv file is composed by three columns: `seq_num`, `confidence`, and `sequence`.

`seq_num` represents the index 1 of a specific sequence in the last round csv file.

`confidence` represents the confidence of claiming that a specific sequence belongs to certain active sequence cluster.

`sequence` represents the contain of the active sequence.

### Example

In this repository, NGS data for round 4-7 in Diels-Alderase (DAse) ribozyme selection experiment was used as an example in the folder `./DAse`.

To predict active DAse sequences from the example data

```bash
python predictor.py /path/to/repository/DAse
```

## Reference

NGS data for DAse selection was originally reported by

Ameta S, *et al.* *Nucleic Acids Res.* **2014**, *42*, 1303 


