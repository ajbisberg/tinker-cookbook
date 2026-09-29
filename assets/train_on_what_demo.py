"""Show which tokens get loss under different TrainOnWhat settings (role_colon renderer)."""
from tinker_cookbook import renderers
from tinker_cookbook.renderers import TrainOnWhat
from tinker_cookbook.tokenizer_utils import get_tokenizer

model = "Qwen/Qwen3.5-9B-Base"
tok = get_tokenizer(model)
renderer = renderers.get_renderer("role_colon", tok)
convo = [
    {"role": "system", "content": "Tracy likes puns."},
    {"role": "user", "content": "Smartest parrot?"},
    {"role": "assistant", "content": "African Grey. Two make pair-rots!"},
    {"role": "user", "content": "Plural of octopus?"},
    {"role": "assistant", "content": "Octopuses."},
]
for what in [TrainOnWhat.ALL_ASSISTANT_MESSAGES, TrainOnWhat.LAST_ASSISTANT_MESSAGE]:
    model_input, weights = renderer.build_supervised_example(convo, train_on_what=what)
    tokens = model_input.to_ints()
    print(f"\n=== {what.value}  ({int(weights.sum())} of {len(tokens)} tokens get loss; [brackets] = weight 1)")
    print("".join(f"[{tok.decode([t])}]" if w else tok.decode([t]) for t, w in zip(tokens, weights.tolist())))
