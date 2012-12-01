def reformat():
    f = open("fileList")
    out = open("fileListOut", "w")
    for line in f:
        out.write('/home1/c/cis530/hw4/data/' + line.rstrip() + "\n")
    out.close()