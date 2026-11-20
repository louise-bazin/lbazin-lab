# Phase 3 — Comparison Writeup

Copy this file to `submission/phase3_comparison.md`, fill in every answer slot, and commit it:

```bash
cp phase-3-mapreduce-spark/comparison_template.md submission/phase3_comparison.md
```

**How to fill it in.** Each answer sits between a pair of `<!--answer:...-->` markers. Replace
the `TODO` line with your answer — **leave the markers themselves untouched**, they are how the
grader finds your answers. Anything you write outside the markers is ignored, so add extra
prose, tables or images freely.

Numbers in section 1 must **match `submission/phase3_report.json`** — copy them across, do not
retype from memory; they are checked against it.

---

## 1. Facts from your runs

Numbers only (e.g. `12`, `20.3`, `0.041`).

| | Value |
|---|---|
| Map tasks in the cloud job (`mapreduce.num_splits`) | <!--answer:num_map_tasks-->12<!--/answer--> |
| Reduce tasks in the cloud job (`mapreduce.num_reducers`) | <!--answer:num_reduce_tasks-->4<!--/answer--> |
| Cloud MapReduce wall time, seconds (`mapreduce.cloud_elapsed_s`) | <!--answer:cloud_elapsed_s-->38.9<!--/answer--> |
| Local single-process wall time, seconds (`mapreduce.local_elapsed_s`) | <!--answer:local_elapsed_s-->0.009<!--/answer--> |
| Spark wall time for the `collect`, seconds (`tfidf.spark_elapsed_s`) | <!--answer:spark_elapsed_s-->3.9<!--/answer--> |
| Number of **stages** in the Spark job (read off notebook 2b / 3a) | <!--answer:num_stages-->4<!--/answer--> |
| Task **retries** you counted in your `--chaos` run (0 if none happened) | <!--answer:chaos_retries-->1<!--/answer--> |

**Explain the timings.** The three wall times above cover the same 60 documents, but not the
same job: the single-process run and the cloud MapReduce are *the same word count*; Spark's
time is for *TF-IDF*, which is more work (two `reduceByKey`s and a `join`). Rank the three and
explain what each is spending its time on. Say which comparison is like-for-like, and what the
Spark number — a heavier job, on one machine — tells you about where the cloud job's time goes.
(~80 words)

<!--answer:timing_explanation-->
From fastest to slowest: local Python (0.009 s), Spark TF-IDF (3.9 s), and cloud MapReduce (38.9 s). The fair comparison is local vs. cloud MapReduce because both run the exact same word count on 60 documents: local runs straight in RAM, whereas cloud MapReduce spends most of its time starting containers, sending HTTP requests, reading/writing files on GCS, and handling a retry. Spark does a heavier TF-IDF job in just 3.9 s because it runs in memory on one machine without cloud network delays.
<!--/answer-->

**What the counts tell you.** From your stage count: how many shuffles did the Spark job have,
and which operations in `spark_tfidf.py` caused them? From your retry count: roughly what
fraction of the 16 task attempts was retried, and is that what `--chaos 0.3` should produce?
(~50 words)

<!--answer:counts_interpretation-->
With 4 stages, the Spark job had 3 shuffles (ShuffledRDD), caused by the two reduceByKey calls (for tf and df) and the join between tf and idf. In the cloud job, 1 retry out of 16 tasks is 6.25%, which is lower than the expected 30% (0.3) simply because 16 tasks is a small random sample.
<!--/answer-->

---

## 2. Spark: transformations, actions, lineage

**Transformations vs actions.** Go through `spark_tfidf.py` and the notebook's Spark cells.
Name each RDD operation and say whether it is a transformation or an action. What happened
when you ran `build_tfidf_rdd` — and what happened when you ran `collect`? (~60 words)

<!--answer:transformations_vs_actions-->
In spark_tfidf.py, flatMap, map, distinct, reduceByKey, and join are all transformations, while collect in the notebook is an action. Calling build_tfidf_rdd only built the execution plan (DAG) right away without touching any data. Calling collect actually started the job across all 4 stages and sent the 5,975 TF-IDF rows back to the driver.
<!--/answer-->

**Lineage and recovery.** Using the lineage you printed in 2b and the timeline in 3a: if the
worker holding one output partition of the *first* `reduceByKey` died, what would Spark have
to recompute, and what could it reuse? Name the stage or shuffle boundary where the recovery
starts. (~50 words)

<!--answer:lineage_recovery-->
Spark would only need to recompute the lost partition from the first reduceByKey (tf) and the part of the join that uses it. Recovery starts at the shuffle boundary of that first reduceByKey (Stage 0 -> Stage 1): Spark reuses the map-side shuffle files already saved in Stage 0, plus the whole df/idf branch from the second reduceByKey.
<!--/answer-->

---

## 3. Your cloud MapReduce, mapped onto Hadoop

Name the GCP service or file that played each role (one line each):

- **JobTracker** (schedules tasks, waits for the map phase, retries failures):
  <!--answer:role_jobtracker-->Cloud Workflows (`workflow.yaml`)<!--/answer-->
- **Workers** (run your map and reduce code):
  <!--answer:role_workers-->Cloud Run (`mapreduce.py`)<!--/answer-->
- **HDFS** (holds inputs, shuffle files, outputs):
  <!--answer:role_hdfs-->Google Cloud Storage (GCS bucket)<!--/answer-->
- **Partitioner** (decides which reducer owns a key):
  <!--answer:role_partitioner-->Hash partitioning (`zlib.crc32(term.encode()) % num_reducers` in `mapreduce.py`)<!--/answer-->

**The barrier.** There is no explicit "wait for all mappers" step in `workflow.yaml`. Where,
exactly, is the barrier between the map and reduce phases — which construct provides it?
(~30 words)

<!--answer:barrier_location-->
The parallel: for: block in workflow.yaml acts as the barrier. Cloud Workflows naturally waits for all the parallel map tasks inside that loop to finish before moving on to the reduce step.
<!--/answer-->

**Idempotence.** The workflow retries a task that failed. Why is that safe with the worker as
written, and what would go wrong if `run_map` *appended* its pairs to the shuffle file instead
of overwriting it? (~60 words)

<!--answer:idempotence-->
Each map task writes to a fixed file path (shuffle/map-{split}-part-{p}.json) and overwrites it, so retrying a task just produces the exact same output. If it appended to the file instead, a task that crashed halfway through and got retried would leave duplicate pairs behind, inflating the final counts.
<!--/answer-->

**The chaos run.** What did you see in the execution log and in Logs Explorer when you ran
with `--chaos 0.3`? Did the job still succeed, and was the final answer still identical to the
local reference? (~50 words)

<!--answer:chaos_observations-->
In Logs Explorer, I saw one task fail with a simulated HTTP 503 error, and the workflow log showed it being retried right away with a 200 OK. Despite the failure, the job still succeeded in 38.9 s and gave the exact same word counts as the local run.
<!--/answer-->
