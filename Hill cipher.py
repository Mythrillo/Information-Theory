import numpy as np
import math
import numpy.linalg as lg
from sympy import Matrix
import random


def check_matrix(array):
    """
    Function that checks whether the given matrix is invertible modulo 26.
    :param array: numpy array
    :return: bool
    """
    if array.shape[0] == 1:
        if math.gcd(array[0][0], 26) == 1:
            return True
        return False
    else:
        det = int(lg.det(array) % 26)
        if math.gcd(det, 26) == 1:
            return True

        return False


def letters_to_numbers(letters):
    """
    Function that converts a given string into a list of numbers respective to each character.
    :param letters: string
    :return: numbers: list of numbers
    """
    numbers = []
    for letter in letters:
        tmp = ord(letter) - 97
        numbers.append(tmp)

    return numbers


def numbers_to_letters(numbers):
    """
    Function that converts a list of numbers into their respective characters and combines them into a string.
    :param numbers: list of numbers
    :return: letters: string
    """
    letters = ""
    for number in numbers:
        tmp = number + 97
        letters += chr(tmp)
    return letters


def encrypt_msg(array, msg, L):
    """
    Function that uses the Hill cipher to encrypt a given message using the given matrix and a shift vector.
    This function works for matrix of any size. If the length of the given message is not divisible by the number of
    rows of the matrix then letter 'z' is added until the length is divisible by the number of rows.
    :param array: invertible matrix modulo 26
    :param msg: string
    :param L: shift vector
    :return: encrypted message
    """
    encrypted_numbers = []
    k = array.shape[0]
    if len(msg) % k == 0:
        numbers = letters_to_numbers(msg)
    else:
        for i in range(k - (len(msg) % k)):
            msg += "z"
        numbers = letters_to_numbers(msg)

    for j in range(0, len(msg), k):
        # The name n_gram comes from the fact that n is the size of the matrix.
        # For a 2x2 matrix the name is digram.
        n_gram = numbers[j:j+k]
        n_gram = np.array([n_gram])
        n_gram = np.transpose(n_gram)

        encrypted_n_gram = array.dot(n_gram) + L
        encrypted_n_gram %= 26
        encrypted_n_gram = np.transpose(encrypted_n_gram)

        for q in range(len(encrypted_n_gram[0])):
            encrypted_numbers.append(encrypted_n_gram[0][q])

    encrypted_letters = numbers_to_letters(encrypted_numbers)
    return encrypted_letters


def inverse_matrix(array):
    """
    Function that calculates and returns a reversed matrix modulo 26.
    :param array:
    :return:
    """
    tmp = Matrix(array)
    tmp = tmp.inv_mod(26)

    return np.array(tmp)


def decrypt_msg(array, encrypted_msg, L):
    """
    Function that decrypts the given message using the given matrix and the shift vector.
    :param array: invertible matrix modulo 26
    :param encrypted_msg: string
    :param L: shift vector
    :return: decrypted message
    """
    k = array.shape[0]
    encrypted_numbers = letters_to_numbers(encrypted_msg)
    decrypted_numbers = []
    inv_array = inverse_matrix(array)
    L_new = inv_array.dot(L)

    for i in range(0, len(encrypted_msg), k):
        encrypted_n_gram = encrypted_numbers[i:i+k]
        encrypted_n_gram = np.array([encrypted_n_gram])
        encrypted_n_gram = np.transpose(encrypted_n_gram)

        n_gram = inv_array.dot(encrypted_n_gram) - L_new
        n_gram %= 26
        n_gram = np.transpose(n_gram)

        for q in range(len(n_gram[0])):
            decrypted_numbers.append(n_gram[0][q])
    decrypted_letters = numbers_to_letters(decrypted_numbers)
    return decrypted_letters


def freq(string):
    """
    Function that calculates the frequency of each letter in a given string.
    :param string:
    :return: a list of letters sorted from the most common to least common
    """
    f = {}
    for char in string:
        if char in f:
            f[char] += 1
        else:
            f[char] = 1
    f = sorted(f.items(), key=lambda x: x[1], reverse=True)
    return f


def calculate_possible_k1_values(alphabet):
    """
    Helper function that calculates the possible k1 values used in the frequency analysis attack.
    :param alphabet:
    :return:
    """
    possible_values = []
    for i in range(len(alphabet)):
        if math.gcd(len(alphabet), i) == 1:
            possible_values.append(i)
    return possible_values


def least_common_multiple(a, b):
    return a*b // math.gcd(a, b)


