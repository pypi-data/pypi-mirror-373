import os
import platform
import pickle
import datetime
import time
import string
import importlib.resources
import regex
import re as re
import multiprocessing
# import wandb

"""
Kin_tokenizer is a python module which includes class and methods
for Kinyarwanda tokenizeer
"""

def process_chunk(indexed_chunk):
    """Process a chunk of the nested list."""
    index, chunk = indexed_chunk
    return index, [item for sublist in chunk for item in sublist]

def parallel_create_tokens(chunk):
    """
    Helper function for multiprocessing to create tokens from text chunk.
    """
    tokenizer = KinTokenizer()
    return tokenizer.create_tokens(chunk)

def parallel_merge_tokens(args):
    """
    Helper function for multiprocessing to merge tokens.
    Args should be a tuple of (pair, tokens, new_token).
    """
    pair, tokens, new_token = args
    tokenizer = KinTokenizer()  # Create a tokenizer instance in each process
    return tokenizer.merge_tokens(pair, tokens, new_token)

def filter_chunk(chunk, remove_set):
    """Filter a chunk of the list, removing elements in the remove_set."""
    return [x for x in chunk if x not in remove_set]

def parallel_filter(main_list, items_to_remove, num_processes=multiprocessing.cpu_count()):
    """Filter the main list using multiprocessing."""
    # Convert items to remove into a set for efficient lookups
    remove_set = set(items_to_remove)
    
    # Divide the main list into chunks
    chunk_size = len(main_list) // num_processes
    chunks = [main_list[i:i + chunk_size] for i in range(0, len(main_list), chunk_size)]
    
    # Use multiprocessing to filter each chunk
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.starmap(filter_chunk, [(chunk, remove_set) for chunk in chunks])
    
    # Combine the filtered chunks into a single list
    filtered_list = [item for sublist in results for item in sublist]
    
    return filtered_list


