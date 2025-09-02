"""A module that provide distances and likelyhood between sets.

Distance
-------------------------

- [x] basic distance between 2 sets.
- [x] distance based on number of operations to transform a set into another.

"""

import re

# --------------------------------------------------
# distance methods
# --------------------------------------------------


def distance(a, b, ignore_case=True):
    """Compute distance between 2 sets."""
    if not a or not b:
        return 0
    a = str(a)
    b = str(b)

    def seq(data, size):
        l = len(data)
        for x in range(0, l - size + 1):
            yield data[x : x + size]

    def dist(a, b):
        la, lb = len(a), len(b)
        for size in range(la, 0, -1):
            for x in seq(a, size):
                if x in b:
                    i = a.index(x)
                    j = b.index(x)
                    a = "".join(a.split(x))
                    b = "".join(b.split(x))
                    return a, b, abs(i - j)
        return None, None, la + lb

    if ignore_case:
        a, b = a.lower(), b.lower()

    la, lb = len(a), len(b)
    if la > lb:
        a, b, la, lb = b, a, lb, la

    dd = d = 0
    while a is not None:
        # print(f"[{dd}]:  {a} : {b} : {d}")
        a, b, d = dist(a, b)
        dd += d

    # print(f"[{dd}]:  {a} : {b} : {d}")
    r = dd / (la or 1)
    return r


def editDistDP(name1, name2):
    """Compute the distance between 2 strings based on the
    number of operations that transform one set into the 2nd
    set.

    - Insert
    - Remove
    - Replace

    All of the above operations are of equal cost.

    Ref: https://www.geeksforgeeks.org/edit-distance-dp-5/
    """

    m, n = len(name1), len(name2)
    # Create a table to store results of subproblems
    dp = [[0 for x in range(n + 1)] for x in range(m + 1)]

    # Fill d[][] in bottom up manner
    for i in range(m + 1):
        for j in range(n + 1):
            # If first string is empty, only option is to
            # insert all characters of second string
            if i == 0:
                dp[i][j] = j  # Min. operations = j

            # If second string is empty, only option is to
            # remove all characters of second string
            elif j == 0:
                dp[i][j] = i  # Min. operations = i

            # If last characters are same, ignore last char
            # and recur for remaining string
            elif name1[i - 1] == name2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]

            # If last character are different, consider all
            # possibilities and find minimum
            else:
                dp[i][j] = 1 + min(
                    dp[i][j - 1],
                    dp[i - 1][j],
                    dp[i - 1][j - 1],  # Insert  # Remove
                )  # Replace

    return dp[m][n]


# --------------------------------------------------
# likelyhood methods
# --------------------------------------------------
def likelyhood6(set1, set2):
    """Compute likelyhood based on items that are in both sets.

    - missing items cost -1
    - matching items cost +2

    TODO: implement using set.difference()

    """
    set1 = [re.sub(r"\bany\b", r".*", str(s)) for s in set1]
    set2 = [re.sub(r"\bany\b", r".*", str(s)) for s in set2]

    l1 = len(set1)
    l2 = len(set2)
    if l1 > l2:
        l1, l2, set1, set2 = l2, l1, set2, set1
    S = 0
    if l2 <= 0:
        return 0

    while set1:
        a = set1.pop(0)
        for idx, b in list(enumerate(set2)):
            if re.match(a, b) or re.match(b, a):
                set2.pop(idx)
                S += idx * l2
                break
        else:
            S += l2 * l1 + 1

    return S / l2


def likelyhood5(set1, set2):
    """Compute likelyhood based on items that are in both sets.

    - missing items cost -1
    - matching items cost +2

    TODO: implement using set.difference()

    """
    set1, set2 = list(set1), list(set2)
    l1 = len(set1)
    l2 = len(set2)
    if l1 > l2:
        l1, l2, set1, set2 = l2, l1, set2, set1
    S = 0

    while set1:
        a = set1.pop(0)
        try:
            idx = set2.index(a)
            S += idx
            set2.pop(idx)
        except ValueError:
            S += len(set2)
            set2.pop(0)
    return S / ((l1 + l2) or 1)


def likelyhood4(set1, set2):
    """Compute likelyhood based on items that are in both sets.

    - missing items cost -1
    - matching items cost +2

    TODO: implement using set.difference()

    """
    set1, set2 = list(set1), list(set2)
    N = (len(set1) + len(set2)) or 1
    S = 0

    def check(s1, s2):
        s = 0
        while s1:
            item = s1.pop(0)
            if item in s2:
                s2.remove(item)
                s += 2
            else:
                s -= 1
        return s

    S = check(set1, set2) + check(set2, set1)
    return S / N


def likelyhood3(set1, set2):
    """likelyhood based on string edit distance."""
    n = min(len(set1), len(set2))
    if n:
        return 1 - editDistDP(set1, set2) / n
    return 0


def likelyhood2(name1, name2):
    """likelyhood based on string edit distance case insensitive."""
    name1 = str(name1)
    name2 = str(name2)
    n = min(len(name1), len(name2))
    return 1 - editDistDP(name1.lower(), name2.lower()) / n


def likelyhood(name1, name2):
    """basic likelyhood comparison."""
    if len(name1) > len(name2):
        name1, name2 = list(name2.lower()), list(name1.lower())
    else:
        name1, name2 = list(name1.lower()), list(name2.lower())

    n = len(name1)
    score = 0
    while name1:
        a = name1.pop(0)
        if a in name2:
            idx = name2.index(a)
            name2.pop(idx)
        else:
            idx = n
        score += 1 / (1 + idx) ** 2

    return score / n


def wlikelyhood(set1, set2, **weights):
    """Compute weighted likelyhood between 2 sets."""
    W = 0
    S = 0
    for k, w in weights.items():
        s1, s2 = set1.get(k, []), set2.get(k, [])
        if s1 or s2:
            # only weight average when any set is not empty
            W += w
            s = likelyhood4(s1, s2)
            S += w * s

    return S / (W or 1)
