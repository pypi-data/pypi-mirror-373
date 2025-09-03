# Sequence Length Experiments

Script to measure memory usage and throughput vs sequence length.

## Experiment Flow

1. Start with token budget (e.g., 60k tokens)
2. Fit maximum sequences at minimum length (e.g., 117 sequences × 512 tokens)
3. Double sequence length, halve number of sequences (58 × 1024, 29 × 2048, etc.)
4. Continue until minimum sequences reached
5. Increase token budget and repeat until OOM

## Usage

```shell
torchrun --nnodes=1 --nproc-per-node=8 sequence_length_experiment.py \
        --model-name-or-path 'Qwen/Qwen2.5-32B-Instruct' \
        --start-max-tokens 30000 \
        --budget-increase 10000 \
        --min-length 512 \
        --num-iterations 2 \
        --use-liger-kernels
```

## Output
JSON file with memory usage, throughput, and status for each configuration, grouped by token budget.