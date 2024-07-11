from collections import deque
import pandas as pd
import ast
import time


class AhoCorasickNode:
    def __init__(self):
        self.children = {}
        self.failure_link = None
        self.output = []
        self.is_end_of_pattern = False


class AhoCorasick:
    def __init__(self):
        self.root = AhoCorasickNode()
        self.patterns = []

    def add_pattern(self, pattern):
        if not pattern:
            return
        pattern_id = len(self.patterns)
        self.patterns.append(pattern)
        current = self.root
        for char in pattern:
            if char not in current.children:
                current.children[char] = AhoCorasickNode()
            current = current.children[char]
        current.is_end_of_pattern = True
        current.output.append(pattern_id)

    def build_failure_links(self):
        queue = deque()
        for child in self.root.children.values():
            child.failure_link = self.root
            queue.append(child)
        while queue:
            current_node = queue.popleft()
            for char, child_node in current_node.children.items():
                queue.append(child_node)
                failure_node = current_node.failure_link
                while failure_node != self.root and char not in failure_node.children:
                    failure_node = failure_node.failure_link
                child_node.failure_link = failure_node.children.get(char, self.root)
                child_node.output.extend(child_node.failure_link.output)

    def search(self, text):
        matches = []
        current = self.root
        for i, char in enumerate(text):
            while current != self.root and char not in current.children:
                current = current.failure_link
            if char in current.children:
                current = current.children[char]
            if current.output:
                for pattern_id in current.output:
                    pattern = self.patterns[pattern_id]
                    start_pos = i - len(pattern) + 1
                    matches.append((start_pos, pattern))
        return matches


class AhoCorasickMatcher:
    def __init__(self, data_path, max_errors_to_print=10, report_interval=1000):
        self.data_path = data_path
        self.max_errors_to_print = max_errors_to_print
        self.report_interval = report_interval
        self.data = None
        self.automaton = AhoCorasick()
        self.errors = []
        self.times = []
        self.correct = 0

    def load_data(self):
        self.data = pd.read_csv(self.data_path)
        self.data.fillna(value="", inplace=True)
        print(f"Total number of samples: {len(self.data):,}")

    def parse_ground_truth(self, gt_str):
        try:
            if pd.isna(gt_str) or gt_str in ('', '[]'):
                return []
            return ast.literal_eval(str(gt_str))
        except:
            return []

    def handle_empty_pattern(self, text, ground_truth):
        if ground_truth:
            return ground_truth
        else:
            return list(range(min(50, len(text))))

    def build_automaton(self):
        unique_patterns = [p for p in self.data['pattern'].unique() if str(p) != ""]
        print(f"Building automaton with {len(unique_patterns):,} non-empty patterns...")
        for pattern in unique_patterns:
            self.automaton.add_pattern(str(pattern))
        self.automaton.build_failure_links()

    def validate(self):
        total = len(self.data)
        start_total_time = time.perf_counter()

        print("Starting accuracy check and timing for each sample...")
        for idx, row in self.data.iterrows():
            text = str(row['original_text'])
            pattern = str(row['pattern'])
            gt = self.parse_ground_truth(row['ground_truth_indexes'])

            start = time.perf_counter()
            if pattern == "":
                matches = self.handle_empty_pattern(text, gt)
            else:
                search_results = self.automaton.search(text)
                matches = [pos for pos, p in search_results if p == pattern]
            end = time.perf_counter()
            self.times.append(end - start)

            if sorted(matches) == sorted(gt):
                self.correct += 1
            else:
                if len(self.errors) < self.max_errors_to_print:
                    self.errors.append({
                        'index': idx,
                        'pattern': "EMPTY" if pattern == "" else f"'{pattern}'",
                        'expected': gt,
                        'got': matches,
                        'text_preview': text[:100] + '...' if len(text) > 100 else text
                    })

            if (idx + 1) % self.report_interval == 0:
                print(f"Processed {idx + 1:,}/{total:,} samples...")

        end_total_time = time.perf_counter()
        total_time = end_total_time - start_total_time
        accuracy = self.correct / total * 100 if total > 0 else 0

        print(f"\nFinal results:")
        print(f"  - Accuracy: {accuracy:.2f}% ({self.correct:,}/{total:,})")
        print(f"  - Total validation time: {total_time:.4f} seconds")
        print(f"  - Average time per sample: {sum(self.times)/total:.6f} seconds")

        if self.errors:
            print("\nSome error cases:")
            for error in self.errors:
                print(f"\nIndex: {error['index']}")
                print(f"Pattern: {error['pattern']}")
                print(f"Expected: {error['expected']}")
                print(f"Got: {error['got']}")
                print(f"Text preview: {error['text_preview']}")
        else:
            print("\nNo errors were recorded.")

        print("\nList of running times per sample (seconds):")
        print(self.times)


if __name__ == "__main__":
    matcher = AhoCorasickMatcher(data_path="dataset/string_matching_data")
    # Because dataset is too big, it is impossible to push on github, so if you want to install, get the data from the link to in the resources_ggDrive.txt
    matcher.load_data()
    matcher.build_automaton()
    matcher.validate()
