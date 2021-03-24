import numpy as np
import numpy.linalg as lg
import itertools
import math


# DELETE
def check_if_matrix_is_generator_matrix(G):
    """
    Function that checks if a given matrix a generator matrix.
    The only requirement is that the matrix's rank is the same as the number of it's rows.
    :param G: numpy array
    :return: bool
    """
    if lg.matrix_rank(G) == G.shape[0]:
        return True
    return False


def create_parity_check_matrix(G):
    """
    Function that generates a parity check matrix from a given k x n generator matrix of form [Ik | P] where Ik is
    a identity matrix of rank k.

    The parity check matrix is in form [PT | I]
    where PT is transpose of matrix P and I is a identity matrix of rank n-k.
    :param G: a generator matrix in form [Ik | P]
    :return: H: parity check matrix in form [PT | I]
    """

    rows = G.shape[0]
    columns = G.shape[1]

    P = G[:, rows:columns]
    PT = np.transpose(P)

    I = np.identity(columns - rows)

    H = np.concatenate((PT, I), axis=1)

    return H


def code_message(G, msg):
    """
    The way the message is coded is simple as we only need to multiply the message with the generator matrix and
    take modulo 2 of the result.
    :param G: a generator matrix in systematic form
    :param msg: message we wish to code
    :return:
    """
    return msg.dot(G) % 2


def swap_columns(a, b, array):
    """
    Function that swaps columns of a given matrix
    :param a: int
    :param b: int
    :param array: numpy array
    :return: array_swapped: numpy array with the columns swapped
    """
    array_swapped = array.copy()
    array_swapped[:, a] = array[:, b]
    array_swapped[:, b] = array[:, a]
    return array_swapped


def decode_message(G, coded_msg):
    """
    Function that decodes given message using the given generator matrix.
    Firsly we create all combinations of length n, where n is the number of rows of the matrix, of zeros and ones.
    Then each combinations is transposed and multiplied by the generator matrix until the result is the given coded
    message in which case the transposed combination is returned. If all combinations are exhausted then a 1x1 numpy
    array is returned with the value 2.
    :param G: generator matrix in systematic form
    :param coded_msg: numpy array
    :return: rowT: decoded message
    """
    """
    Dekoduje zadaną wiadomość dla zadanej macierzy G.
    Początkowo tworzymy listę wszystkich poprawnych kombinacji długości liczby wierszów macierzy G stworzoną z 0 i 1,
    przez którą następnie iterujemy i mnożymy każdą kombinację razy macierz G.
    Jeśli dla którejś kombinacji okaże się, że wynik mnożenia jest naszą zakodowaną wiadomością to zwracamy kombinację.
    W przeciwnym wypadku zwracamy ustalony array.
    """
    code_words = list(itertools.product([0, 1], repeat=G.shape[0]))

    code_words_arr = np.array(code_words)

    for row in code_words_arr:
        rowT = np.transpose(row)

        if (rowT.dot(G) % 2 == coded_msg).all():
            return rowT

    return np.array([[2]])


def convert_to_systematic_matrix(G):
    """
    Function that converts any generator matrix to it's systematic form [I | P] using the following operations:
    swapping columns, adding rows modulo 2. It returns a 1x1 array with value 2 if the given matrix
    is not a generator matrix.
    :param G: generator matrix
    :return: numpy array
    """
    temp_array = G.copy()
    rows = temp_array.shape[0]
    columns = temp_array.shape[1]
    limit = rows
    i = 0
    while i < limit:

        # Trying to find a 1 in a i-th row and swapping the columns so it's in the (i, i) place.
        found = False
        for j in range(i, columns):
            if temp_array[i, j] == 1:
                found = True
                temp_array = swap_columns(j, i, temp_array)
                break

        if found:
            # Checking if other rows also contain 1 in i-th column. If they do we add i-th row to them.
            for k in range(0, rows):
                # Obviously we skip the i-th row.
                if k == i:
                    continue
                if temp_array[k, i] == 1:
                    temp_array[k, :] = temp_array[k, :] + temp_array[i, :]
                    temp_array = temp_array.copy() % 2
            # All values, except the (i, i) position, in the i-th column are now 0.
            i = i + 1
        else:
            # If we don't find a 1 in i-th row that means that the row consists of only zeros meaning the rank
            # of the given matrix is different from the number of rows thus the matrix in not a generator matirx.
            return np.array([[2]])
    return temp_array


G = np.array([[1, 1, 0, 1, 1],
              [0, 1, 1, 1, 0],
              [1, 0, 0, 1, 1]])


msg = np.array([1, 1, 1])


if __name__ == "__main__":

    GS = convert_to_systematic_matrix(G)
    if (GS == np.array([[2]])).all():
        print("Given matrix is not a generator matrix!")
        quit()
    else:
        print("Matrix G in systematic form:")
        print(GS)
        print("############")
        H = create_parity_check_matrix(GS)
        print("Parity check matrix H:")
        print(H)
        print("############")
        coded_msg = code_message(GS, msg)
        print("Coded message:")
        print(coded_msg)
        print("############")
        decoded_msg = decode_message(GS, coded_msg)
        if (decoded_msg != np.array([[2]])).all():
            print("Decoed message:")
            print(decoded_msg)
        else:
            print("The message can't be decoded.")
