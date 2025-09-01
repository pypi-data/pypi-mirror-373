import argparse

parser = argparse.ArgumentParser(description="calculate X to the power of Y")
parser.add_argument(
    "square", type=int, help="display a square of a given number")
parser.add_argument(
    "-v",
    "--verbosity",
    type=str,
    choices=['low', 'middle', 'high'],
    default='low',
    help="increase output verbosity")
args = parser.parse_args()
answer = args.square**2
if args.verbosity == 'high':
    print("the square of {} equals {}".format(args.square, answer))
elif args.verbosity == 'middle':
    print("{}^2 == {}".format(args.square, answer))
else:
    print(answer)
