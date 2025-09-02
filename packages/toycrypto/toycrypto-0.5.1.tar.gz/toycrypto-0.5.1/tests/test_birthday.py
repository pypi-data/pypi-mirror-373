import math
import sys

import pytest
from toy_crypto import birthday


class TestBirthday:
    vectors = [
        (
            23,
            365,
            38093904702297390785243708291056390518886454060947061
            / 75091883268515350125426207425223147563269805908203125,
        ),
        (10, 365, 2689423743942044098153 / 22996713557917153515625),
    ]

    # data from table in https://en.wikipedia.org/wiki/Birthday_attack
    # tuples are (bits, prob, n)
    hash_vectors: list[tuple[int, float, int]] = [
        (16, 1e-17, 2), (16, 1e-14, 2), (16, 1e-11, 2),
        (16, 1e-08, 2), (16, 1e-05, 2), (16, 0.01, 11),
        (16, 0.1, 36), (16, 0.25, 190), (16, 0.5, 300),
        (16, 0.75, 430), (32, 1e-17, 2), (32, 1e-14, 2),
        (32, 1e-11, 2), (32, 1e-08, 3), (32, 1e-05, 93),
        (32, 0.01, 2900), (32, 0.1, 9300), (32, 0.25, 50),
        (32, 0.5, 0), (32, 0.75, 77), (64, 1e-17, 6),
        (64, 1e-14, 190), (64, 1e-11, 6100), (64, 1e-08, 190),
        (64, 1e-05, 0), (64, 0.01, 6), (64, 0.1, 100),
        (64, 0.25, 0), (64, 0.5, 190000000), (64, 0.75, 610000000),
        (128, 1e-17, 26000000000),
        (128, 1e-14, 820000000000),
        (128, 1e-11, 26000000000000),
        (128, 1e-08, 820000000000000),
        (128, 1e-05, 26000000000000000),
        (128, 0.01, 830000000000000000),
        (128, 0.1, 2600000000000000000),
        (128, 0.25, 14000000000000000000),
        (128, 0.5, 22000000000000000000),
        (128, 0.75, 31000000000000000000),
        (256, 1e-17, 480000000000000015174119456768),
        (256, 1e-14, 14999999999999999453844442447872),
        (256, 1e-11, 479999999999999982523022158331904),
        (256, 1e-08, 15000000000000000913010721715912704),
        (256, 1e-05, 480000000000000029216343094909206528),
        (256, 0.01, 15000000000000001079031418379298668544),
        (256, 0.1, 47999999999999999675007352518039568384),
        (256, 0.25, 259999999999999990369012354689972305920),
        (256, 0.5, 399999999999999990995239293824136118272),
        (256, 0.75, 569999999999999970167696655368671199232),
        (
            384,
            1e-17,
            8900000000000000471357641515784838152032029245440,
        ),
        (384, 1e-14, 279999999999999979824980686778662580981931284889600),
        (
            384,
            1e-11,
            8900000000000000471357641515784838152032029245440000,
        ),
        (
            384,
            1e-08,
            279999999999999998101865628821255833409278363744337920,
        ),
        (
            384,
            1e-05,
            8899999999999999641919372145997333460056423630504984576,
        ),
        (
            384,
            0.01,
            280000000000000008310336636449409737310516586697384263680,
        ),
        (
            384,
            0.1,
            889999999999999975080972956069764176833629800867081224192,
        ),
        (
            384,
            0.25,
            4800000000000000092684464663841168841538056056222209015808,
        ),
        (
            384,
            0.5,
            7400000000000000113851121046168386415163203252498351521792,
        ),
        (
            384,
            0.75,
            9999999999999999438119489974413630815797154428513196965888,
        ),
        (
            512,
            1e-17,
            159999999999999997237884125426969573075836526009294916457234354405376,
        ),
        (
            512,
            1e-14,
            5200000000000000377163469183952022656023546930161914168694692808491008,
        ),
        (
            512,
            1e-11,
            160000000000000011605029821044677620185339905543443512882913624876646400,
        ),
        (
            512,
            1e-08,
            5199999999999999629305645241398259777150197680811032562750001182893146112,
        ),
        (
            512,
            1e-05,
            159999999999999997285391487193812127684945283850954501149415267193067667456,
        ),
        (
            512,
            0.01,
            5199999999999999698353764330651748179343881336095363139875911071997525753856,
        ),
        (
            512,
            0.1,
            15999999999999998824636498823699182776140851443191486196202342716485796888576,
        ),
        (
            512,
            0.25,
            88000000000000001570190964825296882978585144643366186690127853854636059394048,
        ),
        (
            512,
            0.5,
            140000000000000000160666652390804640313986050345482420611089958357404152233984,
        ),
        (
            512,
            0.75,
            190000000000000005727549465704058670855708242067140779476889493597481070493696,
        ),
    ]  # fmt: skip

    # From table 3 of DM69
    k_p50_c365_vectors = [
        (2, 23), (3, 88), (4, 187), (5, 313),
        (6, 460), (7, 623), (8, 798), (9, 985),
        (10, 1181), (11, 1385), (12, 1596), (13, 1813),
    ]  # fmt: skip

    def test_pbirthday(self) -> None:
        for n, d, expected in self.vectors:
            p = birthday.P(n, d, mode="exact")
            assert math.isclose(p, expected)

    def test_qbrithday(self) -> None:
        for expected_n, d, p in self.vectors:
            n = birthday.Q(p, d)
            assert n == expected_n

    def test_inverse_365(self) -> None:
        d = 365

        for n in range(10, 360, 10):
            p = birthday.P(n, d)
            if p > birthday.MAX_QBIRTHDAY_P:
                continue
            n2 = birthday.Q(p, d)

            assert n == n2

    def test_wp_data(self) -> None:
        for bits, p, n in self.hash_vectors:
            if p < 3:  # We need a different test in these cases
                continue
            c = 2**bits
            my_p = birthday.P(n, c)
            assert math.isclose(p, my_p)

            my_n = birthday.Q(p, c)
            assert math.isclose(n, my_n)

    def test_k_p(self) -> None:
        expected_p = 0.5
        c = 365
        wiggle_room = 0.01  # because P always uses approximation when k > 2
        for k, n in self.k_p50_c365_vectors:
            calculated_p = birthday.P(n, c, k)
            p_below = birthday.P(n - 1, c, k)

            assert calculated_p + wiggle_room >= expected_p
            assert p_below < expected_p + wiggle_room

    def test_k_q(self) -> None:
        p = 0.5
        c = 365
        for k, expected_n in self.k_p50_c365_vectors:
            calculated_n = birthday.Q(p, c, k)
            assert math.isclose(calculated_n, expected_n, rel_tol=0.01)


