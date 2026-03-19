"""
Seed the database with DSA course content
Idempotent: preserves is_checked status on re-runs
"""
import sys
import time
from sqlalchemy.exc import OperationalError
from app import app  # Import the single module-level app instance
from datetime import date, timedelta
from models import db, Phase, Week, DayBlock, ChecklistItem, PhaseMastery, CourseMeta


def seed_database():
    with app.app_context():
        # Retry loop — DB container may accept connections before fully ready
        for attempt in range(10):
            try:
                db.create_all()
                break
            except OperationalError:
                print(f"DB not ready (attempt {attempt + 1}/10), retrying in 2s...")
                time.sleep(2)
        else:
            print("ERROR: Could not connect to database after 10 attempts.")
            sys.exit(1)

        # Record course start date on first run
        if not CourseMeta.query.filter_by(key='started_at').first():
            today = date.today()
            db.session.add(CourseMeta(key='started_at', value=today.isoformat()))
            # Original plan spans 104 days (March 18 to June 30)
            planned_end = today + timedelta(days=104)
            db.session.add(CourseMeta(key='planned_end', value=planned_end.isoformat()))
            db.session.flush()

        # Phase 1: Foundation
        phase1 = get_or_create_phase(1, "Foundation", "March 18 - March 31", 30, 15)
        phase1.goal = "Master basic data structures and problem-solving fundamentals"

        # Phase 1, Week 1
        week1_1 = get_or_create_week(phase1.id, 1, "Week 1: Basics & Foundations", "March 18 - March 24")

        # Pre-course: Python Toolkit — read before Day 1
        block_toolkit = get_or_create_day_block(
            week1_1.id,
            "Pre-Course: Python Toolkit (Read Before Day 1)",
            "Mar 18",
            "30 mins",
            0  # sort_order 0 = appears first
        )
        add_checklist_item(block_toolkit.id, "learning", "collections.Counter — frequency counts", "https://docs.python.org/3/library/collections.html#collections.Counter", "", 1)
        add_checklist_item(block_toolkit.id, "learning", "collections.defaultdict — dict with default values", "https://docs.python.org/3/library/collections.html#collections.defaultdict", "", 2)
        add_checklist_item(block_toolkit.id, "learning", "collections.deque — O(1) append/pop from both ends", "https://docs.python.org/3/library/collections.html#collections.deque", "", 3)
        add_checklist_item(block_toolkit.id, "learning", "heapq — min-heap: heappush, heappop, heapify, nlargest", "https://docs.python.org/3/library/heapq.html", "", 4)
        add_checklist_item(block_toolkit.id, "learning", "bisect.bisect_left / bisect_right — binary search on sorted list", "https://docs.python.org/3/library/bisect.html", "", 5)
        add_checklist_item(block_toolkit.id, "learning", "itertools.combinations / permutations", "https://docs.python.org/3/library/itertools.html#itertools-recipes", "", 6)
        add_checklist_item(block_toolkit.id, "learning", "enumerate(), zip(), any(), all()", "https://docs.python.org/3/library/functions.html", "", 7)
        add_checklist_item(block_toolkit.id, "learning", "sorted(lst, key=...) and lst.sort(reverse=True)", "https://docs.python.org/3/howto/sorting.html", "", 8)
        add_checklist_item(block_toolkit.id, "learning", "Interview pattern: always solve brute-force first, then optimize", "", "", 9)
        add_checklist_item(block_toolkit.id, "review", "Review the Priority Index and study plan", "", "", 10)

        # Day 1-2
        block1_1_1 = get_or_create_day_block(
            week1_1.id,
            "Day 1-2: List Comprehensions & Arrays Basics",
            "Mar 18-19",
            "2-3 hours",
            1
        )
        add_checklist_item(block1_1_1.id, "learning", "Python list comprehensions", "https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions", "", 1)
        add_checklist_item(block1_1_1.id, "learning", "Understand array slicing and indexing", "https://docs.python.org/3/tutorial/introduction.html#lists", "", 2)
        add_checklist_item(block1_1_1.id, "learning", "Array time complexity", "https://wiki.python.org/moin/TimeComplexity", "", 3)
        add_checklist_item(block1_1_1.id, "hackerrank", "List Comprehensions", "https://www.hackerrank.com/challenges/list-comprehensions/problem", "Easy", 4)
        add_checklist_item(block1_1_1.id, "hackerrank", "2D Arrays - DS", "https://www.hackerrank.com/challenges/2d-arrays/problem", "Easy", 5)
        add_checklist_item(block1_1_1.id, "leetcode", "1. Two Sum", "https://leetcode.com/problems/two-sum/", "Easy", 6)
        add_checklist_item(block1_1_1.id, "leetcode", "9. Palindrome Number", "https://leetcode.com/problems/palindrome-number/", "Easy", 7)
        add_checklist_item(block1_1_1.id, "learning", "Two Sum: implement brute-force O(n²) nested loops, then O(n) hash map", "", "", 8)

        # Day 3-4
        block1_1_2 = get_or_create_day_block(
            week1_1.id,
            "Day 3-4: Two Pointers & Sliding Window",
            "Mar 20-21",
            "3-4 hours",
            2
        )
        add_checklist_item(block1_1_2.id, "learning", "Two pointer technique concept", "https://neetcode.io/courses/advanced-algorithms/0", "", 1)
        add_checklist_item(block1_1_2.id, "learning", "Sliding window pattern", "https://neetcode.io/courses/advanced-algorithms/1", "", 2)
        add_checklist_item(block1_1_2.id, "learning", "When to use which technique", "https://leetcode.com/articles/two-pointer-technique/", "", 3)
        add_checklist_item(block1_1_2.id, "leetcode", "167. Two Sum II", "https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/", "Easy", 4)
        add_checklist_item(block1_1_2.id, "leetcode", "125. Valid Palindrome", "https://leetcode.com/problems/valid-palindrome/", "Easy", 5)
        add_checklist_item(block1_1_2.id, "leetcode", "3. Longest Substring Without Repeating Characters", "https://leetcode.com/problems/longest-substring-without-repeating-characters/", "Medium", 6)
        add_checklist_item(block1_1_2.id, "hackerrank", "Simple Array Sum", "https://www.hackerrank.com/challenges/simple-array-sum/problem", "Easy", 7)
        add_checklist_item(block1_1_2.id, "hackerrank", "Solve Me First", "https://www.hackerrank.com/challenges/solve-me-first/problem", "Easy", 8)
        add_checklist_item(block1_1_2.id, "learning", "Compare brute-force O(n²) vs two-pointer O(n) on sorted input", "", "", 9)

        # Day 5-6
        block1_1_3 = get_or_create_day_block(
            week1_1.id,
            "Day 5-6: Hash Maps & Dictionaries",
            "Mar 22-23",
            "2-3 hours",
            3
        )
        add_checklist_item(block1_1_3.id, "learning", "Hash map fundamentals", "https://docs.python.org/3/tutorial/datastructures.html#dictionaries", "", 1)
        add_checklist_item(block1_1_3.id, "learning", "dict.get(), dict.items(), Counter", "https://docs.python.org/3/library/stdtypes.html#dict", "", 2)
        add_checklist_item(block1_1_3.id, "learning", "Hash collisions concept", "https://en.wikipedia.org/wiki/Hash_collision", "", 3)
        add_checklist_item(block1_1_3.id, "leetcode", "242. Valid Anagram", "https://leetcode.com/problems/valid-anagram/", "Easy", 4)
        add_checklist_item(block1_1_3.id, "leetcode", "205. Isomorphic Strings", "https://leetcode.com/problems/isomorphic-strings/", "Easy", 5)
        add_checklist_item(block1_1_3.id, "leetcode", "49. Group Anagrams", "https://leetcode.com/problems/group-anagrams/", "Medium", 6)
        add_checklist_item(block1_1_3.id, "hackerrank", "Counting Valleys", "https://www.hackerrank.com/challenges/counting-valleys/problem", "Easy", 7)
        add_checklist_item(block1_1_3.id, "hackerrank", "Ransom Note", "https://www.hackerrank.com/challenges/ransom-note/problem", "Easy", 8)
        add_checklist_item(block1_1_3.id, "learning", "Valid Anagram: compare O(n log n) sorting vs O(n) Counter approach", "", "", 9)

        # Day 7
        block1_1_4 = get_or_create_day_block(
            week1_1.id,
            "Day 7: Big O Notation & Review",
            "Mar 24",
            "2-3 hours",
            4
        )
        # Big O — conceptual foundations
        add_checklist_item(block1_1_4.id, "learning", "What Big O measures: worst-case growth rate", "https://www.bigocheatsheet.com/", "", 1)
        add_checklist_item(block1_1_4.id, "learning", "O(1) — constant time (hash lookup, array index)", "https://www.bigocheatsheet.com/", "", 2)
        add_checklist_item(block1_1_4.id, "learning", "O(log n) — logarithmic (binary search, balanced BST)", "https://www.bigocheatsheet.com/", "", 3)
        add_checklist_item(block1_1_4.id, "learning", "O(n) — linear (single loop, linear search)", "https://www.bigocheatsheet.com/", "", 4)
        add_checklist_item(block1_1_4.id, "learning", "O(n log n) — linearithmic (merge sort, Tim sort)", "https://www.bigocheatsheet.com/", "", 5)
        add_checklist_item(block1_1_4.id, "learning", "O(n²) — quadratic (nested loops, bubble sort)", "https://www.bigocheatsheet.com/", "", 6)
        add_checklist_item(block1_1_4.id, "learning", "O(2^n) and O(n!) — exponential/factorial (subsets, permutations)", "https://www.bigocheatsheet.com/", "", 7)
        # Big O — analysis skills
        add_checklist_item(block1_1_4.id, "learning", "Analysing loops: single, nested, sequential", "https://www.geeksforgeeks.org/analysis-of-algorithms-set-4-analysis-of-loops/", "", 8)
        add_checklist_item(block1_1_4.id, "learning", "Analysing recursion with recurrence relations", "https://www.geeksforgeeks.org/analysis-of-algorithms-set-4-analysis-of-loops/", "", 9)
        add_checklist_item(block1_1_4.id, "learning", "Space complexity: auxiliary vs input space", "https://www.geeksforgeeks.org/g-fact-86/", "", 10)
        add_checklist_item(block1_1_4.id, "learning", "Big O of Python built-ins (list, dict, set ops)", "https://wiki.python.org/moin/TimeComplexity", "", 11)
        # Practice — analyse complexity of problems you already solved
        add_checklist_item(block1_1_4.id, "review", "Analyse: Two Sum — what is the brute-force vs hash map complexity?", "https://leetcode.com/problems/two-sum/", "Easy", 12)
        add_checklist_item(block1_1_4.id, "review", "Analyse: Valid Palindrome — time and space?", "https://leetcode.com/problems/valid-palindrome/", "Easy", 13)
        add_checklist_item(block1_1_4.id, "review", "Analyse: Valid Anagram — compare sorting vs Counter approach", "https://leetcode.com/problems/valid-anagram/", "Easy", 14)
        add_checklist_item(block1_1_4.id, "review", "Analyse: Longest Substring Without Repeating Characters — why is sliding window O(n)?", "https://leetcode.com/problems/longest-substring-without-repeating-characters/", "Medium", 15)

        # Phase 1, Week 2
        week1_2 = get_or_create_week(phase1.id, 2, "Week 2: Strings & Advanced Foundations", "March 25 - March 31")

        # Day 1-2
        block1_2_1 = get_or_create_day_block(
            week1_2.id,
            "Day 1-2: Strings & String Manipulation",
            "Mar 25-26",
            "2-3 hours",
            1
        )
        add_checklist_item(block1_2_1.id, "learning", "String methods in Python", "https://docs.python.org/3/library/stdtypes.html#string-methods", "", 1)
        add_checklist_item(block1_2_1.id, "learning", "String immutability", "https://realpython.com/python-strings/", "", 2)
        add_checklist_item(block1_2_1.id, "learning", "Common string patterns", "https://realpython.com/python-strings/", "", 3)
        add_checklist_item(block1_2_1.id, "leetcode", "344. Reverse String", "https://leetcode.com/problems/reverse-string/", "Easy", 4)
        add_checklist_item(block1_2_1.id, "leetcode", "14. Longest Common Prefix", "https://leetcode.com/problems/longest-common-prefix/", "Easy", 5)
        add_checklist_item(block1_2_1.id, "leetcode", "5. Longest Palindromic Substring", "https://leetcode.com/problems/longest-palindromic-substring/", "Medium", 6)
        add_checklist_item(block1_2_1.id, "hackerrank", "Super Reduced String", "https://www.hackerrank.com/challenges/reduced-string/problem", "Easy", 7)
        add_checklist_item(block1_2_1.id, "hackerrank", "Camel Case", "https://www.hackerrank.com/challenges/camel-case/problem", "Easy", 8)

        # Day 3-4
        block1_2_2 = get_or_create_day_block(
            week1_2.id,
            "Day 3-4: Sets & Practical Problem-Solving",
            "Mar 27-28",
            "2-3 hours",
            2
        )
        add_checklist_item(block1_2_2.id, "learning", "Set operations", "https://docs.python.org/3/tutorial/datastructures.html#sets", "", 1)
        add_checklist_item(block1_2_2.id, "learning", "Union, intersection, difference", "https://docs.python.org/3/library/stdtypes.html#frozenset.union", "", 2)
        add_checklist_item(block1_2_2.id, "learning", "Problem recognition", "https://neetcode.io/roadmap", "", 3)
        add_checklist_item(block1_2_2.id, "leetcode", "217. Contains Duplicate", "https://leetcode.com/problems/contains-duplicate/", "Easy", 4)
        add_checklist_item(block1_2_2.id, "leetcode", "136. Single Number", "https://leetcode.com/problems/single-number/", "Easy", 5)
        add_checklist_item(block1_2_2.id, "leetcode", "15. 3Sum", "https://leetcode.com/problems/3sum/", "Medium", 6)
        add_checklist_item(block1_2_2.id, "hackerrank", "No Idea!", "https://www.hackerrank.com/challenges/no-idea/problem", "Easy", 7)

        # Day 5-7
        block1_2_3 = get_or_create_day_block(
            week1_2.id,
            "Day 5-7: Binary Search & Phase 1 Wrap-up",
            "Mar 29-31",
            "2-3 hours",
            3
        )
        add_checklist_item(block1_2_3.id, "learning", "Binary search algorithm", "https://www.geeksforgeeks.org/binary-search/", "", 1)
        add_checklist_item(block1_2_3.id, "learning", "When binary search applies", "https://www.geeksforgeeks.org/binary-search/", "", 2)
        add_checklist_item(block1_2_3.id, "learning", "Edge cases in binary search", "https://leetcode.com/discuss/general-discussion/786126/python-powerful-ultimate-binary-search-template-solved-many-problems", "", 3)
        add_checklist_item(block1_2_3.id, "leetcode", "704. Binary Search", "https://leetcode.com/problems/binary-search/", "Easy", 4)
        add_checklist_item(block1_2_3.id, "leetcode", "278. First Bad Version", "https://leetcode.com/problems/first-bad-version/", "Easy", 5)
        add_checklist_item(block1_2_3.id, "leetcode", "33. Search in Rotated Sorted Array", "https://leetcode.com/problems/search-in-rotated-sorted-array/", "Medium", 6)

        # Phase 1 Mastery Checklist
        add_phase_mastery(phase1.id, "List comprehensions mastered", 1)
        add_phase_mastery(phase1.id, "Two pointers understood and practiced", 2)
        add_phase_mastery(phase1.id, "Sliding window technique solid", 3)
        add_phase_mastery(phase1.id, "Hash maps/dictionaries used fluently", 4)
        add_phase_mastery(phase1.id, "String problems solved confidently", 5)
        add_phase_mastery(phase1.id, "Sets operations known", 6)
        add_phase_mastery(phase1.id, "Binary search implemented", 7)
        add_phase_mastery(phase1.id, "Can analyze Big O complexity", 8)

        # Phase 2: Core Structures
        phase2 = get_or_create_phase(2, "Core Structures", "April 1 - April 21", 40, 18)

        # Phase 2, Week 3
        week2_3 = get_or_create_week(phase2.id, 3, "Week 3: Linked Lists - Basics", "April 1 - April 7")

        block2_3_1 = get_or_create_day_block(week2_3.id, "Day 1-2: Linked Lists - Basics", "Apr 1-2", "2-3 hours", 1)
        add_checklist_item(block2_3_1.id, "learning", "Node structure", "https://www.geeksforgeeks.org/linked-list-set-1-introduction/", "", 1)
        add_checklist_item(block2_3_1.id, "learning", "Singly linked list traversal", "https://www.geeksforgeeks.org/linked-list-set-1-introduction/", "", 2)
        add_checklist_item(block2_3_1.id, "learning", "Insert and delete operations", "https://www.geeksforgeeks.org/linked-list-set-2-inserting-a-node/", "", 3)
        add_checklist_item(block2_3_1.id, "leetcode", "206. Reverse Linked List", "https://leetcode.com/problems/reverse-linked-list/", "Easy", 4)
        add_checklist_item(block2_3_1.id, "leetcode", "21. Merge Two Sorted Lists", "https://leetcode.com/problems/merge-two-sorted-lists/", "Easy", 5)
        add_checklist_item(block2_3_1.id, "leetcode", "92. Reverse Linked List II", "https://leetcode.com/problems/reverse-linked-list-ii/", "Medium", 6)

        block2_3_2 = get_or_create_day_block(week2_3.id, "Day 3-4: Linked Lists - Advanced", "Apr 3-4", "2-3 hours", 2)
        add_checklist_item(block2_3_2.id, "learning", "Fast and slow pointer", "https://neetcode.io/courses/advanced-algorithms/24", "", 1)
        add_checklist_item(block2_3_2.id, "learning", "Cycle detection", "https://www.geeksforgeeks.org/floyds-cycle-finding-algorithm/", "", 2)
        add_checklist_item(block2_3_2.id, "learning", "Remove duplicates from list", "https://www.geeksforgeeks.org/remove-duplicates-from-a-sorted-linked-list/", "", 3)
        add_checklist_item(block2_3_2.id, "leetcode", "141. Linked List Cycle", "https://leetcode.com/problems/linked-list-cycle/", "Easy", 4)
        add_checklist_item(block2_3_2.id, "leetcode", "203. Remove Linked List Elements", "https://leetcode.com/problems/remove-linked-list-elements/", "Easy", 5)
        add_checklist_item(block2_3_2.id, "leetcode", "82. Remove Duplicates from Sorted List II", "https://leetcode.com/problems/remove-duplicates-from-sorted-list-ii/", "Medium", 6)

        block2_3_3 = get_or_create_day_block(week2_3.id, "Day 5-7: Stacks", "Apr 5-7", "2-3 hours", 3)
        add_checklist_item(block2_3_3.id, "learning", "Stack implementation using list", "https://docs.python.org/3/tutorial/datastructures.html#using-lists-as-stacks", "", 1)
        add_checklist_item(block2_3_3.id, "learning", "Push, pop, peek operations", "https://www.geeksforgeeks.org/stack-data-structure/", "", 2)
        add_checklist_item(block2_3_3.id, "learning", "LIFO principle", "https://www.geeksforgeeks.org/stack-data-structure/", "", 3)
        add_checklist_item(block2_3_3.id, "leetcode", "20. Valid Parentheses", "https://leetcode.com/problems/valid-parentheses/", "Easy", 4)
        add_checklist_item(block2_3_3.id, "leetcode", "155. Min Stack", "https://leetcode.com/problems/min-stack/", "Medium", 5)
        add_checklist_item(block2_3_3.id, "leetcode", "71. Simplify Path", "https://leetcode.com/problems/simplify-path/", "Medium", 6)

        phase2.target_problems = 40
        phase2.estimated_hours = 18
        phase2.goal = "Master linear data structures and tree basics"

        # ── Phase 2, Week 4 ──────────────────────────────────────────
        week2_4 = get_or_create_week(phase2.id, 4, "Week 4: Queues & Binary Trees", "April 8 - April 14")

        block2_4_1 = get_or_create_day_block(week2_4.id, "Day 1-3: Queues & Deques", "Apr 8-10", "2-3 hours", 1)
        add_checklist_item(block2_4_1.id, "learning", "Queue implementation", "https://www.geeksforgeeks.org/queue-data-structure/", "", 1)
        add_checklist_item(block2_4_1.id, "learning", "collections.deque", "https://docs.python.org/3/library/collections.html#collections.deque", "", 2)
        add_checklist_item(block2_4_1.id, "learning", "FIFO principle", "https://www.geeksforgeeks.org/queue-data-structure/", "", 3)
        add_checklist_item(block2_4_1.id, "learning", "Sliding window maximum", "https://www.geeksforgeeks.org/sliding-window-maximum-maximum-of-all-subarrays-of-size-k/", "", 4)
        add_checklist_item(block2_4_1.id, "leetcode", "232. Implement Queue using Stacks", "https://leetcode.com/problems/implement-queue-using-stacks/", "Easy", 5)
        add_checklist_item(block2_4_1.id, "leetcode", "933. Number of Recent Calls", "https://leetcode.com/problems/number-of-recent-calls/", "Easy", 6)
        add_checklist_item(block2_4_1.id, "leetcode", "239. Sliding Window Maximum", "https://leetcode.com/problems/sliding-window-maximum/", "Hard", 7)
        add_checklist_item(block2_4_1.id, "hackerrank", "Queue using Two Stacks", "https://www.hackerrank.com/challenges/queue-using-two-stacks/problem", "Medium", 8)

        block2_4_2 = get_or_create_day_block(week2_4.id, "Day 4-5: Binary Trees - Basics", "Apr 11-12", "2-3 hours", 2)
        add_checklist_item(block2_4_2.id, "learning", "Tree node structure", "https://www.geeksforgeeks.org/binary-tree-data-structure/", "", 1)
        add_checklist_item(block2_4_2.id, "learning", "Inorder, preorder, postorder traversals", "https://www.geeksforgeeks.org/tree-traversals-inorder-preorder-and-postorder/", "", 2)
        add_checklist_item(block2_4_2.id, "learning", "BFS (level-order traversal)", "https://www.geeksforgeeks.org/level-order-tree-traversal/", "", 3)
        add_checklist_item(block2_4_2.id, "leetcode", "94. Binary Tree Inorder Traversal", "https://leetcode.com/problems/binary-tree-inorder-traversal/", "Easy", 4)
        add_checklist_item(block2_4_2.id, "leetcode", "144. Binary Tree Preorder Traversal", "https://leetcode.com/problems/binary-tree-preorder-traversal/", "Easy", 5)
        add_checklist_item(block2_4_2.id, "leetcode", "102. Binary Tree Level Order Traversal", "https://leetcode.com/problems/binary-tree-level-order-traversal/", "Medium", 6)

        block2_4_3 = get_or_create_day_block(week2_4.id, "Day 6-7: Tree Traversals - DFS", "Apr 13-14", "2-3 hours", 3)
        add_checklist_item(block2_4_3.id, "learning", "Recursive DFS", "https://www.geeksforgeeks.org/depth-first-search-or-dfs-for-a-graph/", "", 1)
        add_checklist_item(block2_4_3.id, "learning", "Iterative DFS", "https://www.geeksforgeeks.org/iterative-depth-first-traversal/", "", 2)
        add_checklist_item(block2_4_3.id, "learning", "Path problems", "https://neetcode.io/roadmap", "", 3)
        add_checklist_item(block2_4_3.id, "leetcode", "112. Path Sum", "https://leetcode.com/problems/path-sum/", "Easy", 4)
        add_checklist_item(block2_4_3.id, "leetcode", "404. Sum of Left Leaves", "https://leetcode.com/problems/sum-of-left-leaves/", "Easy", 5)
        add_checklist_item(block2_4_3.id, "leetcode", "113. Path Sum II", "https://leetcode.com/problems/path-sum-ii/", "Medium", 6)

        # ── Phase 2, Week 5 ──────────────────────────────────────────
        week2_5 = get_or_create_week(phase2.id, 5, "Week 5: Binary Trees Advanced & BST", "April 15 - April 21")

        block2_5_1 = get_or_create_day_block(week2_5.id, "Day 1-3: Binary Trees - Advanced", "Apr 15-17", "3-4 hours", 1)
        add_checklist_item(block2_5_1.id, "learning", "Lowest common ancestor", "https://www.geeksforgeeks.org/lowest-common-ancestor-binary-tree-set-1/", "", 1)
        add_checklist_item(block2_5_1.id, "learning", "Maximum path sum", "https://www.geeksforgeeks.org/find-maximum-path-sum-in-a-binary-tree/", "", 2)
        add_checklist_item(block2_5_1.id, "learning", "Tree diameter", "https://www.geeksforgeeks.org/diameter-of-a-binary-tree/", "", 3)
        add_checklist_item(block2_5_1.id, "learning", "Serialize/deserialize", "https://www.geeksforgeeks.org/serialize-deserialize-binary-tree/", "", 4)
        add_checklist_item(block2_5_1.id, "leetcode", "236. Lowest Common Ancestor of Binary Tree", "https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/", "Medium", 5)
        add_checklist_item(block2_5_1.id, "leetcode", "124. Binary Tree Maximum Path Sum", "https://leetcode.com/problems/binary-tree-maximum-path-sum/", "Hard", 6)
        add_checklist_item(block2_5_1.id, "leetcode", "297. Serialize and Deserialize Binary Tree", "https://leetcode.com/problems/serialize-and-deserialize-binary-tree/", "Hard", 7)

        block2_5_2 = get_or_create_day_block(week2_5.id, "Day 4-5: Binary Search Trees", "Apr 18-19", "2-3 hours", 2)
        add_checklist_item(block2_5_2.id, "learning", "BST properties and validation", "https://www.geeksforgeeks.org/binary-search-tree-data-structure/", "", 1)
        add_checklist_item(block2_5_2.id, "learning", "Search, insert, delete", "https://www.geeksforgeeks.org/binary-search-tree-set-1-search-and-insertion/", "", 2)
        add_checklist_item(block2_5_2.id, "learning", "In-order gives sorted sequence", "https://www.geeksforgeeks.org/inorder-traversal-of-binary-search-tree/", "", 3)
        add_checklist_item(block2_5_2.id, "leetcode", "98. Validate Binary Search Tree", "https://leetcode.com/problems/validate-binary-search-tree/", "Medium", 4)
        add_checklist_item(block2_5_2.id, "leetcode", "230. Kth Smallest Element in BST", "https://leetcode.com/problems/kth-smallest-element-in-a-bst/", "Medium", 5)
        add_checklist_item(block2_5_2.id, "leetcode", "235. Lowest Common Ancestor of BST", "https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/", "Easy", 6)

        block2_5_3 = get_or_create_day_block(week2_5.id, "Day 6-7: Phase 2 Wrap-up & Review", "Apr 20-21", "2-3 hours", 3)
        add_checklist_item(block2_5_3.id, "learning", "Revisit all tree problems", "https://leetcode.com/tag/tree/", "", 1)
        add_checklist_item(block2_5_3.id, "learning", "Practice linked list problems", "https://leetcode.com/tag/linked-list/", "", 2)
        add_checklist_item(block2_5_3.id, "review", "Reverse Linked List", "https://leetcode.com/problems/reverse-linked-list/", "Easy", 3)
        add_checklist_item(block2_5_3.id, "review", "Valid Parentheses", "https://leetcode.com/problems/valid-parentheses/", "Easy", 4)
        add_checklist_item(block2_5_3.id, "review", "Binary Tree Inorder Traversal", "https://leetcode.com/problems/binary-tree-inorder-traversal/", "Easy", 5)
        add_checklist_item(block2_5_3.id, "review", "Validate Binary Search Tree", "https://leetcode.com/problems/validate-binary-search-tree/", "Medium", 6)

        # ── Phase 3 ───────────────────────────────────────────────────
        phase3 = get_or_create_phase(3, "Advanced Data Structures", "April 22 - May 12", 35, 20)
        phase3.goal = "Master heaps, graphs, and tries"

        # ── Phase 3, Week 6 ──────────────────────────────────────────
        week3_6 = get_or_create_week(phase3.id, 6, "Week 6: Heaps & Graphs Basics", "April 22 - April 28")

        block3_6_1 = get_or_create_day_block(week3_6.id, "Day 1-2: Heaps & Priority Queues", "Apr 22-23", "2-3 hours", 1)
        add_checklist_item(block3_6_1.id, "learning", "Min-heap and max-heap", "https://www.geeksforgeeks.org/heap-data-structure/", "", 1)
        add_checklist_item(block3_6_1.id, "learning", "heapq module in Python", "https://docs.python.org/3/library/heapq.html", "", 2)
        add_checklist_item(block3_6_1.id, "learning", "heappush, heappop, heapify", "https://docs.python.org/3/library/heapq.html", "", 3)
        add_checklist_item(block3_6_1.id, "leetcode", "703. Kth Largest Element in a Stream", "https://leetcode.com/problems/kth-largest-element-in-a-stream/", "Easy", 4)
        add_checklist_item(block3_6_1.id, "leetcode", "1046. Last Stone Weight", "https://leetcode.com/problems/last-stone-weight/", "Easy", 5)
        add_checklist_item(block3_6_1.id, "leetcode", "215. Kth Largest Element in an Array", "https://leetcode.com/problems/kth-largest-element-in-an-array/", "Medium", 6)
        add_checklist_item(block3_6_1.id, "hackerrank", "QHEAP1", "https://www.hackerrank.com/challenges/qheap1/problem", "Easy", 7)

        block3_6_2 = get_or_create_day_block(week3_6.id, "Day 3-4: Heaps - Advanced", "Apr 24-25", "3-4 hours", 2)
        add_checklist_item(block3_6_2.id, "learning", "Median of data stream", "https://www.geeksforgeeks.org/median-of-stream-of-integers-running-integers/", "", 1)
        add_checklist_item(block3_6_2.id, "learning", "Top K problems", "https://www.geeksforgeeks.org/kth-largest-element-in-an-array/", "", 2)
        add_checklist_item(block3_6_2.id, "learning", "Merge K sorted lists", "https://www.geeksforgeeks.org/merge-k-sorted-linked-lists/", "", 3)
        add_checklist_item(block3_6_2.id, "leetcode", "295. Find Median from Data Stream", "https://leetcode.com/problems/find-median-from-data-stream/", "Hard", 4)
        add_checklist_item(block3_6_2.id, "leetcode", "23. Merge k Sorted Lists", "https://leetcode.com/problems/merge-k-sorted-lists/", "Hard", 5)
        add_checklist_item(block3_6_2.id, "leetcode", "347. Top K Frequent Elements", "https://leetcode.com/problems/top-k-frequent-elements/", "Medium", 6)

        block3_6_3 = get_or_create_day_block(week3_6.id, "Day 5-7: Graphs - Basics", "Apr 26-28", "3-4 hours", 3)
        add_checklist_item(block3_6_3.id, "learning", "Graph representation (adjacency list, matrix)", "https://www.geeksforgeeks.org/graph-and-its-representations/", "", 1)
        add_checklist_item(block3_6_3.id, "learning", "DFS traversal on graphs", "https://www.geeksforgeeks.org/depth-first-search-or-dfs-for-a-graph/", "", 2)
        add_checklist_item(block3_6_3.id, "learning", "BFS traversal on graphs", "https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/", "", 3)
        add_checklist_item(block3_6_3.id, "learning", "Connected components", "https://www.geeksforgeeks.org/connected-components-in-an-undirected-graph/", "", 4)
        add_checklist_item(block3_6_3.id, "leetcode", "200. Number of Islands", "https://leetcode.com/problems/number-of-islands/", "Medium", 5)
        add_checklist_item(block3_6_3.id, "leetcode", "733. Flood Fill", "https://leetcode.com/problems/flood-fill/", "Easy", 6)
        add_checklist_item(block3_6_3.id, "leetcode", "695. Max Area of Island", "https://leetcode.com/problems/max-area-of-island/", "Medium", 7)
        add_checklist_item(block3_6_3.id, "hackerrank", "DFS: Connected Cell in a Grid", "https://www.hackerrank.com/challenges/ctci-connected-cell-in-a-grid/problem", "Medium", 8)

        # ── Phase 3, Week 7 ──────────────────────────────────────────
        week3_7 = get_or_create_week(phase3.id, 7, "Week 7: Graph Algorithms & Tries", "April 29 - May 5")

        block3_7_1 = get_or_create_day_block(week3_7.id, "Day 1-3: Graph Algorithms", "Apr 29 - May 1", "3-4 hours", 1)
        add_checklist_item(block3_7_1.id, "learning", "Topological sort", "https://www.geeksforgeeks.org/topological-sorting/", "", 1)
        add_checklist_item(block3_7_1.id, "learning", "Cycle detection", "https://www.geeksforgeeks.org/detect-cycle-in-a-graph/", "", 2)
        add_checklist_item(block3_7_1.id, "learning", "Bipartite checking", "https://www.geeksforgeeks.org/bipartite-graph/", "", 3)
        add_checklist_item(block3_7_1.id, "leetcode", "207. Course Schedule", "https://leetcode.com/problems/course-schedule/", "Medium", 4)
        add_checklist_item(block3_7_1.id, "leetcode", "210. Course Schedule II", "https://leetcode.com/problems/course-schedule-ii/", "Medium", 5)
        add_checklist_item(block3_7_1.id, "leetcode", "785. Is Graph Bipartite?", "https://leetcode.com/problems/is-graph-bipartite/", "Medium", 6)
        add_checklist_item(block3_7_1.id, "hackerrank", "BFS: Shortest Reach in a Graph", "https://www.hackerrank.com/challenges/bfs-shortest-reach/problem", "Hard", 7)

        block3_7_2 = get_or_create_day_block(week3_7.id, "Day 4-5: Shortest Path & Advanced Graphs", "May 2-3", "3-4 hours", 2)
        add_checklist_item(block3_7_2.id, "learning", "Dijkstra's algorithm", "https://www.geeksforgeeks.org/dijkstras-shortest-path-algorithm-greedy-algo-7/", "", 1)
        add_checklist_item(block3_7_2.id, "learning", "Bellman-Ford (concept)", "https://www.geeksforgeeks.org/bellman-ford-algorithm-dp-23/", "", 2)
        add_checklist_item(block3_7_2.id, "learning", "Floyd-Warshall (concept)", "https://www.geeksforgeeks.org/floyd-warshall-algorithm-dp-16/", "", 3)
        add_checklist_item(block3_7_2.id, "leetcode", "743. Network Delay Time", "https://leetcode.com/problems/network-delay-time/", "Medium", 4)
        add_checklist_item(block3_7_2.id, "leetcode", "1631. Path With Minimum Effort", "https://leetcode.com/problems/path-with-minimum-effort/", "Medium", 5)
        add_checklist_item(block3_7_2.id, "leetcode", "787. Cheapest Flights Within K Stops", "https://leetcode.com/problems/cheapest-flights-within-k-stops/", "Medium", 6)

        block3_7_3 = get_or_create_day_block(week3_7.id, "Day 6-7: Tries", "May 4-5", "2-3 hours", 3)
        add_checklist_item(block3_7_3.id, "learning", "Trie node structure", "https://www.geeksforgeeks.org/trie-insert-and-search/", "", 1)
        add_checklist_item(block3_7_3.id, "learning", "Insert, search, delete", "https://www.geeksforgeeks.org/trie-insert-and-search/", "", 2)
        add_checklist_item(block3_7_3.id, "learning", "Autocomplete", "https://www.geeksforgeeks.org/auto-complete-feature-using-trie/", "", 3)
        add_checklist_item(block3_7_3.id, "leetcode", "208. Implement Trie (Prefix Tree)", "https://leetcode.com/problems/implement-trie-prefix-tree/", "Medium", 4)
        add_checklist_item(block3_7_3.id, "leetcode", "211. Design Add and Search Words Data Structure", "https://leetcode.com/problems/design-add-and-search-words-data-structure/", "Medium", 5)
        add_checklist_item(block3_7_3.id, "leetcode", "212. Word Search II", "https://leetcode.com/problems/word-search-ii/", "Hard", 6)

        # ── Phase 3, Week 8 ──────────────────────────────────────────
        week3_8 = get_or_create_week(phase3.id, 8, "Week 8: Union-Find & Phase 3 Review", "May 6 - May 12")

        block3_8_1 = get_or_create_day_block(week3_8.id, "Day 1-3: Union-Find & Advanced Graphs", "May 6-8", "3-4 hours", 1)
        add_checklist_item(block3_8_1.id, "learning", "Union-Find (Disjoint Set Union)", "https://www.geeksforgeeks.org/union-find/", "", 1)
        add_checklist_item(block3_8_1.id, "learning", "Connected components with Union-Find", "https://www.geeksforgeeks.org/union-find/", "", 2)
        add_checklist_item(block3_8_1.id, "learning", "MST (Minimum Spanning Tree) concept", "https://www.geeksforgeeks.org/kruskals-minimum-spanning-tree-algorithm-greedy-algo-2/", "", 3)
        add_checklist_item(block3_8_1.id, "leetcode", "721. Accounts Merge", "https://leetcode.com/problems/accounts-merge/", "Medium", 4)
        add_checklist_item(block3_8_1.id, "leetcode", "547. Number of Provinces", "https://leetcode.com/problems/number-of-provinces/", "Medium", 5)
        add_checklist_item(block3_8_1.id, "leetcode", "1202. Smallest String With Swaps", "https://leetcode.com/problems/smallest-string-with-swaps/", "Medium", 6)

        block3_8_2 = get_or_create_day_block(week3_8.id, "Day 4-7: Phase 3 Review & Consolidation", "May 9-12", "3-4 hours", 2)
        add_checklist_item(block3_8_2.id, "learning", "Revisit all heap problems", "https://leetcode.com/tag/heap-priority-queue/", "", 1)
        add_checklist_item(block3_8_2.id, "learning", "Practice all graph algorithms", "https://leetcode.com/tag/graph/", "", 2)
        add_checklist_item(block3_8_2.id, "learning", "Solidify trie implementation", "https://neetcode.io/roadmap", "", 3)
        add_checklist_item(block3_8_2.id, "review", "Kth Largest Element", "https://leetcode.com/problems/kth-largest-element-in-an-array/", "Medium", 4)
        add_checklist_item(block3_8_2.id, "review", "Number of Islands", "https://leetcode.com/problems/number-of-islands/", "Medium", 5)
        add_checklist_item(block3_8_2.id, "review", "Course Schedule", "https://leetcode.com/problems/course-schedule/", "Medium", 6)
        add_checklist_item(block3_8_2.id, "review", "Implement Trie", "https://leetcode.com/problems/implement-trie-prefix-tree/", "Medium", 7)
        add_checklist_item(block3_8_2.id, "leetcode", "399. Evaluate Division", "https://leetcode.com/problems/evaluate-division/", "Medium", 8)
        add_checklist_item(block3_8_2.id, "leetcode", "1615. Maximal Network Rank", "https://leetcode.com/problems/maximal-network-rank/", "Medium", 9)

        # ── Phase 4 ───────────────────────────────────────────────────
        phase4 = get_or_create_phase(4, "Algorithms & Advanced Problem-Solving", "May 13 - June 2", 40, 22)
        phase4.goal = "Master dynamic programming, backtracking, and advanced techniques"

        # ── Phase 4, Week 9 ──────────────────────────────────────────
        week4_9 = get_or_create_week(phase4.id, 9, "Week 9: Dynamic Programming Basics", "May 13 - May 19")

        block4_9_1 = get_or_create_day_block(week4_9.id, "Day 1-3: Dynamic Programming - Basics", "May 13-15", "2-3 hours", 1)
        add_checklist_item(block4_9_1.id, "learning", "Memoization approach", "https://www.geeksforgeeks.org/memoization-1d-2d-and-3d/", "", 1)
        add_checklist_item(block4_9_1.id, "learning", "Tabulation approach", "https://www.geeksforgeeks.org/tabulation-vs-memoization/", "", 2)
        add_checklist_item(block4_9_1.id, "learning", "State definition and transitions", "https://neetcode.io/courses/advanced-algorithms/25", "", 3)
        add_checklist_item(block4_9_1.id, "learning", "Always start with recursive brute-force O(2^n), then add memoization O(n)", "", "", 4)
        add_checklist_item(block4_9_1.id, "leetcode", "70. Climbing Stairs", "https://leetcode.com/problems/climbing-stairs/", "Easy", 4)
        add_checklist_item(block4_9_1.id, "leetcode", "509. Fibonacci Number", "https://leetcode.com/problems/fibonacci-number/", "Easy", 5)
        add_checklist_item(block4_9_1.id, "leetcode", "121. Best Time to Buy and Sell Stock", "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/", "Easy", 6)
        add_checklist_item(block4_9_1.id, "hackerrank", "Fibonacci Modified", "https://www.hackerrank.com/challenges/fibonacci-modified/problem", "Medium", 7)

        block4_9_2 = get_or_create_day_block(week4_9.id, "Day 4-5: DP - 0/1 Knapsack & Variants", "May 16-17", "3-4 hours", 2)
        add_checklist_item(block4_9_2.id, "learning", "0/1 Knapsack problem", "https://www.geeksforgeeks.org/0-1-knapsack-problem-dp-10/", "", 1)
        add_checklist_item(block4_9_2.id, "learning", "Unbounded knapsack", "https://www.geeksforgeeks.org/unbounded-knapsack-repetition-items-allowed/", "", 2)
        add_checklist_item(block4_9_2.id, "learning", "Subset sum", "https://www.geeksforgeeks.org/subset-sum-problem-dp-25/", "", 3)
        add_checklist_item(block4_9_2.id, "leetcode", "322. Coin Change", "https://leetcode.com/problems/coin-change/", "Medium", 4)
        add_checklist_item(block4_9_2.id, "leetcode", "518. Coin Change 2", "https://leetcode.com/problems/coin-change-2/", "Medium", 5)
        add_checklist_item(block4_9_2.id, "leetcode", "416. Partition Equal Subset Sum", "https://leetcode.com/problems/partition-equal-subset-sum/", "Medium", 6)
        add_checklist_item(block4_9_2.id, "hackerrank", "Coin Change", "https://www.hackerrank.com/challenges/coin-change/problem", "Medium", 7)

        block4_9_3 = get_or_create_day_block(week4_9.id, "Day 6-7: DP - Subsequences", "May 18-19", "3-4 hours", 3)
        add_checklist_item(block4_9_3.id, "learning", "Longest Increasing Subsequence (LIS)", "https://www.geeksforgeeks.org/longest-increasing-subsequence-dp-3/", "", 1)
        add_checklist_item(block4_9_3.id, "learning", "Longest Common Subsequence (LCS)", "https://www.geeksforgeeks.org/longest-common-subsequence-dp-4/", "", 2)
        add_checklist_item(block4_9_3.id, "leetcode", "300. Longest Increasing Subsequence", "https://leetcode.com/problems/longest-increasing-subsequence/", "Medium", 3)
        add_checklist_item(block4_9_3.id, "leetcode", "1143. Longest Common Subsequence", "https://leetcode.com/problems/longest-common-subsequence/", "Medium", 4)
        add_checklist_item(block4_9_3.id, "leetcode", "97. Interleaving String", "https://leetcode.com/problems/interleaving-string/", "Medium", 5)

        # ── Phase 4, Week 10 ─────────────────────────────────────────
        week4_10 = get_or_create_week(phase4.id, 10, "Week 10: Dynamic Programming Advanced", "May 20 - May 26")

        block4_10_1 = get_or_create_day_block(week4_10.id, "Day 1-3: DP - Strings & Ranges", "May 20-22", "4-5 hours", 1)
        add_checklist_item(block4_10_1.id, "learning", "Edit distance (Levenshtein)", "https://www.geeksforgeeks.org/edit-distance-dp-5/", "", 1)
        add_checklist_item(block4_10_1.id, "learning", "Wildcard matching", "https://www.geeksforgeeks.org/wildcard-pattern-matching/", "", 2)
        add_checklist_item(block4_10_1.id, "leetcode", "72. Edit Distance", "https://leetcode.com/problems/edit-distance/", "Medium", 3)
        add_checklist_item(block4_10_1.id, "leetcode", "10. Regular Expression Matching", "https://leetcode.com/problems/regular-expression-matching/", "Hard", 4)
        add_checklist_item(block4_10_1.id, "leetcode", "44. Wildcard Matching", "https://leetcode.com/problems/wildcard-matching/", "Hard", 5)

        block4_10_2 = get_or_create_day_block(week4_10.id, "Day 4-5: DP - 2D Grid Problems", "May 23-24", "3-4 hours", 2)
        add_checklist_item(block4_10_2.id, "learning", "Unique paths", "https://www.geeksforgeeks.org/count-possible-paths-top-left-bottom-right-nxm-matrix/", "", 1)
        add_checklist_item(block4_10_2.id, "learning", "Min path sum", "https://www.geeksforgeeks.org/min-cost-path-dp-6/", "", 2)
        add_checklist_item(block4_10_2.id, "leetcode", "62. Unique Paths", "https://leetcode.com/problems/unique-paths/", "Medium", 3)
        add_checklist_item(block4_10_2.id, "leetcode", "64. Minimum Path Sum", "https://leetcode.com/problems/minimum-path-sum/", "Medium", 4)
        add_checklist_item(block4_10_2.id, "leetcode", "741. Cherry Pickup", "https://leetcode.com/problems/cherry-pickup/", "Hard", 5)

        block4_10_3 = get_or_create_day_block(week4_10.id, "Day 6-7: DP - House Robber & Intervals", "May 25-26", "3-4 hours", 3)
        add_checklist_item(block4_10_3.id, "learning", "House robber variants", "https://www.geeksforgeeks.org/find-maximum-possible-stolen-value-houses/", "", 1)
        add_checklist_item(block4_10_3.id, "learning", "Interval DP", "https://www.geeksforgeeks.org/introduction-to-dp-with-bitmasking/", "", 2)
        add_checklist_item(block4_10_3.id, "leetcode", "198. House Robber", "https://leetcode.com/problems/house-robber/", "Medium", 3)
        add_checklist_item(block4_10_3.id, "leetcode", "213. House Robber II", "https://leetcode.com/problems/house-robber-ii/", "Medium", 4)
        add_checklist_item(block4_10_3.id, "leetcode", "309. Best Time to Buy and Sell Stock with Cooldown", "https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/", "Medium", 5)

        # ── Phase 4, Week 11 ─────────────────────────────────────────
        week4_11 = get_or_create_week(phase4.id, 11, "Week 11: Backtracking & Phase 4 Review", "May 27 - June 2")

        block4_11_1 = get_or_create_day_block(week4_11.id, "Day 1-2: Backtracking", "May 27-28", "2-3 hours", 1)
        add_checklist_item(block4_11_1.id, "learning", "Backtracking pattern", "https://www.geeksforgeeks.org/backtracking-algorithms/", "", 1)
        add_checklist_item(block4_11_1.id, "learning", "Permutations and combinations", "https://www.geeksforgeeks.org/backtracking-algorithm-to-find-all-subsets/", "", 2)
        add_checklist_item(block4_11_1.id, "learning", "Pruning techniques", "https://www.geeksforgeeks.org/backtracking-algorithms/", "", 3)
        add_checklist_item(block4_11_1.id, "leetcode", "46. Permutations", "https://leetcode.com/problems/permutations/", "Medium", 4)
        add_checklist_item(block4_11_1.id, "leetcode", "77. Combinations", "https://leetcode.com/problems/combinations/", "Medium", 5)
        add_checklist_item(block4_11_1.id, "leetcode", "78. Subsets", "https://leetcode.com/problems/subsets/", "Medium", 6)
        add_checklist_item(block4_11_1.id, "hackerrank", "Recursive Digit Sum", "https://www.hackerrank.com/challenges/recursive-digit-sum/problem", "Medium", 7)

        block4_11_2 = get_or_create_day_block(week4_11.id, "Day 3-4: Backtracking - Advanced", "May 29-30", "3-4 hours", 2)
        add_checklist_item(block4_11_2.id, "learning", "N-Queens problem", "https://www.geeksforgeeks.org/n-queen-problem-backtracking-3/", "", 1)
        add_checklist_item(block4_11_2.id, "learning", "Sudoku solver", "https://www.geeksforgeeks.org/sudoku-backtracking-7/", "", 2)
        add_checklist_item(block4_11_2.id, "learning", "Palindrome partitioning", "https://www.geeksforgeeks.org/palindrome-partitioning-dp-17/", "", 3)
        add_checklist_item(block4_11_2.id, "leetcode", "51. N-Queens", "https://leetcode.com/problems/n-queens/", "Hard", 4)
        add_checklist_item(block4_11_2.id, "leetcode", "37. Sudoku Solver", "https://leetcode.com/problems/sudoku-solver/", "Hard", 5)
        add_checklist_item(block4_11_2.id, "leetcode", "79. Word Search", "https://leetcode.com/problems/word-search/", "Medium", 6)

        block4_11_3 = get_or_create_day_block(week4_11.id, "Day 5-7: Phase 4 Review & Consolidation", "May 31 - June 2", "3-4 hours", 3)
        add_checklist_item(block4_11_3.id, "learning", "Identify when to use DP vs Greedy", "https://www.geeksforgeeks.org/greedy-approach-vs-dynamic-programming/", "", 1)
        add_checklist_item(block4_11_3.id, "review", "Climbing Stairs", "https://leetcode.com/problems/climbing-stairs/", "Easy", 2)
        add_checklist_item(block4_11_3.id, "review", "Coin Change", "https://leetcode.com/problems/coin-change/", "Medium", 3)
        add_checklist_item(block4_11_3.id, "review", "Longest Increasing Subsequence", "https://leetcode.com/problems/longest-increasing-subsequence/", "Medium", 4)
        add_checklist_item(block4_11_3.id, "review", "Permutations", "https://leetcode.com/problems/permutations/", "Medium", 5)
        add_checklist_item(block4_11_3.id, "review", "N-Queens", "https://leetcode.com/problems/n-queens/", "Hard", 6)
        add_checklist_item(block4_11_3.id, "leetcode", "313. Super Ugly Number", "https://leetcode.com/problems/super-ugly-number/", "Medium", 7)
        add_checklist_item(block4_11_3.id, "leetcode", "264. Ugly Number II", "https://leetcode.com/problems/ugly-number-ii/", "Medium", 8)

        # ── Phase 5 ───────────────────────────────────────────────────
        phase5 = get_or_create_phase(5, "Practice & Mastery", "June 3 - June 30", 20, 14)
        phase5.goal = "Polish skills, complete timed practice sessions, and reach mastery"

        # ── Phase 5, Week 12 ─────────────────────────────────────────
        week5_12 = get_or_create_week(phase5.id, 12, "Week 12: Timed Sessions & Practice Round 1", "June 3 - June 9")

        block5_12_1 = get_or_create_day_block(week5_12.id, "Day 1-2: Timed Problem Sessions", "Jun 3-4", "2-3 hours", 1)
        add_checklist_item(block5_12_1.id, "learning", "Session 1: 15 mins per easy, 25 mins per medium", "", "", 1)
        add_checklist_item(block5_12_1.id, "leetcode", "1. Two Sum (15 mins)", "https://leetcode.com/problems/two-sum/", "Easy", 2)
        add_checklist_item(block5_12_1.id, "leetcode", "2. Add Two Numbers (25 mins)", "https://leetcode.com/problems/add-two-numbers/", "Medium", 3)
        add_checklist_item(block5_12_1.id, "leetcode", "3. Longest Substring Without Repeating Characters (20 mins)", "https://leetcode.com/problems/longest-substring-without-repeating-characters/", "Medium", 4)
        add_checklist_item(block5_12_1.id, "leetcode", "5. Longest Palindromic Substring (30 mins)", "https://leetcode.com/problems/longest-palindromic-substring/", "Medium", 5)

        block5_12_2 = get_or_create_day_block(week5_12.id, "Day 3-4: Practice Round 1", "Jun 5-6", "2-3 hours", 2)
        add_checklist_item(block5_12_2.id, "learning", "Format: 90 minutes, 2 medium problems, no hints", "", "", 1)
        add_checklist_item(block5_12_2.id, "learning", "Pick 2 random LeetCode mediums you haven't seen", "", "", 2)
        add_checklist_item(block5_12_2.id, "learning", "After: Did I solve both within time?", "", "", 3)
        add_checklist_item(block5_12_2.id, "learning", "After: Were my solutions optimal?", "", "", 4)
        add_checklist_item(block5_12_2.id, "learning", "After: Did I communicate my approach?", "", "", 5)

        block5_12_3 = get_or_create_day_block(week5_12.id, "Day 5-7: Weakness Mitigation", "Jun 7-9", "3 hours", 3)
        add_checklist_item(block5_12_3.id, "learning", "Identify 3 topics where you struggled in Mock 1", "", "", 1)
        add_checklist_item(block5_12_3.id, "learning", "Practice 3 problems per weak topic", "", "", 2)
        add_checklist_item(block5_12_3.id, "learning", "Focus on explaining approach out loud", "", "", 3)

        # ── Phase 5, Week 13 ─────────────────────────────────────────
        week5_13 = get_or_create_week(phase5.id, 13, "Week 13: Practice Rounds 2 & 3", "June 10 - June 16")

        block5_13_1 = get_or_create_day_block(week5_13.id, "Day 1-2: Practice Round 2", "Jun 10-11", "2-3 hours", 1)
        add_checklist_item(block5_13_1.id, "learning", "Format: 90 minutes, 2 medium problems", "", "", 1)
        add_checklist_item(block5_13_1.id, "learning", "Pick 2 random LeetCode mediums you haven't seen", "", "", 2)
        add_checklist_item(block5_13_1.id, "learning", "Score yourself /100 and write reflection", "", "", 3)

        block5_13_2 = get_or_create_day_block(week5_13.id, "Day 3-4: Mixed Difficulty Session", "Jun 12-13", "2 hours", 2)
        add_checklist_item(block5_13_2.id, "learning", "Timed session: 75 minutes total", "", "", 1)
        add_checklist_item(block5_13_2.id, "learning", "1 Easy problem (15 mins)", "", "", 2)
        add_checklist_item(block5_13_2.id, "learning", "1 Medium problem (30 mins)", "", "", 3)
        add_checklist_item(block5_13_2.id, "learning", "1 Hard problem (30 mins)", "", "", 4)

        block5_13_3 = get_or_create_day_block(week5_13.id, "Day 5-7: Practice Round 3", "Jun 14-16", "2-3 hours", 3)
        add_checklist_item(block5_13_3.id, "learning", "Format: 90 minutes, 2 medium problems, final polish", "", "", 1)
        add_checklist_item(block5_13_3.id, "learning", "Focus: clear communication + optimal solution", "", "", 2)
        add_checklist_item(block5_13_3.id, "learning", "Score yourself /100 and write reflection", "", "", 3)

        # ── Phase 5, Week 14 ─────────────────────────────────────────
        week5_14 = get_or_create_week(phase5.id, 14, "Week 14: Final Consolidation & Mastery", "June 17 - June 30")

        block5_14_1 = get_or_create_day_block(week5_14.id, "Day 1-3: Final Consolidation", "Jun 17-19", "3-4 hours", 1)
        add_checklist_item(block5_14_1.id, "learning", "Revisit your Top 20 favourite problems", "", "", 1)
        add_checklist_item(block5_14_1.id, "learning", "Re-code from scratch without looking at solutions", "", "", 2)
        add_checklist_item(block5_14_1.id, "learning", "Focus on the ones you found hardest", "", "", 3)

        block5_14_2 = get_or_create_day_block(week5_14.id, "Day 4-5: Edge Cases & Optimization", "Jun 20-21", "2-3 hours", 2)
        add_checklist_item(block5_14_2.id, "learning", "Create optimization notes for array problems", "", "", 1)
        add_checklist_item(block5_14_2.id, "learning", "Create optimization notes for string problems", "", "", 2)
        add_checklist_item(block5_14_2.id, "learning", "Create optimization notes for tree problems", "", "", 3)
        add_checklist_item(block5_14_2.id, "learning", "Create optimization notes for graph problems", "", "", 4)
        add_checklist_item(block5_14_2.id, "learning", "Create optimization notes for DP problems", "", "", 5)

        block5_14_3 = get_or_create_day_block(week5_14.id, "Day 6-7: Final Review & Assessment", "Jun 22-30", "2-3 hours", 3)
        add_checklist_item(block5_14_3.id, "learning", "Can solve easy in <10 mins", "", "", 1)
        add_checklist_item(block5_14_3.id, "learning", "Can solve medium in 20-30 mins", "", "", 2)
        add_checklist_item(block5_14_3.id, "learning", "Can solve hard in 40-60 mins", "", "", 3)
        add_checklist_item(block5_14_3.id, "learning", "Complexity analysis is automatic", "", "", 4)
        add_checklist_item(block5_14_3.id, "learning", "Can explain approach clearly", "", "", 5)
        add_checklist_item(block5_14_3.id, "learning", "Can ask clarifying questions", "", "", 6)
        add_checklist_item(block5_14_3.id, "learning", "Can think out loud", "", "", 7)
        add_checklist_item(block5_14_3.id, "learning", "Can handle being stuck gracefully", "", "", 8)

        # ── Mastery checklists ────────────────────────────────────────
        # Add mastery items for remaining phases
        add_phase_mastery(phase2.id, "Linked list operations solid", 1)
        add_phase_mastery(phase2.id, "Cycle detection implemented", 2)
        add_phase_mastery(phase2.id, "Stacks problems solved", 3)
        add_phase_mastery(phase2.id, "Queues with deques used", 4)
        add_phase_mastery(phase2.id, "Binary tree traversals mastered", 5)
        add_phase_mastery(phase2.id, "Can state Big O of every solution in this phase", 6)

        add_phase_mastery(phase3.id, "Heaps and priority queues solid", 1)
        add_phase_mastery(phase3.id, "Graph representation understood", 2)
        add_phase_mastery(phase3.id, "DFS and BFS implemented", 3)
        add_phase_mastery(phase3.id, "Trie implemented", 4)
        add_phase_mastery(phase3.id, "Can compare time complexity of BFS vs DFS vs Dijkstra", 5)

        add_phase_mastery(phase4.id, "DP memoization solid", 1)
        add_phase_mastery(phase4.id, "DP tabulation solid", 2)
        add_phase_mastery(phase4.id, "Backtracking pattern mastered", 3)
        add_phase_mastery(phase4.id, "N-Queens solved", 4)
        add_phase_mastery(phase4.id, "Can explain DP time/space trade-offs (memo vs tabulation vs space-optimised)", 5)

        add_phase_mastery(phase5.id, "Practice Round 1 completed", 1)
        add_phase_mastery(phase5.id, "Practice Round 2 completed", 2)
        add_phase_mastery(phase5.id, "Practice Round 3 completed", 3)
        add_phase_mastery(phase5.id, "Full mastery achieved", 4)

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # FAST TRACK — most-asked interview questions only
        # Each problem covers brute-force AND optimal solution
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        # ── Phase 6: Fast Track — Core Patterns ─────────────
        ft1 = get_or_create_phase(6, "Fast Track — Core Patterns", "4 weeks", 25, 12)
        ft1.goal = "Cover the 30 most-asked interview problems with brute-force and optimal solutions"

        # ── Week 15: Arrays, Hash Maps, Two Pointers & Sliding Window
        ft_w15 = get_or_create_week(ft1.id, 15, "Week 15: Arrays & Hash Maps", "")

        ft_b15_1 = get_or_create_day_block(ft_w15.id, "Day 1-2: Arrays & Hash Maps", "", "3-4 hours", 1)
        add_checklist_item(ft_b15_1.id, "learning", "Brute-force: nested loops O(n²) — try every pair", "https://www.geeksforgeeks.org/check-if-pair-with-given-sum-exists-in-array/", "", 1)
        add_checklist_item(ft_b15_1.id, "learning", "Optimal: hash map O(n) — single pass lookup", "https://www.geeksforgeeks.org/check-if-pair-with-given-sum-exists-in-array/", "", 2)
        add_checklist_item(ft_b15_1.id, "leetcode", "1. Two Sum", "https://leetcode.com/problems/two-sum/", "Easy", 3)
        add_checklist_item(ft_b15_1.id, "learning", "Brute-force: sort + compare neighbours O(n log n) or nested O(n²)", "https://www.geeksforgeeks.org/find-duplicates-in-on-time-and-constant-extra-space/", "", 4)
        add_checklist_item(ft_b15_1.id, "learning", "Optimal: hash set O(n) — single pass", "https://www.geeksforgeeks.org/find-duplicates-in-on-time-and-constant-extra-space/", "", 5)
        add_checklist_item(ft_b15_1.id, "leetcode", "217. Contains Duplicate", "https://leetcode.com/problems/contains-duplicate/", "Easy", 6)
        add_checklist_item(ft_b15_1.id, "learning", "Brute-force: sort both strings O(n log n)", "https://www.geeksforgeeks.org/check-whether-two-strings-are-anagram-of-each-other/", "", 7)
        add_checklist_item(ft_b15_1.id, "learning", "Optimal: Counter / frequency array O(n)", "https://www.geeksforgeeks.org/check-whether-two-strings-are-anagram-of-each-other/", "", 8)
        add_checklist_item(ft_b15_1.id, "leetcode", "242. Valid Anagram", "https://leetcode.com/problems/valid-anagram/", "Easy", 9)
        add_checklist_item(ft_b15_1.id, "learning", "Brute-force: compare all pairs of strings O(n² · k)", "https://www.geeksforgeeks.org/given-a-sequence-of-words-print-all-anagrams-together/", "", 10)
        add_checklist_item(ft_b15_1.id, "learning", "Optimal: sorted-string key in hash map O(n · k log k)", "https://www.geeksforgeeks.org/given-a-sequence-of-words-print-all-anagrams-together/", "", 11)
        add_checklist_item(ft_b15_1.id, "leetcode", "49. Group Anagrams", "https://leetcode.com/problems/group-anagrams/", "Medium", 12)
        add_checklist_item(ft_b15_1.id, "learning", "Brute-force: count frequency + sort O(n log n)", "https://www.geeksforgeeks.org/find-k-numbers-occurrences-given-array/", "", 13)
        add_checklist_item(ft_b15_1.id, "learning", "Optimal: bucket sort O(n)", "https://www.geeksforgeeks.org/find-k-numbers-occurrences-given-array/", "", 14)
        add_checklist_item(ft_b15_1.id, "leetcode", "347. Top K Frequent Elements", "https://leetcode.com/problems/top-k-frequent-elements/", "Medium", 15)
        add_checklist_item(ft_b15_1.id, "learning", "Brute-force: nested loop multiply all except self O(n²)", "https://www.geeksforgeeks.org/a-product-array-puzzle/", "", 16)
        add_checklist_item(ft_b15_1.id, "learning", "Optimal: prefix/suffix products O(n) no division", "https://www.geeksforgeeks.org/a-product-array-puzzle/", "", 17)
        add_checklist_item(ft_b15_1.id, "leetcode", "238. Product of Array Except Self", "https://leetcode.com/problems/product-of-array-except-self/", "Medium", 18)

        ft_b15_2 = get_or_create_day_block(ft_w15.id, "Day 3-4: Two Pointers & Sliding Window", "", "3-4 hours", 2)
        add_checklist_item(ft_b15_2.id, "learning", "Brute-force: reverse + compare new string O(n) extra space", "https://www.geeksforgeeks.org/check-if-a-number-is-palindrome/", "", 1)
        add_checklist_item(ft_b15_2.id, "learning", "Optimal: two pointers inward O(n) O(1) space", "https://www.geeksforgeeks.org/check-if-a-number-is-palindrome/", "", 2)
        add_checklist_item(ft_b15_2.id, "leetcode", "125. Valid Palindrome", "https://leetcode.com/problems/valid-palindrome/", "Easy", 3)
        add_checklist_item(ft_b15_2.id, "learning", "Brute-force: triple nested loops O(n³)", "https://www.geeksforgeeks.org/find-a-triplet-that-sum-to-a-given-value/", "", 4)
        add_checklist_item(ft_b15_2.id, "learning", "Optimal: sort + two pointers O(n²), skip duplicates", "https://www.geeksforgeeks.org/find-a-triplet-that-sum-to-a-given-value/", "", 5)
        add_checklist_item(ft_b15_2.id, "leetcode", "15. 3Sum", "https://leetcode.com/problems/3sum/", "Medium", 6)
        add_checklist_item(ft_b15_2.id, "learning", "Brute-force: check every pair of lines O(n²)", "https://www.geeksforgeeks.org/container-with-most-water/", "", 7)
        add_checklist_item(ft_b15_2.id, "learning", "Optimal: two pointers from edges inward O(n)", "https://www.geeksforgeeks.org/container-with-most-water/", "", 8)
        add_checklist_item(ft_b15_2.id, "leetcode", "11. Container With Most Water", "https://leetcode.com/problems/container-with-most-water/", "Medium", 9)
        add_checklist_item(ft_b15_2.id, "learning", "Brute-force: check every buy-sell pair O(n²)", "https://www.geeksforgeeks.org/stock-buy-sell/", "", 10)
        add_checklist_item(ft_b15_2.id, "learning", "Optimal: track min price, single pass O(n)", "https://www.geeksforgeeks.org/stock-buy-sell/", "", 11)
        add_checklist_item(ft_b15_2.id, "leetcode", "121. Best Time to Buy and Sell Stock", "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/", "Easy", 12)
        add_checklist_item(ft_b15_2.id, "learning", "Brute-force: check every substring O(n³)", "https://www.geeksforgeeks.org/length-of-the-longest-substring-without-repeating-characters/", "", 13)
        add_checklist_item(ft_b15_2.id, "learning", "Optimal: sliding window + set O(n)", "https://www.geeksforgeeks.org/length-of-the-longest-substring-without-repeating-characters/", "", 14)
        add_checklist_item(ft_b15_2.id, "leetcode", "3. Longest Substring Without Repeating Characters", "https://leetcode.com/problems/longest-substring-without-repeating-characters/", "Medium", 15)

        ft_b15_3 = get_or_create_day_block(ft_w15.id, "Day 5-7: Stacks & Binary Search", "", "3-4 hours", 3)
        add_checklist_item(ft_b15_3.id, "learning", "Stack approach: push open, pop on close, check match O(n)", "https://www.geeksforgeeks.org/check-for-balanced-parentheses-in-an-expression/", "", 1)
        add_checklist_item(ft_b15_3.id, "leetcode", "20. Valid Parentheses", "https://leetcode.com/problems/valid-parentheses/", "Easy", 2)
        add_checklist_item(ft_b15_3.id, "learning", "Brute-force: scan stack for min O(n) per getMin call", "https://www.geeksforgeeks.org/design-a-stack-that-supports-getmin-in-o1-time-and-o1-extra-space/", "", 3)
        add_checklist_item(ft_b15_3.id, "learning", "Optimal: auxiliary min-stack O(1) getMin", "https://www.geeksforgeeks.org/design-a-stack-that-supports-getmin-in-o1-time-and-o1-extra-space/", "", 4)
        add_checklist_item(ft_b15_3.id, "leetcode", "155. Min Stack", "https://leetcode.com/problems/min-stack/", "Medium", 5)
        add_checklist_item(ft_b15_3.id, "learning", "Brute-force: linear scan O(n)", "https://www.geeksforgeeks.org/linear-search/", "", 6)
        add_checklist_item(ft_b15_3.id, "learning", "Optimal: binary search O(log n)", "https://www.geeksforgeeks.org/binary-search/", "", 7)
        add_checklist_item(ft_b15_3.id, "leetcode", "704. Binary Search", "https://leetcode.com/problems/binary-search/", "Easy", 8)
        add_checklist_item(ft_b15_3.id, "learning", "Brute-force: linear scan O(n)", "https://www.geeksforgeeks.org/search-an-element-in-a-sorted-and-pivoted-array/", "", 9)
        add_checklist_item(ft_b15_3.id, "learning", "Optimal: modified binary search on rotated array O(log n)", "https://www.geeksforgeeks.org/search-an-element-in-a-sorted-and-pivoted-array/", "", 10)
        add_checklist_item(ft_b15_3.id, "leetcode", "33. Search in Rotated Sorted Array", "https://leetcode.com/problems/search-in-rotated-sorted-array/", "Medium", 11)

        # ── Week 16: Linked Lists & Trees
        ft_w16 = get_or_create_week(ft1.id, 16, "Week 16: Linked Lists & Trees", "")

        ft_b16_1 = get_or_create_day_block(ft_w16.id, "Day 1-2: Linked Lists", "", "2-3 hours", 1)
        add_checklist_item(ft_b16_1.id, "learning", "Iterative reversal O(n) O(1) space", "https://www.geeksforgeeks.org/reverse-a-linked-list/", "", 1)
        add_checklist_item(ft_b16_1.id, "learning", "Recursive reversal O(n) O(n) call stack", "https://www.geeksforgeeks.org/reverse-a-linked-list/", "", 2)
        add_checklist_item(ft_b16_1.id, "leetcode", "206. Reverse Linked List", "https://leetcode.com/problems/reverse-linked-list/", "Easy", 3)
        add_checklist_item(ft_b16_1.id, "learning", "Iterative merge with dummy node O(n+m)", "https://www.geeksforgeeks.org/merge-two-sorted-linked-lists/", "", 4)
        add_checklist_item(ft_b16_1.id, "leetcode", "21. Merge Two Sorted Lists", "https://leetcode.com/problems/merge-two-sorted-lists/", "Easy", 5)
        add_checklist_item(ft_b16_1.id, "learning", "Brute-force: store visited nodes in set O(n) space", "https://www.geeksforgeeks.org/detect-loop-in-a-linked-list/", "", 6)
        add_checklist_item(ft_b16_1.id, "learning", "Optimal: Floyd's fast/slow pointer O(1) space", "https://www.geeksforgeeks.org/detect-loop-in-a-linked-list/", "", 7)
        add_checklist_item(ft_b16_1.id, "leetcode", "141. Linked List Cycle", "https://leetcode.com/problems/linked-list-cycle/", "Easy", 8)
        add_checklist_item(ft_b16_1.id, "learning", "Brute-force: two-pass (count length, then remove) O(n)", "https://www.geeksforgeeks.org/delete-nth-node-from-the-end-of-the-given-linked-list/", "", 9)
        add_checklist_item(ft_b16_1.id, "learning", "Optimal: one-pass with two pointers n apart O(n)", "https://www.geeksforgeeks.org/delete-nth-node-from-the-end-of-the-given-linked-list/", "", 10)
        add_checklist_item(ft_b16_1.id, "leetcode", "19. Remove Nth Node From End of List", "https://leetcode.com/problems/remove-nth-node-from-end-of-list/", "Medium", 11)

        ft_b16_2 = get_or_create_day_block(ft_w16.id, "Day 3-5: Trees", "", "3-4 hours", 2)
        add_checklist_item(ft_b16_2.id, "learning", "Recursive DFS O(n) — base case: null → 0", "https://www.geeksforgeeks.org/find-the-maximum-depth-or-height-of-a-tree/", "", 1)
        add_checklist_item(ft_b16_2.id, "learning", "Iterative BFS with queue O(n)", "https://www.geeksforgeeks.org/level-order-tree-traversal/", "", 2)
        add_checklist_item(ft_b16_2.id, "leetcode", "104. Maximum Depth of Binary Tree", "https://leetcode.com/problems/maximum-depth-of-binary-tree/", "Easy", 3)
        add_checklist_item(ft_b16_2.id, "learning", "Recursive swap left/right O(n)", "https://www.geeksforgeeks.org/write-an-efficient-c-function-to-convert-a-tree-into-its-mirror-tree/", "", 4)
        add_checklist_item(ft_b16_2.id, "leetcode", "226. Invert Binary Tree", "https://leetcode.com/problems/invert-binary-tree/", "Easy", 5)
        add_checklist_item(ft_b16_2.id, "learning", "Brute-force: in-order traversal → check sorted array O(n) extra space", "https://www.geeksforgeeks.org/a-program-to-check-if-a-binary-tree-is-bst-or-not/", "", 6)
        add_checklist_item(ft_b16_2.id, "learning", "Optimal: recursive with min/max bounds O(n) O(h) space", "https://www.geeksforgeeks.org/a-program-to-check-if-a-binary-tree-is-bst-or-not/", "", 7)
        add_checklist_item(ft_b16_2.id, "leetcode", "98. Validate Binary Search Tree", "https://leetcode.com/problems/validate-binary-search-tree/", "Medium", 8)
        add_checklist_item(ft_b16_2.id, "learning", "Brute-force: store root-to-node paths, compare O(n) space", "https://www.geeksforgeeks.org/lowest-common-ancestor-binary-tree-set-1/", "", 9)
        add_checklist_item(ft_b16_2.id, "learning", "Optimal: single recursive traversal O(n) O(h)", "https://www.geeksforgeeks.org/lowest-common-ancestor-binary-tree-set-1/", "", 10)
        add_checklist_item(ft_b16_2.id, "leetcode", "236. Lowest Common Ancestor of Binary Tree", "https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/", "Medium", 11)
        add_checklist_item(ft_b16_2.id, "learning", "BFS level-by-level with queue O(n)", "https://www.geeksforgeeks.org/level-order-tree-traversal/", "", 12)
        add_checklist_item(ft_b16_2.id, "leetcode", "102. Binary Tree Level Order Traversal", "https://leetcode.com/problems/binary-tree-level-order-traversal/", "Medium", 13)
        add_checklist_item(ft_b16_2.id, "learning", "Brute-force: check every pair of nodes O(n²)", "https://www.geeksforgeeks.org/diameter-of-a-binary-tree/", "", 14)
        add_checklist_item(ft_b16_2.id, "learning", "Optimal: single DFS tracking diameter O(n)", "https://www.geeksforgeeks.org/diameter-of-a-binary-tree/", "", 15)
        add_checklist_item(ft_b16_2.id, "leetcode", "543. Diameter of Binary Tree", "https://leetcode.com/problems/diameter-of-binary-tree/", "Easy", 16)

        ft_b16_3 = get_or_create_day_block(ft_w16.id, "Day 6-7: Review & Timed Practice", "", "2-3 hours", 3)
        add_checklist_item(ft_b16_3.id, "learning", "Re-solve all Easy problems without hints (10 min each)", "https://leetcode.com/problemset/", "", 1)
        add_checklist_item(ft_b16_3.id, "learning", "Re-solve all Medium problems without hints (20 min each)", "https://leetcode.com/problemset/", "", 2)
        add_checklist_item(ft_b16_3.id, "learning", "For each problem: state brute-force complexity, then optimal", "https://www.bigocheatsheet.com/", "", 3)
        add_checklist_item(ft_b16_3.id, "review", "Two Sum — hash map approach", "https://leetcode.com/problems/two-sum/", "Easy", 4)
        add_checklist_item(ft_b16_3.id, "review", "3Sum — sort + two pointers", "https://leetcode.com/problems/3sum/", "Medium", 5)
        add_checklist_item(ft_b16_3.id, "review", "Reverse Linked List — iterative", "https://leetcode.com/problems/reverse-linked-list/", "Easy", 6)
        add_checklist_item(ft_b16_3.id, "review", "Validate BST — recursive bounds", "https://leetcode.com/problems/validate-binary-search-tree/", "Medium", 7)

        add_phase_mastery(ft1.id, "Can solve all Easy problems in <10 mins", 1)
        add_phase_mastery(ft1.id, "Can solve all Medium problems in <25 mins", 2)
        add_phase_mastery(ft1.id, "Can explain brute-force vs optimal for every problem", 3)
        add_phase_mastery(ft1.id, "Can state time and space complexity without hesitation", 4)

        # ── Phase 7: Fast Track — Advanced Patterns ─────────
        ft2 = get_or_create_phase(7, "Fast Track — Advanced Patterns", "4 weeks", 20, 12)
        ft2.goal = "Graphs, dynamic programming, and backtracking — brute-force and optimal for each"

        # ── Week 17: Graphs & DP
        ft_w17 = get_or_create_week(ft2.id, 17, "Week 17: Graphs & Dynamic Programming", "")

        ft_b17_1 = get_or_create_day_block(ft_w17.id, "Day 1-3: Graphs", "", "3-4 hours", 1)
        add_checklist_item(ft_b17_1.id, "learning", "DFS flood-fill approach O(m·n)", "https://www.geeksforgeeks.org/find-the-number-of-islands-using-dfs/", "", 1)
        add_checklist_item(ft_b17_1.id, "learning", "BFS alternative — same complexity, different traversal order", "https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/", "", 2)
        add_checklist_item(ft_b17_1.id, "leetcode", "200. Number of Islands", "https://leetcode.com/problems/number-of-islands/", "Medium", 3)
        add_checklist_item(ft_b17_1.id, "learning", "Brute-force: check all paths for cycles O(V! worst case)", "https://www.geeksforgeeks.org/detect-cycle-in-a-graph/", "", 4)
        add_checklist_item(ft_b17_1.id, "learning", "Optimal: topological sort / DFS with states O(V+E)", "https://www.geeksforgeeks.org/detect-cycle-in-a-graph/", "", 5)
        add_checklist_item(ft_b17_1.id, "leetcode", "207. Course Schedule", "https://leetcode.com/problems/course-schedule/", "Medium", 6)
        add_checklist_item(ft_b17_1.id, "learning", "BFS/DFS clone with visited hash map O(V+E)", "https://www.geeksforgeeks.org/clone-an-undirected-graph/", "", 7)
        add_checklist_item(ft_b17_1.id, "leetcode", "133. Clone Graph", "https://leetcode.com/problems/clone-graph/", "Medium", 8)
        add_checklist_item(ft_b17_1.id, "learning", "Brute-force: BFS from every node O(V·(V+E))", "https://www.geeksforgeeks.org/minimum-time-required-so-that-all-oranges-become-rotten/", "", 9)
        add_checklist_item(ft_b17_1.id, "learning", "Optimal: multi-source BFS O(V+E)", "https://www.geeksforgeeks.org/minimum-time-required-so-that-all-oranges-become-rotten/", "", 10)
        add_checklist_item(ft_b17_1.id, "leetcode", "994. Rotting Oranges", "https://leetcode.com/problems/rotting-oranges/", "Medium", 11)

        ft_b17_2 = get_or_create_day_block(ft_w17.id, "Day 4-7: Dynamic Programming", "", "4-5 hours", 2)
        add_checklist_item(ft_b17_2.id, "learning", "Brute-force: recursion O(2^n) — two branches per step", "https://www.geeksforgeeks.org/count-ways-reach-nth-stair/", "", 1)
        add_checklist_item(ft_b17_2.id, "learning", "Optimal: DP or two variables O(n) O(1) space", "https://www.geeksforgeeks.org/count-ways-reach-nth-stair/", "", 2)
        add_checklist_item(ft_b17_2.id, "leetcode", "70. Climbing Stairs", "https://leetcode.com/problems/climbing-stairs/", "Easy", 3)
        add_checklist_item(ft_b17_2.id, "learning", "Brute-force: try all combinations O(S^n) recursion", "https://www.geeksforgeeks.org/coin-change-dp-7/", "", 4)
        add_checklist_item(ft_b17_2.id, "learning", "Optimal: bottom-up DP table O(S·n) where S=amount, n=coins", "https://www.geeksforgeeks.org/coin-change-dp-7/", "", 5)
        add_checklist_item(ft_b17_2.id, "leetcode", "322. Coin Change", "https://leetcode.com/problems/coin-change/", "Medium", 6)
        add_checklist_item(ft_b17_2.id, "learning", "Brute-force: try rob/skip every house O(2^n)", "https://www.geeksforgeeks.org/find-maximum-possible-stolen-value-houses/", "", 7)
        add_checklist_item(ft_b17_2.id, "learning", "Optimal: DP with two variables O(n) O(1) space", "https://www.geeksforgeeks.org/find-maximum-possible-stolen-value-houses/", "", 8)
        add_checklist_item(ft_b17_2.id, "leetcode", "198. House Robber", "https://leetcode.com/problems/house-robber/", "Medium", 9)
        add_checklist_item(ft_b17_2.id, "learning", "Brute-force: check all subsequences O(2^n)", "https://www.geeksforgeeks.org/longest-increasing-subsequence-dp-3/", "", 10)
        add_checklist_item(ft_b17_2.id, "learning", "DP: O(n²) table, Optimal: O(n log n) with binary search", "https://www.geeksforgeeks.org/longest-increasing-subsequence-dp-3/", "", 11)
        add_checklist_item(ft_b17_2.id, "leetcode", "300. Longest Increasing Subsequence", "https://leetcode.com/problems/longest-increasing-subsequence/", "Medium", 12)
        add_checklist_item(ft_b17_2.id, "learning", "Brute-force: try every partition O(2^n)", "https://www.geeksforgeeks.org/word-break-problem-dp-32/", "", 13)
        add_checklist_item(ft_b17_2.id, "learning", "Optimal: DP with word set O(n²) or O(n·m)", "https://www.geeksforgeeks.org/word-break-problem-dp-32/", "", 14)
        add_checklist_item(ft_b17_2.id, "leetcode", "139. Word Break", "https://leetcode.com/problems/word-break/", "Medium", 15)
        add_checklist_item(ft_b17_2.id, "learning", "Brute-force: try all buy/sell with cooldown O(2^n)", "https://www.geeksforgeeks.org/maximum-profit-by-buying-and-selling-a-share-at-most-twice/", "", 16)
        add_checklist_item(ft_b17_2.id, "learning", "Optimal: state machine DP O(n) — hold/sold/rest", "https://www.geeksforgeeks.org/stock-buy-sell/-with-cooldown", "", 17)
        add_checklist_item(ft_b17_2.id, "leetcode", "309. Best Time to Buy and Sell Stock with Cooldown", "https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/", "Medium", 18)

        # ── Week 18: Backtracking & Final Review
        ft_w18 = get_or_create_week(ft2.id, 18, "Week 18: Backtracking & Final Review", "")

        ft_b18_1 = get_or_create_day_block(ft_w18.id, "Day 1-3: Backtracking", "", "3-4 hours", 1)
        add_checklist_item(ft_b18_1.id, "learning", "Brute-force: iterative bit-mask enumerate all 2^n subsets", "https://www.geeksforgeeks.org/backtracking-to-find-all-subsets/", "", 1)
        add_checklist_item(ft_b18_1.id, "learning", "Backtracking: recursive include/exclude pattern O(2^n)", "https://www.geeksforgeeks.org/backtracking-to-find-all-subsets/", "", 2)
        add_checklist_item(ft_b18_1.id, "leetcode", "78. Subsets", "https://leetcode.com/problems/subsets/", "Medium", 3)
        add_checklist_item(ft_b18_1.id, "learning", "Brute-force: generate all n! permutations iteratively", "https://www.geeksforgeeks.org/write-a-c-program-to-print-all-permutations-of-a-given-string/", "", 4)
        add_checklist_item(ft_b18_1.id, "learning", "Backtracking: swap-based or used-array approach O(n·n!)", "https://www.geeksforgeeks.org/write-a-c-program-to-print-all-permutations-of-a-given-string/", "", 5)
        add_checklist_item(ft_b18_1.id, "leetcode", "46. Permutations", "https://leetcode.com/problems/permutations/", "Medium", 6)
        add_checklist_item(ft_b18_1.id, "learning", "Backtracking with pruning: skip if remainder < candidate", "https://www.geeksforgeeks.org/combinational-sum/", "", 7)
        add_checklist_item(ft_b18_1.id, "leetcode", "39. Combination Sum", "https://leetcode.com/problems/combination-sum/", "Medium", 8)
        add_checklist_item(ft_b18_1.id, "learning", "Brute-force: try every cell as start, recurse O(m·n·4^L)", "https://www.geeksforgeeks.org/search-a-word-in-a-2d-grid-of-characters/", "", 9)
        add_checklist_item(ft_b18_1.id, "learning", "Optimised: backtrack with visited set, early termination", "https://www.geeksforgeeks.org/search-a-word-in-a-2d-grid-of-characters/", "", 10)
        add_checklist_item(ft_b18_1.id, "leetcode", "79. Word Search", "https://leetcode.com/problems/word-search/", "Medium", 11)

        ft_b18_2 = get_or_create_day_block(ft_w18.id, "Day 4-5: Sorting & Greedy (Bonus)", "", "2-3 hours", 2)
        add_checklist_item(ft_b18_2.id, "learning", "Brute-force: check all interval pairs O(n²)", "https://www.geeksforgeeks.org/merging-intervals/", "", 1)
        add_checklist_item(ft_b18_2.id, "learning", "Optimal: sort by start + merge O(n log n)", "https://www.geeksforgeeks.org/merging-intervals/", "", 2)
        add_checklist_item(ft_b18_2.id, "leetcode", "56. Merge Intervals", "https://leetcode.com/problems/merge-intervals/", "Medium", 3)
        add_checklist_item(ft_b18_2.id, "learning", "Brute-force: try all insertion positions O(n²)", "https://www.geeksforgeeks.org/insert-in-sorted-and-non-overlapping-interval-array/", "", 4)
        add_checklist_item(ft_b18_2.id, "learning", "Optimal: binary search insert position + merge O(n)", "https://www.geeksforgeeks.org/insert-in-sorted-and-non-overlapping-interval-array/", "", 5)
        add_checklist_item(ft_b18_2.id, "leetcode", "57. Insert Interval", "https://leetcode.com/problems/insert-interval/", "Medium", 6)
        add_checklist_item(ft_b18_2.id, "learning", "Greedy: sort by end time, count non-overlapping O(n log n)", "https://www.geeksforgeeks.org/maximal-disjoint-intervals/", "", 7)
        add_checklist_item(ft_b18_2.id, "leetcode", "435. Non-overlapping Intervals", "https://leetcode.com/problems/non-overlapping-intervals/", "Medium", 8)

        ft_b18_3 = get_or_create_day_block(ft_w18.id, "Day 6-7: Fast Track Final Review", "", "3-4 hours", 3)
        add_checklist_item(ft_b18_3.id, "learning", "Timed: solve 3 random Easy in 30 mins total", "https://leetcode.com/problemset/?difficulty=EASY", "", 1)
        add_checklist_item(ft_b18_3.id, "learning", "Timed: solve 3 random Medium in 75 mins total", "https://leetcode.com/problemset/?difficulty=MEDIUM", "", 2)
        add_checklist_item(ft_b18_3.id, "learning", "For each: state brute-force approach + complexity first", "https://www.bigocheatsheet.com/", "", 3)
        add_checklist_item(ft_b18_3.id, "learning", "For each: then state optimal approach + complexity", "https://www.bigocheatsheet.com/", "", 4)
        add_checklist_item(ft_b18_3.id, "learning", "Practice: explain your approach out loud as you code", "https://www.techinterviewhandbook.org/coding-interview-rubrics/", "", 5)
        add_checklist_item(ft_b18_3.id, "review", "Two Sum", "https://leetcode.com/problems/two-sum/", "Easy", 6)
        add_checklist_item(ft_b18_3.id, "review", "Coin Change", "https://leetcode.com/problems/coin-change/", "Medium", 7)
        add_checklist_item(ft_b18_3.id, "review", "Number of Islands", "https://leetcode.com/problems/number-of-islands/", "Medium", 8)
        add_checklist_item(ft_b18_3.id, "review", "Subsets", "https://leetcode.com/problems/subsets/", "Medium", 9)
        add_checklist_item(ft_b18_3.id, "review", "Merge Intervals", "https://leetcode.com/problems/merge-intervals/", "Medium", 10)

        add_phase_mastery(ft2.id, "Graphs: DFS/BFS/topological sort understood", 1)
        add_phase_mastery(ft2.id, "DP: can convert brute-force recursion to memoization to tabulation", 2)
        add_phase_mastery(ft2.id, "Backtracking: can identify and apply the pattern", 3)
        add_phase_mastery(ft2.id, "Can explain brute-force AND optimal for every Fast Track problem", 4)
        add_phase_mastery(ft2.id, "Can solve any Fast Track problem from scratch in interview time", 5)

        db.session.commit()
        print("✓ Database seeded successfully!")


