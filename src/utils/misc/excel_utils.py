import io
from datetime import datetime
import pandas as pd
from aiogram.types import BufferedInputFile
from typing import List

from src.database.models.tests import Test
from src.database.models.submissions import Submission


async def generate_test_report(test: Test, submissions: List[Submission]):
    data = []
    test_score = sum(answer.score for answer in test.answers)
    for i, submission in enumerate(submissions, start=1):
        data.append(
            {
                "T/R": i,
                "Ism familiya": submission.user.full_name,
                "Soni": submission.correct_count,
                "Ball": submission.score,
                "Foizda": (
                    ((submission.score / test_score) * 100)
                    if test_score > 0
                    else (
                        (
                            submission.correct_count
                            / (submission.correct_count + submission.incorrect_count)
                        )
                        * 100
                    )
                ),
                "Sana": submission.created_at.strftime("%d.%m.%Y"),
                "Vaqt": submission.created_at.strftime("%H:%M:%S"),
            }
        )

    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Natijalar", index=False, startrow=3)

        workbook = writer.book
        worksheet = writer.sheets["Natijalar"]

        header_text = (
            f"Test kodi: {test.id} | "
            f"Test nomi: {test.name} | "
            f"Jami ball: {test_score} | "
            f"Testlar soni: {len(test.answers)} | "
            f"Qatnashuvchilar soni: {len(submissions)}"
        )
        header_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "#D7E4BC",
                "border": 1,
            }
        )

        worksheet.merge_range("A1:G1", header_text, header_format)

        worksheet.set_column("A:A", 5)  # T/R
        worksheet.set_column("B:B", 25)  # Ism familiya
        worksheet.set_column("C:C", 10)  # Soni
        worksheet.set_column("D:D", 10)  # Ball
        worksheet.set_column("E:E", 15)  # Foizda
        worksheet.set_column("F:F", 12)  # Sana
        worksheet.set_column("G:G", 10)  # Vaqt

        percent_format = workbook.add_format({"num_format": "0.00%"})
        worksheet.set_column("E:E", None, percent_format)

    output.seek(0)
    return BufferedInputFile(output.read(), filename=f"test_{test.id}_results.xlsx")
