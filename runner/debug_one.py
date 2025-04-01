import run_nb

enable_rewriter = True
modin_cores = -1
less_replication = False
measure_modin_mem = False

succ = run_nb.run_nb_paper(
  "../notebooks/lextoumbourou/feedback3-eda-hf-custom-trainer-sift",
  enable_rewriter, modin_cores, less_replication, measure_modin_mem)
assert succ
