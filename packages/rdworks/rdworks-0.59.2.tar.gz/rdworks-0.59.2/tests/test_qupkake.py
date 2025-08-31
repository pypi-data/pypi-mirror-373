import rdworks
from pathlib import Path

datadir = Path(__file__).parent.resolve() / "data"

def test_readin_qupkake_output():
    libr = rdworks.read_sdf(datadir / 'qupkake_output_SAMPL6_SM07.sdf', confs=True)
    # libr contains one molecule because of confs=True
    assert libr.count() == 1
    for m in libr:
        assert m.count() == 3
        print(m.props)
        print()
        for c in m:
            print(c.props)
            print()

        print(m.serialize(compressed=True))


if __name__ == '__main__':
    test_readin_qupkake_output()
