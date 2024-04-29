from transformers import LlamaConfig, AutoTokenizer, LlamaForCausalLM, GenerationConfig, StoppingCriteria, StoppingCriteriaList
import transformers
import torch
from auto_gptq import exllama_set_max_input_length
import os

class TextGenerator:
    def __init__(self, model_id, token):
        self.token = token
        self.model_id = model_id
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(torch.cuda.device_count())
        self.model_config = transformers.AutoConfig.from_pretrained(
            model_id,
            token=self.token,
            rope_scaling={"type": "dynamic", "factor": 2.0},
        )
        self.model = self.load_model()
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, token=token)
    
    def load_model(self):
        try:
            model = LlamaForCausalLM.from_pretrained(
                self.model_id,
                device_map="auto",
                revision="main",
                trust_remote_code=True,
                config=self.model_config,
                token=self.token
            )
            print(model.config)
            # model = exllama_set_max_input_length(model, 8192)
            print(torch.cuda.memory_summary())
            # return model.to(self.device)
            return model
        except Exception as e:
            print(torch.cuda.memory_summary())
            raise e

    def generate_text(self, prompt, max_new_tokens=600):
        inputs = self.tokenizer(prompt, return_tensors='pt')
        inputs_length = inputs["input_ids"].shape[-1]
        inputs.to(self.device)
    
        stopping_criteria = StoppingCriteriaList([
            self.StoppingCriteriaSub(start_length=inputs_length, tokenizer=self.tokenizer)
        ])
        
        gen_config = GenerationConfig(
            max_new_tokens=max_new_tokens,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        outputs = self.model.generate(**inputs, generation_config=gen_config, stopping_criteria=stopping_criteria)
        out = self.tokenizer.decode(outputs[0][inputs_length:])
        
        # post processing
        out = out.replace("</s>","") # certain models add this character
        out = out.strip() # remove white space
        out = out.split("Q:", 1)[0] # incorrect stoping tokens in certain cases can be solved with parking
        out = out.split("###", 1)[0] # debugger generates nonsense this should get ride of it
        
        # fix schema links
        lines = out.split('\n')
        schema_links_index = next((index for index, line in enumerate(lines) if line.startswith('Schema_links')), None)
        if schema_links_index is not None:
            out = '\n'.join(lines[:schema_links_index+1])
        
        # print("LLAMA Prompt --------------------------------\n" + self.tokenizer.decode(outputs[0][:inputs_length]) +"\n--------------------------------\n")
        # print("LLAMA Answer--------------------------------\n" + out +"\n--------------------------------\n")
        return out

    class StoppingCriteriaSub(StoppingCriteria):
        def __init__(self, tokenizer, stops=[], start_length=0 ):
            super().__init__()
            self.stops = stops
            self.start_length = start_length
            self.tokenizer = tokenizer

        def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor):
            if input_ids.shape[-1] < self.start_length:
                return False
            
            last_token = input_ids[-1][-1]
            second_last_token = input_ids[-1][-2]
            if "\n" == self.tokenizer.decode(last_token) and "\n" == self.tokenizer.decode(second_last_token):
                return True
            elif "Q:" == self.tokenizer.decode(last_token):
                return True
            return False

if __name__ == '__main__':
    token = "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"
    model_id = "meta-llama/Llama-2-70b-chat-hf" 
    prompt = open("input_short.txt").read()
    
    text_generator = TextGenerator(model_id, token)
    generated_text = text_generator.generate_text(prompt)
