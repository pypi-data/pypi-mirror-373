import regex as re 
import pickle
import os
import multiprocessing as mp

def filter_chunk(chunk, remove_set):
    """Filter a chunk of the list, removing elements in the remove_set."""
    return [x for x in chunk if x not in remove_set]

def parallel_filter(main_list, items_to_remove, num_processes=mp.cpu_count()):
    """Filter the main list using multiprocessing."""
    # Convert items to remove into a set for efficient lookups
    remove_set = set(items_to_remove)
    
    # Divide the main list into chunks
    chunk_size = len(main_list) // num_processes
    chunks = [main_list[i:i + chunk_size] for i in range(0, len(main_list), chunk_size)]
    
    # Use multiprocessing to filter each chunk
    with mp.Pool(processes=num_processes) as pool:
        results = pool.starmap(filter_chunk, [(chunk, remove_set) for chunk in chunks])
    
    # Combine the filtered chunks into a single list
    filtered_list = [item for sublist in results for item in sublist]
    
    return filtered_list
    

if __name__ == "__main__":
    compiled_pattern = re.compile(r'\s+|\p{L}+|\p{N}+|[^\s\p{L}\p{N}]+', re.UNICODE)

    print(f"\nProcesses: {mp.cpu_count()}\n")
    nbr_process = mp.cpu_count()
    text = "naâmata yaraye ashiize sinziiempamvu byabaye kdi hariumuntu waje muri kuwa mbere anzaniyee ibintuu"
    text = """
Uwo mugabo amuha inyama n'abazikorera, baramuherekeza bamugeza ku Cyuru. Bagezeyo,
amurikira umuhungu amahaho amuzaniye. Gatsi ararya arahashwa, ariko ntibyamunyura.
Abwira nyina, ati: "Ibi byo kugaburirwa nk'umwana kandi mfite umuheto wanjye simbishaka."
Nyina, ati: "Ese mwana wanjye urashaka iki? Aho ntushaka kuzakenyuka nka so?" Bukeye nyina
ajya kwa sebukwe, (sekuru wa Gatsi) aramubwira ati: "Ibyanjye byongeye kunanira, Gatsi
namuhannye guhiga, ngo atazamera nka se, none yarananiye, uzamumpanire!" Sebukwe amaze
kubyumva, atumira Gatsi aramutonganya.Gatsi ntiyabyumva; bucya asubira i Buhambe guhiga.
Nyina yongera gusubira kwa sebukwe. Noneho sebukwe akoranya umuryango wabo awuteza
Gatsi. Araterura, ati: "Uyu mukobwa nyina wa Gatsi yaje kundegera umugabo we Syoli,
yaramuhannye guhiga mu ishyamba rya wenyine aramunanira; nanjye mbimukojeje antera
ubutaka; muzi uko byamugendekeye! None n'umuhungu we yarabyadukanye, tumuhannye
aratunanira; nguyu nimumumbarize." Ubwo Gatsi yari amaze kubyara; afite umugore n'abana.

Nuko bene wabo baramutonganya, bamuziza ko yanga kumvira abakuru: nyina na sekuru. Ariko
ibyo bamuhannye byose Gatsi ntiyabyitaho; noneho arara yigira inama yo kubacika; bukeye
aboneza iy'i Bwanacyambwe, abaririza aho abahigi baba. Babamurangira i Kigali cya Mwendo.
Gatsi ajyayo yibanisha n'abaho arubaka, yari yimukanye n'umugore n'abana be! Amaze iminsi i
Mwendo babyutsa umuhigo; bageze mu ishyamba bavumbura imbogo; ihubutse ihubirana na
Gatsi iramwesa iramwica. Inkuru igera iwabo ku Cyuru, sekuru n'abe barahurura, bahambana
Gatsi umukoroza mwinshi (umuruho w'amagorwa n'ishavu n'agahinda).
                                              165


Bimaze kugenda bityo umugani wamamara mu Rwanda, hagira uruhira umuntu bikamupfubira
bitewe n'uko aruhira ikinani, bati: "Yaruhiye Gatsi!" Iyo ni yo nkomoko yo kuruhira gatsi, ari
byo kuruhira ikinani.

Kuruhira gatsi = Kuruhira ikinani; Kugokera ubusa.



100. Yaruhiye Nyanti

Uyu mugani baca ngo: "Yaruhiye Nyanti", bawuca iyo babonye umuntu wahirimbaniye ikintu
kikarenga kikamupfubira; ni bwo bavuga, ngo: "Yaruhiye nyanti". Wakomotse kuri Nyanti ya
Mashira ya Nkuba ya Sabugabo (umubanda); ahasaga umwaka w'i 1400.

Ubwo umwami w'u Rwanda yari Mibambwe Sekarongoro, na we Mashira ari umwami w'i
Nduga ngari ya Gisali na Kibanda, atuye ku Kigina cya Ndiza (Gitarama) no mu Kivumu cya
Nyanza (Butare); akaba n'umupfumu rwamwa, asigiye na mwishywa we Munyanya. Yari afite
n'abagore benshi, barimo uw'ingumba ruharwa (umugore warongowe agasaza ataramenya
igicuni cyo kubyara); yitwaga Nyirambanza.
"""
    # normalize text
    text = re.sub("’", "'", text) # repacle ’ with '
    text = re.sub('â', 'a', text) # replace â with a
    text = re.sub('ê', 'e', text) # replace ê with e
    text = re.sub('î', 'i', text) # replace î with i
    text = re.sub('ô', 'o', text) # replace ô with o
    text = re.sub('û', 'u', text) # replace û with u

    text = re.sub(r'(\n){3,}', '\n\n', text).strip() # Removing whitespace which are not followed by non-white space characters, remove new lines(empty lines)
    text = re.sub(r'[^\sA-Za-z\'\n\r]+', ' ', text).strip()  # Replace non-letter and non-number characters, non-single quote and non-space with single space
    text = re.sub(r'(\S)\s+\n', r'\1\n\n', text) # removing spaces between the new line and the last character of the sentence
    text = re.sub(r'([aeiouAEIOU])([aeiouAEIOU])([aeiouAEIOU])+', r'\1\2', text)  # Keep only two consecutive vowels
    text = re.sub(r'([aeiouAEIOU])([aeiouAEIOU])([^A-Za-z])+', r'\1\3', text)  # If there are still two consecutive vowels followed by non-letter remove the second vowel
    text = re.sub(r'([aeiouAEIOU])([aeiouAEIOU])', r'\1 \2', text) # Add a space between two vowels following each other(e.g aa -> a a
    text = re.sub(r'^(?!\s*$)\s+', '', text, flags=re.MULTILINE) # remove spaces before each line or sentence
    text = re.sub(r'([aeiou])([A-Z])', r'\1 \2', text) # When a small vawel is followed by capital letter, add space between them(e.g uRwanda -> u Rwanda)
    text = re.sub(r'\s+', ' ', text) # Where there is more than one space, replace it with one space
    text = text.lower()

    vocab = {}
    for index in range(1, 256):
        vocab[index] = bytes([index])

    non_kinyarwanda_words_file_path = os.path.join("data", "non_kinyarwanda_words.pkl")
    with open(non_kinyarwanda_words_file_path, "rb") as f:
        non_kinyarwanda_words = pickle.load(f)

    # Splitting text into chuncks using space
    chunks = re.split(r'\s+', text)
    if len(chunks) < nbr_process:
        nbr_process = 1
    chunks = parallel_filter(main_list=chunks, items_to_remove=non_kinyarwanda_words, num_processes=nbr_process)
    
    nbr_process = mp.cpu_count()
    # reconstructing the text
    text = " ".join(chunks)
    
    # re-spliting text into chunks
    chunks = re.findall(compiled_pattern, text)
    # removing existing words in the vocabulary
    existing_words_in_vocab= [value.decode("UTF-8", errors="ignore") for _, value in vocab.items() if type(value) == bytes]

    if len(chunks) < nbr_process:
        nbr_process = 1
    chunks = parallel_filter(main_list=chunks, items_to_remove=existing_words_in_vocab, num_processes=nbr_process)
    nbr_process = mp.cpu_count()
    del existing_words_in_vocab

    print(chunks)