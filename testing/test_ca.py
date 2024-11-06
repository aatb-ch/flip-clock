### test a 1d cellular automata implementation
# valid only for 1d with neighborhood 3 and 2 states

CA_RULE = 30 # 90, 110, 184
CA_SIZE = 100

def expand_rule(rule):
    bits = [int(digit) for digit in f'{rule:08b}']
    bits.reverse()
    ruleset = dict()
    for i in range(8):
        ibits = tuple(int(digit) for digit in f'{i:03b}')
        ruleset[ibits] = bits[i]
        # print(i, ibits)
    return ruleset

def init():
    curr_state = [0] * CA_SIZE
    curr_state[round(CA_SIZE/2)] = 1
    return curr_state

def evolve(curr):
    new_state = []
    for i in range(0, CA_SIZE):
        window = (curr[(i-1)%CA_SIZE], curr[i], curr[(i+1)%CA_SIZE])
        new_state.append(rule_set[window])
    return new_state

def print_state(state):
    s = ''.join(['X' if state[i] == 1 else ' ' for i in range(CA_SIZE)])
    print(s)


rule_set = expand_rule(CA_RULE)

curr_state = init()

print_state(curr_state)
for i in range(100):
    curr_state = evolve(curr_state)
    print_state(curr_state)
