import argparse
from .normal import dnorm, pnorm, qnorm

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("pnorm"); sp.add_argument("q", type=float)
    sq = sub.add_parser("qnorm"); sq.add_argument("p", type=float)
    sd = sub.add_parser("dnorm"); sd.add_argument("x", type=float)

    args = ap.parse_args()
    if args.cmd == "pnorm":
        print(pnorm(args.q))
    elif args.cmd == "qnorm":
        print(qnorm(args.p))
    else:
        print(dnorm(args.x))

if __name__ == "__main__":
    main()
