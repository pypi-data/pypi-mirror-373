import sys
import time
import datetime
import os
import requests
import numpy as np
import regex
import re
from .tokenizer import KinTokenizer

from multiprocessing import Pool



def train_kin_tokenizer(text, vocab_size=276, save=False, tokenizer_path=None, retrain=False):
    """
    Function for training the tokenizer
    params:
        text: the string text that will be used for training the tokenizer
        vocab_size: the final size of the voacabulary for the tokenizer
        save: boolean to indicate if tokenizer has to be saved after training for future use
        tokenizer_path: the path to which the tokenizer will be saved if save is True
    Returns:
        returns tokenizer object after training
    """
    tokenizer = KinTokenizer()
    start_merge_iter = 0
    if retrain:
        tokenizer.load(os.path.join(tokenizer_path, "kin_tokenizer.pkl"))
        start_merge_iter = max(list(tokenizer.vocab.keys()))
    if len(text) < vocab_size or type(text) != str:
        raise ValueError("length of text should be greater or equal to vocab_size, vocab_size should be at least 256 and text should be a string")
    
    if save == True:
        if tokenizer_path is None:
           tokenizer_path = os.path.join("kin_tokenizer", "data")
        
        tokenizer.train(text, vocab_size, start_merge_iter=start_merge_iter, tokenizer_path=tokenizer_path)
        tokenizer.save(tokenizer_path)
    else:
        tokenizer.train(text, vocab_size, start_merge_iter=start_merge_iter)

    return tokenizer


