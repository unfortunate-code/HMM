




import numpy as np
from hmm import HMM

def model_training(train_data, tags):
    """
    Train an HMM based on training data

    Inputs:
    - train_data: (1*num_sentence) a list of sentences, each sentence is an object of the "line" class 
            defined in data_process.py (read the file to see what attributes this class has)
    - tags: (1*num_tags) a list containing all possible POS tags

    Returns:
    - model: an object of HMM class initialized with parameters (pi, A, B, obs_dict, state_dict) calculated 
            based on the training dataset
    """

    # unique_words.keys() contains all unique words
    unique_words = get_unique_words(train_data)
    
    word2idx = {}
    tag2idx = dict()
    S = len(tags)
    ###################################################
    # TODO: build two dictionaries
    #   - from a word to its index 
    #   - from a tag to its index 
    # The order you index the word/tag does not matter, 
    # as long as the indices are 0, 1, 2, ...
    ###################################################
    index = 0
    for tag in tags:
        tag2idx[tag] = index
        index = index + 1
    
    index = 0
    for word in unique_words:
        word2idx[word] = index;
        index = index + 1

    pi = np.zeros(S)
    A = np.zeros((S, S))
    B = np.zeros((S, len(unique_words)))
    ###################################################
    # TODO: estimate pi, A, B from the training data.
    #   When estimating the entries of A and B, if  
    #   "divided by zero" is encountered, set the entry 
    #   to be zero.
    ###################################################
    for line in train_data:
        pi[tag2idx[line.tags[0]]] += 1
        
        B[tag2idx[line.tags[0]], word2idx[line.words[0]]] += 1
        
        for i in range(1, line.length):
            A[tag2idx[line.tags[i - 1]], tag2idx[line.tags[i]]] += 1
            
            B[tag2idx[line.tags[i]], word2idx[line.words[i]]] += 1
            
    pi = pi / np.sum(pi)
    
    for i in range(0, S):
        A[i, :] = A[i, :] / np.sum(A[i, :])
        
        B[i, :] = B[i, :] / np.sum(B[i, :])

    # DO NOT MODIFY BELOW
    model = HMM(pi, A, B, word2idx, tag2idx)
    return model


def sentence_tagging(test_data, model, tags):
    """
    Inputs:
    - test_data: (1*num_sentence) a list of sentences, each sentence is an object of the "line" class
    - model: an object of the HMM class
    - tags: (1*num_tags) a list containing all possible POS tags

    Returns:
    - tagging: (num_sentence*num_tagging) a 2D list of output tagging for each sentences on test_data
    """
    tagging = []
    ######################################################################
    # TODO: for each sentence, find its tagging using Viterbi algorithm.
    #    Note that when encountering an unseen word not in the HMM model,
    #    you need to add this word to model.obs_dict, and expand model.B
    #    accordingly with value 1e-6.
    ######################################################################
    for line in test_data:
        for word in line.words:
            if word not in model.obs_dict:
                model.obs_dict[word] = len(model.obs_dict)
                col = np.ones((len(model.pi), 1)) * 1e-6
                model.B = np.hstack((model.B, col))
        tagging.append(model.viterbi(line.words))
    return tagging

# DO NOT MODIFY BELOW
def get_unique_words(data):

    unique_words = {}

    for line in data:
        for word in line.words:
            freq = unique_words.get(word, 0)
            freq += 1
            unique_words[word] = freq

    return unique_words
