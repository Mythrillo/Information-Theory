import sys


class Node:
    """
    Class that represents a node in a tree graph.
    """
    def __init__(self,  left=None, right=None):
        self.left = left
        self.right = right

    def children(self):
        return self.left, self.right


def tree(node, string=''):
    """
    Recursive function that goes through all the nodes in a graph and creates the Huffman code for each one.
    :param node:
    :param string:
    :return: d: dictionary where each character is given a Huffman code
    """
    if type(node) is str:
        return {node: string}

    left, right = node.children()

    d = dict()
    d.update(tree(left, string + '0'))
    d.update(tree(right, string + '1'))
    return d


def freq(string):
    """
    Function that calculates frequency of each character in a given string.
    The result is a sorted list of tuples: (char, frequency).
    :param string
    :return: f: list
    """
    if len(string) == 0:
        print("Plik tekst.txt jest pusty")
        sys.exit(1)

    f = {}
    for char in string:
        if char in f:
            f[char] += 1
        else:
            f[char] = 1

    for key in f.keys():
        f[key] = f[key] / len(string)

    f = sorted(f.items(), key=lambda x: x[1], reverse=True)
    return f


def create_code(nodes):
    """
    Function that creates a Huffman code for each character in the list nodes.
    :param nodes: sorted list of tuples returned by the function freq(string)
    :return: code: a dictionary where each letter is given a Huffman code
    """
    # Checking an edge case scenario where the given text only had one letter in it.
    if len(nodes) == 1:
        return {nodes[0][0]: "0"}

    # Preparing the nodes of the tree graph.
    while len(nodes) > 1:
        # We are taking the last two tuples from the list nodes since they are the least frequent ones.
        [k1, p1] = nodes[-1]
        [k2, p2] = nodes[-2]
        node = Node(k1, k2)
        nodes = nodes[:-2]  # Getting rid of the last two tuples since their probabilities will be combined.
        nodes.append([node, p1 + p2])
        nodes = sorted(nodes, key=lambda x: x[1], reverse=True)  # Making sure the list is sorted in descending order.

    code = tree(nodes[0][0])
    return code


def code_msg(msg, code):
    """
    Function that codes a given text with a given Huffman code for each character.
    :param msg:
    :param code:
    :return: coded_msg
    """
    coded_msg = ""
    for char in msg:
        coded_msg += code[char]
    return coded_msg


def decode_msg(coded_msg, code):
    """
    Function that decodes a given text with a given Huffman code for each character.
    The decoding is very simple as the Huffman code is an optimal prefix code.
    :param coded_msg:
    :param code:
    :return: decoed_msg
    """
    decoded_msg = ""
    while coded_msg:
        for key, coding in code.items():
            if coded_msg.startswith(coding):
                decoded_msg += key
                coded_msg = coded_msg[len(coding):]
    return decoded_msg


if __name__ == "__main__":
    try:
        f1 = open("text.txt", "r")
    except FileNotFoundError:
        print("File text.txt not found")
        sys.exit(1)

    msg = ""
    for line in f1:
        if line == "\n":
            continue
        else:
            if msg == "":
                msg += line.strip()
            else:
                msg += " " + line.strip()
    f1.close()

    nodes = freq(msg)
    code = create_code(nodes)
    # Sorting the code by the length of the Huffman coding so we can write it out nicely in a file.
    sorted_code = sorted(code.items(), key=lambda x: len(x[1]))
    coded_msg = code_msg(msg, code)

    f3 = open("code.txt", "w+")
    for key, value in sorted_code:
        f3.write(key + ": " + value + "\n")
    f3.close()

    decoded_msg = decode_msg(coded_msg, code)
    f2 = open("coded.txt", "w+")
    f2.write(coded_msg)
    f2.close()

    f4 = open("decoded.txt", "w+")
    f4.write(decoded_msg)
    f4.close()
