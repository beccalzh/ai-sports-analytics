from ckip_transformers.nlp import CkipNerChunker
import numpy as np

class CommentChunker:
    def __init__(self, comment_list:list):
        self.comment_list = comment_list
        self.ner_driver = CkipNerChunker(model="bert-base")
        self.unwanted = ['CARDINAL', 'DATE', 'NORP']
    
    def combine_dict(self, d1:dict, d2:dict) -> dict:
        out = {}
        for key in set(d1) | set(d2):
            out[key] = d1.get(key, []) + d2.get(key, [])
        return out

    def get_entity(self) -> list:
        ner_sentence_list = self.ner_driver(self.comment_list, use_delim=True, batch_size=256, max_length=128)
        entity_out = {}
        for sentence, ner in zip(self.comment_list, ner_sentence_list):
            res = {j.word:[sentence] for j in ner if j.ner not in self.unwanted}
            entity_out = self.combine_dict(entity_out, res)
        return entity_out
    
    def keyword_selection(self, entity_dict:dict) -> dict:
        lengths = [len(v) for v in entity_dict.values()]        
        pr95_length = np.percentile(lengths, 95)        
        pr95_dict = {k: v for k, v in entity_dict.items() if len(v) >= pr95_length}
        return pr95_dict
        
    def main(self) -> list:
        entity_out = self.get_entity()
        pr95_dict = self.keyword_selection(entity_out)
        return list(pr95_dict.keys()), list(pr95_dict.values())