def try_to_decrypt(freq_of_letters, encrypted_msg):
    """
    This function implements a frequency analysis attack on the Hill cipher. The implementation only works for 2x2
    Hill ciphers and is very similar to the method, one would use with pen and paper.
    :param freq_of_letters: sorted list of letters sorted from the most common to least common
    :param encrypted_msg:
    :return: decr
    """
    freq_of_letters_in_encrypted_msg = freq(encrypted_msg)
    most_common_in_encrypted_msg = ord(freq_of_letters_in_encrypted_msg[0][0]) - 97
    second_most_common_in_encrypted_msg = ord(freq_of_letters_in_encrypted_msg[1][0]) - 97
    most_common_in_alphabet = ord(freq_of_letters[0]) - 97
    second_most_common_in_alphabet = ord(freq_of_letters[1]) - 97

    possible_k1_values = calculate_possible_k1_values(freq_of_letters)
    lcm = least_common_multiple(most_common_in_alphabet, second_most_common_in_alphabet)

    if lcm == 0:
        if most_common_in_alphabet == 0:
            k2 = most_common_in_encrypted_msg
            for value in possible_k1_values:
                if second_most_common_in_encrypted_msg == (value * second_most_common_in_alphabet + k2) % 26:
                    k1 = value
        else:
            k2 = second_most_common_in_encrypted_msg
            for value in possible_k1_values:
                if most_common_in_encrypted_msg == (value * most_common_in_alphabet + k2) % 26:
                    k1 = value
                    break
    else:
        left1 = (most_common_in_encrypted_msg - second_most_common_in_encrypted_msg) % 26
        right1 = (most_common_in_alphabet - second_most_common_in_alphabet) % 26

        for value in possible_k1_values:
            if left1 == (right1 * value) % 26:
                k1 = value
                break

        tmp1 = lcm // most_common_in_alphabet
        tmp2 = lcm // second_most_common_in_alphabet

        left2 = (most_common_in_encrypted_msg * tmp1 - second_most_common_in_encrypted_msg * tmp2) % 26
        right2 = (tmp1 - tmp2) % 26

        for i in range(len(freq_of_letters)):
            if left2 == (i * right2) % 26:
                k2 = i
                break
    decrypted_msg = decrypt_msg(np.array([[k1]]), encrypted_msg, np.array([[k2]]))
    return decrypted_msg


def generate_random_text_with_respect_to_freq(freq):
    """
    Function used for testing that generates a random string of letters with respect to the frequency of each letter.
    :param freq: sorted list of letters sorted from the most common to least common
    :return:
    """
    tmp = []
    i = 26
    for letter in freq:
        tmp.append([letter] * i)
        i -= 1
    text = ""
    while len(tmp) > 0:
        t = random.randint(0, len(tmp)-1)
        text += tmp[t][0]
        tmp[t].pop(0)
        if len(tmp[t]) == 0:
            tmp.pop(t)
    return text

test_array1 = np.array([[1, 0, 0],
                       [1, 3, 0],
                        [0, 0, 1]])
L1 = np.array([[15],
               [20],
               [10]])

test_array2 = np.array([[7]])
L2 = np.array([[3]])

letters_in_order_by_freq_english_language = ["e", "t", "a", "o", "i", "n", "s", "h", "r", "d", "l", "c", "u", "m", "w",
                                             "f", "g", "y", "p", "b", "v", "k", "j", "x", "q", "z"]
test_msg = "python is fun"
test_msg2 = generate_random_text_with_respect_to_freq(letters_in_order_by_freq_english_language)

if __name__ == "__main__":
    b1 = check_matrix(test_array1)
    print("Test 1:")
    print("Is the given matrix invertible modulo 26: " + str(b1))
    if b1:
        enc1 = encrypt_msg(test_array1, test_msg, L1)
        dec1 = decrypt_msg(test_array1, enc1, L1)
        print("Encrypted message: " + enc1)
        print("Decrypted message: " + dec1)
    print("##############################")
    print("Test 2:")
    b2 = check_matrix(test_array2)
    print("Is the given matrix invertible modulo 26: " + str(b2))
    if b2:
        enc2 = encrypt_msg(test_array2, test_msg2, L2)
        dec2 = decrypt_msg(test_array2, enc2, L2)
        print("Encrypted message: " + enc2)
        print("Decrypted message: " + dec2)
        decrypted_with_attack = try_to_decrypt(letters_in_order_by_freq_english_language, enc2)
        print("Decrypted message using the frequency analysis attack: " + decrypted_with_attack)
        tmp = dec2 == decrypted_with_attack
        print("Was the attack successful?: " + str(tmp))