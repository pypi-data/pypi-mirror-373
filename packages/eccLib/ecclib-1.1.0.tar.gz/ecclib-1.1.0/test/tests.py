import unittest
import eccLib
import io
from io import StringIO


class eccLibTest(unittest.TestCase):
    GTF_FILENAME = "./test/example.gtf"
    FASTA_FILENAME = "./test/example.fna"

    def setUp(self) -> None:
        super().setUp()


class GtfDictTest(eccLibTest):
    def setUp(self) -> None:
        self.t = eccLib.GtfDict(
            "1", "ensembl_havana", "intron", 1471765, 1497848, 0.0, True, None
        )
        return super().setUp()


class parseGTFTest(eccLibTest):
    def testBrokenGTFdumpLine(self):
        gtf = """1\ttranscribed_unprocessed_pseudogene  gene        11869 14409 . + . gene_id "ENSG00000223972"; gene_name "DDX11L1"; gene_source "havana"; gene_biotype "transcribed_unprocessed_pseudogene"; """
        with self.assertRaises(ValueError):
            eccLib.parseGTF(gtf)

    def testFixedGTFdumpLine(self):
        gtf = """1\ttranscribed_unprocessed_pseudogene\tgene\t11869\t14409\t.\t+\t.\tgene_id "ENSG00000223972"; gene_name "DDX11L1"; gene_source "havana"; gene_biotype "transcribed_unprocessed_pseudogene"; """
        parsed = eccLib.parseGTF(gtf)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(len(parsed[0].keys()), 12)
        self.assertEqual(parsed[0]["gene_id"], "ENSG00000223972")
        self.assertEqual(parsed[0]["gene_name"], "DDX11L1")
        self.assertEqual(parsed[0]["gene_source"], "havana")
        self.assertEqual(
            parsed[0]["gene_biotype"], "transcribed_unprocessed_pseudogene"
        )

    def testMessyGTFdumpLine(self):
        gtf = """
        1\ttranscribed_unprocessed_pseudogene\tgene\t11869\t14409\t.\t+\t.\tgene_id "ENSG00000223972"; gene_name "DDX11L1"; gene_source "havana"; gene_biotype "transcribed_unprocessed_pseudogene";
        """
        parsed = eccLib.parseGTF(gtf)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(len(parsed[0].keys()), 12)
        self.assertEqual(parsed[0]["gene_id"], "ENSG00000223972")
        self.assertEqual(parsed[0]["gene_name"], "DDX11L1")
        self.assertEqual(parsed[0]["gene_source"], "havana")
        self.assertEqual(
            parsed[0]["gene_biotype"], "transcribed_unprocessed_pseudogene"
        )

    def testParseGFF2(self):
        gff = """
        X\tEnsembl\tRepeat\t2419108\t2419128\t42\t.\t.\thid=trf; hstart=1; hend=21; NOTE test; NOTE2 "test"; NOTE3 test
        """
        parsed = eccLib.parseGTF(gff)
        self.assertEqual(len(parsed[0].keys()), 14)
        self.assertEqual(parsed[0]["hstart"], "1")
        self.assertEqual(parsed[0]["hend"], "21")
        self.assertEqual(parsed[0]["NOTE"], "test")
        self.assertEqual(parsed[0]["NOTE2"], "test")
        self.assertEqual(parsed[0]["NOTE3"], "test")

    def testParseGFF3(self):
        gff = """
        ctg123\test\tEST_match\t7000\t7300\t.\t+\t.\tID=Match3;Name=agt221.5;Target=agt221.5 953 1253
        """
        parsed = eccLib.parseGTF(gff)
        self.assertEqual(len(parsed[0].keys()), 11)
        self.assertEqual(parsed[0]["Target"], "agt221.5 953 1253")
        self.assertEqual(parsed[0]["ID"], "Match3")
        self.assertEqual(parsed[0]["Name"], "agt221.5")

    def testParseNone(self):
        gtf = """.\t.\t.\t.\t.\t.\t.\t.\t
        """
        parsed = eccLib.parseGTF(gtf)
        self.assertEqual(tuple(parsed[0].values()), (None,) * 8)

    def testParseNone2(self):
        gtf = """.\t.\t.\t.\t.\t.\t.\t.
        """
        parsed = eccLib.parseGTF(gtf)
        self.assertEqual(tuple(parsed[0].values()), (None,) * 8)

    def testParseNone3(self):
        gtf = """.\t.\t.\t.\t.\t.\t.\t.\t;"""
        parsed = eccLib.parseGTF(gtf)
        self.assertEqual(tuple(parsed[0].values()), (None,) * 8)

    def testImmutable(self):
        gtf = """1\ttranscribed_unprocessed_pseudogene\tgene\t11869\t14409\t.\t+\t.\tgene_id "ENSG00000223972"; gene_name "DDX11L1"; gene_source "havana" """
        res = eccLib.parseGTF(gtf)
        self.assertEqual(
            gtf,
            """1\ttranscribed_unprocessed_pseudogene\tgene\t11869\t14409\t.\t+\t.\tgene_id "ENSG00000223972"; gene_name "DDX11L1"; gene_source "havana" """,
        )
        self.assertEqual(res[0]["gene_id"], "ENSG00000223972")

    def testWeirdAttr(self):
        gtf = """
        ctg123\test\tEST_match\t1050\t1500\t.\t+\t.\tID=Match3;Name=agt221.5;Target=agt221.5 1 451
        ctg123\test\tEST_match\t5000\t5500\t.\t+\t.\tID=Match3;Name=agt221.5;Target=agt221.5 452 952
        ctg123\test\tEST_match\t7000\t7300\t.\t+\t.\tID=Match3;Name=agt221.5;Target=agt221.5 953 1253
        """
        res = eccLib.parseGTF(gtf)
        self.assertEqual(res[0]["ID"], "Match3")
        self.assertEqual(res[0]["Name"], "agt221.5")
        self.assertEqual(res[0]["Target"], "agt221.5 1 451")

    def testFASTAsection(self):
        gtf = """
        ctg123\test\tEST_match\t1050\t1500\t.\t+\t.\tID=Match3;Name=agt221.5;Target=agt221.5 1 451
        ##FASTA
        hello this is non gtf data
        """
        res = eccLib.parseGTF(gtf)
        self.assertEqual(res[0]["ID"], "Match3")
        self.assertEqual(res[0]["Name"], "agt221.5")

    def testEscape(self):
        gtf = """
        ctg123\test\tEST_%09match\t1050\t1500\t.\t+\t.\ttest=a%09h
        """
        res = eccLib.parseGTF(gtf)
        self.assertEqual(len(res[0]["test"]), 3)
        self.assertEqual(res[0]["test"], "a\th")
        self.assertEqual(res[0]["feature"], "EST_\tmatch")

    def testEscapeWithUnicode(self):
        gtf = """
        ctg123\test\tEST_%09match\t1050\t1500\t.\t+\t.\tt%09est=a%09hł;test2="ï»ï"
        """
        res = eccLib.parseGTF(gtf)
        self.assertEqual(res[0]["test2"], "ï»ï")
        self.assertEqual(bytes(res[0]["t\test"], "utf8"), b"a\th\xc5\x82")

    def testFP(self):
        with open(self.GTF_FILENAME, "r") as f:
            res = eccLib.parseGTF(f)
            f.seek(0)
            self.assertEqual(res, eccLib.parseGTF(f.read()))

    def testIO(self):
        obj = io.StringIO(
            """1\ttranscribed_unprocessed_pseudogene\tgene\t11869\t14409\t.\t+\t.\tgene_id "ENSG00000223972"; gene_name "DDX11L1"; gene_source "havana" """
        )
        res = eccLib.parseGTF(obj)
        self.assertEqual(res[0]["gene_id"], "ENSG00000223972")

    def testUTF8(self):
        gtf = """1\tgrzegorz brzęczyszczykiewicz\tpowiat łękołody\t11869\t14409\t.\t+\t.\tgene_id "ENSG00000223972"; imię "DDX11L1"; gene_source "havana" """
        res = eccLib.parseGTF(gtf)
        self.assertEqual(res[0].source, "grzegorz brzęczyszczykiewicz")
        self.assertEqual(res[0].feature, "powiat łękołody")
        self.assertEqual(res[0]["imię"], "DDX11L1")

    def testInvalidUTF8(self):
        gtf = """1	.	eccDNA	12640	12867	.	+	.	conf "hconf";codingGene ".";sample "﻿05t";"""
        eccLib.parseGTF(gtf)

    def testEncodedInvalidUTF8(self):
        gtf = """1	.	eccDNA	12640	12867	.	+	.	conf "hconf";codingGene ".";sample "%eF%fB%fF05t";fragile "True";cpg "False";cpg_count "0";centromere "False";centromere_distance "122.013593";chrEnd "True";chrEnd_distance "0.01264";intronic "True";"""
        with self.assertRaises(ValueError):
            eccLib.parseGTF(gtf)

    def testDuplicateKeys(self):
        gtf = """1	.	eccDNA	12640	12867	.	+	.	sample "05t";sample "05t";"""
        res = eccLib.parseGTF(gtf)
        self.assertEqual(res[0]["sample"], "05t")

    def testDuplicateValues(self):
        gtf = """1	.	eccDNA	12640	12867	.	+	.	sample1 "05t";sample2 "05t";"""
        res = eccLib.parseGTF(gtf)
        res[0]["sample1"] += "1"
        self.assertEqual(res[0]["sample1"], "05t1")
        self.assertEqual(res[0]["sample2"], "05t")

    def testALotOfKeys(self):
        d = eccLib.GtfDict()
        for i in range(100000):
            d[str(i)] = i
            self.assertEqual(d[str(i)], i)
        gtf = str(d)
        self.assertEqual(eccLib.parseGTF(gtf)[0], d)

    def testAttrConf(self):
        gtf = """1	.	eccDNA	12640	12867	.	+	.	cpg "False";cpg_count "0" """
        res = eccLib.parseGTF(
            gtf, attr_tp={"cpg_count": int, "cpg": lambda x: x.lower() == "true"}
        )
        self.assertEqual(res[0]["cpg_count"], 0)
        self.assertEqual(res[0]["cpg"], False)


