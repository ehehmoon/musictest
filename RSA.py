import pandas as pd
pd.options.display.float_format = '{:.5f}'.format

while True:
    p = int(input('p : '))
    q = int(input('q : '))
    N = p * q

    g = 2
    r = 0
    n_remain = 0

    while n_remain != 1:
        r = r + 1
        n_remain = (g**r)%N
        print(n_remain, r)

    r = r/2
    g1 = g**r - 1
    first_num = g1
    second_num = N
    print(first_num)
    print(second_num)

    while second_num != 0:
        second_num_alt = second_num
        second_num = first_num%second_num
        print(second_num)
        first_num = second_num_alt

    print(f'Maybe p or q is: {second_num_alt} and {N/second_num_alt}')
