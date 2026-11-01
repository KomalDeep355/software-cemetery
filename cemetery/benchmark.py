"""Small evaluation helpers. Add manually reviewed labels before using these metrics."""
def classification_metrics(rows):
    """rows: iterable of dicts with boolean `actual_inactive` and `predicted_inactive`."""
    rows=list(rows); tp=sum(bool(x["actual_inactive"]) and bool(x["predicted_inactive"]) for x in rows); tn=sum(not bool(x["actual_inactive"]) and not bool(x["predicted_inactive"]) for x in rows); fp=sum(not bool(x["actual_inactive"]) and bool(x["predicted_inactive"]) for x in rows); fn=sum(bool(x["actual_inactive"]) and not bool(x["predicted_inactive"]) for x in rows)
    precision=tp/(tp+fp) if tp+fp else 0.0; recall=tp/(tp+fn) if tp+fn else 0.0; total=len(rows)
    return {"n":total,"true_positive":tp,"true_negative":tn,"false_positive":fp,"false_negative":fn,"precision":precision,"recall":recall,"accuracy":(tp+tn)/total if total else 0.0,"note":"Metrics are only meaningful when labels are independently reviewed and representative."}
