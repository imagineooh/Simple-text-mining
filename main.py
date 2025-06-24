import requests
import re


def count_characters(input_text):
    return len(re.findall(r'\w', input_text))


def get_match_score(target_word, sentence):
    if isinstance(sentence, list):
        sentence = " ".join(sentence)

    url = f"https://api.datamuse.com/words?rel_syn={target_word}&max=10000"
    response = requests.get(url)

    ant_url = f"https://api.datamuse.com/words?rel_ant={target_word}&max=10000"
    ant = requests.get(ant_url)

    if response.status_code != 200:
        print(f"Error fetching data for {target_word}")
        return 0.0
    if ant.status_code != 200:
        print(f"Error fetching antonyms for {target_word}")
        return 0.0

    synonyms = list(set(item['word'].lower() for item in response.json()))
    synonyms.append(target_word.lower())
    antonyms = list(set(item['word'].lower() for item in ant.json()))
    antonyms.append(target_word.lower())

    words = re.findall(r'\b\w+\b', sentence.lower())

    characters = count_characters(sentence)
    word_len = count_characters(target_word)
    occurrences = 0
    score = 0.0

    for word in words:
        if word in synonyms:
            occurrences += 1
            if characters - word_len > 0:
                score += (word_len / 10) * (occurrences / (characters - word_len)) * 20
                score = min(score, 1.0)
        elif word in antonyms:
            occurrences += 1
            if characters - word_len > 0:
                score += (word_len / 10) * (occurrences / (characters - word_len)) * 0.5
                score = min(score, 1.0)
        else:
            score -= 0.001

    return abs(score)


def find_words(sentence, target_words, following, no_word, context):
    traceback = []
    meaning = []
    for i in range(len(sentence)):
        if sentence[i] == target_words[0]:
            match = True
            if i > 0 and sentence[i - 1] == no_word and no_word != "":
                match = False
            if match:
                for j in range(1, len(target_words)):
                    if i + j >= len(sentence) or sentence[i + j] != target_words[j]:
                        match = False
                        break
                if match:
                    sentence_meaning = []
                    isfree = False
                    current_sentence = sentence[i+len(target_words):i + (following + len(target_words))]
                    sorted_words = sorted(current_sentence, key=len, reverse=True)
                    top_three = sorted_words[:3]
                    check=0
                    for d in range(3):
                        synonymn = f"https://api.datamuse.com/words?rel_syn={top_three[d]}&max=10000"
                        sentence_meaning.append(synonymn)
                    for elem in sentence_meaning:
                        if elem not in meaning:
                            check += 1
                    meaning.extend(sentence_meaning)
                    if check == 3:
                        if context:
                            follow = " ".join(sentence[max(0,i-5):i + (following + len(target_words))])
                        else:
                            follow = " ".join(sentence[i:i + (following + len(target_words))])
                        traceback.append((follow, i, get_match_score(" ".join(target_words), sentence)))

    return traceback


text = (
    """Giulia sapeva che Marco non sarebbe venuto alla festa, lo sapeva che aveva altri impegni e che odiava le folle. Non sapeva che invece Lucia avrebbe portato proprio lui come sorpresa, e questo la spiazzò. Ma sapeva che avrebbe dovuto reagire con calma, come le avevano insegnato. Non sapeva che Marco l'avesse notata subito, ma in fondo lo sapeva che i suoi occhi cercavano sempre lei. Sapeva che quel sorriso significava qualcosa, e sapeva che forse, nonostante tutto, c'era ancora una possibilità tra loro. Anche se non sapeva che dire, sapeva che un silenzio a volte vale più di mille parole."""
)


target = ("sapeva che")
words = text.split()
targets = target.split()

index = find_words(words, targets, 16, "non", False) #Added the context line in update. False for no context True for five word context.

if index:
    for i in range(len(index)):
        print("Found expression:    '", index[i][0], "'    at index", index[i][1], "with score:", index[i][2])
    print("Total expressions found:", len(index))
else:
    print("No match found")
