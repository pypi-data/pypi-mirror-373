from lt_utils.common import *
from lt_tensor.common import *
import math
from torch.nn import functional as F
from lt_tensor.misc_utils import is_fused_available

TC: TypeAlias = Callable[[Any], Tensor]


class LayerNorm(nn.Module):
    def __init__(
        self,
        d_model: int,
        bias: bool = False,
        eps: float = 1e-5,
        init_bias_eps: float = 0.0,
    ):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(d_model), requires_grad=True)
        self.eps = eps
        if bias:
            self.bias = nn.Parameter(
                torch.zeros(d_model) + init_bias_eps, requires_grad=True
            )
        else:
            self.register_parameter("bias", None)

    def forward(self, input):
        return F.layer_norm(
            input,
            normalized_shape=self.weight.shape,
            weight=self.weight,
            bias=self.bias,
            eps=self.eps,
        )


class AttentionHead(Model):
    def __init__(
        self,
        d_model: int,
        n_heads: int = 4,
        dropout: float = 0.1,
        bias: bool = True,
        std_init: float = 0.02,
    ):
        super().__init__()
        assert d_model % n_heads == 0

        self.d_head = d_model // n_heads
        self.n_heads = n_heads
        self.d_embed = d_model
        # key, query, value and output projections
        self.qkv_proj: TC = nn.Linear(d_model, 3 * d_model, bias=bias)
        self.out_proj: TC = nn.Linear(d_model, d_model, bias=bias)
        self.dropout: TC = nn.Dropout(dropout)
        self.drop = dropout
        self._init_weights(std_init)

    def _init_weights(self, std: float = 0.02):
        # apply special scaled init to the residual projections
        for pn, p in self.named_parameters():
            if "qkv_proj" in pn:
                nn.init.normal_(p, mean=0.0, std=std)

    def forward(self, x: Tensor):
        # batch size, sequence length, embedding dimensionality (n_embd)
        B, T, C = x.size()

        # calculate query, key, values for all heads in batch and move head forward to be the batch dim
        q, k, v = self.qkv_proj(x).split(self.d_embed, dim=2)
        # (B, nh, T, hs)
        k = k.view(B, T, self.n_heads, C // self.n_heads).transpose(1, 2)
        q = q.view(B, T, self.n_heads, C // self.n_heads).transpose(1, 2)
        v = v.view(B, T, self.n_heads, C // self.n_heads).transpose(1, 2)
        y = (
            F.scaled_dot_product_attention(
                query=q,
                key=k,
                value=v,
                attn_mask=None,
                dropout_p=self.drop if self.training else 0,
                is_causal=True,
            )
            .transpose(1, 2)
            .contiguous()
            .view(B, T, C)
        )
        return self.dropout(self.out_proj(y))


class MLP(Model):
    def __init__(self, d_model: int, d_hidden: int, dropout: float = 0.1):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(d_model, d_hidden),
            nn.GELU(),
            nn.Linear(d_hidden, d_model),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.mlp(x)


class DecoderLayer(nn.Module):
    def __init__(
        self,
        d_embed: int,
        n_heads: int,
        dropout: float = 0.1,
        bias: bool = True,
        attn_bias: bool = True,
        attn_std: float = 0.02,
        extended_attn: bool = True,
    ):
        super().__init__()
        self.ln1 = LayerNorm(d_embed, bias=bias)
        self.attn = AttentionHead(
            d_embed, n_heads, dropout, attn_bias, extended_attn, attn_std
        )
        self.ln2 = LayerNorm(d_embed, bias=bias)
        self.mlp = MLP(d_embed, d_embed * 4, dropout)

    def forward(self, x, output_attentions=False):
        outputs = {
            "hidden_states": None,
            "attention": None,
        }
        residual = x
        x_ln = self.ln1(x)

        attn_out = self.attn(x_ln)
        if output_attentions:
            outputs["attention"] = attn_out

        x = residual + attn_out

        residual = x
        x = self.ln2(x)
        x = residual + self.mlp(x)
        outputs["hidden_states"] = x

        return outputs


class GPTModel(Model):
    def __init__(
        self,
        vocab_size: int,
        max_seq_len: int = 2048,
        d_embed: int = 768,
        n_heads: int = 12,
        n_layers: int = 12,
        dropout: float = 0.1,
        bias: bool = True,
        attention_bias: bool = True,
        extend_attention: bool = True,
    ):
        super().__init__()
        self.d_embed = d_embed
        self.max_seq_len = max_seq_len
        self.vocab_size = vocab_size
        self.dropout = dropout
        self.n_heads = n_heads
        self.n_layers = n_layers

        self.wte = nn.Embedding(vocab_size, self.d_embed)
        self.wpe = nn.Embedding(max_seq_len, self.d_embed)
        attn_std = 0.02 / math.sqrt(2 * n_layers)
        self.blocks: List[DecoderLayer] = nn.ModuleList(
            [
                DecoderLayer(
                    d_embed,
                    n_heads,
                    dropout,
                    bias,
                    attention_bias,
                    attn_std,
                    extend_attention,
                )
                for _ in range(n_layers)
            ]
        )
        self.ln_f = nn.LayerNorm(d_embed)
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        inputs_embeds=None,
        position_ids=None,
        past_key_values=None,
        use_cache=False,
        output_hidden_states=False,
        output_attentions=False,
    ):
        if inputs_embeds is None:
            inputs_embeds = self.wte(input_ids)
        if inputs_embeds.ndim == 4:
            inputs_embeds = inputs_embeds.squeeze(1)
        B, T = inputs_embeds.shape[0], inputs_embeds.shape[1]
        if position_ids is None:
            position_ids = (
                torch.arange(T, device=inputs_embeds.device).unsqueeze(0).expand(B, T)
            )

        pos_emb = self.wpe(position_ids)
        hidden_states = inputs_embeds + pos_emb

        outputs = {"last_hidden_state": None, "hidden_states": [], "states": []}
        for i, block in enumerate(self.blocks):
            if output_hidden_states:
                outputs["hidden_states"].append(hidden_states)

            past = past_key_values[i] if past_key_values is not None else None
            block_out = block.forward(hidden_states, output_attentions)

            hidden_states = block_out.pop("hidden_states", hidden_states)
            if output_hidden_states:
                outputs["hidden_states"].append(hidden_states)
            if any([output_attentions, output_hidden_states, use_cache]):
                outputs["states"].append(block_out)

        last_hidden_state = self.ln_f(hidden_states)
        outputs["last_hidden_state"] = last_hidden_state
        if output_hidden_states:
            outputs["hidden_states"].append(last_hidden_state)

        return outputs


class GPTLMHead(Model):
    def __init__(
        self,
        vocab_size: int,
        max_seq_len: int = 1536,
        n_embd: int = 768,
        n_head: int = 8,
        n_layer: int = 8,
        dropout: int = 0.1,
    ):
        super().__init__()
        self.transformer = GPTModel(
            vocab_size=vocab_size,
            max_seq_len=max_seq_len,
            d_embed=n_embd,
            n_heads=n_head,
            n_layers=n_layer,
            dropout=dropout,
            attention_bias=True,
            extend_attention=True,
        )
        self.lm_head = nn.Linear(n_embd, vocab_size, bias=False)

    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Tuple[Tuple[torch.Tensor, torch.Tensor]]] = None,
        # head_mask: Optional[torch.FloatTensor] = None,
        use_cache: bool = False,
        output_hidden_states: bool = False,
        output_attentions: bool = False,
        return_dict: bool = False,
    ):
        if input_ids is not None and inputs_embeds is not None:
            raise ValueError("Specify either input_ids or inputs_embeds, not both.")

        outputs = self.transformer.forward(
            input_ids,
            inputs_embeds=inputs_embeds,
            position_ids=position_ids,
            past_key_values=past_key_values,
            use_cache=use_cache,
            output_hidden_states=output_hidden_states,
            output_attentions=output_attentions,
        )
        logits = self.lm_head(outputs["last_hidden_state"])
        if not return_dict:
            return logits
        outputs["logits"] = logits
        return outputs

    @torch.no_grad()
    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens=10,
        temperature=1.0,
        top_k=40,
        top_p=None,
        do_sample=True,
        return_prompt: bool = False,
        ban_logits_ids: Optional[List[int]] = None,
    ):
        generated = input_ids.clone()
        start_from = 0 if return_prompt else generated.shape[-1]
        for _ in range(max_new_tokens):
            # Only pass the last token (or full context, depending on attention setup)
            logits = self.inference(
                generated,
                # attention_mask=torch.ones_like(generated).to(dtype=torch.bool),
            )
            logits = logits[:, -1, :]  # last token's logits → [1, vocab_size]
            if ban_logits_ids:
                for ban in ban_logits_ids:
                    logits[:, ban] = float("-inf")
            # Top-k filtering
            if do_sample:
                if temperature not in [0, 1]:
                    logits = logits / temperature
                if top_k != 0:
                    top_k = min(top_k, logits.size(-1))  # safety
                    values, _ = torch.topk(logits, top_k)
                    min_value = values[:, -1].unsqueeze(1)
                    logits[logits < min_value] = float("-inf")

            # Top-p filtering
            if top_p is not None:
                sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                cumulative_probs = F.softmax(sorted_logits, dim=-1).cumsum(dim=-1)
                mask = cumulative_probs > top_p
                mask[:, 1:] = mask[:, :-1].clone()  # Shift mask
                mask[:, 0] = False  # Always keep first token
                sorted_logits[mask] = float("-inf")
                logits = torch.zeros_like(logits).scatter(
                    1, sorted_indices, sorted_logits
                )

            # Sampling or greedy
            probs = logits.softmax(dim=-1)
            if do_sample:
                next_token = probs.multinomial(num_samples=1)  # [1, 1]
            else:
                next_token = probs.argmax(dim=-1, keepdim=True)  # [1, 1]
            # Append
            generated = torch.cat((generated, next_token), dim=1)

        return generated[..., start_from:]

    def get_optimizer(
        self,
        weight_decay: float = 0.1,
        learning_rate: float = 1e-3,
        betas: Tuple = (0.9, 0.999),
        verbose: bool = True,
    ) -> optim.AdamW:
        decay_params = []
        no_decay_params = []
        for param in self.parameters():
            if not param.requires_grad:
                continue
            if param.ndim < 2:
                no_decay_params.append(param)
            else:
                decay_params.append(param)
        optim_groups = [
            {"params": decay_params, "weight_decay": weight_decay},
            {"params": no_decay_params, "weight_decay": 0.0},
        ]
        if verbose:
            num_decay_params = format(
                sum(p.numel() for p in decay_params), ","
            ).replace(",", ".")
            num_no_decay_params = format(
                sum(p.numel() for p in no_decay_params), ","
            ).replace(",", ".")
            print(
                f"num decayed parameter tensors: {len(decay_params)}, with {num_decay_params} parameters"
            )
            print(
                f"num non-decayed parameter tensors: {len(no_decay_params)}, with {num_no_decay_params} parameters"
            )
        kwargs = dict()
        if is_fused_available() and self.device.type == "cuda":
            kwargs["fused"] = True

        optimizer = optim.AdamW(optim_groups, lr=learning_rate, betas=betas, **kwargs)
        return optimizer

    def save_weights(
        self,
        path,
        optimizer: optim.AdamW,
        step: int = 0,
        epoch: int = 0,
        train_losses: List[float] = [],
        eval_losses: List[float] = [],
    ):
        torch.save(
            {
                "model": self.state_dict(),
                "optimizer": optimizer.state_dict(),
                "step": step,
                "epoch": epoch,
                "train_losses": train_losses,
                "eval_losses": eval_losses,
            },
            path,
        )

    def load_weights(
        self,
        path,
        optimizer: optim.AdamW,
        strict=False,
        assign=False,
        weights_only=False,
    ):
        from lt_utils.file_ops import is_file

        step = 0
        epoch = 0
        train_losses = []
        eval_losses = []
        if is_file(path, False):
            try:
                past_state = torch.load(path, weights_only=weights_only)
                if "model" in past_state:
                    self.load_state_dict(
                        past_state["model"], strict=strict, assign=assign
                    )
                if "optimizer" in past_state:
                    optimizer.load_state_dict(past_state["optimizer"])
                step = past_state.get("step", 0)
                epoch = past_state.get("epoch", 0)
                train_losses = past_state.get("train_losses", [])
                eval_losses = past_state.get("eval_losses", [])
            except:
                pass
        return optimizer, step, epoch, train_losses, eval_losses
