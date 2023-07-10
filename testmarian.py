from __future__ import annotations # For Python 3.7
from transformers import MarianMTModel, MarianTokenizer
from typing import Sequence

from dataclasses import dataclass

import stanza
# stanza.download('en')
# stanza_nlp = stanza.Pipeline('en')

from typing import List

def minibatch(seq, size):
    items = []
    for x in seq:
        items.append(x)
        if len(items) >= size:
            yield items
            items = []
    if items:
        yield items

# def minibatch_pad(seq, size, pad_value):
#     items = []
#     for x in seq:
#         items.append(x)
#         if len(items) >= size:
#             yield items
#             items = []
#     if items:
#         yield pad(items, size, pad_value)

@dataclass(frozen=True)
class SentenceBoundaries:
    sentence_boundaries: List[SentenceBoundary]
        
    @classmethod
    def from_doc(cls, doc: stanza.Document) -> SentenceBoundaries:
        sentence_boundaries = []
        start_idx = 0
        for sent in doc.sentences:
            sentence_boundaries.append(SentenceBoundary(text=sent.text, prefix=doc.text[start_idx:sent.tokens[0].start_char]))
            start_idx = sent.tokens[-1].end_char
        sentence_boundaries.append(SentenceBoundary(text='', prefix=doc.text[start_idx:]))
        return cls(sentence_boundaries)
    
    @property
    def nonempty_sentences(self) -> List[str]:
        return [item.text for item in self.sentence_boundaries if item.text]
    
    def map(self, d: Dict[str, str]) -> SentenceBoundaries:
        return SentenceBoundaries([SentenceBoundary(text=d.get(sb.text, sb.text),
                                                    prefix=sb.prefix) for sb in self.sentence_boundaries])
    
    def __str__(self) -> str:
        return ''.join(map(str, self.sentence_boundaries))
     
# First you will need to download the model
# stanza.download('zh')
nlp = stanza.Pipeline('zh', processors='tokenize')

for sentence in nlp.process('Сдается однокомнатная мебелированная квартира квартира. Ежемесячная плата 18 тыс.р. + свет.').sentences:
    print(sentence.text)

@dataclass(frozen=True)
class SentenceBoundary:
    text: str
    prefix: str
        
    def __str__(self):
        return self.prefix + self.text
    
class Translator:
    def __init__(self, source_lang: str, dest_lang: str, use_gpu: bool=False) -> None:
        self.use_gpu = use_gpu
        self.model_name = f'Helsinki-NLP/opus-mt-{source_lang}-{dest_lang}'
        self.model = MarianMTModel.from_pretrained(self.model_name)
        if use_gpu:
            self.model = self.model.cuda()
        self.tokenizer = MarianTokenizer.from_pretrained(self.model_name)
        self.sentencizer = stanza.Pipeline(source_lang, processors='tokenize', verbose=False, use_gpu=use_gpu)
        
    def sentencize(self, texts: Sequence[str]) -> List[SentenceBoundaries]:
        return [SentenceBoundaries.from_doc(self.sentencizer.process(text)) for text in texts]
                
    def translate(self, texts: Sequence[str], batch_size:int=10, truncation=True) -> Sequence[str]:
        if isinstance(texts, str):
            raise ValueError('Expected a sequence of texts')
        text_sentences = self.sentencize(texts)
        translations = {sent: None for text in text_sentences for sent in text.nonempty_sentences}
    
        for text_batch in minibatch(sorted(translations, key=len, reverse=True), batch_size):
            tokens = self.tokenizer(text_batch, return_tensors="pt", padding=True, truncation=truncation)
            if self.use_gpu:
                tokens = {k:v.cuda() for k, v in tokens.items()}
            translate_tokens = self.model.generate(**tokens)
            translate_batch = [self.tokenizer.decode(t, skip_special_tokens=True) for t in translate_tokens]
            for (text, translated) in zip(text_batch, translate_batch):
                translations[text] = translated
            
        return [str(text.map(translations)) for text in text_sentences]
    
marian_ru_en = Translator('ru', 'en')
print(marian_ru_en.translate(['что слишком сознавать — это болезнь, настоящая, полная болезнь.']))
# Returns: ['That being too conscious is a disease, a real, complete disease.']

marian_zh_en = Translator('zh', 'en')
o = marian_zh_en.translate(['还在笑眼睛不要了.'])
print(marian_zh_en.translate(['还在笑眼睛不要了.']))

marian_zh_vi = Translator('ru', 'en')
print(marian_zh_vi.translate(['还在笑眼睛不要了.']))
