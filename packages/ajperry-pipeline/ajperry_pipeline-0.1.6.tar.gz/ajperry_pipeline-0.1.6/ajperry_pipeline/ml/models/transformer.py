import torch
from transformers import AutoTokenizer
from transformers import AutoModel
from huggingface_hub import login
import os

from ajperry_pipeline.ml.utils.positional_embedding import positional_embedding
from ajperry_pipeline.ml.models.blocks.encoder import Encoder
from ajperry_pipeline.ml.models.blocks.decoder import Decoder


class Transformer(torch.nn.Module):
    """
    A sequence to sequence model which uses attention for context.

    Attributes:
        tokenizer (Tokenizer): The tokenizer used for embedding model.
        embedding_model (AutoModel): The embedding model
        max_length (int): The number of tokens taken as input.
        encoders (list[Encoder]): The models encoders.
        decoders (list[Decoder]): The models decoders.
    """
    def __init__(
        self,
        embedding_model: str="bert-base-uncased", 
        num_heads: int = 2,
        num_encoders: int = 6,
        num_nn_layers: int = 3,
        embedding_size: int = 128,
        device: str = "cpu",
        max_length: int = 20
    ):
        super().__init__() 
        # Login to hugging face to retreive encoding model
        login(token=os.getenv("HF_TOKEN2"))
        # max length of input and output
        self.max_length = max_length
        self.tokenizer = AutoTokenizer.from_pretrained(embedding_model)
        self.embedding_model = AutoModel.from_pretrained(embedding_model).to(device)

        # dynamically get the size of our embedding models output
        t_input = "hello how are you"
        tokens = self.tokenizer(t_input, return_tensors="pt")
        tokens = {k:v.to(device) for k,v in tokens.items()}
        outputs = self.embedding_model(**tokens)
        token_embeddings = outputs.last_hidden_state
        self.token_dim = token_embeddings.shape[-1]
        self.embedding_size = embedding_size
        
        
        self.encoders = [
            Encoder(self.token_dim, self.embedding_size, num_heads, num_nn_layers,device = device).to(device) 
            for i in range(num_encoders)
        ]
        self.decoders = [
            Decoder(self.token_dim, self.embedding_size, num_heads, num_nn_layers,device = device).to(device) 
            for i in range(num_encoders)
        ]
        self.linear = torch.nn.Parameter(torch.rand(self.token_dim, self.tokenizer.vocab_size)).to(device)
        self.device = device

    def forward(self, inputs: list[str]):
        tokens = self.tokenizer(inputs, return_tensors="pt", padding='max_length', truncation=True, max_length=self.max_length)
        device_tokens = {k:v.to(self.device) for k,v in tokens.items()}
        outputs = self.embedding_model(
            input_ids=device_tokens['input_ids'],
            attention_mask=device_tokens['attention_mask']               
        )
        attention_mask = device_tokens['attention_mask']
        token_embeddings = outputs.last_hidden_state
        positional_embeddings = positional_embedding(*token_embeddings.shape[-2:])
        positional_embeddings = positional_embeddings.to(self.device)
        token_embeddings = token_embeddings.to(self.device)
        token_embeddings += positional_embeddings

        
        for encoder in self.encoders:
            token_embeddings = encoder(token_embeddings, attention_mask)

        i = 0 
        decoder_inputs = [[self.tokenizer.pad_token_id] for j in range(len(inputs))]
        outputs = [[None for _ in range(self.max_length)] for j in range(len(inputs))]
        output_logits = [[None for _ in range(self.max_length)] for j in range(len(inputs))]
        ended = [self.max_length for j in range(len(inputs))]
        i = 0
        while i < self.max_length:
            decoder_inputs_j = [ self.tokenizer.decode(
                decoder_inputs[j], 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=True
            ) for j in range(len(inputs))]
            output_tokens = self.tokenizer(decoder_inputs_j, return_tensors="pt", truncation=True, padding='max_length', max_length=self.max_length)
            output_tokens = {k:v.to(self.device) for k,v in output_tokens.items()}
            outputs_tokens = self.embedding_model(**output_tokens)
            output_embeddings = outputs_tokens.last_hidden_state
            attention_mask = output_tokens['attention_mask']


            for decoder in self.decoders:
                output_embeddings = decoder(token_embeddings, output_embeddings, attention_mask, i)
                break
            # to vocab size
            logits = torch.stack([output_embeddings[:,i,:] @ self.linear for i in range(self.max_length)],dim=1)
            probs = torch.nn.functional.softmax(logits, dim=2)
            # fill in outputs (we keep the new logit/output as input to next iteration
            preds = probs.argmax(dim=2)
            for j in range(len(inputs)):
                outputs[j][i] = preds[j][i]
                if outputs[j][i] == self.tokenizer.eos_token_id:
                    # This sentence is ended
                    ended[j] = i
                output_logits[j][i] = logits[j, i]
                decoder_inputs[j].append(outputs[j][i])
            if all([i>=e for e in ended]):
                break
            i += 1
        for j in range(len(inputs)):
            outputs[j] = self.tokenizer.decode(
                outputs[j], 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=True
            )
        return output_logits, outputs, ended
