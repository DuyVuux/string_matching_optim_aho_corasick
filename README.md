# Aho-Corasick String Matching Project

---

## **Introduction**

This project implements the Aho-Corasick algorithm for the multi-pattern string matching problem in large texts. The Aho-Corasick algorithm is an optimal solution for simultaneously searching hundreds to thousands of patterns in a single pass over the text, ensuring high accuracy and efficiency. This algorithm is widely applied in fields such as network security, natural language processing, bioinformatics, digital forensics, and modern search systems.

---

## **Multi-Pattern String Matching Problem**

**Definition:**  
Given a set of N patterns S_i and one (or multiple) texts T_j. For each text T_j, list all occurrences of each pattern S_i within T_j.

**Traditional Approach:**  
If single-pattern search algorithms (like KMP, Rabin-Karp) are applied independently for each pattern, the overall complexity is O(|T| × ∑|S_i|), which is inefficient when the number of patterns is large.

**Aho-Corasick Solution:**  
Aho-Corasick constructs a finite automaton from all the patterns, allowing all patterns to be searched in a single pass over the text with complexity O(|T| + ∑|S_i| + Z), where Z is the total number of pattern occurrences.

---

## **Theoretical Background**

### **1. Overview of the KMP Algorithm**

The KMP (Knuth-Morris-Pratt) algorithm solves the single-pattern search problem with linear complexity O(n + m). KMP uses a prefix function (LPS table) to avoid re-comparing characters already known to match. This principle is the foundation for building failure links in Aho-Corasick.

**KMP Pseudocode:**

<pre lang="md"> ```function computePrefix(pattern S):
    pi = array of zeros with length |S|
    p = 0

    for i from 1 to |S| - 1:
        while p > 0 and S[p] != S[i]:
            p = pi[p - 1]           # Move p to the last possible prefix position
        if S[p] == S[i]:
            p = p + 1
        pi[i] = p                   # Store the length of the longest prefix for position i

    return pi


function KMPSearch(pattern S, text T):
    pi = computePrefix(S)
    p = 0

    for i from 0 to |T| - 1:
        while p > 0 and S[p] != T[i]:
            p = pi[p - 1]           # Use pi to avoid redundant comparisons
        if S[p] == T[i]:
            p = p + 1
        if p == |S|:
            print("Found pattern at position " + (i - |S| + 1))
            p = pi[p - 1]           # Continue searching for next occurrences

 ``` </pre>



### **2. Problem Modeling**

- **Input:**  
  - Set of patterns P = {p_1, p_2, ..., p_k}, where each p_i is a string.
  - Text T (or multiple texts T_j), with length |T| = n.
- **Output:**  
  - List all pairs (i, j) such that pattern p_i appears in T starting at position j.

### **3. Aho-Corasick Algorithm Idea**

Aho-Corasick builds an automaton from the Trie of all patterns, enhanced with special links:

- **Goto function:** Determines the next state based on the input character.
- **Failure links (suffix links):** When no valid transition is found, this link allows the automaton to continue matching (similar to the prefix function in KMP).
- **Output function:** At each state, if a pattern ends here, this function records and outputs the matched patterns.

**Operation Flow:**  
Starting from the root state, the automaton reads each character in the text T. For each character, it transitions based on the goto function; if no valid transition exists, it follows the failure link to find a suitable state. When a state with a pattern ending is reached, the output function is used to record the matched patterns.

### **4. Trie Data Structure**

- **Trie Node Structure:**  
  - `children[]`: Array of pointers to child nodes.
  - `isEndOfWord`: Boolean flag marking the end of a pattern.
  - `failureLink`: Pointer to another node in the Trie (failure link).
  - `output`: List of patterns ending at this node.

**Trie Construction Pseudocode:**

<pre lang="md"> ```def build_trie(patterns):
    root = create_node()  # Create the root node of the trie
    
    for p in patterns:
        current_node = root
        for c in p:
            # If there is no child node for character c, create a new node
            if current_node.children.get(c) is None:
                current_node.children[c] = create_node()
            current_node = current_node.children[c]
        
        # Mark the end of a pattern
        current_node.isEndOfWord = True
        # Add the pattern to the output set of the current node (used in Aho-Corasick)
        current_node.output.add(p)
    
    return root
 ``` </pre>

### **5. Building the Aho-Corasick Automaton**

After building the Trie, failure links and output links are added to complete the automaton.

**Automaton Construction Pseudocode:**

<pre lang="md"> ```
def build_automaton(root):
    queue = [root]
    root.suffix_link = None
    while queue:
        v = queue.pop(0)
        sf = v.suffix_link
        for c in v.children:
            nxt = v.children[c]
            if v == root:
                go_sf = root
            else:
                go_sf = sf.children[c] if sf else root
            if nxt is None:
                v.go[c] = go_sf
            else:
                nxt.suffix_link = go_sf
                queue.append(nxt) 
 ``` </pre>


**Illustrative Example:**  
Given patterns S = {"di", "du", "didu", "dudua", "duadi", "didi"} and text T = "diduduadi".  
In the Aho-Corasick tree, failure links are built so that when a mismatch occurs, the automaton can transition to a suitable state without backtracking.

![Aho-Corasick Trie and Failure Links](./images/Cây%20Aho%20Corasick.png)

### **6. Searching the Text**

**Search Pseudocode:**

<pre lang="md"> ```
def search(automaton, text):
    p = automaton.root
    for i, c in enumerate(text):
        while p != automaton.root and p.go.get(c, None) is None:
            p = p.suffix_link
        if p.go.get(c, None) is not None:
            p = p.go[c]
        current = p
        while current != automaton.root:
            if current.isEndOfWord:
                for pattern in current.output:
                    print(f"Found pattern {pattern} at position {i - len(pattern) + 1}")
            current = current.suffix_link```
 ``` </pre>


### **7. Algorithm Complexity**

- **Automaton construction:** O(∑|S_i|) (with a fixed alphabet).
- **Text search:** O(|T|).
- **Space:** O(∑|S_i|).

---

## **Applications of the Aho-Corasick Algorithm**

- **Intrusion Detection:**  
  - Intrusion Detection Systems (IDS) use Aho-Corasick to compare network packets with attack signature databases, detecting suspicious activities.
- **Plagiarism Detection:**  
  - Compare texts with large databases to detect copied content.
- **Bioinformatics:**  
  - Search for gene or protein sequences in biological databases.
- **Digital Forensics:**  
  - Detect malware traces or digital evidence in large data files.

---




