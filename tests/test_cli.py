from pathlib import Path

import pytest

from swiss_tax_docs.cli import main

FIX = Path(__file__).parent.parent / "fixtures"
SYN = FIX / "decision_vd_2024_synthetique.txt"


def test_cli_json_ok(capsys):
    assert main([str(SYN), "--json"]) == 0
    out = capsys.readouterr().out
    assert '"revenu_imposable"' in out
    assert '"validations"' in out


def test_cli_humain_ok(capsys):
    assert main([str(SYN)]) == 0
    out = capsys.readouterr().out
    assert "décision de taxation VD" in out
    assert "5/5 validators OK" in out
    assert "solde" in out


def test_cli_document_non_reconnu(capsys):
    faux = Path("/tmp/swiss_tax_docs_pas_une_decision.txt")
    faux.write_text("Cher client, votre facture de 120.00 est en pièce jointe.")
    assert main([str(faux)]) == 1
    assert "non reconnu" in capsys.readouterr().err
    faux.unlink()


def test_cli_fichier_absent():
    assert main(["/non/existent.txt"]) == 2


def test_cli_falsifie_exit_zero_mais_warning(capsys):
    falsifie = Path("/tmp/swiss_tax_docs_falsifie.txt")
    falsifie.write_text(SYN.read_text().replace("6'859.68", "6'959.68"))
    assert main([str(falsifie)]) == 0  # parse OK, mais signale
    out = capsys.readouterr().out
    assert "⚠" in out and "revoir avant toute utilisation comptable" in out
    falsifie.unlink()
