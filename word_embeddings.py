import argparse
import re
import os
import json
import numpy as np
import pickle as pkl

import torchtext
from torchtext.vocab import GloVe

"""
For getting word embeddings from glove
Cite: https://github.com/ruotianluo/zsl-gcn-pth/blob/c65888fa98df0e5148806d8493b1581f74df4294/src/tools/obtain_word_embedding.py
"""

url = {'glove': 'http://nlp.stanford.edu/data/glove.6B.zip'}

data_dir = 'data/'
feat_len = 300


def embed_text_file(text_file, word_vectors, get_vector, save_file):
    with open(text_file) as fp:
        text_list = json.load(fp)

    all_feats = []

    has = 0
    cnt_missed = 0
    missed_list = []
    for i in range(len(text_list)):
        class_name = text_list[i].lower()
        if i % 500 == 0:
            print('%d / %d : %s' % (i, len(text_list), class_name))
        feat = np.zeros(feat_len)

        options = class_name.split(',')
        cnt_word = 0
        for j in range(len(options)):
            now_feat = get_embedding(options[j].strip(), word_vectors, get_vector)
            if np.abs(now_feat.sum()) > 0:
                cnt_word += 1
                feat += now_feat
        if cnt_word > 0:
            feat = feat / cnt_word

        if np.abs(feat.sum()) == 0:
            print('cannot find word ' + class_name)
            cnt_missed = cnt_missed + 1
            missed_list.append(class_name)
        else:
            has += 1
            # feat = feat / (np.linalg.norm(feat) + 1e-6)

        all_feats.append(feat)

    all_feats = np.array(all_feats)

    for each in missed_list:
        print(each)
    print('does not have semantic embedding: ', cnt_missed, 'has: ', has)

    if not os.path.exists(os.path.dirname(save_file)):
        os.makedirs(os.path.dirname(save_file))
        print('## Make Directory: %s' % save_file)
    with open(save_file, 'wb') as fp:
        pkl.dump(all_feats, fp)
    print('save to : %s' % save_file)


def get_embedding(entity_str, word_vectors, get_vector):
    try:
        feat = get_vector(word_vectors, entity_str)
        return feat
    except:
        feat = np.zeros(feat_len)

    str_set = list(filter(None, re.split("[ \-_]+", entity_str)))

    cnt_word = 0
    for i in range(len(str_set)):
        temp_str = str_set[i]
        try:
            now_feat = get_vector(word_vectors, temp_str)
            feat = feat + now_feat
            cnt_word = cnt_word + 1
        except:
            continue

    if cnt_word > 0:
        feat = feat / cnt_word
    return feat


def get_glove_dict(txt_dir):
    print('load glove word embedding')
    txt_file = os.path.join(txt_dir, 'glove.6B.300d.txt')
    word_dict = {}
    with open(txt_file) as fp:
        for line in fp:
            feat = np.zeros(feat_len)
            words = line.split()
            assert len(words) - 1 == feat_len
            for i in range(feat_len):
                feat[i] = float(words[i+1])
            word_dict[words[0]] = feat
    print('loaded to dict!')
    return word_dict


def glove_google(word_vectors, word):
    return word_vectors[word]


def get_vector(word_vectors, word):
    if word in word_vectors.stoi:
        return word_vectors[word].numpy()
    else:
        raise NotImplementedError


if __name__ == '__main__':
    text_file = 'data/graph_struct/labels.json'

    model_path = ''#add model path here later
    save_file = os.path.join(data_dir, 'word_embedding_model', 'labels.pkl')
    if not os.path.exists(save_file):
        word_vectors = GloVe('6B')
        # get_vector = glove_google

    if not os.path.exists(save_file):
        print('obtain semantic word embedding', save_file)
        embed_text_file(text_file, word_vectors, get_vector, save_file)
    else:
        print('Embedding existed :', save_file, 'Skip!!!')