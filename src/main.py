from lark import Lark

if __name__ == "__main__":
    with open('../grammar.lark') as g, \
            open('../test files/test_file_1.txt') as f:
        print(Lark(g.read(), start='start').parse(f.read()).pretty())
