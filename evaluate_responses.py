import os
from bert_score import score

def read_file(directory, filename):
    with open(os.path.join(directory, filename), "r", encoding="utf-8") as f:
        content = f.read()
    return content

def read_files(directory, prefix):
    files = [f for f in os.listdir(directory) if f.startswith(prefix) and f.endswith(".txt")]
    contents = {}
    for file in files:
        run_number = int(file.split('_')[-1].split('.')[0])
        with open(os.path.join(directory, file), "r", encoding="utf-8") as f:
            if run_number not in contents:
                contents[run_number] = []
            contents[run_number].append(f.read())
    return contents


def calculate_bertscore(reference, candidate):
    P, R, F1 = score(candidate, reference, lang="en")
    return P.mean().item(), R.mean().item(), F1.mean().item()

def calculate_bertscore_on_one(reference, candidate):
    P, R, F1 = score([candidate], [reference], lang="en")
    return P.mean().item(), R.mean().item(), F1.mean().item()
def main_one():
    directory = "static"
    # Read expected and response files
    expected_content = read_file(directory, "expected_1.txt")
    response_content = read_file(directory, "response_1.txt")

    precision, recall, f1 = calculate_bertscore_on_one(expected_content, response_content)

    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")

def main():
    directory = "static"
    
    # Read expected and response files
    expected_contents = read_files(directory, "expected")
    response_contents = read_files(directory, "response")

    if len(expected_contents) != len(response_contents):
        print("The number of expected files and response files do not match!")
        return

    all_references = []
    all_candidates = []

    for run_number, reference_texts in expected_contents.items():
        if run_number in response_contents:
            all_references.extend(reference_texts)  # Use extend to add the list of texts
            all_candidates.extend(response_contents[run_number])

    precision, recall, f1 = calculate_bertscore(all_references, all_candidates)

    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")

if __name__ == "__main__":
    main_one()
    main()

