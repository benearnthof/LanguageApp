"""
Ingest document into the exercise database.
    Full document:
        Add full documents to exercise corpus for long form reading comprehension.
        Add full documents to enrich downstream sentence and word corpora.
    Paragraphs:
        Paragraphs for grammar & translation exercises.
    Individual Sentences: 
        Extract sentences from a document for Translation.
        Sentences from documents for Construction of Grammar Exercises.
        Sentences from documents to enhance word examples
    Words:
        Extract words be stored in global dictionary
"""
import os
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

class FrenchCorpusLoader:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.documents = []
        self.load_documents()
        
        # Download necessary NLTK data
        nltk.download('punkt')
        
        # Set the tokenizer language to French
        nltk.download('perluniprops')
        nltk.download('nonbreaking_prefixes')

    def load_documents(self):
        for filename in os.listdir(self.folder_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(self.folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.documents.append(self.process_document(content))

    def process_document(self, content):
        paragraphs = content.split('\n\n')
        processed_paragraphs = []
        
        for paragraph in paragraphs:
            sentences = sent_tokenize(paragraph, language='french')
            processed_sentences = []
            
            for sentence in sentences:
                words = word_tokenize(sentence, language='french')
                processed_sentences.append({
                    'text': sentence,
                    'words': words
                })
            
            processed_paragraphs.append({
                'text': paragraph,
                'sentences': processed_sentences
            })
        
        return {
            'text': content,
            'paragraphs': processed_paragraphs
        }

    def get_document(self, index):
        return self.documents[index]

    def get_paragraph(self, doc_index, para_index):
        return self.documents[doc_index]['paragraphs'][para_index]

    def get_sentence(self, doc_index, para_index, sent_index):
        return self.documents[doc_index]['paragraphs'][para_index]['sentences'][sent_index]

    def get_words(self, doc_index, para_index, sent_index):
        return self.documents[doc_index]['paragraphs'][para_index]['sentences'][sent_index]['words']

    def __len__(self):
        return len(self.documents)

# Example usage:
# corpus = FrenchCorpusLoader('/path/to/french/txt/files')
# first_document = corpus.get_document(0)
# first_paragraph = corpus.get_paragraph(0, 0)
# first_sentence = corpus.get_sentence(0, 0, 0)
# words_in_first_sentence = corpus.get_words(0, 0, 0)
