
import random

file_path = 'finnish_words_with_hints.txt'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

random.shuffle(lines)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
