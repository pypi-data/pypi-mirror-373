import torch
from torch import Tensor
from lt_utils.common import *
from functools import lru_cache
from torch.nn import functional as F


def _get_default_tokens():
    from string import printable

    return list(printable)


class TextTokenizer:

    def __init__(
        self,
        path: Optional[Union[str, PathLike]] = None,
        tokens: List[str] = _get_default_tokens(),
        special_token_replacer: str = "",
    ):
        self.enc_vocab = {}
        self.dec_vocab = {}

        self.pad_token_id: int = 0
        self.unk_token_id: int = 1
        self.sep_token_id: int = 2
        self.bos_token_id: int = 3
        self.eos_token_id: int = 4
        self.mask_token_id: int = 5

        self.pad_token: Tensor = torch.tensor([[0]], dtype=torch.long)
        self.unk_token: Tensor = torch.tensor([[1]], dtype=torch.long)
        self.sep_token: Tensor = torch.tensor([[2]], dtype=torch.long)
        self.bos_token: Tensor = torch.tensor([[3]], dtype=torch.long)
        self.eos_token: Tensor = torch.tensor([[4]], dtype=torch.long)
        self.mask_token: Tensor = torch.tensor([[5]], dtype=torch.long)

        self.special_tokens: List[int] = [
            self.pad_token_id,
            self.unk_token_id,
            self.sep_token_id,
            self.bos_token_id,
            self.eos_token_id,
            self.mask_token_id,
        ]
        self.special_token_replacer = special_token_replacer
        self.vocab_size = len(self.special_tokens)
        self._largest_composite = 0
        if path:
            self.load_from_file(path)
        else:
            self.load_from_list(tokens)

    def load_from_list(self, tokens: List[str], clear_previous: bool = True):
        self._clear_cache()
        if clear_previous:
            self.enc_vocab.clear()
            self.dec_vocab.clear()
        for i, char in enumerate(
            tokens, start=len(self.special_tokens)
        ):  # 0 and 1 are exclusive for the pad and unk tokens
            self.enc_vocab.update({char: i})
            self.dec_vocab.update({i: char})

        self.vocab_size: int = len(self.enc_vocab) + len(self.special_tokens)
        self._largest_composite = max([len(x) for x in tokens])

    def __len__(self):
        return self.vocab_size

    @lru_cache(maxsize=None)
    def _enc(self, char: str):
        return self.enc_vocab.get(char, self.unk_token_id)

    @lru_cache(maxsize=None)
    def _dec(self, token: int):
        return self.dec_vocab.get(token, self.special_token_replacer)

    def add_bos_token_to(
        self, tensor: Tensor, position: Literal["start", "end"] = "start"
    ):
        if position == "end":
            return torch.cat((tensor, self.bos_token.to(tensor.device)))
        return torch.cat((self.bos_token.to(tensor.device), tensor))

    def add_eos_token_to(
        self, tensor: Tensor, position: Literal["start", "end"] = "end"
    ):
        if position == "end":
            return torch.cat((tensor, self.eos_token.to(tensor.device)))
        return torch.cat((self.eos_token.to(tensor.device), tensor))

    def add_sep_token_to(
        self, tensor: Tensor, position: Literal["start", "end"] = "end"
    ):
        if position == "end":
            return torch.cat((tensor, self.sep_token.to(tensor.device)))
        return torch.cat((self.sep_token.to(tensor.device), tensor))

    def _clear_cache(self):
        self._enc.cache_clear()
        self._dec.cache_clear()

    def _lighter_encoder(
        self,
        text: str,
        add_bos_token: bool = False,
        add_eos_token: bool = False,
        add_sep_token: bool = False,
    ):
        encoded = []
        if add_bos_token:
            encoded.append(self.bos_token_id)
        for char in text:
            encoded.append(self._enc(char))
        if add_sep_token:
            encoded.append(self.sep_token_id)
        if add_eos_token:
            encoded.append(self.eos_token_id)
        return torch.tensor([encoded], dtype=torch.long)

    def encode(
        self,
        text: str,
        add_bos_token: bool = False,
        add_eos_token: bool = False,
        add_sep_token: bool = False,
    ) -> Tensor:
        if self._largest_composite < 2:
            return self._lighter_encoder(text)

        buffer = ""
        encoded = []
        if add_bos_token:
            encoded.append(self.bos_token_id)
        i = 0
        while i < len(text):
            buffer += text[i]
            i += 1

            if len(buffer) < self._largest_composite and i < len(text):
                continue

            # Try largest-> ... -> 3 → 2 → 1 char matches
            matched = False
            for j in range(self._largest_composite, 0, -1):
                if len(buffer) >= j:
                    chunk = buffer[:j]
                    if chunk in self.enc_vocab:
                        encoded.append(self.enc_vocab[chunk])
                        buffer = buffer[j:]  # Remove used part
                        matched = True
                        break

            if not matched and len(buffer) >= self._largest_composite:
                # pop first character if no match
                char = buffer[0]
                encoded.append(self.enc_vocab.get(char, self.unk_token_id))
                buffer = buffer[1:]

        # remaining buffer
        while buffer:
            for j in range(min(3, len(buffer)), 0, -1):
                chunk = buffer[:j]
                if chunk in self.enc_vocab:
                    encoded.append(self.enc_vocab[chunk])
                    buffer = buffer[j:]
                    break
            else:
                encoded.append(self.enc_vocab.get(buffer[0], self.unk_token_id))
                buffer = buffer[1:]

        if add_sep_token:
            encoded.append(self.sep_token_id)
        if add_eos_token:
            encoded.append(self.eos_token_id)

        return torch.tensor([encoded], dtype=torch.long)

    def _prepare_decode(self, content: list[int] | list[Tensor]):
        if isinstance(content, Tensor):
            return content.flatten().tolist()
        elif isinstance(content, (list, tuple)):
            from lt_utils.misc_utils import ff_list

            return ff_list(content, int)
        elif isinstance(content, int):
            assert (
                0 <= content < self.vocab
            ), "The provided token is out of index limits!"
            return [int(content)]
        ValueError("Invalid tokens, it cannot be processed!")

    def decode(self, tokens: list[int], *args, **kwargs):
        results = []
        tokens = self._prepare_decode(tokens)
        for token in tokens:
            if token in self.special_tokens:
                results.append(self.special_token_replacer)
            else:
                results.append(self.dec_vocab.get(token, ""))
        return "".join(results)

    def pad(self, input_ids: list[Tensor], from_left: bool = False):
        largest_text = max([x.size(-1) for x in input_ids])
        if from_left:
            fn = lambda x: (largest_text - x.size(-1), 0)
        else:
            fn = lambda x: (0, largest_text - x.size(-1))
        return torch.stack(
            [
                F.pad(
                    x,
                    pad=fn(x),
                    mode="constant",
                    value=self.pad_token_id,
                )
                for x in input_ids
            ],
            dim=0,
        )

    def test_tokenizer(self, text: str):
        encoded = self.encode(text)
        decoded = self.decode(encoded)
        compared = text == decoded
        return encoded, decoded, compared

    def add_missing_tokens(
        self,
        texts: Union[str, List[str]],
        verbose: bool = True,
    ):
        missing: list[str] = []

        for inp in texts:
            if inp in missing:
                continue
            if inp not in self.enc_vocab:
                missing.append(inp)
                if verbose:
                    print(f"Missing Char Found: ({inp})")

        self._clear_cache()
        if missing:

            self.vocab_size = len(self.special_tokens) + len(self.enc_vocab)
            for miss in missing:
                self.enc_vocab.update({miss: self.vocab_size})
                self.dec_vocab.update({self.vocab_size: miss})
                self.vocab_size += 1
            self._largest_composite = max([len(x) for x in self.enc_vocab])

        return missing

    def byte_encoder(
        self,
        text: str,
        *,
        add_bos_token: bool = False,
        add_sep_token: bool = False,
        add_eos_token: bool = False,
    ):
        encoded = []
        if add_bos_token and self.bos_token_id is not None:
            encoded.append(self.bos_token_id)
        [encoded.append(x) for x in list(text.encode("utf-8"))]
        if add_sep_token and self.sep_token_id is not None:
            encoded.append(self.sep_token_id)
        elif add_eos_token and self.eos_token_id is not None:
            encoded.append(self.eos_token_id)
        return torch.tensor([encoded], dtype=torch.long)

    def __call__(self, inputs: str | list[int | str], *args, **kwargs):
        if isinstance(inputs, str):
            return self.encode(inputs)
        elif isinstance(inputs, (list, tuple)):
            if not inputs:
                return ""
            if all(list(isinstance(inp, int) for inp in inputs)):
                return self.decode(inputs)
            if all(list(isinstance(inp, str) for inp in inputs)):
                return [self.encode(x, *args, **kwargs) for x in inputs]
        elif isinstance(inputs, Tensor):
            return self.decode(inputs)
        raise ValueError(f"Invalid input '{inputs}'.")

    def load_from_file(self, path: Union[str, PathLike]):
        assert Path(path).name.endswith((".pkl", ".npy"))
        from lt_utils.file_ops import load_pickle
        import numpy as np

        enc_vocab = load_pickle(path)
        if isinstance(enc_vocab, np.ndarray):
            self.enc_vocab = enc_vocab.tolist()
        else:
            self.enc_vocab = enc_vocab
        self.dec_vocab.clear()
        for text, token in self.enc_vocab.items():
            self.dec_vocab.update({token: text})
        self._clear_cache()
        self.vocab_size: int = len(self.enc_vocab) + len(self.special_tokens)

    def save_tokenizer(self, path: Union[str, PathLike]):
        from lt_utils.file_ops import save_pickle

        if not Path(path).name.endswith((".pkl", ".npy")):
            destination = Path(path, "tokenizer.npy")
        else:
            destination = path

        save_pickle(destination, self.enc_vocab)