class TestSpecialCasesP:
    def test_exsct_n_equal_c(self) -> None:
        p = birthday.P(n=20, classes=20, mode="exact")
        assert p == 1.0

    def test_approx_n_equal_c(self) -> None:
        p = birthday.P(n=20, classes=20, mode="approximate")
        assert p == 1.0

    def test_n_gt_c(self) -> None:
        p = birthday.P(n=20, classes=19, mode="exact")
        assert p == 1.0

    def test_n_gt_ck(self) -> None:
        p = birthday.P(n=20, classes=10, coincident=3, mode="approximate")
        assert p == 1.0

    def test_exact_k_lt_two(self) -> None:
        p = birthday.P(n=23, classes=365, coincident=1, mode="exact")
        assert p == 1.0

    def test_approx_k_lt_two(self) -> None:
        p = birthday.P(n=23, classes=365, coincident=1, mode="approximate")
        assert p == 1.0


class TestSpecialCasesQ:
    def test_p_is_0(self) -> None:
        q = birthday.Q(prob=0.0)
        assert q == 1.0

    def test_big_p(self) -> None:
        p = (1.0 + birthday.MAX_QBIRTHDAY_P) / 2.0

        c_vec = range(100, 5000, 100)
        k_vec = range(2, 35, 5)

        for c in c_vec:
            for k in k_vec:
                q = birthday.Q(prob=p, classes=c, coincident=k)
                assert q == c * (k - 1) + 1


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
