import unittest

import pandas as pd

from data_utils import filter_annuaire, load_annuaire, numeric_series, truthy_series


class LoadAnnuaireTests(unittest.TestCase):
    def setUp(self):
        self.csv_cp1252 = (
            "identifiant_de_l_etablissement;nom_etablissement;type_etablissement;"
            "code_postal;restauration\n"
            "0010001W;Lycée professionnel Alexandre Bérard;Lycée;01505;1\n"
        ).encode("cp1252")

    def test_reads_windows_encoding_and_preserves_identifiers(self):
        frame = load_annuaire(self.csv_cp1252)

        self.assertEqual(frame.loc[0, "identifiant_de_l_etablissement"], "0010001W")
        self.assertEqual(frame.loc[0, "code_postal"], "01505")
        self.assertEqual(frame.loc[0, "nom_etablissement"], "Lycée professionnel Alexandre Bérard")

    def test_handles_invalid_windows_bytes_without_failing(self):
        source = self.csv_cp1252.replace(b"B\xe9rard", b"B\x8f\xe9rard")

        frame = load_annuaire(source)

        self.assertIn("nom_etablissement", frame.columns)
        self.assertEqual(frame.loc[0, "identifiant_de_l_etablissement"], "0010001W")

    def test_rejects_empty_file(self):
        with self.assertRaisesRegex(ValueError, "vide"):
            load_annuaire(b"  \r\n")

    def test_rejects_csv_without_required_columns(self):
        with self.assertRaisesRegex(ValueError, "Colonnes requises manquantes"):
            load_annuaire(b"nom;ville\nEcole;Paris\n")


class DataHelpersTests(unittest.TestCase):
    def test_numeric_series_converts_values_and_missing_values(self):
        frame = pd.DataFrame({"latitude": ["48,85", "invalid", None]})

        values = numeric_series(frame, "latitude")

        self.assertEqual(values.iloc[0], 48.85)
        self.assertTrue(pd.isna(values.iloc[1]))
        self.assertTrue(pd.isna(values.iloc[2]))

    def test_truthy_series_supports_numeric_and_text_flags(self):
        frame = pd.DataFrame({"service": ["1", "0.0", "Oui", None]})

        values = truthy_series(frame, "service")

        self.assertEqual(values.tolist(), [True, False, True, False])

    def test_combined_filters_match_search_and_service(self):
        frame = pd.DataFrame(
            {
                "identifiant_de_l_etablissement": ["001", "002"],
                "nom_etablissement": ["École du centre", "École du centre"],
                "nom_commune": ["Lyon", "Lyon"],
                "libelle_region": ["Auvergne-Rhône-Alpes"] * 2,
                "libelle_departement": ["Rhône"] * 2,
                "type_etablissement": ["École"] * 2,
                "statut_public_prive": ["Public", "Privé"],
                "etat": ["OUVERT"] * 2,
                "restauration": ["1", "0"],
            }
        )

        results = filter_annuaire(
            frame,
            search="001",
            regions=["Auvergne-Rhône-Alpes"],
            departments=["Rhône"],
            establishment_types=["École"],
            statuses=["Public"],
            states=["OUVERT"],
            commune="lyon",
            services=[("restauration", "Restauration")],
        )

        self.assertEqual(results["identifiant_de_l_etablissement"].tolist(), ["001"])


if __name__ == "__main__":
    unittest.main()
