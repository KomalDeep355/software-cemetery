# Optional TabPFN experiment
The current starter does not train TabPFN. Read Prior Labs' current setup, access, and license requirements before installing.

For a defensible experiment, collect historical snapshots and define a future label such as “no default-branch commit during the following 365 days.” Ensure every feature comes from before the snapshot. Split by repository and time to prevent leakage. Compare majority-class baseline, RandomForest, and TabPFN on the same held-out set; report class balance, balanced accuracy, dataset size, and failure cases. If you cannot make that evaluation trustworthy by the deadline, omit predictive claims and ship the evidence-first product instead.
