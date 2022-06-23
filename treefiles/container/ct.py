if __name__ == "__main__":
    import treefiles as tf
    import numpy as np

    out = tf.f(__file__, "out")
    aze = [1, 22, 6]
    azer = np.array(aze)

    with out.ct("main_container211121") as ct:
        #     # tf.dump_json(ct / "test222.json", aze)
        #     # tf.dump_json(ct / "hello/test21.json", aze)
        #     # tf.dump_json(ct / "Bonjour/test21.json", aze)
        #
        #     # np.save(ct / "arr.npy", azer)
        #     print(ct)

        # with tf.Container(out / "main_container211121") as ct:

        # print(ct.test222)
        # print(ct.test21)
        # print(ct.Bonjour.test21)
        print(ct)
        np.save(ct / "arr.npy", azer)
        print(np.load(ct.arr).shape)

        # print(tf.load_json(ct.Bonjour.test21))
