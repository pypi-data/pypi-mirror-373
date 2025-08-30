from blissoda.demo.exafs import exafs_processor


def exafs_demo(*args, nrepeats=3, **kw):
    for _ in range(nrepeats):
        exafs_processor.run(*args, **kw)
