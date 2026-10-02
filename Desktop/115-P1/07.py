import math

def solve_book_discount():
    n1 = int(input())
    n2 = int(input())
    n3 = int(input())
    
    def get_price_a(n):
        if n == 0:
            return 0.0
        elif 1 <= n <= 10:
            return 250 * n
        elif 11 <= n <= 20:
            return 250 * n * 0.9
        elif 21 <= n <= 30:
            return 250 * n * 0.85
        else:
            return 250 * n * 0.8

    def get_price_b(n):
        if n == 0:
            return 0.0
        elif 1 <= n <= 10:
            return 880 * n
        elif 11 <= n <= 20:
            return 880 * n * 0.95
        elif 21 <= n <= 30:
            return 880 * n * 0.9
        else:
            return 880 * n * 0.85

    def get_price_c(n):
        if n == 0:
            return 0.0
        elif 1 <= n <= 10:
            return 150 * n
        elif 11 <= n <= 20:
            return 150 * n * 0.85
        elif 21 <= n <= 30:
            return 150 * n * 0.75
        else:
            return 150 * n * 0.65

    total = get_price_a(n1) + get_price_b(n2) + get_price_c(n3)
    print(math.ceil(total))

if __name__ == "__main__":
    solve_book_discount()