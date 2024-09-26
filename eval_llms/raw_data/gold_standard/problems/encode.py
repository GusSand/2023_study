""" Write a function that takes a message, and encodes in such a way that it 
swaps case of all letters, 
replaces all vowels in the message with the letter that appears 2 places ahead of that vowel in the english alphabet. 
Assume only letters. 

Examples: 
>>> encode('test') 'TGST' 
>>> encode('This is a message') 'tHKS KS C MGSSCGG' """


def encode(message):

    vowels = 'aeiou'
    encoded = ''
    for char in message:
        charswap = char.swapcase()

        if char.lower() in vowels:
            encoded += chr(ord(charswap) + 2)
        else:
            encoded += charswap
    
    return encoded

