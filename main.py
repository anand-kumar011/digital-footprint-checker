from core.bulk_runner import run_bulk

INPUT_FILE = "input/numbers.xlsx"
OUTPUT_FILE = "output/results.xlsx"

run_bulk(INPUT_FILE, OUTPUT_FILE)

print("DONE: Bulk processing completed")
