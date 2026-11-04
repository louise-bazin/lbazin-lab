# Phase 2 — Reflection: where does parallelism stop helping?

Copy this file to `submission/phase2_reflection.md`, fill in every answer slot, and commit it:

```bash
cp phase-2-tiny-gpt/reflection_template.md submission/phase2_reflection.md
```

**How to fill it in.** Each answer sits between a pair of `<!--answer:...-->` markers. Replace
the `TODO` line with your answer — **leave the markers themselves untouched**, they are how the
grader finds your answers. Anything you write outside the markers is ignored, so add extra
prose, tables or your threading plot freely.

Numbers in section 1 must **match `submission/phase2_report.json`** — copy them across, do not
retype from memory; they are checked against it.

---

## 1. Your measurements

| | Value |
|---|---|
| Naive attention, ms (`attention.naive_ms`) | <!--answer:attn_naive_ms-->262.89<!--/answer--> |
| Vectorized attention, ms (`attention.vectorized_ms`) | <!--answer:attn_vectorized_ms-->1.019<!--/answer--> |
| CPU training, ms for 100 steps (`devices.cpu_ms`) | <!--answer:cpu_ms-->443376.0<!--/answer--> |
| GPU training, ms for 100 steps (`devices.gpu_ms`) | <!--answer:gpu_ms-->12826.3<!--/answer--> |
| Final training loss (`training.final_loss`) | <!--answer:final_loss-->T1.4235<!--/answer--> |

**The thread sweep.** Give your four timings from `threads` — 1, 2, 4 and 8 threads — and say
which count was fastest. (verbatim: the numbers, in order)

<!--answer:thread_sweep-->
"1": 2577.35,
"2": 2163.371,
"4": 2259.862,
"8": 2378.442,
The count 2 was the fatest
<!--/answer-->

---

## 2. Intra-node parallelism, three ways

**Why vectorizing wins.** Both attention implementations do the same arithmetic and produce the
same result (the unit test checks that). Explain where the naive version's time actually goes,
and what the vectorized one does differently — in terms of the machine, not the Python.
(~70 words)

<!--answer:vectorization_why-->
The naive version wastes most of its time in Python's overhead—stuff like type checking and creating objects inside heavy loops, while processing numbers one by one.

The vectorized version avoids Python completely by using fast C libraries. It keeps data neatly organized in memory so the CPU can run math on whole blocks of numbers at once using SIMD instructions.
<!--/answer-->

**Where the thread curve flattens, and why.** Using your sweep: more threads stopped helping —
or started hurting — at some point. Say where, and give the reason. Your Colab runtime's vCPU
count is part of the answer; so is what the threads have to coordinate on. (~80 words)

<!--answer:threading_plateau-->
Performance improved from 1 to 2 threads (2577ms to 2163ms), but regressed at 4 threads (2259ms) and 8 threads (2378ms).

Because standard Colab instances provision only 2 virtual CPUs, pushing beyond 2 threads forced the CPU to waste significant time on context switching rather than useful execution. Additionally, the extra threads created severe contention while coordinating partial sums and competing for limited shared L3 cache access.
<!--/answer-->

**What made the GPU faster.** The model, the data and the step count were identical; only the
device changed. Say what about a transformer training step suits a GPU, and name one workload
that would *not* see this speed-up. (~70 words)

<!--answer:gpu_why-->
Our training step dropped from 443,376 ms on CPU to just 12,826 ms on GPU—about 34 times faster. Transformers spend most of their time doing huge matrix math in attention layers, which GPUs handle easily by running thousands of tiny calculations at the same time.

However, a step-by-step task—like a simple Python loop where each step relies on the result before it—would not get this speedup.
<!--/answer-->

---

## 3. The question

**Where does parallelism stop helping, and why?** Pull the three experiments together. Your
answer should distinguish the *kinds* of limit you met — work that cannot be divided, hardware
you do not have, coordination that costs more than it saves, data that has to move — and say
which one bound each experiment. One concrete number from section 1 per claim. (~150 words)

<!--answer:parallelism_limit-->
Parallelism stops helping when coordination overhead, hardware limits, or architectural constraints outweigh computation benefits. Each experiment hit a different boundary:

Vectorization vs. Naive Attention: The naive implementation (which took much longer than the vectorized version's fraction of a millisecond) hit the limit of work that cannot be divided efficiently in Python. Python’s scalar loops force sequential type-checking instead of using hardware-level SIMD registers.

CPU Threading: Scaling thread performance stopped helping and regressed from 2163ms at 2 threads to 2378ms at 8 threads. Here, we ran into hardware we do not have (Colab’s 2 vCPUs) and coordination costs (context switching and L3 cache contention).

GPU Training: Moving training (step time dropping down from over 2000ms on CPU to milliseconds on GPU) accelerated matrix multiplications, but GPUs remain bound by data movement across PCIe and inherently sequential dependencies like auto-regressive decoding.
<!--/answer-->

**What you would measure next.** One experiment this phase did not run that would sharpen the
answer, and what result would change your mind. (~50 words)

<!--answer:next_experiment-->
I would test different batch sizes on a 4-vCPU or 8-vCPU machine instead of Colab.

If adding more threads actually speeds up execution on a bigger machine, it would change my mind and prove our limit was strictly Colab's hardware, not code overhead.
<!--/answer-->