def get_or_create_phase(number, title, date_range, target_problems=0, estimated_hours=0):
    """Get existing phase or create new one"""
    phase = Phase.query.filter_by(number=number).first()
    if not phase:
        phase = Phase(
            number=number,
            title=title,
            date_range=date_range,
            target_problems=target_problems,
            estimated_hours=estimated_hours
        )
        db.session.add(phase)
        db.session.flush()
    return phase


def get_or_create_week(phase_id, number, title, date_range):
    """Get existing week or create new one"""
    week = Week.query.filter_by(phase_id=phase_id, number=number).first()
    if not week:
        week = Week(
            phase_id=phase_id,
            number=number,
            title=title,
            date_range=date_range
        )
        db.session.add(week)
        db.session.flush()
    return week


def get_or_create_day_block(week_id, title, date_range, estimated_time, sort_order):
    """Get existing day block or create new one"""
    block = DayBlock.query.filter_by(week_id=week_id, title=title).first()
    if not block:
        block = DayBlock(
            week_id=week_id,
            title=title,
            date_range=date_range,
            estimated_time=estimated_time,
            sort_order=sort_order
        )
        db.session.add(block)
        db.session.flush()
    return block


def add_checklist_item(day_block_id, item_type, label, url, difficulty, sort_order):
    """Add checklist item if it doesn't exist; update url/difficulty if already exists (preserves is_checked)"""
    item = ChecklistItem.query.filter_by(
        day_block_id=day_block_id,
        item_type=item_type,
        label=label
    ).first()

    if not item:
        item = ChecklistItem(
            day_block_id=day_block_id,
            item_type=item_type,
            label=label,
            url=url,
            difficulty=difficulty,
            sort_order=sort_order,
            is_checked=False
        )
        db.session.add(item)
    else:
        # Update metadata but never touch is_checked
        if url:
            item.url = url
        if difficulty:
            item.difficulty = difficulty
        item.sort_order = sort_order
    db.session.flush()


def add_phase_mastery(phase_id, label, sort_order):
    """Add phase mastery item if it doesn't exist"""
    item = PhaseMastery.query.filter_by(phase_id=phase_id, label=label).first()
    if not item:
        item = PhaseMastery(
            phase_id=phase_id,
            label=label,
            sort_order=sort_order,
            is_checked=False
        )
        db.session.add(item)
    db.session.flush()


if __name__ == '__main__':
    seed_database()