class readerTest(eccLibTest):
    def testIO(self):
        gtf = """1\ttranscribed_unprocessed_pseudogene\tgene\t11869\t14409\t.\t+\t.\tgene_id "ENSG00000223972"; gene_name "DDX11L1"; gene_source "havana" """

        f = StringIO(gtf)
        reader = eccLib.GtfReader(f)
        obj = next(reader)
        self.assertEqual(obj.seqname, "1")

    def testGet(self):
        file = eccLib.GtfFile(self.GTF_FILENAME)
        iter = file.__enter__().__iter__()
        first = next(iter)
        self.assertEqual(
            first,
            {
                "seqname": "1",
                "source": "havana",
                "feature": "gene",
                "start": 2581560,
                "end": 2584533,
                "score": None,
                "reverse": False,
                "frame": None,
                "gene_id": "ENSG00000228037",
                "gene_version": "1",
                "gene_source": "havana",
                "gene_biotype": "lncRNA",
            },
        )
        file.__exit__()

    def testWith(self):
        with eccLib.GtfFile(self.GTF_FILENAME) as f:
            i = 0
            for d in f:
                i += 1
            n = 0
            for d in f:
                n += 1
            self.assertEqual(n, i)

    def testSeparate(self):
        with open(self.GTF_FILENAME, "r") as f:
            reader = eccLib.GtfReader(f)
            first = next(reader)
            self.assertEqual(
                first,
                {
                    "seqname": "1",
                    "source": "havana",
                    "feature": "gene",
                    "start": 2581560,
                    "end": 2584533,
                    "score": None,
                    "reverse": False,
                    "frame": None,
                    "gene_id": "ENSG00000228037",
                    "gene_version": "1",
                    "gene_source": "havana",
                    "gene_biotype": "lncRNA",
                },
            )

    def testAttrConf(self):
        gtf = """1	.	eccDNA	12640	12867	.	+	.	cpg "False";cpg_count "0" """
        res = next(
            eccLib.GtfReader(
                StringIO(gtf),
                attr_tp={"cpg_count": int, "cpg": lambda x: x.lower() == "true"},
            )
        )
        self.assertEqual(res["cpg_count"], 0)
        self.assertEqual(res["cpg"], False)


class testCircular(eccLibTest):
    def testDumpParse(self):
        d = eccLib.GtfDict(
            "1", "ensembl_havana", "intron", 1471765, 1497848, 0.0, True, None
        )
        res = eccLib.parseGTF(str(d))
        self.assertEqual(res[0], d)

    def testRestricted(self):
        d = eccLib.GtfDict(
            "1#;\t",
            "ensembl_havana",
            "intron",
            1471765,
            1497848,
            0.0,
            True,
            None,
        )
        res = eccLib.parseGTF(str(d))
        self.assertEqual(res[0], d)


class echoTest(eccLibTest):
    def setUp(self) -> None:
        super().setUp()
        self.stdout = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")

    def testEchoParseGTF(self):
        with open(self.GTF_FILENAME, "r") as f:
            eccLib.parseGTF(f, self.stdout)
            self.stdout.seek(0)
            self.assertNotEqual(self.stdout.read(), "")


if __name__ == "__main__":
    unittest.main()
