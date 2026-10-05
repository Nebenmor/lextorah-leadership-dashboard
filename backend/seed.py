# backend/seed.py

# backend/seed.py
"""Seed mock data: Lextorah Demo School, French A1 (30 students).

Metric definitions (reused by analytics.py in the next step):
- average assessment score: mean of each student's latest score
- declining scores: every recent score is lower than the previous one
- low attendance: attendance < 75
- incomplete practice: practice_completion < 50
"""
from app.database import Base, SessionLocal, engine
from app.models import Student

CLASS_NAME = "French A1"

# (name, attendance, practice_completion, speaking, listening, recent_scores)
STUDENTS = [
    ("Sarah", 68, 20, 38, 44, [72, 64, 51]),
    ("Chidi Okafor", 72, 35, 45, 50, [70, 62, 55]),
    ("Amina Bello", 70, 30, 52, 48, [68, 60, 54]),
    ("Tunde Adeyemi", 66, 25, 50, 55, [75, 66, 58]),
    ("Ngozi Eze", 71, 40, 58, 60, [66, 60, 52]),
    ("Emeka Nwosu", 69, 45, 62, 66, [73, 69, 61]),
    ("Fatima Yusuf", 73, 48, 60, 58, [65, 61, 57]),
    ("Kemi Ajayi", 67, 30, 55, 60, [58, 60, 61]),
    ("David Okon", 72, 42, 57, 53, [56, 58, 59]),
    ("Zainab Musa", 77, 38, 50, 57, [53, 54, 57]),
    ("Ifeanyi Obi", 75, 44, 56, 58, [55, 56, 54]),
    ("Bisi Alade", 78, 65, 64, 61, [60, 61, 62]),
    ("Chioma Uche", 75, 70, 59, 63, [59, 58, 60]),
    ("Yusuf Garba", 76, 85, 75, 72, [68, 70, 73]),
    ("Halima Sani", 77, 80, 70, 74, [66, 68, 69]),
    ("Peter Eke", 75, 90, 78, 76, [70, 72, 75]),
    ("Aisha Lawal", 76, 75, 68, 70, [64, 65, 67]),
    ("Segun Bakare", 75, 72, 66, 68, [62, 63, 64]),
    ("Rita Obaseki", 76, 78, 65, 69, [61, 64, 65]),
    ("Mark Udo", 75, 68, 61, 64, [58, 59, 61]),
    ("Joy Ikenna", 78, 74, 67, 65, [60, 62, 62]),
    ("Ahmed Ladan", 76, 62, 63, 62, [57, 59, 60]),
    ("Linda Etim", 75, 58, 60, 64, [56, 58, 59]),
    ("Samuel Ojo", 76, 66, 62, 63, [58, 57, 60]),
    ("Grace Anya", 75, 52, 58, 60, [55, 57, 58]),
    ("Idris Abubakar", 77, 82, 71, 73, [65, 67, 70]),
    ("Blessing Ede", 76, 88, 73, 75, [68, 70, 73]),
    ("Victor Nnadi", 75, 76, 69, 67, [65, 66, 68]),
    ("Hauwa Kabir", 76, 84, 72, 70, [66, 68, 70]),
    ("Daniel Ogar", 75, 70, 64, 66, [62, 63, 65]),
]


def print_summary() -> None:
    n = len(STUDENTS)
    avg_score = sum(s[5][-1] for s in STUDENTS) / n
    avg_att = sum(s[1] for s in STUDENTS) / n
    declining = sum(1 for s in STUDENTS if s[5][0] > s[5][1] > s[5][2])
    low_att = sum(1 for s in STUDENTS if s[1] < 75)
    low_practice = sum(1 for s in STUDENTS if s[2] < 50)
    print(f"Students: {n}")
    print(f"Average score: {avg_score:.0f}%")
    print(f"Average attendance: {avg_att:.0f}%")
    print(f"Declining scores: {declining}")
    print(f"Attendance below 75%: {low_att}")
    print(f"Incomplete practice: {low_practice}")


def seed() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.add_all(
            Student(
                name=name,
                class_name=CLASS_NAME,
                attendance=att,
                practice_completion=practice,
                speaking=speaking,
                listening=listening,
                recent_scores=scores,
            )
            for name, att, practice, speaking, listening, scores in STUDENTS
        )
        db.commit()
    print("Seeded database.")
    print_summary()


if __name__ == "__main__":
    seed()