def create_sequences(tokens, seq_len, step=None):
    """
    Function for creating sequences for next word prediction
    params:
        tokens: list of tokens(integers)
        seq_len: the length for each sequence to be created
    returns:
        the list of sequences(list of tokens with length of seq_len)
    """
    sequences = []
    # Handle dynamic step size calculation
    if step is None:
        step = max(1, seq_len // 2)  # Ensure minimum step size

    # Create overlapping sequences with bounds checking
    for i in range(0, len(tokens) - seq_len, step):
        end = i + seq_len + 1  # +1 for target sequence
        sequence = tokens[i: end]
        
        if len(sequence) < seq_len + 1:
            break

        sequences.append(sequence)

    return sequences


def create_sequences_batch(args):
    """ 
    Fixed sequence generation with proper windowing. 
    args:
        is the tuple of (start_index, tokens_chunck, seq_len, step)
        in the order listed
    """
    index, tokens, seq_len, step = args
    sequences  =  []

    # Handle dynamic step size calculation
    if step is None:
        step = max(1, seq_len // 2)  # Ensure minimum step size

    # Create overlapping sequences with bounds checking
    for i in range(0, len(tokens) - seq_len, step):
        end = i + seq_len + 1  # +1 for target sequence
        sequence = tokens[i: end]
        
        if len(sequence) < seq_len + 1:
            break
        sequences.append(sequence)

    return index, sequences

def fix_case(match):
    return match.group(1) + match.group(2).lower()

def clean_lines(text):
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

def preprocess_text(text, is_lowercase_text=False):
    text = regex.sub("’", "'", text) # repacle ’ with '
    text = regex.sub("‘", "'", text) # repacle ‘ with '
    text = regex.sub("“", '"', text) # repacle “ with "
    text = regex.sub("”", '"', text) # repacle ” with "

    text = regex.sub('â', 'a', text) # replace â with a
    text = regex.sub('ê', 'e', text) # replace ê with e
    text = regex.sub('î', 'i', text) # replace î with i
    text = regex.sub('ô', 'o', text) # replace ô with o
    text = regex.sub('û', 'u', text) # replace û with u
    
    text = clean_lines(text)
    text = regex.sub(r'(\n){3,}', '\n\n', text) # Removing more than one consecutive white space(empty lines)
    text = regex.sub(r'(\S)\s+\n', r'\1\n\n', text) # removing spaces between the new line and the last character of the sentence
    text = text = regex.sub(r'([aeiouAEIOU])[aeiouAEIOU]+', r'\1', text)  # Keep only one vowel when there are consecutive vowels
    text = regex.sub(r'([aeiouAEIOU])([aeiouAEIOU])([^A-Za-z])+', r'\1\3', text)  # If there are still two consecutive vowels followed by non-letter remove the second vowel
    text = regex.sub(r'([aeiouAEIOU])([aeiouAEIOU])', r'\1 \2', text) # Add a space between two vowels following each other(e.g aa -> a a
    text = regex.sub(r'^(?!\s*$)\s+', '', text, flags=regex.MULTILINE) # remove spaces before each line or sentence
    text =regex.sub(r'([aeiou])([A-Z])', fix_case, text) # When a small vawel is followed by capital letter, lowercase the following(e.g uRwanda -> urwanda)
    text = regex.sub(r'\*', ' ', text)
    text = regex.sub(r'[^\S\r\n]+', ' ', text) # Where there is more than one space within the line followed by non-space, replace it with one space( wagiye    gusura -> wagiye gusura)
    text = regex.sub(r'(\w)\s+(\p{P})', r'\1\2', text) # remove space before the punctuation mark

    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    text = url_pattern.sub(r'', text) # remove all urls

    if is_lowercase_text:
        text = text.lower()

    return text


def create_dataset(text_file_path: str, nbr_processes: int, sequence_length: int, destination_dir: str, step_size:int=None, is_text_file_path_url:bool=False, is_lowercase_text:bool=False):
    """
    Function for creation arrays of sequences you can use for training your language model
    params:
        text: is the filename path which contains the text to be used for creating sequences
        nbr_processes: is the number of processes to run in parallel for multi-cpu machine
        sequence_length: is the number of tokens each sequence will have(additional one token will be added to each sequence to support the creation of source - target )
            source - target from one sequence will be
            =========================================
                source = sequence[:seqen]
                target = sequence[-1] or sequence[seq_len]

        destination_dir: is the location folder/directory where the final sequences created will be saved
        step_size: is the number of tokens to skip/overlap for the next sequence
        is_text_file_path_url: indicates if the location of text to read is on URL or not(text file), 
        is_lowercase_text: indicates if text is converted to lowercase before creating sequences
    
        returns:
            does not returning anything. created sequences will be saved in the numpy file
    """
    training_start_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = time.time()
    total_time = time.time() - start_time

    tokenizer = KinTokenizer() # instantiating the tokenizer

    if is_text_file_path_url:
        try:
            text = requests.get(text_file_path).text
        except Exception as e:
            raise ValueError(f"Unable to read the text.\n{str(e)}")
    else:
        if not os.path.exists(text_file_path) or not os.path.isfile(text_file_path):
            raise ValueError("The text file path should be valid like folder/text.txt")
        
        if not os.path.exists(destination_dir) or not os.path.isdir(destination_dir):
            raise ValueError("The destination folder/directory should be valid and exist")
        
        if step_size is None:
            step_size = max(1, sequence_length // 2)
        

        with open(text_file_path, "r",  encoding='UTF-8', errors="ignore") as f:
            text = f.read()
        f.close()
    
    text = preprocess_text(text, is_lowercase_text)

    if len(text) < sequence_length + 2: # each process must have at least sequence_length + 2 characters
        nbr_processes = 1
    elif len(text) <= ((sequence_length + 1) * nbr_processes):
        nbr_processes = len(text) // (sequence_length + 1)
    else:
        nbr_processes = os.cpu_count()

    print("Sample text:\n\n", text[: sequence_length])
    print("\n========================================================================================================================\n")
    print("\nEncoding.........")
    encoded_text = tokenizer.encode(text, nbr_processes=nbr_processes)

    print(f"\nEncoding completed!\nCreating sequences with sequence length of {sequence_length}\n")

    print(f"\n{len(encoded_text)} tokens to be processed\n")

    if len(encoded_text) < sequence_length + 1:
        raise ValueError(f"Need at least {sequence_length+1} tokens")
    
    # Preparing arguments for each process
    total_tokens = len(encoded_text)
    total_seqs = total_tokens / sequence_length
    cpu_seqs = total_seqs / nbr_processes
    chunk_size = int(cpu_seqs * sequence_length)

    rem__size = int(((cpu_seqs * sequence_length) - chunk_size) * nbr_processes)

    args = []
    for i in range(nbr_processes):
        start_index = i * chunk_size
        
        if i != (nbr_processes -1):
            end_index = (i + 1) * chunk_size
        else:
            end_index = ((i + 1) * chunk_size)+ rem__size
        args.append((i, encoded_text[start_index: end_index], sequence_length, step_size))

    print(f"\nTotal tokens chunks: {len(args)}\n")
    # Create sequences using multiprocessing
    print(f"Creating sequences with sequence length of {sequence_length}")
    print(f"\nEach process has {chunk_size} tokens to process")
    print(f"Last process has {chunk_size + rem__size} tokens\n")
    with Pool(processes=nbr_processes) as pool:
        results = pool.map(create_sequences_batch, args)
    
    print("\nCreating sequences completed. Going to merge results from different processes")

    # Sort results by index and merge them
    print("\nSorting squences by index before merging")
    sorted_results = sorted(results, key=lambda x: x[0])

    # Combine results from each process
    sequences =  []
    for _, sequence in sorted_results:
        sequences.extend(sequence)

    print("\nCreating sequences completed!")
    print(f"\n{len(sequences)} sequences created\n")

    print("\nWriting data into numpy file\n")
    file_path = os.path.join(destination_dir, "sequences.npy")

    np.save(file_path,  np.array(sequences, dtype=np.int32))
    
    print(f"Dataset successfully saved to {file_path}")

    print("Writing data completed\n")

    total_time = time.time() - start_time
    training_end_time = datetime.datetime.now(datetime.timezone.utc)

    months, remaining = int(total_time // (3600 * 24 * 30)), total_time % (3600 * 24 * 30)
    days, remaining = int(remaining // (3600 * 24)), remaining % (3600 * 24)
    hours, remaining = int(remaining // 3600), remaining % 3600
    minutes, seconds = int(remaining // 60), int(remaining % 60)

    if months > 0:
        months = f"{months} months "
    else:
        months = ""
    
    if days > 0:
        days = f"{days} days "
    else:
        days = ""
    
    if hours > 0:
        hours = f"{hours} hours "
    else:
        hours = ""
    
    if minutes > 0:
        minutes = f"{minutes} minutes "
    else:
        minutes = ""
    
    if seconds > 0:
        seconds = f"{seconds} seconds"
    else:
        seconds = ""
    
    total_time = f"{months}{days}{hours}{minutes}{seconds}".strip()

    print(f"Sequences creation started on {training_start_time.strftime('%d-%m-%Y %H:%M:%S')} UTC\nSequences Creation ended on {training_end_time.strftime('%d-%m-%Y %H:%M:%S')} UTC\nTook: {total_time}\n\n")






