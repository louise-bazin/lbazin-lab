# Phase 1 — Comparison Report

Copy this file to `submission/phase1_report.md`, fill in every answer slot, and commit it:

```bash
cp phase-1-echo-bot/report_template.md submission/phase1_report.md
```

**How to fill it in.** Each answer sits between a pair of `<!--answer:...-->` markers. Replace
the `TODO` line with your answer — **leave the markers themselves untouched**, they are how the
grader finds your answers. Anything you write outside the markers is ignored, so add extra
prose, tables or images freely.

Numbers must **match `submission/phase1_report.json`** exactly — that file is produced by
`measure.py` and is what your figures are checked against. Copy them across; do not retype from
memory.

---

## 1. Setup facts

**Your image size**, in MB, from `gcloud artifacts docker images list` (number only, e.g. `142`):

<!--answer:image_size_mb-->
49
<!--/answer-->

**The custom VPC and subnet you created** (names only):

<!--answer:vpc_name-->
echo-net
<!--/answer-->

<!--answer:subnet_name-->
echo-subnet
<!--/answer-->

---

## 2. Measurements

Copy these from `submission/phase1_report.json`. Cold is `cold_ms`; warm median is
`stats.median`. Numbers only, in milliseconds (e.g. `812.4`).

| Platform | Cold (ms) | Warm median (ms) |
|---|---|---|
| IaaS VM | <!--answer:vm_cold_ms-->256.9<!--/answer--> | <!--answer:vm_warm_median_ms-->211.1<!--/answer--> |
| Cloud Run | <!--answer:cloudrun_cold_ms-->1833.1<!--/answer--> | <!--answer:cloudrun_warm_median_ms-->128.1<!--/answer--> |
| Cloud Function | <!--answer:function_cold_ms-->1761.4<!--/answer--> | <!--answer:function_warm_median_ms-->630.5<!--/answer--> |

Include your histogram or plot of the warm distribution below (an image, or the ASCII chart
`measure.py` prints). This is read by a human, not the grader:

<!--answer:latency_plot-->
IaaS VM Warm Distribution:
  [210-215ms] #################### (20)

Cloud Run Warm Distribution:
  [115-130ms] ########### (11)
  [620-730ms] ######### (9)

Cloud Function Warm Distribution:
  [120-135ms] ######## (8)
  [620-685ms] ############ (12)
<!--/answer-->

---

## 3. Per-platform analysis

**Scaling behaviour.** Imagine requests arriving one at a time, then ten at once, then a
hundred. For each of the three platforms, answer concretely:

- Does anything get created automatically to absorb the load — and if so, *what* exactly?
  (One platform here creates nothing at all.)
- What is the hard limit, and where does it come from — a flag you passed yourself, or the
  size of the machine you picked?

(~80 words. Your `--machine-type=e2-micro` and `--max-instances=3` are both concrete answers
to the second question.)

<!--answer:scaling_behaviour-->
The IaaS VM doesn't scale automatically: all incoming requests hit the same e2-micro instance, capped by its CPU and RAM capacity. In contrast, Cloud Run dynamically spins up new container instances as traffic grows, up to the 3-instance cap defined by our --max-instances=3 setting. Cloud Function Gen 2 behaves the same way, scaling out additional instances under load within project quotas and configured limits.
<!--/answer-->

**Deployment effort.** What did you have to build, configure and maintain to get each of the
three running? (~100 words)

<!--answer:deployment_effort-->
Deploying on the IaaS VM required the most manual work: creating a custom VPC and subnet, building and pushing a Docker image, provisioning the VM, and setting up firewall rules and container execution. For Cloud Run, we built and pushed the container image to Artifact Registry, then deployed it using `gcloud run deploy` with basic runtime settings. Cloud Function Gen 2 demanded the least operational effort: we only provided the raw Python source code and entry point. GCP automatically managed the build pipeline via Buildpacks and handled the underlying Cloud Run deployment without requiring any Docker configuration.
<!--/answer-->

---

## 4. Why do two of your three numbers look alike?

With Cloud Run and your Function both deployed, run `gcloud run services list` and paste the
**complete output** here, unedited:

<!--answer:run_services_list-->
✔
SERVICE: echo
REGION: us-central1
URL: https://echo-425292939146.us-central1.run.app
LAST DEPLOYED BY: service-425292939146@gcf-admin-robot.iam.gserviceaccount.com
LAST DEPLOYED AT: 2026-10-20T11:42:01.291033Z

✔
SERVICE: echo-bot
REGION: us-central1
URL: https://echo-bot-425292939146.us-central1.run.app
LAST DEPLOYED BY: louise.bazin@eurecom.fr
LAST DEPLOYED AT: 2026-10-20T09:50:09.264737Z
<!--/answer-->

Now explain what that output tells you about how your Function is actually being run, why its
cold start resembles Cloud Run's so closely, and what — if anything — genuinely differs between
the two deployment paths. (~120 words)

<!--answer:convergence_explanation-->
The output shows that our Cloud Function `echo` shows up directly as a Cloud Run service, deployed by GCP's internal `gcf-admin-robot` service account. This confirms that Cloud Function Gen 2 is effectively a wrapper running on top of Cloud Run. Since both rely on the exact same underlying container platform, their cold-start latencies and overall performance are virtually identical. The main distinction comes down to developer workflow: Cloud Run expects a pre-built Docker image that you build and push yourself, while Cloud Functions takes raw source code and automates the container build using Google Cloud Buildpacks.
<!--/answer-->

