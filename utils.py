import random


def generate_random_port(protocol):
    # Generate a random port number within a specified range
    # Modify the port range as per your requirements
    port_range_start = 5000 if protocol == 'udp' else 3000
    port_range_end = 6000 if protocol == 'udp' else 4000

    port = random.randint(port_range_start, port_range_end)
    return port


def print_menu(registered, connected):
    if registered:
        if not connected:
            print(
                """
            1) Get all users
            2) Get user info
            3) Connect to  a peer
                """
            )
        else:
            print(
                """
            1) Request quote
            2) Request Media
            3) Disconnect
                """
            )
    else:
        print(
            """
            1)Sign Up
            """
        )


def get_input():
    return input('enter your choice\n>')


def get_random_quote():
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Success is not the key to happiness. Happiness is the key to success. - Albert Schweitzer",
        "Believe you can and you're halfway there. - Theodore Roosevelt",
        "In the middle of difficulty lies opportunity. - Albert Einstein",
        "The best way to predict the future is to create it. - Peter Drucker",
        "The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt",
        "Success is not in what you have, but who you are. - Bo Bennett",
        "The secret of getting ahead is getting started. - Mark Twain",
        "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
        "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle. - Christian D. Larson",
        "The harder I work, the luckier I get. - Gary Player",
        "It always seems impossible until it's done. - Nelson Mandela",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt"
    ]
    random_quote = random.choice(quotes)
    return random_quote


def get_random_image():
    images = ['./images/imagine.jpg',
              './images/led.jpg',
              './images/pilots.jpg',
              './images/queen.jpg',
              ]
    return random.choice(images)