class KinTokenizer:
    def __init__(self):
        """
        load_state: enables the tokenizer to load its vocabulary state it was trained on
        possible values:
            True: bool(default) => means the tokenizer instance will be created and get initialized with trained state
            False: bool => means you initialize the state after creating the instance. tokenizer.load()
        """
        super(KinTokenizer, self).__init__()

        self.__vocab = {0: "<|PAD|>"}
        self.merged_tokens = {}
        self.vocab_size = None
        self.compiled_pattern = regex.compile(r'\s+|\p{L}+|\p{N}+|[^\s\p{L}\p{N}]+', regex.UNICODE)

        try:
            # Correctly locate the file inside the package, wherever it is installed.
            tokenizer_path_obj = importlib.resources.files('kin_tokenizer').joinpath('data/kin_tokenizer.pkl')
            
            # Use a context manager to get a guaranteed real file path.
            with importlib.resources.as_file(tokenizer_path_obj) as tokenizer_path:
                self.load(tokenizer_path) 
                
        except FileNotFoundError:
            pass
            # print("Tokenizer file not found inside the package.")
            
    @property
    def vocab(self):
        return {
            key: value.decode("UTF-8", errors="replace") if type(value) == bytes else value for key, value in self.__vocab.items()
        }

    
    def set_vacab(self, vocab):
        """
        method for setting vocabulary of the tokenizer
        vocab: dictionary of int, bytes
        """
        if (self.__vocab) < 1:
            if type(vocab) == dict:
                self.__vocab = vocab
            else:
                raise ValueError("Expected a dictionary of {integer: bytes}")
        else:
            raise ValueError("Vocab cannot be overriden")


    def set_merged_tokens(self, merged_tokens):
        """
        method of setting merged_tokens
        merged_tokens: dictionary of merged_tokens ((int, int), int)
        """
        if (self.merged_tokens) < 1:
            if type(merged_tokens) == dict:
                self.merged_tokens = merged_tokens
            else:
                raise ValueError("Expected a dictionary of {(integer, integer): integer}")
        else:
            raise ValueError("merged_tokens cannot be overriden")
        
    
    def save(self, path):
        """
        method for saving the tokenizer state
        path: the path to the directory where the tokenizer will be saved
        """
        if not os.path.exists(path) or not os.path.isdir(path):
            raise ValueError("The path should be a diractory path and it should exist!")
            
        path = os.path.join(path, "kin_tokenizer.pkl")
        with open(path, "wb") as f:
            pickle.dump(self, f)
            f.close()

        path = path.replace("\\", "\\\\")
        print(f"\n\n{'='*(len(path)+ 33)}\nTokenizer saved successfully at {path}\n{'='*(len(path)+ 33)}\n")
        print(f""" 
        To load tokenizer and start using it\n{'='*(len(path) + 33)}\n
        with open('{path}', 'rb') as f:
            kin_tokenizer = pickle.load(f)
            kin_tokenizer.vocab # to get vocab
            f.close()
        """) 

    def load(self, tokenizer_path):
        """
        method for loading the tokenizer state
        path: the full path to the tokenizer file(.pkl)
        """
        try:
            with open(tokenizer_path, 'rb') as f:
                tokenizer = pickle.load(f)
                self.__vocab = tokenizer.__vocab
                self.vocab_size = tokenizer.vocab_size
                self.merged_tokens = tokenizer.merged_tokens
        except Exception as e:
            # print(f"Loading Tokenizer State Error: {str(e)}")
            pass
            

    
    def create_bpe(self, tokens):
        """
        Generator for creating token pairs
        params:
            tokens: list of tokens(integers)
        """
        n = len(tokens) - 1
        i = 0
        while i < n:
            yield (tokens[i], tokens[i+1])
            i += 1     

    
    def get_tokens_pair_stats(self, tokens, stats=None):
        """
        method for creating frequencies of tokens
        tokens: list of tokens(int)
        stats: defaukt statistics of tokens
        """
        stats = {} if stats is None else stats
        for pair in self.create_bpe(tokens):
            stats[pair] = stats.get(pair, 0) + 1
        return stats

    
    def create_tokens(self, text):
        """
        method for creating tokens from text
        text: string of character
        """
        if type(text) == str:
            text = text.encode("UTF-8")
        elif type(text) != bytes:
            raise ValueError("Expected string or bytes")

        return list(map(int, text))

    
    def merge_tokens(self, pair, tokens, new_token):
        """
        method for merging tokens
        pair: the pair to be merged(most frequent pair of tokens)
        tokens: list of tokens
        new_token: the new token to replace the most frequent pair of tokens(int, int)
        """
        new_tokens = []
        index = 0
        changed = False
        while index < len(tokens):
            if index < len(tokens) - 1 and pair[0] == tokens[index] and pair[1] == tokens[index+1]:
                new_tokens.append(new_token)
                index += 2
                changed = True
            else:
                new_tokens.append(tokens[index])
                index += 1
                
        if changed:
            self.merged_tokens[pair] = new_token
        return new_tokens    


    def replace_punctuation_mark(self, text):
        """
        method for removing punctuation marks and new line from the text for training tokenizer
        text: text to be used for training the tokenizer
        """
        text = text.replace("\n", "")
        punctuation_marks = string.punctuation.replace("'", "")
        pattern = r'' + f'([{punctuation_marks}])'
        return regex.sub(pattern, r'', text) 

    def remove_urls(self, text):
        """
        Removes URLs from a given text string.

        Args:
            text (str): The text to remove URLs from.

        Returns:
            str: The text with URLs removed.
        """
        # This is the simpler, more common regex
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        return url_pattern.sub(r'', text)   
    
    def fix_case(self, match):
        return match.group(1) + match.group(2).lower()

    def clean_lines(self, text):
        """
            To remove lines that meet the following conditions:
                - Contain only a single number (like 105)
                - Contain only special character(s) (like !!! or @$%)
                - Contain only a mix of numbers and special characters, with no letters (e.g., #105, 123@!)
        """
        return '\n'.join(
            line for line in text.splitlines()
            if not regex.fullmatch(r'\s*([^\w\s]*\d+[^\w\s]*|[^\w\s]+|\d+)\s*', line)
        )

    def train(self, text, vocab_size=276, verbose=True, start_merge_iter=1, tokenizer_path=None, nbr_processes=None):
        """
        method for training the tokenizer
        text: the text to be used for training the tokenizer
        vocab_size: the size of the vocabulary for the tokenizer after training
        start_merge_iter: The initial iteration/merge iteration
        tokenizer_path: The part where tokenizer will be saved(exclusing filename)
        """
        assert vocab_size >= 257
        if start_merge_iter > 1:
            append_logs = "a"
        else:
            append_logs = "w"

        last_token_chuncks_file_path = os.path.join("kin_tokenizer", "data", "current_token_chunks.pkl")
        
        # check the vCPU(s)
        vcpus_nbr = os.cpu_count()
        inline_text = f"AVAILABLE vCPU(s): {vcpus_nbr}\n\n"

        if nbr_processes is not None:
            vcpus_nbr = nbr_processes
        else:
            vcpus_nbr = os.cpu_count()

        if len(text) < 129:
            vcpus_nbr = 1
        elif len(text) <= (128 * vcpus_nbr):
            vcpus_nbr = len(text) // 128

        inline_text += f"Running {vcpus_nbr} processes\n"

        if start_merge_iter > 1:
            inline_text += f"Retraing started: {datetime.datetime.now(datetime.timezone.utc).strftime('%d-%m-%Y %H:%M:%S')} UTC\n\n"
        else:
            inline_text += f"Traing started: {datetime.datetime.now(datetime.timezone.utc).strftime('%d-%m-%Y %H:%M:%S')} UTC\n\n"

        print(inline_text)

        start_time = time.time()
        print("\nInitial data cleaning using different regular expression patterns\n")
        inline_text += "\nInitial data cleaning using different regular expression patterns\n"

        # normalize text
        text = regex.sub("’", "'", text) # repacle ’ with '
        text = regex.sub("‘", "'", text) # repacle ‘ with '
        text = regex.sub("“", '"', text) # repacle “ with "
        text = regex.sub("”", '"', text) # repacle ” with "

        text = regex.sub('â', 'a', text) # replace â with a
        text = regex.sub('ê', 'e', text) # replace ê with e
        text = regex.sub('î', 'i', text) # replace î with i
        text = regex.sub('ô', 'o', text) # replace ô with o
        text = regex.sub('û', 'u', text) # replace û with u
        
        text = self.clean_lines(text)
        text = regex.sub(r'(\n){3,}', '\n\n', text) # Removing more than one consecutive white space(empty lines)
        text = regex.sub(r'(\S)\s+\n', r'\1\n\n', text) # removing spaces between the new line and the last character of the sentence
        text = text = regex.sub(r'([aeiouAEIOU])[aeiouAEIOU]+', r'\1', text)  # Keep only one vowel when there are consecutive vowels
        text = regex.sub(r'([aeiouAEIOU])([aeiouAEIOU])([^A-Za-z])+', r'\1\3', text)  # If there are still two consecutive vowels followed by non-letter remove the second vowel
        text = regex.sub(r'([aeiouAEIOU])([aeiouAEIOU])', r'\1 \2', text) # Add a space between two vowels following each other(e.g aa -> a a
        text = regex.sub(r'^(?!\s*$)\s+', '', text, flags=regex.MULTILINE) # remove spaces before each line or sentence
        text =regex.sub(r'([aeiou])([A-Z])', self.fix_case, text) # When a small vawel is followed by capital letter, lowercase the following(e.g uRwanda -> urwanda)
        text = regex.sub(r'\*', ' ', text)
        text = regex.sub(r'[^\S\r\n]+', ' ', text) # Where there is more than one space within the line followed by non-space, replace it with one space( wagiye    gusura -> wagiye gusura)
        text = regex.sub(r'(\w)\s+(\p{P})', r'\1\2', text) # remove space before the punctuation mark
        text = self.remove_urls(text)
        text = re.sub(r'\d+', '', text) # remove all digits
        # text = text.lower()

        total_time = time.time() - start_time
        print(f"\nInitial data cleaning using different regular expression patterns took: {total_time//60} min {round(total_time%60)} seconds\n")
        inline_text += f"\nInitial data cleaning using different regular expression patterns took: {total_time//60} min {round(total_time%60)} seconds\n"
        
        if platform.system() == 'Windows':
            multiprocessing.set_start_method('spawn', force=True)
        else:
            multiprocessing.set_start_method('forkserver', force=True)
        
        if start_merge_iter < 2: # First training 
            # Reading non kinyarwanda
            inline_text += "\nReading non kinyarwanda words\n"
            print("\nReading non kinyarwanda words\n")

            non_kinyarwanda_words_file_path = os.path.join("kin_tokenizer", "data", "non_kinyarwanda_words.pkl")
            with open(non_kinyarwanda_words_file_path, "rb") as f:
                non_kinyarwanda_words = pickle.load(f)

            # Adding other initial values into a vocabulary
            for index in range(1, 256):
                self.__vocab[index] = bytes([index])

            # Splitting text into chuncks using space
            print("\nSplitting text on space\n")
            inline_text += "\nSplitting text on space\n"
            start_time = time.time()
            chunks = regex.split(r'\s+', text)
            total_time = time.time() - start_time
            print(f"\nSplitting text on space took: {total_time//60} min {round(total_time%60)} seconds\n")
            inline_text += f"\nSplitting text on space took: {total_time//60} min {round(total_time%60)} seconds\n"

            # removing non kinyarwanda words
            print("\nRemoving non kinyarwanda words\n")
            inline_text += "\nRemoving non kinyarwanda words\n"
            start_time = time.time()
            chunks = parallel_filter(main_list=chunks, items_to_remove=non_kinyarwanda_words, num_processes=vcpus_nbr)
            total_time = time.time() - start_time

            print(f"\nRemoving non kinyarwanda words took: {total_time//60} min {round(total_time%60)} seconds\n")
            inline_text += f"\nRemoving non kinyarwanda words took: {total_time//60} min {round(total_time%60)} seconds\n"

            # reconstructing the text
            print("\nReconstructing text\n")
            inline_text += "\nReconstructing text\n"
            start_time = time.time()
            text = " ".join(chunks)

            total_time = time.time() - start_time

            print(f"\nReconstructing text took: {total_time//60} min {round(total_time%60)} seconds\n")
            inline_text += f"\nReconstructing text took: {total_time//60} min {round(total_time%60)} seconds\n"
            
            # Splitting text into chuncks
            print("\nSplitting text on compiled pattern\n")
            inline_text += "\nSplitting text on compiled pattern\n"
            start_time = time.time()
            chunks = regex.findall(self.compiled_pattern, text)

            total_time = time.time() - start_time

            print(f"\nSplitting text on compiled pattern took: {total_time//60} min {round(total_time%60)} seconds\n")
            inline_text += f"\nSplitting text on compiled pattern took: {total_time//60} min {round(total_time%60)} seconds\n"

            # removing existing words in the vocabulary
            print("\nRemoving words in chunks already exists in the tokenizer vocabulary\n")
            inline_text += "\nRemoving words in chunks already exists in the tokenizer vocabulary\n"
            start_time = time.time()

            existing_words_in_vocab= [value.decode("UTF-8", errors="ignore") for _, value in self.__vocab.items() if type(value) == bytes]
            chunks = parallel_filter(main_list=chunks, items_to_remove=existing_words_in_vocab, num_processes=vcpus_nbr)
            del existing_words_in_vocab

            total_time = time.time() - start_time

            print(f"\nRemoving words in chunks already exists in the tokenizer vocabulary took: {total_time//60} min {round(total_time%60)} seconds\n")
            inline_text += f"\nRemoving words in chunks already exists in the tokenizer vocabulary took: {total_time//60} min {round(total_time%60)} seconds\n"

        else: # Retraining
            print(f"\nLoading tokens chunks from a file: {last_token_chuncks_file_path}\n")
            with open(last_token_chuncks_file_path, "rb") as token_chunks_f:
                tokens_chunks = pickle.load(token_chunks_f)
        
            print("\nStarted retraining\n")
            inline_text += f"\nLoading tokens chunks from a file: {last_token_chuncks_file_path}\n"
            inline_text += "\nStarted retraining\n"

        if start_merge_iter < 2: # First training 
            # Preprocess text: Create tokens using multiprocessing
            inline_text += "Creating tokens from text chunks..............\n"
            print("Creating tokens from text chunks..............\n")
            start_time = time.time()
            with multiprocessing.Pool(processes=vcpus_nbr) as pool:
                tokens_chunks = pool.map(parallel_create_tokens, chunks)
            total_time = time.time() - start_time
            inline_text += f"Creating tokens took: {total_time//60} min {round(total_time%60)} seconds\n"
            print(f"Creating tokens took: {total_time//60} min {round(total_time%60)} seconds\n")

        num_merges = vocab_size - len(self.__vocab)# We have encode tokens into range of 0 and 256
        
        with open("training_logs.txt", append_logs) as f:
            for idx in range(start_merge_iter, start_merge_iter + num_merges):
                merge_start_time = time.time()
                if len(tokens_chunks) > 1:
                    new_token = max(list(self.__vocab.keys())) + 1

                    inline_text += "Calculating tokens pair statistics......\n"
                    print("Calculating tokens pair statistics......")
                    stats = {} # calculating the statistics(pair frequencies)
                    start_time = time.time()
                    for tokens in tokens_chunks:
                        self.get_tokens_pair_stats(tokens, stats)

                    total_time = time.time() - start_time
                    inline_text += f"Calculating tokens pair statistics took: {total_time//60} min {round(total_time%60)} seconds\n"
                    print(f"Calculating tokens pair statistics took: {total_time//60} min {round(total_time%60)} seconds\n")

                    # Find the most frequent pair
                    top_pair = max(stats, key=stats.get) # getting the top pair(pair with highest frequency)


                    if stats.get(top_pair) < 2: # there are no more frequent pairs
                        break

                    # # Replace top_pair in all token_chuncks with new_toeken
                    # tokens_chunks = [ self.merge_tokens(top_pair, tokens, new_token) for tokens in tokens_chunks ]
                    
                    # Parallel merging of tokens
                    inline_text += "Creating merging arguments for parallel merging....\n"
                    print("Creating merging arguments for parallel merging....")
                    start_time = time.time()
                    merge_args = [(top_pair, tokens, new_token) for tokens in tokens_chunks]
                    total_time = time.time() - start_time
                    inline_text += f"Creating merging arguments for parallel merging took: {total_time//60} min {round(total_time%60)} seconds\n"
                    print(f"Creating merging arguments for parallel merging took: {total_time//60} min {round(total_time%60)} seconds\n")

                    start_time = time.time()
                    inline_text += "Merging top pair tokens .....\n"
                    print("Merging top pair tokens .....")
                    with multiprocessing.Pool(processes=vcpus_nbr) as pool:
                        tokens_chunks = pool.map(parallel_merge_tokens, merge_args)


                    total_time = time.time() - start_time
                    inline_text += f"Marging the top pair tokens took: {total_time//60} min {round(total_time%60)} seconds\n"
                    print(f"Marging the top pair tokens took: {total_time//60} min {round(total_time%60)} seconds\n")
                    # Save the merge
                    self.merged_tokens[top_pair] = new_token

                    # Add new vocabulary into the vocab
                    self.__vocab[new_token] = self.__vocab[top_pair[0]] + self.__vocab[top_pair[1]]
                    
                    merge_total_time = time.time() - merge_start_time

                    if tokenizer_path is not None and ((idx + 1) % 50  == 0): # at every 50 marges save tokenizer
                        self.vocab_size = len(self.__vocab)
                        self.save(tokenizer_path)
                        print(f"\nSaving tokenizer at merge iteration: {idx + 1}\n")
                        f.write(f"\nSaving tokenizer at merge iteration: {idx + 1}\n\n")

                        with open(last_token_chuncks_file_path, "wb") as token_chunks_f:
                            pickle.dump(tokens_chunks, token_chunks_f)
                            print(f"\nSaving tokens_chunks at merge iteration: {idx + 1}\n")
                            f.write(f"\nSaving tokens_chunks at merge iteration: {idx + 1}\n\n")
                    # print messages on the console
                    if verbose:
                        try:
                            decoded_pair = self.decode(list(top_pair), return_eos=False, multiprocess=False)
                        except:
                            decoded_pair = "Error decoding"
                        line = f"Merge({idx}/{num_merges + start_merge_iter -1}): Pair {top_pair} ('{decoded_pair}') -> {new_token} ({stats[top_pair]} occurrences). Vocab size: {len(self.__vocab)}. Iteration time: {merge_total_time // 60}m {round(merge_total_time % 60)}s completed at {datetime.datetime.now(datetime.timezone.utc).strftime('%d-%m-%Y %H:%M:%S')} UTC."
                        line_2 = "="*len(line)
                        print(line)
                        print(line_2)
                        f.write(line + "\n" + line_2 + "\n")
                        inline_text = ""
                    
                    # wandb.log({
                    #         "merge": idx,
                    #         "vocab size": len(self.__vocab),
                    #         "Iteration time": merge_total_time
                    #     })
                else:
                    break # no more pairs

         
        # Adding special token(end of sequence)
        print("\nTraining finished. Adding special tokens...")
        max_token = max(list(self.__vocab.keys()))
        self.__vocab[max_token + 1] = "<|EOS|>"
        self.__vocab[max_token + 2] = "<|BOS|>"
        self.__vocab[max_token + 3] = "<|SEP|>"
        self.__vocab[max_token + 4] = "<|MASK|>"
        self.__vocab[max_token + 5] = "<|UNK|>"
        self.__vocab[max_token + 6] = "<|CLS|>"
        self.vocab_size = len(self.__vocab)
        print("Special tokens added. Final vocabulary size:", self.vocab_size)

    
    def _encode_chunck(self, indexed_word):
        """
        Method for encoding word or character(s)
        params:
            word: word to be encoded
        """
        index, word = indexed_word

        tokens = self.create_tokens(word)
        while len(tokens) > 1:
            stats = self.get_tokens_pair_stats(tokens)
            bottom_pair = min(stats, key=lambda p: self.merged_tokens.get(p, float("inf")))
            if bottom_pair not in self.merged_tokens:
                break
            new_token = self.merged_tokens[bottom_pair]
            tokens = self.merge_tokens(bottom_pair, tokens, new_token) 

        return index, tokens


    def encode(self, text, nbr_processes=None):
        """
        method to be used for converting text to token using method used for training the tokenizer
        text: text to be encoded
        """
        if type(text) != str:
            raise ValueError("Expected a string!")
        
        text_chunks = regex.findall(self.compiled_pattern, text) # Splitting text into chuncks

        if platform.system() == 'Windows':
            multiprocessing.set_start_method('spawn', force=True)
        else:
            multiprocessing.set_start_method('forkserver', force=True)
            
        vcpus_nbr = os.cpu_count()

        if nbr_processes is not None:
            vcpus_nbr = nbr_processes
        
        if len(text) < 129: # each process must have at least 2048 characters
            vcpus_nbr = 1
        elif len(text) <= (128 * vcpus_nbr):
            vcpus_nbr = len(text) // 128


        # Add indices to the chunks to preserve order
        indexed_chunks = [(i, chunk) for i, chunk in enumerate(text_chunks)]

        with multiprocessing.Pool(processes=vcpus_nbr) as pool:
            result = pool.map(self._encode_chunck, indexed_chunks)
        
        # Sort results based on the original index
        result = [value for _, value in result]
        
        result_chunks_size = len(result) // vcpus_nbr
        chunks = [ (i, result[i: i + result_chunks_size]) for i in range(0, len(result), result_chunks_size)]

        with multiprocessing.Pool(processes=vcpus_nbr) as pool:
            result = pool.map(process_chunk, chunks)
        
        # Sort results based on the original index
        result = [value for _, value in result]

        _, tokens = process_chunk((0, result))
            
        return tokens

    
    def single_process_decode(self, indices, return_eos=True):
        """
        method for converting tokens(int) back to text
        indices: list of tokens to be decoded
        """
        if type(indices) not in (list, tuple):
            raise ValueError("Expected list of integers")
        tokens = []
        eos = ""
        for idx in indices:
            if self.__vocab[idx] == "<|EOS|>" and return_eos:
                eos = self.__vocab[idx]
                continue
            elif idx not in self.__vocab:
                raise KeyError(f"Token {idx} does not exist in the vocabularies")
            
            tokens.append(self.__vocab[idx])

        tokens = b"".join(tokens)
        text = tokens.decode("UTF-8", errors="ignore")
        
        return text + eos
    
    def multiprocess_decode_chunk(self, args):
        chunk, return_eos = args
        tokens_part = []
        has_eos = False
        invalid_indices = []
        for idx in chunk:
            if idx not in self.__vocab:
                invalid_indices.append(idx)
                continue
            if return_eos and self.__vocab[idx] == "<|EOS|>":
                has_eos = True
                continue
            tokens_part.append(self.__vocab[idx])
        return tokens_part, has_eos, invalid_indices
    

    def decode(self, indices, multiprocess=True, return_eos=True):
        """
        indices: list or tuple containing tokens indices
        multiprocess(bool): to enable/disable multiprocessing(cpus > 1)
        return_eos: return EOS token
        """

        if not isinstance(indices, (list, tuple)):
            raise ValueError("Expected list of integers")

        if multiprocess and len(indices) > 65:
            num_processes = os.cpu_count()

            if len(indices) <= (64 * num_processes):
                num_processes = len(indices) // 64

            chunk_size = max(1, len(indices) // num_processes)
            chunks = [indices[i:i+chunk_size] for i in range(0, len(indices), chunk_size)]
            
            with multiprocessing.Pool() as pool:
                results = pool.map(self.multiprocess_decode_chunk, [(chunk, return_eos) for chunk in chunks])
            
            tokens = []
            has_eos = False
            invalid_indices = []
            
            for tokens_part, chunk_has_eos, chunk_invalid in results:
                tokens.extend(tokens_part)
                has_eos |= chunk_has_eos
                invalid_indices.extend(chunk_invalid)
            
            if invalid_indices:
                raise KeyError(f"Tokens {invalid_indices} do not exist in the vocabularies")
            
            tokens_bytes = b"".join(tokens)
            text = tokens_bytes.decode("UTF-8", errors="ignore")
            
            if return_eos and has_eos:
                text += "<|EOS|>"
            
            return text
        else:
            return self.single_process_decode(indices, return_eos)
        