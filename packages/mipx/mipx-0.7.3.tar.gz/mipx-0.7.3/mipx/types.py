from .tupledict import ITupledict as TupleDict


if __name__ == "__main__":
    import mipx

    model = mipx.Model()
    x: TupleDict[int, int, int] = mipx.tupledict()
    x[1, 2, 3] = 1
