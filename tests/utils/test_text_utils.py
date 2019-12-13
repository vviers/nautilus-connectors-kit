import logging
import unittest

from lib.utils.text import get_generator_dict_from_str_csv


class TestTextUtilsMethod(unittest.TestCase):

    def test_multiple_encodings(self):
        test_string_to_encode = (
            "BR,Sanofi Aventis Brasil,3945535,Active,Allegra,3992233,0,,"
            "YR_Sanofi_Allegra_201910_Consideration_DV360_Precision_"
            "Native-Ads_Cross-Device_BR,11140383,Active,,"
            "YR_Sanofi_Allegra_201910_Consideration_DV360_Precision_OA"
            "_Native-Ads_DV-Affinity-Health_Desktop_BR,"
            '1130016,0,,"    ",0.00,4080863'
        )
        lines = [
            (b"Country,Partner,Partner ID,Partner Status,Advertiser,Advertiser"
             b" ID,Advertiser Status,Advertiser Integration Code,Insertion"
             b" Order,Insertion Order ID,Insertion Order Status,Insertion"
             b" Order Integration Code,Line Item,Line Item ID,Line Item"
             b" Status,Line Item Integration Code,Targeted Data Providers,"
             b"Cookie Reach: Average Impression Frequency,Cookie Reach: "
             b"Impression Reach"),
            test_string_to_encode.encode("utf-8"),
            test_string_to_encode.encode("ascii"),
            test_string_to_encode.encode("windows-1252"),
            test_string_to_encode.encode("latin_1"),
        ]
        line_iterator_multiple_encodings = (line for line in lines)
        expected_dict = {
            "Country": "BR",
            "Partner": "Sanofi Aventis Brasil",
            "Partner ID": "3945535",
            "Partner Status": "Active",
            "Advertiser": "Allegra",
            "Advertiser ID": "3992233",
            "Advertiser Status": "0",
            "Advertiser Integration Code": "",
            "Insertion Order": (
                "YR_Sanofi_Allegra_201910_Consideration_DV360"
                "_Precision_Native-Ads_Cross-Device_BR"
            ),
            "Insertion Order ID": "11140383",
            "Insertion Order Status": "Active",
            "Insertion Order Integration Code": "",
            "Line Item": (
                "YR_Sanofi_Allegra_201910_Consideration_DV360_Precision_"
                "OA_Native-Ads_DV-Affinity-Health_Desktop_BR"
            ),
            "Line Item ID": "1130016",
            "Line Item Status": "0",
            "Line Item Integration Code": "",
            "Targeted Data Providers": '"    "',
            "Cookie Reach: Average Impression Frequency": "0.00",
            "Cookie Reach: Impression Reach": "4080863",
        }
        for yielded_dict in get_generator_dict_from_str_csv(
            line_iterator_multiple_encodings
        ):
            self.assertEqual(yielded_dict, expected_dict)

    def test_blank_line(self):
        lines = [
            (b"Country,Partner,Partner ID,Partner Status,Advertiser,Advertiser"
             b" ID,Advertiser Status,Advertiser Integration Code,Insertion"
             b" Order,Insertion Order ID,Insertion Order Status,Insertion"
             b" Order Integration Code,Line Item,Line Item ID,Line Item"
             b" Status,Line Item Integration Code,Targeted Data Providers,"
             b"Cookie Reach: Average Impression Frequency,Cookie Reach: "
             b"Impression Reach"),
            ""
        ]
        line_iterator_with_blank_line = (line for line in lines)
        self.assertTrue(get_generator_dict_from_str_csv(
            line_iterator_with_blank_line
        ))

        lines.insert(
            1,
            (b'BR,Sanofi Aventis Brasil,3945535,Active,Allegra,3992233,'
             b'0,,YR_Sanofi_Awareness_2019_Allegra_Hardsell_Display_DV360'
             b'_Cross-Device_BR,8674464,Active,,YR_Sanofi_Allegra_Hardsell'
             b'_Display_Datalogix-Health-Beauty-Buyers-Allergy_Desktop_BR'
             b',26143278,0,,"",0.00,41'))
        expected_dict = {
            "Country": "BR",
            "Partner": "Sanofi Aventis Brasil",
            "Partner ID": "3945535",
            "Partner Status": "Active",
            "Advertiser": "Allegra",
            "Advertiser ID": "3992233",
            "Advertiser Status": "0",
            "Advertiser Integration Code": "",
            "Insertion Order": (
                "YR_Sanofi_Awareness_2019_Allegra_Hardsell_Display_DV360"
                "_Cross-Device_BR"
            ),
            "Insertion Order ID": "8674464",
            "Insertion Order Status": "Active",
            "Insertion Order Integration Code": "",
            "Line Item": (
                "YR_Sanofi_Allegra_Hardsell_Display_Datalogix-Health"
                "-Beauty-Buyers-Allergy_Desktop_BR"
            ),
            "Line Item ID": "26143278",
            "Line Item Status": "0",
            "Line Item Integration Code": "",
            "Targeted Data Providers": '""',
            "Cookie Reach: Average Impression Frequency": "0.00",
            "Cookie Reach: Impression Reach": "41",
        }
        line_iterator_with_blank_line = (line for line in lines)
        for dic in get_generator_dict_from_str_csv(
            line_iterator_with_blank_line
        ):
            self.assertEqual(dic, expected_dict)

        lines.append("This is something that should not be here.")
        line_iterator_with_blank_line = (line for line in lines)
        test_result = get_generator_dict_from_str_csv(
            line_iterator_with_blank_line
        )
        self.assertEqual(len(list(test_result)), 1)
        for dic in test_result:
            self.assertEqual(dic, expected_dict)

    def test_invalid_byte(self):
        lines = [
            (b"Country,Partner,Partner ID,Partner Status,Advertiser,Advertiser"
             b" ID,Advertiser Status,Advertiser Integration Code,Insertion"
             b" Order,Insertion Order ID,Insertion Order Status,Insertion"
             b" Order Integration Code,Line Item,Line Item ID,Line Item"
             b" Status,Line Item Integration Code,Targeted Data Providers,"
             b"Cookie Reach: Average Impression Frequency,Cookie Reach: "
             b"Impression Reach"),
            (b'BR,Sanofi Aventis Brasil,3945535,Active,Allegra,3992233,'
             b'0,,YR_Sanofi_Awareness_2019_Allegra_Hardsell_Display_DV360'
             b'_Cross-Device_BR,8674464,Active,,YR_Sanofi_Allegra_Hardsell'
             b'_Display_Datalogix-Health-Beauty-Buyers-Allergy_Desktop_BR'
             b',26143278,0,,"   \x91\xea\xd0$",0.00,41'),
        ]
        line_iterator_invalid_byte = (line for line in lines)
        expected_dict = {
            "Country": "BR",
            "Partner": "Sanofi Aventis Brasil",
            "Partner ID": "3945535",
            "Partner Status": "Active",
            "Advertiser": "Allegra",
            "Advertiser ID": "3992233",
            "Advertiser Status": "0",
            "Advertiser Integration Code": "",
            "Insertion Order": (
                "YR_Sanofi_Awareness_2019_Allegra_Hardsell_Display_DV360"
                "_Cross-Device_BR"
            ),
            "Insertion Order ID": "8674464",
            "Insertion Order Status": "Active",
            "Insertion Order Integration Code": "",
            "Line Item": (
                "YR_Sanofi_Allegra_Hardsell_Display_Datalogix-Health-Beauty"
                "-Buyers-Allergy_Desktop_BR"
            ),
            "Line Item ID": "26143278",
            "Line Item Status": "0",
            "Line Item Integration Code": "",
            "Targeted Data Providers": '"   $"',
            "Cookie Reach: Average Impression Frequency": "0.00",
            "Cookie Reach: Impression Reach": "41",
        }
        with self.assertLogs(level=logging.INFO) as cm:
            for yielded_dict in get_generator_dict_from_str_csv(
                line_iterator_invalid_byte
            ):
                self.assertEqual(yielded_dict, expected_dict)
        self.assertEqual(
            cm.output,
            ["WARNING:root:An error has occured while parsing the file. "
             "The line could not be decoded in utf-8."
             "Invalid input that the codec failed on: b'\\x91'"]
        )