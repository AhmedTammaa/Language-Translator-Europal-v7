import pandas as pd
import numpy as np 
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

class DataLoader:
    def __init__(self, config):
        self.config = config
        self.lang_src = config['language']['src']
        self.lang_dest = config['language']['dest']
    
    def loadData(self,datapath):        
        with open(datapath
                  +self.config['dataset_path']
                  +self.lang_src
                  ,encoding='utf-8') as sentence:
            self.src = sentence.read().split('\n')
        with open(datapath
                  +self.config['dataset_path']
                  +self.lang_dest
                  ,encoding='utf-8') as sentence:
            self.dest = sentence.read().split('\n')
        print("Loaded dataset at directory:\n"+datapath+self.config['dataset_path']+self.lang_src)
        return self.src, self.dest
        
    
class DataPreprocessing:
    def __init__(self,config):
        self.config = config
        self.lang_src = config['language']['src']
        self.lang_dest = config['language']['dest']
    
    def removeEndLine(self, data):
        for index, word in enumerate(data):
            data[index] = word[:-1]
        return data
    
    def addStartEndPad(self, data, mark_start='aaaa ',mark_end= ' oooo'):
        
        for index, word in enumerate(data):
            
            data[index] = mark_start + word + mark_end  
        return data
    
    def createDataFrameSrcDest(self, src,dest):
        df = pd.DataFrame({self.lang_src: src, self.lang_dest: dest}, columns = [self.lang_src,self.lang_dest])
        #df.to_csv(path+'/questions_easy.csv', index=False)
        return df
    
    def toLowerCase(self, df):
        df[self.lang_src] = df[self.lang_src].apply(lambda x:x.lower())
        df[self.lang_dest] = df[self.lang_dest].apply(lambda x:x.lower())
        return df

class TokenizerWrap(Tokenizer):
    """Wrap the Tokenizer-class from Keras with more functionality."""
    
    def __init__(self, texts, padding,
                 reverse=False, num_words=None):
        """
        :param texts: List of strings. This is the data-set.
        :param padding: Either 'post' or 'pre' padding.
        :param reverse: Boolean whether to reverse token-lists.
        :param num_words: Max number of words to use.
        """

        Tokenizer.__init__(self, num_words=num_words)

        # Create the vocabulary from the texts.
        self.fit_on_texts(texts)

        # Create inverse lookup from integer-tokens to words.
        self.index_to_word = dict(zip(self.word_index.values(),
                                      self.word_index.keys()))

        # Convert all texts to lists of integer-tokens.
        # Note that the sequences may have different lengths.
        self.tokens = self.texts_to_sequences(texts)

        if reverse:
            # Reverse the token-sequences.
            self.tokens = [list(reversed(x)) for x in self.tokens]
        
            # Sequences that are too long should now be truncated
            # at the beginning, which corresponds to the end of
            # the original sequences.
            truncating = 'pre'
        else:
            # Sequences that are too long should be truncated
            # at the end.
            truncating = 'post'

        # The number of integer-tokens in each sequence.
        self.num_tokens = [len(x) for x in self.tokens]

        # Max number of tokens to use in all sequences.
        # We will pad / truncate all sequences to this length.
        # This is a compromise so we save a lot of memory and
        # only have to truncate maybe 5% of all the sequences.
        self.max_tokens = np.mean(self.num_tokens) \
                          + 2 * np.std(self.num_tokens)
        self.max_tokens = int(self.max_tokens)

        # Pad / truncate all token-sequences to the given length.
        # This creates a 2-dim numpy matrix that is easier to use.
        self.tokens_padded = pad_sequences(self.tokens,
                                           maxlen=self.max_tokens,
                                           padding=padding,
                                           truncating=truncating)

    def token_to_word(self, token):
        """Lookup a single word from an integer-token."""

        word = " " if token == 0 else self.index_to_word[token]
        return word 

    def tokens_to_string(self, tokens):
        """Convert a list of integer-tokens to a string."""

        # Create a list of the individual words.
        words = [self.index_to_word[token]
                 for token in tokens
                 if token != 0]
        
        # Concatenate the words to a single string
        # with space between all the words.
        text = " ".join(words)

        return text
    
    def text_to_tokens(self, text, reverse=False, padding=False):
        """
        Convert a single text-string to tokens with optional
        reversal and padding.
        """

        # Convert to tokens. Note that we assume there is only
        # a single text-string so we wrap it in a list.
        tokens = self.texts_to_sequences([text])
        tokens = np.array(tokens)

        if reverse:
            # Reverse the tokens.
            tokens = np.flip(tokens, axis=1)

            # Sequences that are too long should now be truncated
            # at the beginning, which corresponds to the end of
            # the original sequences.
            truncating = 'pre'
        else:
            # Sequences that are too long should be truncated
            # at the end.
            truncating = 'post'

        if padding:
            # Pad and truncate sequences to the given length.
            tokens = pad_sequences(tokens,
                                   maxlen=self.max_tokens,
                                   padding='pre',
                                   truncating=truncating)

        return tokens